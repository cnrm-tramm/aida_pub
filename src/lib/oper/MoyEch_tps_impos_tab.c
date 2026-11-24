/*******************************************************************
* OPERATOR      MoyEch_tps_impos_tab.c FUNCTION ANSI-C
*
*
* PURPOSE 	Moyenne et échantillonnage d'une variable sur une autre base
*               de temps. 
*
*		
* DESCRIPTION	Cette fonction échantillonne une variable "Var_in"
*		qui est daté par le vecteur temps "time_in" sur une 
*		autre base de temps "time_out".
*		La variable resultat est "Var_out"		
*               On ne fait aucune supposition sur la régularité de
*               l'échantillonnage des 2 variables. Cette fonction peut
*		donc servir, par exemple, à transformer une serie temporelle
*               asynchrone en une série réguliere.
*		On suppose que time_in est "à peu près" trié par ordre
*               croissant.
*		 
* VERSION       $Revision$
*
* ARGUMENTS     IN  float   Var_in       any       variable de depart a échantillonner
*               IN  double  time_in    second      base de temps de depart
*               IN  double  Nb_Sec_ecart_avant second    Ecart AVANT sur lequel s'effectue la moyenne
*               IN  double  Nb_Sec_ecart_apres second    Ecart max APRES sur lequel s'effectue la moyenne
*               IN  int     tolerance_mnq   Nombre mini de valeur pour accepter de faire la moyenne (mettre 0 pour faire
*                                           la moyenne meme si un seul point !)
*               IN  double  time_out   second    base de temps d'arrivee
*               IN  int     size_out   any       Nb de valeurs dans la base de temps d'arrivee
*
*               OUT float   Var_out     same as "Var_in"  variable "Var_in" échantillonnée
*					             sur la base "time_out"	
*
* CHANGES 	NONE
*
* ENTRY         NONE
*
* SUBPROGRAMS   NONE
*
* REFERENCES     
*             
* COPYRIGHT     Meteo-France
*               Centre National de Recherches Meteorologiques
*               GMEI/TRAMM
*               42, av. G. Coriolis
*               31057   TOULOUSE cedex
*              
*******************************************************************/

#define _POSIX_SOURCE 1
#define _XOPEN_SOURCE 600

#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <math.h>
#include <limits.h>
#include <float.h>
#include "struct_oper.h"

long
MoyEch_tps_impos_tab (unsigned long size_in,
		      float *Var_in,
		      int dim_in,
		      double *time_in,
		      double Nb_Sec_ecart_avant,
		      double Nb_Sec_ecart_apres,
		      int tolerance_mnq,
		      double *time_out,
		      unsigned long size_out, float *Var_out, long TabStat[3])
{
  unsigned long i, j, j_inf;
  long k;
  long Nb_moy, Nb_zero, Nb_inf;
  long pre_diag;

  double time_inf, time_sup;

  double *loc_som;
  unsigned long *Nb_mnq;
  unsigned long *Nb_OK;
  const float misval_out = K_NaN;


  pre_diag = 0;

  if (dim_in <= 0)
    return -101;

  if (dim_in > 8192)
    return -102;

  if (tolerance_mnq <= 0)
    return -103;

  if (time_in[size_in - 1] < (time_out[0] - Nb_Sec_ecart_avant))
    {
      pre_diag = -1;
      Nb_zero = size_out*dim_in;
    }

  if ((time_out[size_out - 1] + Nb_Sec_ecart_apres) < time_in[0])
    {
      pre_diag = -2;
      Nb_zero = size_out*dim_in;
    }

  if ((Nb_Sec_ecart_avant + Nb_Sec_ecart_apres) <= 0)
    {
      pre_diag = -3;
      Nb_zero = size_out*dim_in;
    }

  if (pre_diag != 0)
    {
      for (i = 0; i < size_out; i++)
	{
	  for (k = 0; k < dim_in; k++)
	    {
	      Var_out[i * dim_in + k] = misval_out;
	    }
	}
      TabStat[0] = 0;		/* Nb_moy */
      TabStat[1] = Nb_zero;
      TabStat[2] = 0;		/* Nb_inf */
      return pre_diag;
    }



  Nb_OK = malloc (dim_in * sizeof (*Nb_OK));
  Nb_mnq = malloc (dim_in * sizeof (*Nb_mnq));
  loc_som = malloc (dim_in * sizeof (*loc_som));

  Nb_moy = 0;
  Nb_zero = 0;
  Nb_inf = 0;

  j_inf = 0;
  for (i = 0; i < size_out; i++)
    {
      time_inf = time_out[i] - Nb_Sec_ecart_avant;
      time_sup = time_out[i] + Nb_Sec_ecart_apres;

      for (k = 0; k < dim_in; k++)
	{
	  Nb_OK[k] = 0;
	  Nb_mnq[k] = 0;
	  loc_som[k] = 0.0;
	}

      j = j_inf;
      while ((j < size_in) && (time_in[j] <= time_sup))
	{
	  if (time_in[j] >= time_inf)
	    {
	      for (k = 0; k < dim_in; k++)
		{
		  if (!isfinite (Var_in[j * dim_in + k]))
		    {
		      Nb_mnq[k]++;
		    }
		  else
		    {
		      loc_som[k] += Var_in[j * dim_in + k];
		      Nb_OK[k]++;
		    }
		}
	    }
	  j = j + 1;
	}
      for (k = 0; k < dim_in; k++)
	{
	  if (Nb_OK[k] == 0)
	    {
	      Var_out[i * dim_in + k] = misval_out;
	      Nb_zero++;
	    }
	  else if (Nb_OK[k] <= tolerance_mnq)
	    {
	      Var_out[i * dim_in + k] = misval_out;
	      Nb_inf++;
	    }
	  else
	    {
	      Var_out[i * dim_in + k] = loc_som[k] / Nb_OK[k];
	      Nb_moy++;
	    }
	}
      /* On repart du premier élément de var_in 
       * qui a passé le test (time_in[j] >= time_inf) */
      if (j > Nb_OK[0] + Nb_mnq[0] + 1)
	j_inf = j - Nb_OK[0] - Nb_mnq[0] - 1;
      else
	j_inf = 0;
    }

  TabStat[0] = Nb_moy;
  TabStat[1] = Nb_zero;
  TabStat[2] = Nb_inf;

  free (Nb_OK);
  free (Nb_mnq);
  free (loc_som);
  return i;
}

