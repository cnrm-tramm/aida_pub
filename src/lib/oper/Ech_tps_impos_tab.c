/*******************************************************************
* OPERATOR      Ech_tps_impos_tab.c FUNCTION ANSI-C
*
*
* PURPOSE 	Echantillonnage d'une variable sur une autre base de temps. 
*
*		
* DESCRIPTION	Cette fonction échantillonne une variable "x_in"
*		qui est daté par le vecteur temps "time_in" sur une 
*		autre base de temps "time_out".
*		La variable resultat est "x_out"		
*               On ne fait aucune supposition sur la régularité de
*               l'échantillonnage des 2 variables. Cette fonction peut
*		donc servir, par exemple, à transformer une serie temporelle
*               asynchrone en une série réguliere.
*		On suppose que time_in est "à peu près" trié par ordre
*               croissant.
*		 
* VERSION       1.1  
*
* ARGUMENTS     IN   float   x_in      any       variable de depart a échantillonner
*               IN   double  time_in   second    base de temps de depart
*               IN   int     dim_in    nb        base de temps de depart
*               IN   double  ecart_max second    Ecart max toléré.
*               IN   double  time_out  second    base de temps d'arrivee
*               IN   int     size_out  any       Nb de valeurs dans la base de temps d'arrivee
*
*               OUT  float   x_out     same as "x_in"  variable "x_in" échantillonnée
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

int
Ech_tps_impos_tab (unsigned long size_in,
		   float *x_in,
		   double *time_in,
		   int dim_in,
		   double Nb_Sec_ecart_max,
		   double *time_out, unsigned long size_out, float *x_out)
{
  unsigned long i;
  /* unsigned */ long jinf, jsup, jsup2;
  long jinf2;
  long k;

  double min_delta_T;
  double d_time_inf, d_time_sup;

  jsup = 1;
  jinf = 0;

/********************************************************
  * On parcourt le time_out et on cherche
  * les 2 valeurs de time_in qui l'encadrent.
  *********************************************************/

  for (i = 0; i < size_out; i++)
    {
      /* Etape 1 : */
      /* Recherche d'un temps time_in plus grand que time_out[i] */

      /* Pour éviter de parcourir toute les valeurs, voire de */
      /* les trier, on estime j_sup */
      if (jinf < size_in - 1)
	jsup = jinf + 1;
      else
	jsup = 0;

      while ((jsup < (size_in - 1)) && (time_in[jsup] <= time_out[i]))
	{
	  jsup = jsup + 1;
	}
      /* Dans certains cas, on peut vouloir chercher */
      /* plus loin une valeur convenable.            */
      min_delta_T = time_in[jsup] - time_out[i];
      jsup2 = jsup + 1;
      while ((jsup2 <= (size_in - 1))
	     && (time_in[jsup2] - time_out[i] <= min_delta_T))
	{
	  if (time_in[jsup2] > time_out[i])
	    {
	      min_delta_T = time_in[jsup2] - time_out[i];
	      jsup = jsup2;
	    }
	  jsup2 = jsup2 + 1;
	}

      /* Etape 2 : */
      /* Recherche d'un temps asynchone plus petit que time_out[i] */

      /* Pour éviter de parcourir toute les valeurs, voire de */
      /* les trier, on estime j_inf */
      if (jsup > 0)
	jinf = jsup - 1;
      else
	jinf = 0;

      while ((jinf > 0) && (time_out[i] < time_in[jinf]))
	{
	/** ceci est pour prendre en compte le cas ou 
           (time_in[jsup] < time_in[jsup-1]) 
        **/
	  jinf = jinf - 1;
	}
      /* Comme pour la recherche de valeur plus grande,
       * il faut aller voir si il n'y a pas "avant" une
       * valeur plus proche du temps recherché 
       * (le temps asynchrone n'est pas forcement trié).  */
      min_delta_T = time_out[i] - time_in[jinf];
      jinf2 = jinf - 1;
      while ((jinf2 >= 0) && ((time_out[i] - time_in[jinf2]) <= min_delta_T))
	{
	  if (time_in[jinf2] < time_out[i])
	    {
	      jinf = jinf2;
	      min_delta_T = time_out[i] - time_in[jinf];
	    }
	  jinf2 = jinf2 - 1;
	}
/*
      if (i % 1000 == 0)
	{
	  fprintf (stderr,
		   "i=%d, time_out : %f, time_in_inf : %f, Jinf=%d, Jsup=%d\n",
		   i, time_out[i], time_in[jinf], jinf, jsup);
	}
*/

/*** Recherche du plus proche et échantillonnage */

      /* Il se peut (cas des "trous" de données en début
       * ou fin) que time_in[jsup] et  time_in[jinf] soient
       * du "même coté" de time_out[i]
       *   --> soyons prudents !
       * 1 : cas ou les time_in sont plus grands que time_out[i]
       */
      if (time_out[i] < time_in[jinf])
	{
	  if (fabs (time_in[jinf] - time_out[i]) < Nb_Sec_ecart_max)
	    {
	      for (k = 0; k < dim_in; k++)
		{
		  x_out[(i * dim_in) + k] = x_in[(jinf * dim_in) + k];
		}
	    }
	  else
	    {
	      for (k = 0; k < dim_in; k++)
		{
		  x_out[(i * dim_in) + k] = K_NaN;
		}
	    }
	}
      else if (time_out[i] > time_in[jsup])
	{
	  if (fabs (time_out[i] - time_in[jsup]) < Nb_Sec_ecart_max)
	    {
	      for (k = 0; k < dim_in; k++)
		{
		  x_out[(i * dim_in) + k] = x_in[(jsup * dim_in) + k];
		}
	    }
	  else
	    {
	      for (k = 0; k < dim_in; k++)
		{
		  x_out[(i * dim_in) + k] = K_NaN;
		}
	    }
	}
      else
	{
	  d_time_inf = time_in[jinf];
	  d_time_sup = time_in[jsup];

	  if (fabs (d_time_sup - time_out[i]) >
	      fabs (time_out[i] - d_time_inf))
	    {
	      if (fabs (time_out[i] - d_time_inf) < Nb_Sec_ecart_max)
		{
		  for (k = 0; k < dim_in; k++)
		    {
		      x_out[(i * dim_in) + k] = x_in[(jinf * dim_in) + k];
		    }
		}
	      else
		{
		  for (k = 0; k < dim_in; k++)
		    {
		      x_out[(i * dim_in) + k] = K_NaN;
		    }
		}
	    }
	  else
	    {
	      if (fabs (time_out[i] - d_time_sup) < Nb_Sec_ecart_max)
		{
		  for (k = 0; k < dim_in; k++)
		    {
		      x_out[(i * dim_in) + k] = x_in[(jsup * dim_in) + k];
		    }
		}
	      else
		{
		  for (k = 0; k < dim_in; k++)
		    {
		      x_out[(i * dim_in) + k] = K_NaN;
		    }
		}
	    }
	}
    }


  return 0;
}

