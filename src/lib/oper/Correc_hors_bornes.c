/****************************************************************
* OPERATOR 	Correc_hors_bornes  FUNCTION  ANSI-C
* 
* PURPOSE	correction of out-of-range values 
*
* DESCRIPTION   Cette fonction "corrige" les valeurs
*	   	hors de bornes. La nature de la correction
*		est paramètrable : 
*                    Les series "hors bornes" de durée <= seuil_duree
*                          sont remplacées par une interpolation
*                    Les series "hors bornes" de durée > seuil_duree
*                          sont remplacées par des "valeur manquantes"
*
*
* VERSION       $Revision$
*
* ARGUMENTS 	IN 	float 	X   	    parametre brut	
*		IN 	float 	borne_inf   valeur min. permise
*		IN 	float 	borne_sup   valeur max. permise
*		IN 	int 	seuil_duree Nb pt max ou on interpolle.
*		IN 	float 	MisVal      Special value for missing data
* 		OUT 	float 	Xcor 	    parametre corrige
*
* ENTRY		NONE
*
* SUBPROGRAMS 	NONE
* 
* REFERENCES	NONE
*
* CHANGES       1.2   
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

/* Pour la fonction isfinite */
#define _HPUX_SOURCE 1


#include <stdio.h>
#include <string.h>
#include <limits.h>
#include <math.h>
#include "struct_oper.h"

unsigned long
Correc_hors_bornes (unsigned long Nloop,
		    const float *X,
		    const float borne_inf,
		    const float borne_sup,
		    const int seuil_duree,
		    const float MisVal,
		    float *Xcor,
		    unsigned long *Tab_diagno)
{
  unsigned long i, j;
  unsigned long nb_sup, nb_inf, nb_abs, nb_NaN, nbOK;
  unsigned long duree_trou;
  int Flag_OK;
  const float *last_X_ok;
  float X_courant;
  double Tmp_coeff;

  if (borne_inf >= borne_sup)
    {
      Tab_diagno[0] = 0;
      Tab_diagno[1] = Nloop;
      Tab_diagno[2] = Nloop;
      Tab_diagno[3] = Nloop;
      Tab_diagno[4] = Nloop;
      return ULONG_MAX;
    }

  if ((MisVal > borne_inf) && (MisVal < borne_sup))
    {
      (void) fprintf (stderr,
		      "Bizarre : Misval(%g) est dans l'intervalle [min, max] ([%g, %g])\n",
		      MisVal, borne_inf, borne_sup);
    }

  nb_sup = 0;
  nb_inf = 0;
  nb_abs = 0;
  nb_NaN = 0;
  nbOK = 0;
  last_X_ok = NULL;
  duree_trou = 0;
  for (i = 0; i < Nloop; i++)
    {
      X_courant = *X;
      /* Valeur correctement représentée par un float ?   */
      if (!isfinite (X_courant))
	{
	  nb_NaN = nb_NaN + 1;
	  Flag_OK = 0;
	}
      else if (X_courant == MisVal)
	{
	  nb_abs = nb_abs + 1;
	  Flag_OK = 0;
	}
      else if (X_courant > borne_sup)
	{
	  nb_sup = nb_sup + 1;
	  Flag_OK = 0;
	}
      else if (X_courant < borne_inf)
	{
	  nb_inf = nb_inf + 1;
	  Flag_OK = 0;
	}
      else
	{
	  nbOK = nbOK + 1;
	  Flag_OK = 1;
	}

      if (Flag_OK == 1)
	{
	  /*   Si cette valeur OK suit un "trou" (suite continue de */
	  /* valeurs invalides), il faut d'abord "boucher ce trou". */
	  if (duree_trou > seuil_duree)
	    {			/* Le trou entre last_X_ok et X. est "long" */
	      /* on remplit par des "valeurs manquantes" */
	      for (j = 0; j < duree_trou; j++)
		{
		  *Xcor = MisVal;
		  Xcor++;
		}
	    }
	  else if (duree_trou != 0)
	    {			/* Le trou entre last_X_ok et X. est "court" */
	      if (last_X_ok == NULL)
		{		/* Que faire ? */
		  for (j = 0; j < duree_trou; j++)
		    {
		      *Xcor = *X;
		      Xcor++;
		    }
		}
	      else
		{		/* Interpolation */
		  Tmp_coeff = 1.0 / (duree_trou + 1);
		  for (j = 0; j < duree_trou; j++)
		    {
		      *Xcor = ((duree_trou - j) * *last_X_ok +
			 (j + 1) * *X) * Tmp_coeff;
		      Xcor++;
		    }
		}
	    }
	  /* Et dans TOUS LES CAS, on recopie la valeur actuelle. */
	  *Xcor = *X;
	  Xcor++;
	  last_X_ok = X;
	  duree_trou = 0;
	}
      else
	{
	  duree_trou = duree_trou + 1;
	}

      X++;
    }
  /* La boucle est finie... */
  /* Mais toutes les corrections n'ont peut-être pas été faites */

  if (last_X_ok == NULL)
    {				/* Y'a pas une seule valeur bonne !! */
      for (j = 0; j < duree_trou; j++)
	{
	  *Xcor = MisVal;
	  Xcor++;
	}
    }
  else if (duree_trou > seuil_duree)
    {				/* Il y a un GRAND trou avant la fin.  */
      for (j = 0; j < duree_trou; j++)
	{
	  *Xcor = MisVal;
	  Xcor++;
	}

    }
  else if (duree_trou > 0)
    {				/* Il y a un petit trou avant la fin.  */
      for (j = 0; j < duree_trou; j++)
	{
	  *Xcor = *last_X_ok;
	  Xcor++;
	}
    }

  /* Test de validité interne */
  if (nb_sup + nb_inf + nb_abs + nb_NaN + nbOK != Nloop)
    {
      (void) fprintf (stderr, "internal error : \n");
    }
  /* Et Nb_cor (si on le calculait) doit être égal à  nb_sup + nb_inf + nb_abs */

  Tab_diagno[0] = nbOK;
  Tab_diagno[1] = nb_sup;
  Tab_diagno[2] = nb_inf;
  Tab_diagno[3] = nb_abs;
  Tab_diagno[4] = nb_NaN;
  return nb_sup + nb_inf + nb_abs + nb_NaN;
}

