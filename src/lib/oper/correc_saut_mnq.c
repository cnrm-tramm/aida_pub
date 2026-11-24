/****************************************************************
* OPERATOR 	correc_saut_mnq  FUNCTION  ANSI-C
* 
* PURPOSE	correction de pics
*
* DESCRIPTION   Cette fonction supprime les pics vers
*	   	le haut ou vers le bas qui se produisent
*		sur une seule valeur et qui sont superieurs
*		a un seuil: dans ce cas, la valeur en sortie
*		est une interpolation lineaire des points (i-1,i+1).
*		Cette fonction est une evolution de correc_saut 
*		permettant de supprimer les pics avant ou apres
*		une valeur manquante : dans ce cas, la valeur en
*		sortie est NaN et le seuil teste est seuil_mnq.
*		Cette fonction renvoie aussi un vecteur flag.
*
* VERSION       1.3
*
* ARGUMENTS 	IN 	float 	X   		parametre brut	
*		IN 	float 	seuil		seuil de detection d'un saut
*		IN 	float 	seuil_mnq	seuil d'un saut apres 1 manquant
* 		OUT 	float 	flag 		flag concernant la detection de pic
* 		OUT 	float 	Xcor 		parametre corrige
*
* ENTRY		NONE
*
* SUBPROGRAMS 	NONE
* 
* REFERENCES	NONE
*
* CHANGES      1.2 : rajout du flag en sortie et tests par rapport a seuil_mnq
*                    C.Berne 07/11/2005
* CHANGES      1.3 : rajout du traitement des pics au debut et a la fin
*                    O.Traulle 17/11/2006
* 
* COPYRIGHT 	Meteo-France
*		Centre de Recherches Meteorologiques
*		GMEI/TRAMM
*		42, av. G. Coriolis
*		31057	TOULOUSE cedex
*
******************************************************************/

#define _POSIX_SOURCE 1
#define _XOPEN_SOURCE 600

#include <stdio.h>
#include <string.h>
#include <math.h>
#include "struct_oper.h"

