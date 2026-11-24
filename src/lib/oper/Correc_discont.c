/****************************************************************
* OPERATOR 	Correc_discont  FUNCTION  ANSI-C
* 
* PURPOSE	correction of discontinuities in time series.
*
* DESCRIPTION   Cette fonction "corrige" les discontinuités
*	   	rencontrées dans des séries temporelles.
*               Une valeur particulière d'une série temporelle fait
*               partie d'une discontinuité si :
*                    - elle est hors de bornes de "normalité"
*                    - l'écart avec la précédente valeur correcte est
*                      supérieur à un seuil
*
* VERSION         1.1
*
* ARGUMENTS 	IN 	float 	X   	    parametre brut	
*		IN 	float 	borne_inf   valeur min. permise
*		IN 	float 	borne_sup   valeur max. permise
*		IN 	int 	seuil_saut  ecart max permis (en val. absolue)
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

/* pour pouvoir utiliser la fonction isfinite */
/*
#define __HPUX_SOURCE 1
*/
#define _HPUX_SOURCE 1


#include <stdio.h>
#include <string.h>
#include <limits.h>
#include <math.h>
#include "struct_oper.h"

unsigned long
Correc_discont (unsigned long Nloop,
		const float *X,
		const float borne_inf,
		const float borne_sup,
		const float seuil_saut,
		const int seuil_duree,
		const float MisVal,
		float *Xcor)
{
  unsigned long i, j;
  unsigned long nbsup, nbinf, nbabs, nbOK;
  unsigned long duree_trou;
  int Flag_OK;
  const float *last_X_ok;
  float X_courant;
  double Tmp_coeff;

  if (borne_inf >= borne_sup)
    {
      return ULONG_MAX;
    }

  if ((MisVal > borne_inf) && (MisVal < borne_sup))
    {
      (void) fprintf (stderr,
       "Bizarre : Misval(%g) est dans l'intervalle [min, max] ([%g, %g])\n",
		      MisVal, borne_inf, borne_sup);
    }

  nbsup = 0;
  nbinf = 0;
  nbabs = 0;
  nbOK = 0;
  last_X_ok = NULL;
  duree_trou = 0;
  for (i = 0; i < Nloop; i++)
    {
      X_courant = *X;
      /* Valeur présente ?   */
      if (X_courant == MisVal)
	{
	  nbabs = nbabs + 1;
	  Flag_OK = 0;
	}
      /* Valeur correctement représentée par un float ?   */
      if (!isfinite(X_courant))
	{
	  nbabs = nbabs + 1;
	  Flag_OK = 0;
	}
      /* Valeur dans les bornes ? */
      else if (X_courant > borne_sup)
	{
	  nbsup = nbsup + 1;
	  Flag_OK = 0;
	}
      else if (X_courant < borne_inf)
	{
	  nbinf = nbinf + 1;
	  Flag_OK = 0;
	}
      /*  Valeur proche de la précédente ? */
      else if (last_X_ok != NULL)
	{
	  if (fabs (*last_X_ok - X_courant) > seuil_saut)
	    {
	      nbinf = nbinf + 1;
	      Flag_OK = 0;
	    }
	  else
	    {
	      nbOK = nbOK + 1;
	      Flag_OK = 1;
	    }
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
		      *Xcor = ((duree_trou - j) * *last_X_ok + (j + 1) * *X) * Tmp_coeff;
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
  if (nbsup + nbinf + nbabs + nbOK != Nloop)
    {
      (void) fprintf (stderr, "Internal error : \n");
    }
  /* Et Nb_cor (si on le calculait) doit être égal à  nbsup + nbinf + nbabs */

  return nbsup + nbinf + nbabs;
}

/* fonction d'enrobage */

int
OP_Correc_discont (unsigned long Nbval, void *ArgList[], char *DiagExec)
{
  unsigned long CodRet;

  /* sprintf (DiagExec,""); */

  CodRet = Correc_discont (Nbval,
			   (float *) ArgList[0],
			   *((float *) ArgList[1]),
			   *((float *) ArgList[2]),
			   *((float *) ArgList[3]),
			   *((int *) ArgList[4]),
			   *((float *) ArgList[5]),
			   (float *) ArgList[6]);

  if (CodRet == ULONG_MAX)
    {
      sprintf (DiagExec, "Error : borne_min >= borne_max");
      return OP_FAIL;
    }
  else
    {
      sprintf (DiagExec, "%lu valeurs (sur %lu) corrigées", CodRet, Nbval);
      return OP_OK;
    }

}

void
ID_Correc_discont (oper * optr)
{
  strcpy (optr->Nom, "Correc_discont");
  optr->Version = "1.0";
  optr->Date = "04/19/99";
  optr->fctptr = OP_Correc_discont;
  optr->misval_auto = 0;	/* Cette fct gère elle-même les misval.*/
  optr->NbArg = 7;
  optr->Arg_Car[0].direction = DIR_IN;
  optr->Arg_Car[0].categorie = VECTOR;
  optr->Arg_Car[0].typ = ATYC_IF32;
  optr->Arg_Car[0].array_dim = "1";
  optr->Arg_Car[0].unite = "";
  optr->Arg_Car[0].type_sample = "any";
  optr->Arg_Car[0].sample = "any";

  optr->Arg_Car[1].direction = DIR_IN;
  optr->Arg_Car[1].categorie = COEFFICIENT;
  optr->Arg_Car[1].typ = ATYC_IF32;
  optr->Arg_Car[1].array_dim = "1";
  optr->Arg_Car[1].unite = "";
  optr->Arg_Car[1].type_sample = NULL;
  optr->Arg_Car[1].sample = NULL;

  optr->Arg_Car[2].direction = DIR_IN;
  optr->Arg_Car[2].categorie = COEFFICIENT;
  optr->Arg_Car[2].typ = ATYC_IF32;
  optr->Arg_Car[2].array_dim = "1";
  optr->Arg_Car[2].unite = "";
  optr->Arg_Car[2].type_sample = NULL;
  optr->Arg_Car[2].sample = NULL;

  optr->Arg_Car[3].direction = DIR_IN;
  optr->Arg_Car[3].categorie = COEFFICIENT;
  optr->Arg_Car[3].typ = ATYC_IF32;
  optr->Arg_Car[3].array_dim = "1";
  optr->Arg_Car[3].unite = "";
  optr->Arg_Car[3].type_sample = NULL;
  optr->Arg_Car[3].sample = NULL;

  optr->Arg_Car[4].direction = DIR_IN;
  optr->Arg_Car[4].categorie = COEFFICIENT;
  optr->Arg_Car[4].typ = ATYC_I32;
  optr->Arg_Car[4].array_dim = "1";
  optr->Arg_Car[4].unite = "";
  optr->Arg_Car[4].type_sample = NULL;
  optr->Arg_Car[4].sample = NULL;

  optr->Arg_Car[5].direction = DIR_IN;
  optr->Arg_Car[5].categorie = COEFFICIENT;
  optr->Arg_Car[5].typ = ATYC_IF32;
  optr->Arg_Car[5].array_dim = "1";
  optr->Arg_Car[5].unite = "";
  optr->Arg_Car[5].type_sample = NULL;
  optr->Arg_Car[5].sample = NULL;

  optr->Arg_Car[6].direction = DIR_OUT;
  optr->Arg_Car[6].categorie = VECTOR;
  optr->Arg_Car[6].typ = ATYC_IF32;
  optr->Arg_Car[6].array_dim = "1";
  optr->Arg_Car[6].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[6].sample = "$Arg1.sample";
  optr->Arg_Car[6].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[6].ref_time = "$Arg1.ref_time";
  optr->Arg_Car[6].unite = "$Arg1.unit";
  optr->Arg_Car[6].famille = "$Arg1.famille";
  optr->Arg_Car[6].misval = "$Arg6";
}
