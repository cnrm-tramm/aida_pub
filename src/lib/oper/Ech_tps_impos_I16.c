/*******************************************************************
* OPERATOR      Ech_tps_impos_I16.c FUNCTION ANSI-C
*
*
* PURPOSE 	Echantillonnage d'une variable sur une autre base de temps. 
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
* ARGUMENTS     IN   short   x_in     any       variable de depart a échantillonner
*               IN   double  time_in  second    base de temps de depart
*               IN   double  time_out second    base de temps d'arrivee
*               IN   int     size_out any       Nb de valeurs dans la base de temps d'arrivee
*
*               OUT  short   x_out    same as "x_in"  variable "x_in" échantillonnée
*					             sur la base "time_out"	
* CHANGES 	1.1 time_in est passe en double
*
* ENTRY         NONE
*
* SUBPROGRAMS   NONE
*
* REFERENCES     
*             
* COPYRIGHT     Meteo-France
*               Centre National de Recherches Meteorologiques
*               GMEI/MMA
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
Ech_tps_impos_I16 (unsigned long size_in,
                   short *x_in,
                   double *time_in,
                   double *time_out,
                   unsigned long size_out,
                   short *x_out)
{
  long i, jinf, jinf2, jsup, jsup2;

  const float Nb_Sec_ecart_max = 10.0;

  double min_delta_T;
  double d_time_inf, d_time_sup;

  jsup = 1;
  jinf = 0;

/********************************************************
 * On parcourt le time_out et on cherche
 * les 2 valeurs de time_in qui l'encadrent.
 *********************************************************
 */

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
      /* Comme pour la recherche de valeur plus grande, */
      /* il faut aller voir si il n'y a pas "avant" une */
      /* valeur plus proche du temps recherché */
      /* (le temps asynchrone n'est pas forcement trié).  */
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
   fprintf(stderr, "i=%d, time_out : %f, time_in : %f , Jinf=%d, Jsup=%d",
   i, time_out[i], time_in[i], jinf, jsup );
 */

/*** Recherche du plus proche et échantillonnage */

      /* Il se peut (cas des "trous" de données en début */
      /* ou fin) que time_in[jsup] et  time_in[jinf] soient */
      /* "même coté" de time_out[i] */
      /*   --> soyons prudents ! */
      /* 1 : cas ou les time_in sont plus grands que time_out[i] */
      if (time_out[i] < time_in[jinf])
	{
	  if (fabs (time_in[jinf] - time_out[i]) < Nb_Sec_ecart_max)
	    {
	      x_out[i] = x_in[jinf];
	    }
	  else
	    {
	      x_out[i] = K_NaN;
	    }
	}
      else if (time_out[i] > time_in[jsup])
	{
	  if (fabs (time_out[i] - time_in[jsup]) < Nb_Sec_ecart_max)
	    {
	      x_out[i] = x_in[jsup];
	    }
	  else
	    {
	      x_out[i] = K_NaN;
	    }
	}
      else
	{
	  d_time_inf = time_in[jinf];
	  d_time_sup = time_in[jsup];

	  if (fabs (d_time_sup - time_out[i]) >
	      fabs (time_out[i] - d_time_inf))
	    {
	      x_out[i] = x_in[jinf];
	    }
	  else
	    {
	      x_out[i] = x_in[jsup];
	    }
	}
    }

  return 0;
}

/* fonction d'enrobage */

int
OP_Ech_tps_impos_I16 (unsigned long Nbval, void *ArgList[], char *DiagExec)
{
  int NCar;
  int CodRet;
  unsigned long *nb_resu;

  nb_resu = (unsigned long *) ArgList[3];

  NCar = sprintf (DiagExec, "Ech_tps_impos_I16 (%lu ech), ", Nbval);
  DiagExec += NCar;
  DiagExec = ecrit_bornes_temps (DiagExec, "Time_in", (double *) ArgList[1],
                                 Nbval);
  DiagExec = ecrit_bornes_temps (DiagExec, "Time_out", (double *) ArgList[2],
			         *nb_resu);
  DiagExec += NCar;
  NCar = sprintf (DiagExec, ", nb_resu =%lu", *nb_resu);
  DiagExec += NCar;

  CodRet = Ech_tps_impos_I16 (Nbval,
			      (short *) ArgList[0],
			      (double *) ArgList[1],
			      (double *) ArgList[2],
			      *((unsigned long *) ArgList[3]),
			      (short *) ArgList[4]);

  return OP_OK;
}

void
ID_Ech_tps_impos_I16 (oper * optr)
{
  strcpy (optr->Nom, "Ech_tps_impos_I16");
  optr->Version = "$Revision$";
  optr->Date = "$Date$";
  optr->fctptr = OP_Ech_tps_impos_I16;
  optr->NbArg = 5;

  /* 1: X_in */
  optr->Arg_Car[0].direction = DIR_IN;
  optr->Arg_Car[0].categorie = VECTOR;
  optr->Arg_Car[0].typ = ATYC_I16;
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

  /* 3: time_out */
  optr->Arg_Car[2].direction = DIR_IN;
  optr->Arg_Car[2].categorie = VECTOR;
  optr->Arg_Car[2].typ = ATYC_IF64;
  optr->Arg_Car[2].array_dim = "1";
  optr->Arg_Car[2].type_sample = "any";
  optr->Arg_Car[2].sample = "any";
  optr->Arg_Car[2].unite = "second";

  /* 4: size_out */
  optr->Arg_Car[3].direction = DIR_IN;
  optr->Arg_Car[3].categorie = COEFFICIENT;
  optr->Arg_Car[3].typ = ATYC_LOCAL_ULONG;
  optr->Arg_Car[3].array_dim = "1";
  optr->Arg_Car[3].type_sample = "any";
  optr->Arg_Car[3].sample = "any";
  optr->Arg_Car[3].unite = "";

  /* 5: X_out */
  optr->Arg_Car[4].direction = DIR_OUT;
  optr->Arg_Car[4].categorie = VECTOR;
  optr->Arg_Car[4].typ = ATYC_I16;
  optr->Arg_Car[4].array_dim = "1";
  optr->Arg_Car[4].NbVal = "$Arg3.NbVal";
  optr->Arg_Car[4].type_sample = "$Arg3.type_sample";
  optr->Arg_Car[4].sample = "$Arg3.sample";
  optr->Arg_Car[4].ref_time = " $Arg3.nom ";
  optr->Arg_Car[4].unite = "$Arg1.unit";
  optr->Arg_Car[4].famille = "$Arg1.famille";
  optr->Arg_Car[4].misval = "$Arg1.misval";
  optr->Arg_Car[4].name = "$Arg1.name + \" echantillonne sur \" + $Arg3.name";
  optr->Arg_Car[4].en_name =
    "$Arg1.english_name + \" sampled on \" + $Arg3.english_name";

}