long
correc_saut_mnq (unsigned long Nloop,
		 const float *X, const float seuil,
		 const float seuil_mnq, float *flag, float *Xcor,
		 unsigned long *Tab_diagno)
{
  unsigned long i;
  signed long nbsaut;
  signed long nbsaut_mnq, nb_forte_variation;
  /* Même si i parcourt toute l'étendue des "unsigned", on peut utiliser 
   * nbsaut en "signed", car il est limité à Nloop/3. */
  const float misval_out = K_NaN;

  /*** correction vite fait d'un bug sur ces 4 valeurs de flag ***/
  flag[0] = flag[1] = flag[Nloop-2] = flag[Nloop-1] = 0. ;


  if (Nloop == 0)
    return 0;

  Xcor[0] = X[0];

  nbsaut = 0;
  nbsaut_mnq = 0;
  nb_forte_variation = 0;

/* Valeurs du flag :
*   Si la valeur X a ete remplacee par la moyenne (X-1,X+1) --> flag = 1 pour un pic
*#   Si la valeur X a ete remplacee par la moyenne (X-1,X+1) --> flag = -1 pour un pic negatif 
*   Si la valeur X a ete remplacee par valeur manquante
*   et  s'il s'agit d'un 1/2 pic positif avant une valeur manquante --> flag = 2
*   Si la valeur X a ete remplacee par valeur manquante
*   et  s'il s'agit d'un 1/2 pic negatif avant une valeur manquante --> flag = -2
*   Si la valeur X a ete remplacee par valeur manquante
*   et  s'il s'agit d'un 1/2 pic positif apres une valeur manquante --> flag = 3
*   Si la valeur X a ete remplacee par valeur manquante
*   et  s'il s'agit d'un 1/2 pic negatif apres une valeur manquante --> flag = -3
*   Si une variation positive importante est detectee (> seuil) --> flag = 4
*   Si une variation negative importante est detectee (> seuil) --> flag = -4
*   Si la valeur est OK --> flag = 0 */

/* traitement de la premiere valeur */
/*Xcor[0] = X[0];*/
/* si pas de valeurs manquantes ensuite*/
  if (isfinite (X[3]) && isfinite (X[2]) && isfinite (X[1]))
    {
/*si la premiere valeur existe : on regarde si elle n'est pas un 1/2 pic */
      if (isfinite (X[0]))
	{
	  if ((X[0] - X[1]) > seuil_mnq)
	    {
	      if ((X[2] - X[1]) > seuil)
		{
		  /*pic vers le bas */
		  Xcor[0] = X[0];
		  Xcor[1] = (X[0] + X[2]) / 2;
		  flag[1] = 1;
		  nbsaut = nbsaut + 1;
		}
	      else if ((X[1] - X[2]) > seuil)
		{
		/*** Forte variation  (negative)--> on flagge uniquement ***/
		  flag[1] = -4;
		  nb_forte_variation = nb_forte_variation + 1;
		}
	      else
		{
		  /*valeur trop haute (1/2 pic positif apres val mnq (en fait debut acquisition) : on invalide */
		  Xcor[0] = misval_out;
		  flag[0] = 3;
		  nbsaut = nbsaut + 1;
		}
	    }

	  else if ((X[1] - X[0]) > seuil_mnq)
	    {
	      if ((X[2] - X[1]) > seuil)
		{
		/*** Forte variation  (positive)--> on flagge uniquement ***/
		  flag[1] = 4;
		  nb_forte_variation = nb_forte_variation + 1;
		}
	      else if ((X[1] - X[2]) > seuil)
		{
		  /*pic vers le haut */
		  Xcor[0] = X[0];
		  Xcor[1] = (X[0] + X[2]) / 2;
		  flag[1] = 1;
		  nbsaut = nbsaut + 1;
		}
	      else
		{
		  /*deuxieme valeur apres val mnq trop basse : on invalide */
		  Xcor[0] = misval_out;
		  flag[2] = -3;
		  nbsaut = nbsaut + 1;
		}
	    }
	  else
	    {
	      Xcor[0] = X[0];
	      Xcor[1] = X[1];
	    }
	}

/* si la premiere valeur est manquante*/
      /* else */

      if (!isfinite (X[0]))
	{
	  if ((X[1] - X[2]) > seuil_mnq)
	    {
	      if ((X[3] - X[2]) > seuil)
		{
		  /*pic vers le bas apres valmnq */
		  Xcor[1] = X[1];
		  Xcor[2] = (X[1] + X[3]) / 2;
		  flag[2] = 1;
		  nbsaut = nbsaut + 1;
		}
	      else if ((X[2] - X[3]) > seuil)
		{
		/*** Forte variation  (negative)--> on flagge uniquement ***/
		  flag[1] = -4;
		  nb_forte_variation = nb_forte_variation + 1;
		}
	      else
		{
		  /*deuxieme valeur apres val mnq trop haute : on invalide */
		  Xcor[1] = misval_out;
		  flag[2] = 3;
		  nbsaut = nbsaut + 1;
		}
	    }
	  else if ((X[2] - X[1]) > seuil_mnq)
	    {
	      if ((X[3] - X[2]) > seuil)
		{
		/*** Forte variation  (positive)--> on flagge uniquement ***/
		  flag[1] = 4;
		  nb_forte_variation = nb_forte_variation + 1;
		}
	      else if ((X[2] - X[3]) > seuil)
		{
		  /*pic vers le haut apres valmnq */
		  Xcor[1] = X[1];
		  Xcor[2] = (X[1] + X[3]) / 2;
		  flag[2] = 1;
		  nbsaut = nbsaut + 1;
		}
	      else
		{
		  /*deuxieme valeur apres val mnq trop basse : on invalide */
		  Xcor[1] = misval_out;
		  flag[2] = -3;
		  nbsaut = nbsaut + 1;
		}
	    }
	  else
	    {
	      Xcor[0] = X[0];
	      Xcor[1] = X[1];
	    }
	}
    }
  else
    {
/*si une des valeurs est manquantes*/
      Xcor[1] = X[1];
      Xcor[2] = X[2];
      Xcor[3] = X[3];
    }


/*Traitement derniere valeur*/
  Xcor[Nloop - 1] = X[Nloop - 1];
/*si les 3 dernieres valeurs ne sont pas nulles*/
  if (isfinite (X[Nloop - 4]) && isfinite (X[Nloop - 3])
      && isfinite (X[Nloop - 2]))
    {
      /*si la derniere valeur existe */
      if (isfinite (X[Nloop - 1]))
	{
	  if ((X[Nloop - 1] - X[Nloop - 2]) > seuil_mnq)
	    {
	      if ((X[Nloop - 3] - X[Nloop - 2]) > seuil)
		{
		  /*pic vers le bas avant valmnq */
		  Xcor[Nloop - 1] = X[Nloop - 1];
		  Xcor[Nloop - 2] = (X[Nloop - 3] + X[Nloop - 1]) / 2;
		  flag[Nloop - 2] = 1;
		  nbsaut = nbsaut + 1;
		}
	      else if ((X[Nloop - 2] - X[Nloop - 3]) > seuil)
		{
				/*** Forte variation  (negative)--> on flagge uniquement ***/
		  flag[Nloop - 2] = -4;
		  nb_forte_variation = nb_forte_variation + 1;
		}
	      else
		{
		  /*deuxieme valeur avant val mnq trop haute : on invalide */
		  Xcor[Nloop - 1] = misval_out;
		  flag[Nloop - 1] = 2;
		  nbsaut = nbsaut + 1;
		}
	    }
	  else if ((X[Nloop - 2] - X[Nloop - 1]) > seuil_mnq)
	    {
	      if ((X[Nloop - 3] - X[Nloop - 2]) > seuil)
		{
				/*** Forte variation  (positive)--> on flagge uniquement ***/
		  flag[Nloop - 2] = 4;
		  nb_forte_variation = nb_forte_variation + 1;
		}
	      else if ((X[Nloop - 2] - X[Nloop - 3]) > seuil)
		{
		  /*pic vers le haut avant valmnq */
		  Xcor[Nloop - 1] = X[Nloop - 1];
		  Xcor[Nloop - 2] = (X[Nloop - 1] + X[Nloop - 3]) / 2;
		  flag[Nloop - 2] = 1;
		  nbsaut = nbsaut + 1;
		}
	      else
		{
		  /*deuxieme valeur avant val mnq trop basse : on invalide */
		  Xcor[Nloop - 1] = misval_out;
		  flag[Nloop - 1] = -2;
		  nbsaut = nbsaut + 1;
		}
	    }
	  else
	    {
	      Xcor[Nloop - 1] = X[Nloop - 1];
	      Xcor[Nloop - 2] = X[Nloop - 2];
	    }
	}

      /*si la derniere valeur est manquante */
      /*si pas de valeurs manquantes ensuite */
      if (!isfinite (X[Nloop - 1]))
	{
	  if ((X[Nloop - 2] - X[Nloop - 3]) > seuil_mnq)
	    {
	      if ((X[Nloop - 4] - X[Nloop - 3]) > seuil)
		{
		  /*pic vers le bas avant valmnq */
		  Xcor[Nloop - 2] = X[Nloop - 2];
		  Xcor[Nloop - 3] = (X[Nloop - 4] + X[Nloop - 2]) / 2;
		  flag[Nloop - 3] = 1;
		  nbsaut = nbsaut + 1;
		}
	      else if ((X[Nloop - 3] - X[Nloop - 4]) > seuil)
		{
				/*** Forte variation  (negative)--> on flagge uniquement ***/
		  flag[Nloop - 3] = -4;
		  nb_forte_variation = nb_forte_variation + 1;
		}
	      else
		{
		  /*deuxieme valeur avant val mnq trop haute : on invalide */
		  Xcor[Nloop - 2] = misval_out;
		  flag[Nloop - 3] = 2;
		  nbsaut = nbsaut + 1;
		}
	    }
	  else if ((X[Nloop - 3] - X[Nloop - 2]) > seuil_mnq)
	    {
	      if ((X[Nloop - 4] - X[Nloop - 3]) > seuil)
		{
				/*** Forte variation  (positive)--> on flagge uniquement ***/
		  flag[Nloop - 3] = 4;
		  nb_forte_variation = nb_forte_variation + 1;
		}
	      else if ((X[Nloop - 3] - X[Nloop - 4]) > seuil)
		{
		  /*pic vers le haut avant valmnq */
		  Xcor[Nloop - 2] = X[Nloop - 2];
		  Xcor[Nloop - 3] = (X[Nloop - 2] + X[Nloop - 4]) / 2;
		  flag[Nloop - 3] = 1;
		  nbsaut = nbsaut + 1;
		}
	      else
		{
		  /*deuxieme valeur avant val mnq trop basse : on invalide */
		  Xcor[Nloop - 2] = misval_out;
		  flag[Nloop - 3] = -2;
		  nbsaut = nbsaut + 1;
		}
	    }
	  else
	    {
	      Xcor[Nloop - 2] = X[Nloop - 2];
	      Xcor[Nloop - 3] = X[Nloop - 3];
	    }
	}
    }
  else
    {
/*une des valeurs est manquante ; ce sera traite dans la boucle principale*/
      Xcor[Nloop - 2] = X[Nloop - 2];
      Xcor[Nloop - 3] = X[Nloop - 3];
      Xcor[Nloop - 4] = X[Nloop - 4];
    }


/*Boucle principale*/
  for (i = 2; i < (Nloop - 2); i++)
    {
/*	  printf (" X (i-1) (i) (i+1) = %g %g %g\n",
		   X[i - 1], X[i], X[i + 1] ); */
/*	  printf ("|dXi|=%f , |dXi+1|=%f \n",
		   fabs (X[i] - X[i - 1]), fabs (X[i + 1] - X[i])); */
      if (((X[i] - X[i - 1]) > seuil) && ((X[i] - X[i + 1]) > seuil))
	      /*** Pic vers le haut ***/
	{
	  fprintf (stderr, "|dXi|=%g , |dXi+1|=%g \n",
		   (X[i] - X[i - 1]), (X[i + 1] - X[i]));
	  Xcor[i] = (X[i + 1] + X[i - 1]) / 2;
	  flag[i] = 1;
	  nbsaut = nbsaut + 1;
	}
      else if (((X[i - 1] - X[i]) > seuil) && ((X[i + 1] - X[i]) > seuil))
	      /*** Pic vers le bas ***/
	{
	  fprintf (stderr, "|dXi|=%g , |dXi+1|=%g \n",
		   (X[i] - X[i - 1]), (X[i + 1] - X[i]));
	  Xcor[i] = (X[i + 1] + X[i - 1]) / 2;
	  flag[i] = 1;
	  nbsaut = nbsaut + 1;
	}
      else if (((X[i + 1] - X[i]) > seuil) && ((X[i] - X[i - 1]) > seuil))
	      /*** Forte variation (positive) --> on flagge uniquement ***/
	{
	  Xcor[i] = X[i];
	  flag[i] = 4;
	  nb_forte_variation = nb_forte_variation + 1;
	}
      else if (((X[i - 1] - X[i]) > seuil) && ((X[i] - X[i + 1]) > seuil))
	      /*** Forte variation  (negative)--> on flagge uniquement ***/
	{
	  Xcor[i] = X[i];
	  flag[i] = -4;
	  nb_forte_variation = nb_forte_variation + 1;
	}
      else if (!isfinite (X[i - 1]) && ((X[i] - X[i + 1]) > seuil_mnq))
	/*demi pic positif apres */
	/* Valeur i-1 manquante avant pic --> valeur mnq */
	{
	  Xcor[i] = misval_out;
	  flag[i] = 3;
	  nbsaut_mnq = nbsaut_mnq + 1;
	}
      else if (!isfinite (X[i + 1]) && ((X[i] - X[i - 1]) > seuil_mnq))
	/*demi pic positif avant */
	/* Valeur i+1 manquante apres pic */
	/* On ne fait rien --> on flagge */
	{
	  Xcor[i] = X[i];
	  flag[i] = 2;
	}
      else
	{
	  Xcor[i] = X[i];
	  flag[i] = 0;
	}

      if (nbsaut >= Nloop / 3)
	{
	  /* ce qu'on est en train de faire n'a pas beaucoup de sens. */
	  /* ==> On annule tout !! */
	  for (i = 1; i < (Nloop); i++)
	    {
	      Xcor[i] = X[i];
	      flag[i] = 0;
	    }
	  return -nbsaut;
	}
    }

/*  Xcor[Nloop - 1] = X[Nloop - 1];*/

  Tab_diagno[0] = nbsaut;
  Tab_diagno[1] = nbsaut_mnq;
  Tab_diagno[2] = nb_forte_variation;

  return nbsaut + nbsaut_mnq + nb_forte_variation;
}

