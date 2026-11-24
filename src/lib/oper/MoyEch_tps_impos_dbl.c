/*******************************************************************
* OPERATOR      MoyEch_tps_impos_dbl.c FUNCTION ANSI-C
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
* VERSION       1.1  
*
* ARGUMENTS     IN  double  Var_in       any       variable de depart a échantillonner
*               IN  double  time_in    second      base de temps de depart
*               IN  double  Nb_Sec_ecart_avant second    Ecart AVANT sur lequel s'effectue la moyenne
*               IN  double  Nb_Sec_ecart_apres second    Ecart max APRES sur lequel s'effectue la moyenne
*               IN  int     tolerance_mnq   Nombre mini de valeur pour accepter de faire la moyenne (mettre 0 pour faire
*                                           la moyenne meme si un seul point !)
*               IN  double  time_out   second     base de temps d'arrivee
*               IN  int     size_out   any        Nb de valeurs dans la base de temps d'arrivee
*
*               OUT double  Var_out   same as "Var_in"  variable "Var_in" échantillonnée
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
#include <math.h>
#include <limits.h>
#include <float.h>

#include "struct_oper.h"
#include "oper_util.h"

long
MoyEch_tps_impos_dbl (unsigned long size_in,
		  double *Var_in,
		  double *time_in,
		  double Nb_Sec_ecart_avant,
		  double Nb_Sec_ecart_apres,
		  int tolerance_mnq,
		  double *time_out,
		  unsigned long size_out, double *Var_out, long TabStat[3])
{
  unsigned long i, j, j_inf;
  long Nb_moy, Nb_zero, Nb_inf;
  long pre_diag;

  double time_inf, time_sup;

  register double loc_som;
  register long Nb_mnq;
  register long Nb_OK;
  const float misval_out = K_NaN;

  Nb_moy = 0;
  Nb_zero = 0;
  Nb_inf = 0;

  pre_diag = 0;
  if (time_in[size_in - 1] < (time_out[0] - Nb_Sec_ecart_avant))
    {
      pre_diag = -1;
      Nb_zero = size_out;
    }

  if ((time_out[size_out - 1] + Nb_Sec_ecart_apres) < time_in[0])
    {
      pre_diag = -2;
      Nb_zero = size_out;
    }

  if ((Nb_Sec_ecart_avant + Nb_Sec_ecart_apres) <= 0)
    {
      pre_diag = -3;
      Nb_zero = size_out;
    }

  if (pre_diag != 0)
    {
      for (i = 0; i < size_out; i++)
	{
	  Var_out[i] = misval_out;
	}
      TabStat[0] = Nb_moy;
      TabStat[1] = Nb_zero;
      TabStat[2] = Nb_inf;
      return pre_diag;
    }

  j_inf = 0;
  for (i = 0; i < size_out; i++)
    {
      time_inf = time_out[i] - Nb_Sec_ecart_avant;
      time_sup = time_out[i] + Nb_Sec_ecart_apres;

      loc_som = 0.0;
      Nb_mnq = 0;
      Nb_OK = 0;

      j = j_inf;
      while ((j < size_in) && (time_in[j] <= time_sup))
	{
	  if (time_in[j] >= time_inf)
	    {
	      if (!isfinite (Var_in[j]))
		{
		  Nb_mnq++;
		}
	      else
		{
		  loc_som += Var_in[j];
		  Nb_OK++;
		}
	    }
	  j = j + 1;
	}
      if (Nb_OK == 0)
	{
	  Var_out[i] = misval_out;
	  Nb_zero++;
	}
      else if (Nb_OK <= tolerance_mnq)
	{
	  Var_out[i] = misval_out;
	  Nb_inf++;
	}
      else
	{
	  Var_out[i] = loc_som / Nb_OK;
	  Nb_moy++;
	}
      /* On repart du premier élément de var_in 
       * qui a passé le test (time_in[j] >= time_inf) */
      if (j > Nb_OK + Nb_mnq + 1)
	j_inf = j - Nb_OK - Nb_mnq - 1;
      else
	j_inf = 0;
    }

  TabStat[0] = Nb_moy;
  TabStat[1] = Nb_zero;
  TabStat[2] = Nb_inf;

  return i;
}

/* fonction d'enrobage */

