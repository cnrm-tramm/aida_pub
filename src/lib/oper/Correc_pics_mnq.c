/****************************************************************
* OPERATOR 	Correc_pics_mnq  FUNCTION  ANSI-C
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
* VERSION       1.0
*
* ARGUMENTS 	IN 	float 	X   		parametre brut	
*		IN 	float 	seuil		seuil de detection d'un saut
*		IN 	float 	seuil_mnq	seuil d'un saut apres 1 manquante
*		IN 	float	seuil_duree	nombre maximum de points invalides consecutifs a remplacer par une interpolation lineaire
* 		OUT 	float 	flag 		flag concernant la detection de pic
* 		OUT 	float 	Xcor 		parametre corrige
*
* ENTRY		NONE
*
* SUBPROGRAMS 	NONE
* 
* REFERENCES	NONE
*
* CHANGES       Cet opérateur est une version corrigee de "Correc_pics_mnq"
* 		  - correction d'une bug qui ne permettait pas de detecter les    
* 		  pics vers le bas après ou avant une valeur manquante
* 		  - correction d'un comportement qui ne corrigeait jamais les sauts
* 		  se produisant avant une valeur manquante. "Correc_pics_mnq" flague 
* 		  uniquement la valeur sans la corriger
* 		  - correction des pics successifs
* 		  - ajout d'un seuil de duree pour le remplacement des pics 
* 		  simples (pas avant ou apres une valeur manquante) detectes par
* 		  une interpolation lineaire
*
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
Correc_pics_mnq (unsigned long Nloop,
		 const float *X, 
		 const float seuil,
		 const float seuil_mnq, 
		 const float seuil_duree, 
		 float *flag, 
		 float *Xcor,
		 unsigned long *Tab_diagno)
{
  unsigned long i,j;
  long idx_last_Xok, idx_last_Xmnq, idx_last_pic_mnq;
  long nbsaut;
  long nbsaut_mnq, nb_forte_variation;
  /* Même si i parcourt toute l'étendue des "unsigned", on peut utiliser 
   * nbsaut en "signed", car il est limité à Nloop/3. */
  const float misval_out = K_NaN;
  float a;


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
/*si la premiere valeur existe : on regarde si elle n'est pas un 1/2 pic */
/* on considere que la 1ere valeur vient après une valeur manquante */
  if ((X[0] - X[1]) > seuil_mnq) 
  /*demi pic negatif  */
      {
        Xcor[0] = misval_out;
        flag[0] = -3;
	nbsaut_mnq = nbsaut_mnq + 1;
     }
  else if ((X[1] - X[0]) > seuil_mnq)
     {
 /*demi pic positif  */
       Xcor[0] = misval_out;
       flag[0] = -2;
       nbsaut_mnq = nbsaut_mnq + 1;
     }
  else 
     {
       Xcor[0] = X[0];
       flag[0] = 0;
     }

/* traitement de la derniere valeur */

  if ((X[Nloop-2] - X[Nloop-1]) > seuil_mnq)
  /*demi pic negatif  */
      {
        Xcor[Nloop-1] = misval_out;
        flag[Nloop-1] = -3;
	nbsaut_mnq = nbsaut_mnq + 1;
     }
  else if ((X[Nloop-1] - X[Nloop-2]) > seuil_mnq)
     {
 /*demi pic positif  */
       Xcor[Nloop-1] = misval_out;
       flag[Nloop-1] = -2;
       nbsaut_mnq = nbsaut_mnq + 1;
     }
  else 
     {
       Xcor[Nloop-1] = X[Nloop-1];
       flag[Nloop-1] = 0;
     }