/* fonction d'enrobage */

int
OP_MoyEch_tps_impos_tab (unsigned long Nbval, void *ArgList[], char *DiagExec)
{
  int NCar;
  long CodRet;
  long TabStat[3];
  unsigned long nb_val_dest;

  nb_val_dest = *((unsigned long *) ArgList[7]);
  NCar = sprintf (DiagExec,
		  "MoyEch_tps_impos_tab (%ld, %f, de %g à %g, %g, %g, %d, de %g a %g, %lu), ",
		  Nbval, *((float *) ArgList[0]),
		  ((double *) ArgList[2])[0],
		  ((double *) ArgList[2])[Nbval - 1],
		  *((double *) ArgList[3]), *((double *) ArgList[4]),
		  *((int *) ArgList[5]), ((double *) ArgList[6])[0],
		  ((double *) ArgList[6])[nb_val_dest - 1],
		  *((unsigned long *) ArgList[7]));
  DiagExec += NCar;

  CodRet = MoyEch_tps_impos_tab (Nbval, (float *) ArgList[0],
				 *((int *) ArgList[1]),
				 (double *) ArgList[2],
				 *((double *) ArgList[3]),
				 *((double *) ArgList[4]),
				 *((int *) ArgList[5]),
				 (double *) ArgList[6],
				 *((unsigned long *) ArgList[7]),
				 (float *) ArgList[8], TabStat);
  if (CodRet <= -100)
    {
      sprintf (DiagExec,
	       "Dimension ou nombre mini de valeur pour moyenne hors-limite : %d, %d",
		 *((int *) ArgList[1]), *((int *) ArgList[5]));
      return OP_FAIL;
    }

  if (CodRet == -1)
    {
      sprintf (DiagExec, "Les 2 periodes de temps ne se chevauchent pas, "
	       "Le dernier temps d'origine (%g) est avant le premier temps demandé (%g)",
	       ((double *) ArgList[1])[Nbval - 1],
	       ((double *) ArgList[5])[0] - *((double *) ArgList[2]));
    }
  else if (CodRet == -2)
    {
      sprintf (DiagExec, "Les 2 periodes de temps ne se chevauchent pas, "
	       "Le premier temps d'origine (%g) est apres le dernier temps demandé (%g)",
	       ((double *) ArgList[1])[0],
	       ((double *) ArgList[5])[nb_val_dest] +
	       *((double *) ArgList[3]));
    }
  else if (CodRet == -3)
    {
      sprintf (DiagExec,
	       "intervalle de temps trop petit : %g sec. avant, %g sec. apres",
	       *((double *) ArgList[2]), *((double *) ArgList[3]));
    }
  else
    {
      sprintf (DiagExec,
	       "OK: %ld val. en sortie,  (OK:%ld, 0:%ld, pas_assez:%ld).",
	       CodRet, TabStat[0], TabStat[1], TabStat[2]);
    }

  return OP_OK;
}