/* fonction d'enrobage */

int
OP_Correc_hors_bornes (unsigned long Nbval, void *ArgList[], char *DiagExec)
{
  unsigned long CodRet;
  unsigned long toto[5];
  int N;

  N = sprintf (DiagExec,
	       "Correc_hors_bornes : %lu ech, gamme = [%g, %g], nb_ech_max_interpol = %d",
	       Nbval, *((float *) ArgList[1]), *((float *) ArgList[2]),
               *((int *) ArgList[3]));
  if (N > 0)
    DiagExec += N;

  CodRet = Correc_hors_bornes (Nbval,
			       (float *) ArgList[0],
			       *((float *) ArgList[1]),
			       *((float *) ArgList[2]),
			       *((int *) ArgList[3]),
			       *((float *) ArgList[4]),
			       (float *) ArgList[5],
			       toto);

  if (CodRet == ULONG_MAX)
    {
      sprintf (DiagExec, "Error : borne_min >= borne_max");
      return OP_FAIL;
    }
  else
    {
      sprintf (DiagExec,
	       "%lu valeurs (sur %lu) rejetée(s) [s:%lu, i:%lu, a:%lu, n:%lu]",
	       CodRet, Nbval, toto[1], toto[2], toto[3], toto[4]);
      return OP_OK;
    }

}

void
ID_Correc_hors_bornes (oper * optr)
{
  strcpy (optr->Nom, "Correc_hors_bornes");
  optr->Version = "$Revision$";
  optr->Date = "$Date$";
  optr->fctptr = OP_Correc_hors_bornes;
  optr->NbArg = 6;
  optr->misval_auto = 0;	/*On traite explicitement misval */

  /*    X       */
  optr->Arg_Car[0].direction = DIR_IN;
  optr->Arg_Car[0].categorie = VECTOR;
  optr->Arg_Car[0].typ = ATYC_IF32;
  optr->Arg_Car[0].array_dim = "1";
  optr->Arg_Car[0].unite = "";
  optr->Arg_Car[0].type_sample = "any";
  optr->Arg_Car[0].sample = "any";

  /*    borne_inf       */
  optr->Arg_Car[1].direction = DIR_IN;
  optr->Arg_Car[1].categorie = COEFFICIENT;
  optr->Arg_Car[1].typ = ATYC_IF32;
  optr->Arg_Car[1].array_dim = "1";
  optr->Arg_Car[1].unite = "";
  optr->Arg_Car[1].type_sample = NULL;
  optr->Arg_Car[1].sample = NULL;

  /*    borne_sup       */
  optr->Arg_Car[2].direction = DIR_IN;
  optr->Arg_Car[2].categorie = COEFFICIENT;
  optr->Arg_Car[2].typ = ATYC_IF32;
  optr->Arg_Car[2].array_dim = "1";
  optr->Arg_Car[2].unite = "";
  optr->Arg_Car[2].type_sample = NULL;
  optr->Arg_Car[2].sample = NULL;

  /*    seuil_duree  */
  optr->Arg_Car[3].direction = DIR_IN;
  optr->Arg_Car[3].categorie = COEFFICIENT;
  optr->Arg_Car[3].typ = ATYC_I32;
  optr->Arg_Car[3].array_dim = "1";
  optr->Arg_Car[3].unite = "";
  optr->Arg_Car[3].type_sample = NULL;
  optr->Arg_Car[3].sample = NULL;

  optr->Arg_Car[4].direction = DIR_IN;
  optr->Arg_Car[4].categorie = COEFFICIENT;
  optr->Arg_Car[4].typ = ATYC_IF32;
  optr->Arg_Car[4].array_dim = "1";
  optr->Arg_Car[4].unite = "";
  optr->Arg_Car[4].type_sample = NULL;
  optr->Arg_Car[4].sample = NULL;

  /*    Xcor       */
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
  optr->Arg_Car[5].misval = "$Arg5";
  optr->Arg_Car[5].name = "$Arg1.name + \" sans valeurs hors-gamme\" ";
  optr->Arg_Car[5].en_name =
    "$Arg1.english_name + \", with only in-range values\" ";
}