/* fonction d'enrobage */

int
OP_Ech_tps_impos_tab (unsigned long Nbval, void *ArgList[], char *DiagExec)
{
  int NCar;
  int CodRet;
  unsigned long Nb_val_out;

  Nb_val_out = *((unsigned long *) ArgList[5]);

  NCar = sprintf (DiagExec, "Ech_tps_impos_tab (%lu ech de taille %d), ",
	          Nbval, *((int *) ArgList[2]));
  DiagExec += NCar;
  DiagExec = ecrit_bornes_temps (DiagExec, "T(x)", (double *) ArgList[1],
			         Nbval);
  NCar = sprintf (DiagExec, "ec_max = %g, nb_resu =%lu, ",
	         *((double *) ArgList[3]), Nb_val_out);
  DiagExec += NCar;
  DiagExec = ecrit_bornes_temps (DiagExec, "T_resu", (double *) ArgList[4],
			         Nb_val_out);

  CodRet =
    Ech_tps_impos_tab (Nbval, (float *) ArgList[0],
		       (double *) ArgList[1],
		       *((int *) ArgList[2]),
		       *((double *) ArgList[3]),
		       (double *) ArgList[4],
		       *((unsigned long *) ArgList[5]), (float *) ArgList[6]);
  return OP_OK;
}

void
ID_Ech_tps_impos_tab (oper * optr)
{
  strcpy (optr->Nom, "Ech_tps_impos_tab");
  optr->Version = "$Revision$";
  optr->Date = "$Date$";
  optr->fctptr = OP_Ech_tps_impos_tab;
  optr->NbArg = 7;

  /* 1: X_in */
  optr->Arg_Car[0].direction = DIR_IN;
  optr->Arg_Car[0].categorie = VECTOR;
  optr->Arg_Car[0].typ = ATYC_IF32;
  optr->Arg_Car[0].array_dim = "*";
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

  /* 3: dim_in */
  optr->Arg_Car[2].direction = DIR_IN;
  optr->Arg_Car[2].categorie = COEFFICIENT;
  optr->Arg_Car[2].typ = ATYC_I32;
  optr->Arg_Car[2].array_dim = "1";

  /* 4: Ecart Max */
  optr->Arg_Car[3].direction = DIR_IN;
  optr->Arg_Car[3].categorie = COEFFICIENT;
  optr->Arg_Car[3].typ = ATYC_IF64;
  optr->Arg_Car[3].array_dim = "1";
  optr->Arg_Car[3].unite = "";

  /* 5: time_out */
  optr->Arg_Car[4].direction = DIR_IN;
  optr->Arg_Car[4].categorie = VECTOR;
  optr->Arg_Car[4].typ = ATYC_IF64;
  optr->Arg_Car[4].array_dim = "1";
  optr->Arg_Car[4].type_sample = "any";
  optr->Arg_Car[4].sample = "any";
  optr->Arg_Car[4].unite = "second";

  /* 6: size_out */
  optr->Arg_Car[5].direction = DIR_IN;
  optr->Arg_Car[5].categorie = COEFFICIENT;
  optr->Arg_Car[5].typ = ATYC_LOCAL_ULONG;
  optr->Arg_Car[5].array_dim = "1";
  optr->Arg_Car[5].type_sample = "any";
  optr->Arg_Car[5].sample = "any";
  optr->Arg_Car[5].unite = "";

  /* 7: X_out */
  optr->Arg_Car[6].direction = DIR_OUT;
  optr->Arg_Car[6].categorie = VECTOR;
  optr->Arg_Car[6].typ = ATYC_IF32;
  optr->Arg_Car[6].array_dim = "$Arg1.array_dim";
  optr->Arg_Car[6].bornes = "$Arg1.bornes";
  optr->Arg_Car[6].unit_bornes = "$Arg1.unit_bornes";
  optr->Arg_Car[6].NbVal = "$Arg5.NbVal";
  optr->Arg_Car[6].type_sample = "$Arg5.type_sample";
  optr->Arg_Car[6].sample = "$Arg5.sample";
  optr->Arg_Car[6].ref_time = " $Arg5.nom ";
  optr->Arg_Car[6].unite = "$Arg1.unit";
  optr->Arg_Car[6].famille = "$Arg1.famille";
  optr->Arg_Car[6].misval = "$Arg1.misval";
  optr->Arg_Car[6].name = "$Arg1.name + \" echantillonne sur \" + $Arg5.name";
  optr->Arg_Car[6].en_name =
    "$Arg1.english_name + \" sampled on \" + $Arg5.english_name";
}