void
ID_MoyEch_tps_impos_tab (oper * optr)
{
  int i;
  strcpy (optr->Nom, "MoyEch_tps_impos_tab");
  optr->Version = "$Revision$";
  optr->Date = "$Date$";
  optr->fctptr = OP_MoyEch_tps_impos_tab;
  optr->NbArg = 9;
  i = 0;

  /* 1: X_in */
  optr->Arg_Car[i].direction = DIR_IN;
  optr->Arg_Car[i].categorie = VECTOR;
  optr->Arg_Car[i].typ = ATYC_IF32;
  optr->Arg_Car[i].array_dim = "any";
  optr->Arg_Car[i].type_sample = "any";
  optr->Arg_Car[i].sample = "any";
  optr->Arg_Car[i].unite = "";
  i++;

  /* 2: dim_in */
  optr->Arg_Car[i].direction = DIR_IN;
  optr->Arg_Car[i].categorie = COEFFICIENT;
  optr->Arg_Car[i].typ = ATYC_I32;
  optr->Arg_Car[i].array_dim = "";
  optr->Arg_Car[i].type_sample = "";
  optr->Arg_Car[i].sample = "";
  optr->Arg_Car[i].unite = "";
  optr->Arg_Car[i].famille = "";
  i++;

  /* 3: time_in */
  optr->Arg_Car[i].direction = DIR_IN;
  optr->Arg_Car[i].categorie = VECTOR;
  optr->Arg_Car[i].typ = ATYC_IF64;
  optr->Arg_Car[i].array_dim = "1";
  optr->Arg_Car[i].type_sample = "any";
  optr->Arg_Car[i].sample = "any";
  optr->Arg_Car[i].unite = "second";
  i++;

  /* 4: Ecart avant */
  optr->Arg_Car[i].direction = DIR_IN;
  optr->Arg_Car[i].categorie = COEFFICIENT;
  optr->Arg_Car[i].typ = ATYC_IF64;
  optr->Arg_Car[i].array_dim = "1";
  optr->Arg_Car[i].type_sample = "any";
  optr->Arg_Car[i].sample = "any";
  optr->Arg_Car[i].unite = "";
  i++;

  /* 5: Ecart apres */
  optr->Arg_Car[i].direction = DIR_IN;
  optr->Arg_Car[i].categorie = COEFFICIENT;
  optr->Arg_Car[i].typ = ATYC_IF64;
  optr->Arg_Car[i].array_dim = "1";
  optr->Arg_Car[i].type_sample = "any";
  optr->Arg_Car[i].sample = "any";
  optr->Arg_Car[i].unite = "";
  i++;

  /* 6: Mini_OK acceptés */
  optr->Arg_Car[i].direction = DIR_IN;
  optr->Arg_Car[i].categorie = COEFFICIENT;
  optr->Arg_Car[i].typ = ATYC_I32;
  optr->Arg_Car[i].array_dim = "1";
  optr->Arg_Car[i].type_sample = "any";
  optr->Arg_Car[i].sample = "any";
  optr->Arg_Car[i].unite = "";
  i++;

  /* 7: time_out */
  optr->Arg_Car[i].direction = DIR_IN;
  optr->Arg_Car[i].categorie = VECTOR;
  optr->Arg_Car[i].typ = ATYC_IF64;
  optr->Arg_Car[i].array_dim = "1";
  optr->Arg_Car[i].type_sample = "any";
  optr->Arg_Car[i].sample = "any";
  optr->Arg_Car[i].unite = "second";
  i++;

  /* 8: size_out */
  optr->Arg_Car[i].direction = DIR_IN;
  optr->Arg_Car[i].categorie = COEFFICIENT;
  optr->Arg_Car[i].typ = ATYC_LOCAL_ULONG;
  optr->Arg_Car[i].array_dim = "1";
  optr->Arg_Car[i].type_sample = "any";
  optr->Arg_Car[i].sample = "any";
  optr->Arg_Car[i].unite = "";
  i++;

  /* 9: X_out */
  optr->Arg_Car[i].direction = DIR_OUT;
  optr->Arg_Car[i].categorie = VECTOR;
  optr->Arg_Car[i].typ = ATYC_IF32;
  optr->Arg_Car[i].array_dim = "$Arg1.array_dim";
  optr->Arg_Car[i].bornes = "$Arg1.bornes";
  optr->Arg_Car[i].unit_bornes = "$Arg1.unit_bornes";
  optr->Arg_Car[i].NbVal = "$Arg7.NbVal";
  optr->Arg_Car[i].type_sample = "$Arg7.type_sample";
  optr->Arg_Car[i].sample = "$Arg7.sample";
  optr->Arg_Car[i].ref_time = " $Arg7.nom ";
  optr->Arg_Car[i].unite = "$Arg1.unit";
  optr->Arg_Car[i].famille = "$Arg1.famille";
  optr->Arg_Car[i].misval = "$Arg1.misval";
  optr->Arg_Car[i].name = "$Arg1.name + \" synchronise sur \" + $Arg7.name";
  optr->Arg_Car[i].en_name =
    "$Arg1.english_name + \" synchronised on \" + $Arg7.english_name";
}
