/****************************************************************
* OPERATOR 	Decale_quantile  FUNCTION  ANSI-C
* 
* PURPOSE	Correction of an offset in the baseline
*
* DESCRIPTION   Cette fonction enlève un offset à une mesure.
*	   	L'offest est estimé comme un quantile de la distribution
*
* VERSION       $Revision: 5097 $
*
* ARGUMENTS	IN   float   X            parametre brut	
*	        IN   float   Quantile     [0-1]
* 		OUT  float   Xcor 	  parametre corrige
*
* ENTRY		NONE
*
* SUBPROGRAMS 	NONE
* 
* REFERENCES	NONE
*
* CHANGES       
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

#include <math.h>
#include <stdlib.h>
#include <string.h>

#include <gsl/gsl_sort.h>
#include <gsl/gsl_statistics.h>

#include "struct_oper.h"

long
Decale_quantile (unsigned long NLoop,
		 const float *X,
		 const double quantile, double *base, float *X_dec)
{
  unsigned long i;
  long nb_val = 0;
  double *tmp_tab;

  if ((quantile < 0.0) || (quantile > 1.0))
    {
      return -2;
    }

  tmp_tab = calloc (NLoop, sizeof (double));
  if (tmp_tab == NULL)
    {
      return -1;
    }

  for (i = 0; i < NLoop; i++)
    {
      if (isfinite (X[i]))
	{
	  tmp_tab[nb_val] = X[i];
	  nb_val++;
	}
    }

  gsl_sort (tmp_tab, 1, nb_val);
  *base = gsl_stats_quantile_from_sorted_data (tmp_tab, 1, nb_val, quantile);
  free (tmp_tab);

  for (i = 0; i < NLoop; i++)
    {
      *X_dec = *X - *base;

      X++;
      X_dec++;
    }

  return nb_val;
}

/* la fonction d'enrobage classique */

int
OP_Decale_quantile (unsigned long NbVal, void *ArgList[], char *DiagExec)
{
  long CodRet;
  double base;

  (void) sprintf (DiagExec,
		  "OP_Decale_quantile, NbVal=%lu, quantile=%f)",
		  NbVal, *((float *) ArgList[0]));

  CodRet = Decale_quantile (NbVal,
			    (float *) ArgList[0],
			    *((double *) ArgList[1]),
			    &base, (float *) ArgList[2]);

  switch (CodRet)
    {
    case -1:
      /* Dans la version actuelle, cela ne devrait jamais arriver */
      strcat (DiagExec, "Alloc. memoire ratée");
      return OP_FAIL;
    case -2:
      sprintf (DiagExec, "Quantile %g hors de [0.0, 1.0]",
	       *((double *) ArgList[1]));
      return OP_FAIL;
    default:
      sprintf (DiagExec, "Valeur du quantile %g : %g",
	       *((double *) ArgList[1]), base);
      return OP_OK;
    }
}

void
ID_Decale_quantile (oper * optr)
{
  int i;
  strcpy (optr->Nom, "Decale_quantile");
  optr->Version = "$Revision: 5097 $";
  optr->Date = "$Date: 2013-03-25 13:23:40 +0100 (lun. 25 mars 2013) $";
  optr->fctptr = OP_Decale_quantile;
  optr->misval_auto = 1;	/* gestion auto des misval */
  optr->NbArg = 3;
  i = 0;

  /* X */
  optr->Arg_Car[i].direction = DIR_IN;
  optr->Arg_Car[i].categorie = VECTOR;
  optr->Arg_Car[i].typ = ATYC_IF32;
  optr->Arg_Car[i].array_dim = "1";
  optr->Arg_Car[i].type_sample = "any";
  optr->Arg_Car[i].sample = "any";
  optr->Arg_Car[i].unite = "any";
  i++;

  /* Quantile */
  optr->Arg_Car[i].direction = DIR_IN;
  optr->Arg_Car[i].categorie = COEFFICIENT;
  optr->Arg_Car[i].typ = ATYC_IF64;
  optr->Arg_Car[i].array_dim = "1";
  optr->Arg_Car[i].unite = "1";
  i++;

  /* X_cor */
  optr->Arg_Car[i].direction = DIR_OUT;
  optr->Arg_Car[i].categorie = VECTOR;
  optr->Arg_Car[i].typ = ATYC_IF32;
  optr->Arg_Car[i].array_dim = "1";
  optr->Arg_Car[i].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[i].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[i].sample = "$Arg1.sample";
  optr->Arg_Car[i].ref_time = "$Arg1.ref_time";
  optr->Arg_Car[i].misval = "-99999.0";
  optr->Arg_Car[i].unite = "$Arg1.unit";
  optr->Arg_Car[i].famille = "$Arg1.famille";
}