int
OP_MoyEch_tps_impos_dbl (unsigned long Nbval, void *ArgList[], char *DiagExec)
{
  int NCar;
  long CodRet;
  long TabStat[3];
  unsigned long nb_val_dest;

  nb_val_dest = *((unsigned long *) ArgList[6]);

  NCar = sprintf (DiagExec, "MoyEch_tps_impos_dbl (%lu ech), ", Nbval);
  DiagExec += NCar;
  DiagExec = ecrit_bornes_temps (DiagExec, "time_orig", (double *) ArgList[1],
			         Nbval);
  NCar = sprintf (DiagExec, "ecart_av=%g, ecart_ap=%g, mini_ok=%d, ",
		  *((double *) ArgList[2]), *((double *) ArgList[3]),
		  *((int *) ArgList[4]));
  DiagExec += NCar;
  DiagExec = ecrit_bornes_temps (DiagExec, "time_dest", (double *) ArgList[5],
			         nb_val_dest);
  NCar = sprintf (DiagExec, " nb_resu=%lu", *((unsigned long *) ArgList[6]));
  DiagExec += NCar;

  CodRet = MoyEch_tps_impos_dbl (Nbval, (double *) ArgList[0],
			     (double *) ArgList[1],
			     *((double *) ArgList[2]),
			     *((double *) ArgList[3]),
			     *((int *) ArgList[4]),
			     (double *) ArgList[5],
			     *((unsigned long *) ArgList[6]),
			     (double *) ArgList[7], TabStat);
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
ID_MoyEch_tps_impos_dbl (oper * optr)
{
  strcpy (optr->Nom, "MoyEch_tps_impos_dbl");
  optr->Version = "$Revision$";
  optr->Date = "$Date$";
  optr->fctptr = OP_MoyEch_tps_impos_dbl;
  optr->NbArg = 8;

  /* 1: X_in */
  optr->Arg_Car[0].direction = DIR_IN;
  optr->Arg_Car[0].categorie = VECTOR;
  optr->Arg_Car[0].typ = ATYC_IF64;
  optr->Arg_Car[0].array_dim = "1";
  optr->Arg_Car[0].type_sample = "any";
  optr->Arg_Car[0].sample = "any";
  optr->Arg_Car[0].unite = "";

  /* 2: time_in */
  optr->Arg_Car[1].direction = DIR_IN;
  optr->Arg_Car[1].categorie = VECTOR;
  optr->Arg_Car[1].typ = ATYC_IF64;
  optr->Arg_Car[1].array_dim = "1";
  optr->Arg_Car[1].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[1].type_sample = "any";
  optr->Arg_Car[1].sample = "any";
  optr->Arg_Car[1].unite = "second";

  /* 3: Ecart avant */
  optr->Arg_Car[2].direction = DIR_IN;
  optr->Arg_Car[2].categorie = COEFFICIENT;
  optr->Arg_Car[2].typ = ATYC_IF64;
  optr->Arg_Car[2].array_dim = "1";
  optr->Arg_Car[2].type_sample = "any";
  optr->Arg_Car[2].sample = "any";
  optr->Arg_Car[2].unite = "";

  /* 4: Ecart apres */
  optr->Arg_Car[3].direction = DIR_IN;
  optr->Arg_Car[3].categorie = COEFFICIENT;
  optr->Arg_Car[3].typ = ATYC_IF64;
  optr->Arg_Car[3].array_dim = "1";
  optr->Arg_Car[3].type_sample = "any";
  optr->Arg_Car[3].sample = "any";
  optr->Arg_Car[3].unite = "";

  /* 5: Mini_OK acceptés */
  optr->Arg_Car[4].direction = DIR_IN;
  optr->Arg_Car[4].categorie = COEFFICIENT;
  optr->Arg_Car[4].typ = ATYC_I32;
  optr->Arg_Car[4].array_dim = "1";
  optr->Arg_Car[4].type_sample = "any";
  optr->Arg_Car[4].sample = "any";
  optr->Arg_Car[4].unite = "";

  /* 6: time_out */
  optr->Arg_Car[5].direction = DIR_IN;
  optr->Arg_Car[5].categorie = VECTOR;
  optr->Arg_Car[5].typ = ATYC_IF64;
  optr->Arg_Car[5].array_dim = "1";
  optr->Arg_Car[5].type_sample = "any";
  optr->Arg_Car[5].sample = "any";
  optr->Arg_Car[4].unite = "second";

  /* 7: size_out */
  optr->Arg_Car[6].direction = DIR_IN;
  optr->Arg_Car[6].categorie = COEFFICIENT;
  optr->Arg_Car[6].typ = ATYC_LOCAL_ULONG;
  optr->Arg_Car[6].array_dim = "1";
  optr->Arg_Car[6].type_sample = "any";
  optr->Arg_Car[6].sample = "any";
  optr->Arg_Car[6].unite = "";

  /* 8: X_out */
  optr->Arg_Car[7].direction = DIR_OUT;
  optr->Arg_Car[7].categorie = VECTOR;
  optr->Arg_Car[7].typ = ATYC_IF64;
  optr->Arg_Car[7].array_dim = "1";
  optr->Arg_Car[7].NbVal = "$Arg6.NbVal";	/* ou $Arg7.value */
  optr->Arg_Car[7].type_sample = "$Arg6.type_sample";
  optr->Arg_Car[7].sample = "$Arg6.sample";
  optr->Arg_Car[7].ref_time = " $Arg6.nom ";
  optr->Arg_Car[7].unite = "$Arg1.unit";
  optr->Arg_Car[7].famille = "$Arg1.famille";
  optr->Arg_Car[7].misval = "$Arg1.misval";
  optr->Arg_Car[7].name = "$Arg1.name + \" synchronise sur \" + $Arg6.name";
  optr->Arg_Car[7].en_name = 
         "$Arg1.english_name + \" synchronised on \" + $Arg6.english_name";
}