/*Boucle principale*/
  for (i = 1; i < (Nloop - 1); i++)
    {
/*	  printf (" X (i-1) (i) (i+1) = %g %g %g\n",
		   X[i - 1], X[i], X[i + 1] ); */
/*	  printf ("|dXi|=%f , |dXi+1|=%f \n",
		   fabs (X[i] - X[i - 1]), fabs (X[i + 1] - X[i])); */
      if (((X[i] - X[i - 1]) > seuil) && ((X[i] - X[i + 1]) > seuil))
	      /*** Pic vers le haut ***/
	{
	  /*fprintf (stderr, "|dXi|=%g , |dXi+1|=%g \n",
		   (X[i] - X[i - 1]), (X[i + 1] - X[i]));
		   */
	  Xcor[i] = misval_out;
	  flag[i] = 1;
	  nbsaut = nbsaut + 1;
	}
      else if (((X[i - 1] - X[i]) > seuil) && ((X[i + 1] - X[i]) > seuil))
	      /*** Pic vers le bas ***/
	{
	/*
	  fprintf (stderr, "|dXi|=%g , |dXi+1|=%g \n",
		   (X[i] - X[i - 1]), (X[i + 1] - X[i]));
		   */
	  Xcor[i] = misval_out;
	  flag[i] = -1;
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
      else if (!isfinite (X[i - 1]) && ((X[i+1] - X[i]) > seuil_mnq))
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
	{
	  Xcor[i] = misval_out;
	  flag[i] = 2;
	  nbsaut_mnq = nbsaut_mnq + 1;
	}
      else if (!isfinite (X[i - 1]) && ((X[i] - X[i+1]) > seuil_mnq))
	/*demi pic negatif apres */
	/* Valeur i-1 manquante avant pic --> valeur mnq */
	{
	  Xcor[i] = misval_out;
	  flag[i] = -3;
	  nbsaut_mnq = nbsaut_mnq + 1;
	}
      else if (!isfinite (X[i + 1]) && ((X[i-1] - X[i]) > seuil_mnq))
	/*demi pic negatif avant */
	/* Valeur i+1 manquante apres pic */
	{
	  Xcor[i] = misval_out;
	  flag[i] = -2;
	  nbsaut_mnq = nbsaut_mnq + 1;
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
  
/* 2eme boucle pour combler les trous genere par la suppression des pics simple
 flag=1 ou -1 ) */
  idx_last_Xok = -1; 
  idx_last_Xmnq = -1; 
  idx_last_pic_mnq = -1; 

  if ( flag[0] == 0 )
      idx_last_Xok = 0; 
  if ( !isfinite ( X[i] ) ) 
      idx_last_Xmnq = 0;

  for ( i = 1; i < Nloop; i++ )
   {
    if ( (fabs( flag[i])==2) || ( fabs( flag[i])==3 )  ) 
      {
       idx_last_pic_mnq = i; 
      } 
    else if ((flag[i] == 0) || (fabs( flag[i]) == 4) ) 
      {
	if ( ( fabs(flag[i-1]) == 1. ) && 
	   ( idx_last_Xmnq < idx_last_Xok ) && 
           ( idx_last_pic_mnq < idx_last_Xok ) &&
           ( (i - idx_last_Xok - 1 ) <= seuil_duree )  )
	/* cas ou la periode invalide contient que des sauts simples 
	 * flag = 1 ou -1 et ne contient pas de valeurs manquantes
	 * dus signal X d'origine 
	 * on laisse volontairement les valeurs manquantes originales de X */
	   {	
            a = (X[i] - X[idx_last_Xok])/(float)(i - idx_last_Xok); 
	    for ( j = idx_last_Xok +1; j < i; j++)
	      {
		Xcor[j] = (float)(j-idx_last_Xok) * a + X[idx_last_Xok];
	      }

           }
	  
         idx_last_Xok = i ;
	 if ( !isfinite ( X[i] ) ) 
	   idx_last_Xmnq = i;
       
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
OP_Correc_pics_mnq (unsigned long Nbval, void *ArgList[], char *DiagExec)
{
  long CodRet;
  unsigned long diagno[3];
  int N;

  N =
    sprintf (DiagExec, "Seuil= %f ; Seuil_mnq= %f", *((float *) ArgList[1]),
	     *((float *) ArgList[2]));

  if (N > 0)
    DiagExec += N;

  CodRet = Correc_pics_mnq (Nbval,
			    (float *) ArgList[0],
			    *((float *) ArgList[1]), 
			    *((float *) ArgList[2]),
			    *((float *) ArgList[3]),
			    (float *) ArgList[4],
			    (float *) ArgList[5], diagno);

  if (CodRet < 0)
    {
      (void) strcat (DiagExec, "Trop grand nombre de sauts : Abandon\n");
    }
  else if (CodRet >= 0)
    {
      (void) sprintf (DiagExec,
		      "; Pics corriges= %lu- Idem apres MNQ= %lu- Var. fortes non cor= %lu\n",
		      diagno[0], diagno[1], diagno[2]);
    }
  return OP_OK;
}

void
ID_Correc_pics_mnq (oper * optr)
{
  strcpy (optr->Nom, "Correc_pics_mnq");
  optr->Version = "$Revision: 5097 $";
  optr->Date = "$Date: 2013-03-25 13:23:40 +0100 (lun. 25 mars 2013) $";
  optr->fctptr = OP_Correc_pics_mnq;
  optr->NbArg = 6;

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

/* seuil_duree */
  optr->Arg_Car[3].direction = DIR_IN;
  optr->Arg_Car[3].categorie = COEFFICIENT;
  optr->Arg_Car[3].typ = ATYC_IF32;
  optr->Arg_Car[3].array_dim = "1";
  optr->Arg_Car[3].unite = "";
  optr->Arg_Car[3].type_sample = NULL;
  optr->Arg_Car[3].sample = NULL;


  /* flag */
  optr->Arg_Car[4].direction = DIR_OUT;
  optr->Arg_Car[4].categorie = VECTOR;
  optr->Arg_Car[4].typ = ATYC_IF32;
  optr->Arg_Car[4].array_dim = "1";
  optr->Arg_Car[4].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[4].sample = "$Arg1.sample";
  optr->Arg_Car[4].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[4].ref_time = "$Arg1.ref_time";
  optr->Arg_Car[4].unite = "";
  optr->Arg_Car[4].famille = "\"controle\"";
  optr->Arg_Car[4].misval = "$Arg1.misval";

  /* Xcor */
  optr->Arg_Car[5].direction = DIR_OUT;
  optr->Arg_Car[5].categorie = VECTOR;
  optr->Arg_Car[5].typ = ATYC_IF32;
  optr->Arg_Car[5].array_dim = "1";
  optr->Arg_Car[5].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[5].sample = "$Arg1.sample";
  optr->Arg_Car[5].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[5].ref_time = "$Arg1.ref_time";
  optr->Arg_Car[5].unite = "$Arg1.unit";
  optr->Arg_Car[5].famille = "$Arg1.famille";
  optr->Arg_Car[5].misval = "$Arg1.misval";
  optr->Arg_Car[5].name = "$Arg1.name + \" sans pics isolés\" ";
  optr->Arg_Car[5].en_name =
    "$Arg1.english_name + \", with isolated peaks removed\" ";
}