/* fonction d'enrobage */

int
OP_correc_saut_mnq (unsigned long Nbval, void *ArgList[], char *DiagExec)
{
  long CodRet;
  unsigned long toto[3];
  int N;

  N =
    sprintf (DiagExec, "Seuil= %f ; Seuil_mnq= %f", *((float *) ArgList[1]),
	     *((float *) ArgList[2]));

  if (N > 0)
    DiagExec += N;

  CodRet = correc_saut_mnq (Nbval,
			    (float *) ArgList[0],
			    *((float *) ArgList[1]), *((float *) ArgList[2]),
			    (float *) ArgList[3], (float *) ArgList[4], toto);

  if (CodRet < 0)
    {
      (void) strcat (DiagExec, "Trop grand nombre de sauts : Abandon\n");
    }
  else if (CodRet >= 0)
    {
      (void) sprintf (DiagExec,
		      "; Pics corriges= %lu- Idem apres MNQ= %lu- Var. fortes non cor= %lu\n",
		      toto[0], toto[1], toto[2]);
    }
  return OP_OK;
}

void
ID_correc_saut_mnq (oper * optr)
{
  strcpy (optr->Nom, "correc_saut_mnq");
  optr->Version = "$Revision$";
  optr->Date = "$Date$";
  optr->fctptr = OP_correc_saut_mnq;
  optr->NbArg = 5;
  optr->repl_oper = "Correc_pics_mnq";
  optr->repl_cause = "Ne corrige pas correctement les sauts avant ou apres une valeur manquante";


  /* X */
  optr->Arg_Car[0].direction = DIR_IN;
  optr->Arg_Car[0].categorie = VECTOR;
  optr->Arg_Car[0].typ = ATYC_IF32;
  optr->Arg_Car[0].array_dim = "1";
  optr->Arg_Car[0].unite = "";
  optr->Arg_Car[0].type_sample = "any";
  optr->Arg_Car[0].sample = "any";

  /* seuil */
  optr->Arg_Car[1].direction = DIR_IN;
  optr->Arg_Car[1].categorie = COEFFICIENT;
  optr->Arg_Car[1].typ = ATYC_IF32;
  optr->Arg_Car[1].array_dim = "1";
  optr->Arg_Car[1].unite = "";
  optr->Arg_Car[1].type_sample = NULL;
  optr->Arg_Car[1].sample = NULL;

  /* seuil_mnq */
  optr->Arg_Car[2].direction = DIR_IN;
  optr->Arg_Car[2].categorie = COEFFICIENT;
  optr->Arg_Car[2].typ = ATYC_IF32;
  optr->Arg_Car[2].array_dim = "1";
  optr->Arg_Car[2].unite = "";
  optr->Arg_Car[2].type_sample = NULL;
  optr->Arg_Car[2].sample = NULL;

  /* flag */
  optr->Arg_Car[3].direction = DIR_OUT;
  optr->Arg_Car[3].categorie = VECTOR;
  optr->Arg_Car[3].typ = ATYC_IF32;
  optr->Arg_Car[3].array_dim = "1";
  optr->Arg_Car[3].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[3].sample = "$Arg1.sample";
  optr->Arg_Car[3].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[3].ref_time = "$Arg1.ref_time";
  optr->Arg_Car[3].unite = "";
  optr->Arg_Car[3].famille = "\"controle\"";
  optr->Arg_Car[3].misval = "$Arg1.misval";

  /* Xcor */
  optr->Arg_Car[4].direction = DIR_OUT;
  optr->Arg_Car[4].categorie = VECTOR;
  optr->Arg_Car[4].typ = ATYC_IF32;
  optr->Arg_Car[4].array_dim = "1";
  optr->Arg_Car[4].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[4].sample = "$Arg1.sample";
  optr->Arg_Car[4].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[4].ref_time = "$Arg1.ref_time";
  optr->Arg_Car[4].unite = "$Arg1.unit";
  optr->Arg_Car[4].famille = "$Arg1.famille";
  optr->Arg_Car[4].misval = "$Arg1.misval";
  optr->Arg_Car[4].name = "$Arg1.name + \" sans pics isolés\" ";
  optr->Arg_Car[4].en_name =
    "$Arg1.english_name + \", with isolated peaks removed\" ";
}
