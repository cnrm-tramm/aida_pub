/*******************************************************************
* OPERATOR      Interpol_irreg_mnq.c FUNCTION ANSI-C
*
* PURPOSE 	Interpolation d'une variable sur une autre base de temps. 
*		
* DESCRIPTION	Cette fonction Interpole une variable "x_as"
*		qui est date par le vecteur temps "time_as" sur une 
*		autre base de temps "time_rg".
*		La variable resultat est "x_rg"		
*		L'interpolation est lineaire, mais sa durée est 
*		limitée (par l'argument max_interp).
*               On ne fait aucune supposition sur la régularité de
*               l'échantillonnage des 2 variables. Cette fonction peut
*		donc servir, par exemple, à transformer une serie temporelle
*               asynchrone en une serie reguliere.
*		On suppose que time_as est "à peu près" trié par ordre
*               croissant.
*		 
* VERSION       $Revision$
*
* ARGUMENTS     IN  double time_rg    second  base de temps d'arrivée
*               IN  double time_as    second  base de temps de départ
*               IN  float  x_as       any     variable de départ à interpoler 
*               IN  int    size_as    any     Nb de valeurs du param à interpoler.
*               IN  float  max_interp second  Ecart max toléré entre deux échantillons d'origine
*               IN  float  max_extrap second  durée max d'extrapolation.
*
*               OUT  float   x_rg   same as "x_as"  variable "x-as" Interpolee 
*					             sur la base "time_rg"	
* CHANGES 	1.1 time_as est passe en double
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
Interpol_irreg_mnq (unsigned long size,
		    double *time_rg,
		    double *time_as,
		    float *x_as,
		    unsigned long size_as,
		    float Nb_Sec_interpol, float Nb_Sec_extrapol, float *x_rg)
{
  unsigned long i;
  unsigned long jinf, jsup, jsup2;
  long jinf2;

  /* const float Nb_Sec_extrapol = 10.0; */

  double min_delta_T;
  double d_x_sup, d_x_inf, d_time_inf, d_time_sup;
  double a, b;
  const double epsilon = 10.0 * DBL_MIN;

  /* Pour éviter les cas limites.
   * Après  ce test, on peut utiliser (en unsigned) (size_as -1) sans crainte. */
  if (size_as == 0)
    {
      for (i = 0; i < size; i++)
	{
	  x_rg[i] = K_NaN;
	}
      return 0;
    }

  jsup = 1;
  jinf = 0;

/********************************************************
 * On incremente le time_rg (regulier) et on cherche
 * les 2 valeurs de time_as qui l'encadrent.
 * On Interpole lineairement la valeur entre les 2 points
 *********************************************************
 */

  for (i = 1; i < size; i++)
    {
      /* Etape 1 : */
      /* Recherche d'un temps asynchone plus grand que time_rg[i] */

      /* Pour éviter de parcourir toute les valeurs, voire de */
      /* les trier, on estime j_sup */
      if (jinf < size_as - 1)
	jsup = jinf + 1;
      else
	jsup = 0;

      while ((jsup < (size_as - 1)) && (time_as[jsup] <= time_rg[i]))
	{
	  jsup = jsup + 1;
	}
      /* Dans certains cas, on peut vouloir chercher */
      /* plus loin une valeur convenable.            */
      min_delta_T = time_as[jsup] - time_rg[i];
      jsup2 = jsup + 1;
      while ((jsup2 <= (size_as - 1))
	     && (time_as[jsup2] - time_rg[i] <= min_delta_T))
	{
	  if (time_as[jsup2] > time_rg[i])
	    {
	      min_delta_T = time_as[jsup2] - time_rg[i];
	      jsup = jsup2;
	    }
	  jsup2 = jsup2 + 1;
	}

      /* Etape 2 : */
      /* Recherche d'un temps asynchone plus petit que time_rg[i] */

      /* Pour éviter de parcourir toute les valeurs, voire de */
      /* les trier, on estime j_inf */
      if (jsup > 0)
	jinf = jsup - 1;
      else
	jinf = 0;

      while ((jinf > 0) && (time_rg[i] < time_as[jinf]))
	{
	/** ceci est pour prendre en compte le cas ou 
           (time_as[jsup] < time_as[jsup-1]) 
        **/
	  jinf = jinf - 1;
	}
      /* Comme pour la recherche de valeur plus grande,
       * il faut aller voir si il n'y a pas "avant" une
       * valeur plus proche du temps recherché.
       * (le temps asynchrone n'est pas forcement trié).  */
      min_delta_T = time_rg[i] - time_as[jinf];
      jinf2 = jinf - 1;		/* jinf2 est le seul "signed" de code.. */
      while ((jinf2 >= 0) && ((time_rg[i] - time_as[jinf2]) <= min_delta_T))
	{
	  if (time_as[jinf2] < time_rg[i])
	    {
	      jinf = jinf2;
	      min_delta_T = time_rg[i] - time_as[jinf];
	    }
	  jinf2 = jinf2 - 1;
	}
/*
   fprintf(stderr, "i=%d, time_rg : %f, time_as : %f , Jinf=%d, Jsup=%d",
   i, time_rg[i], time_as[i], jinf, jsup );
 */

/*** Interpolation lineaire ***/

      /* Il se peut (cas des "trous" de données en début */
      /* ou fin) que time_as[jsup] et  time_as[jinf] soient */
      /* "même coté" de time_rg[i] */
      /*   --> soyons prudents ! */
      /* 1 : cas ou les time_as sont plus grands que time_rg[i] */
      if (time_rg[i] < time_as[jinf])
	{
	  if (fabs (time_as[jinf] - time_rg[i]) < Nb_Sec_extrapol)
	    {
	      x_rg[i] = x_as[jinf];
	    }
	  else
	    {
	      x_rg[i] = K_NaN;
	    }
	}
      else if (time_rg[i] > time_as[jsup])
	{
	  if (fabs (time_rg[i] - time_as[jsup]) < Nb_Sec_extrapol)
	    {
	      x_rg[i] = x_as[jsup];
	    }
	  else
	    {
	      x_rg[i] = K_NaN;
	    }
	}
      else
	{
	  /* question soulevee lors d'une relecture de code le 22/02/1999 :
	   *  pourquoi ne pas coder plus simplement l'interpolation lineaire  
	   * du genre :
	   * x_rg = x_as[jinf] + 
	   *   (time_rg[i]-time_as[jinf]) * (x_as[jsup]-x_as[jinf])/(time_as[jsup]-time_as[jinf])
	   * debut de reponse : 
	   *    pour le test (fabs (d_time_inf - d_time_sup) > epsilon)
	   **/

	  d_x_inf = (double) x_as[jinf];
	  d_x_sup = (double) x_as[jsup];

	  d_time_inf = time_as[jinf];
	  d_time_sup = time_as[jsup];

	  if (fabs (d_time_inf - d_time_sup) > Nb_Sec_interpol)
	    {
	      x_rg[i] = K_NaN;
	    }
	  else if (fabs (d_time_inf - d_time_sup) > epsilon)
	    {
	      a = (d_x_inf - d_x_sup) / (d_time_inf - d_time_sup);
	      b = ((d_time_inf * d_x_sup) - (d_time_sup * d_x_inf)) /
		(d_time_inf - d_time_sup);

	      x_rg[i] = (float) (a * time_rg[i] + b);
	    }
	  else
	    {
	      x_rg[i] = x_as[jsup];
	    }
	}
    }

  /* Est-ce utile ??? */
  x_rg[0] = x_rg[1];

  return 0;
}

/* fonction d'enrobage */

int
OP_Interpol_irreg_mnq (unsigned long Nbval, void *ArgList[], char *DiagExec)
{
  int NCar;
  int CodRet;

  NCar = sprintf (DiagExec,
		  "Interpol_irreg_mnq. Dest : %lu ech, orig = %lu ech,"
		  " duree max interpol : %g, extrapol : %g s.",
		  Nbval, *((unsigned long *) ArgList[3]),
		  *((float *) ArgList[4]), *((float *) ArgList[5]));
  DiagExec += NCar;
  DiagExec = ecrit_bornes_temps (DiagExec, "Time_rg", (double *) ArgList[0],
				 Nbval);
  DiagExec = ecrit_bornes_temps (DiagExec, "Time_as", (double *) ArgList[1],
				 *((unsigned long *) ArgList[3]));

  CodRet = Interpol_irreg_mnq (Nbval,
			       (double *) ArgList[0],
			       (double *) ArgList[1],
			       (float *) ArgList[2],
			       *((unsigned long *) ArgList[3]),
			       *((float *) ArgList[4]),
			       *((float *) ArgList[5]), (float *) ArgList[6]);

  return OP_OK;
}

void
ID_Interpol_irreg_mnq (oper * optr)
{
  strcpy (optr->Nom, "Interpol_irreg_mnq");
  optr->Version = "$Revision$";
  optr->Date = "$Date$";
  optr->fctptr = OP_Interpol_irreg_mnq;
  optr->NbArg = 7;

  /*  time_rg */
  optr->Arg_Car[0].direction = DIR_IN;
  optr->Arg_Car[0].categorie = VECTOR;
  optr->Arg_Car[0].typ = ATYC_IF64;
  optr->Arg_Car[0].array_dim = "1";
  optr->Arg_Car[0].type_sample = "any";
  optr->Arg_Car[0].sample = "any";
  optr->Arg_Car[0].unite = "second";

  /*  time_as */
  optr->Arg_Car[1].direction = DIR_IN;
  optr->Arg_Car[1].categorie = VECTOR;
  optr->Arg_Car[1].typ = ATYC_IF64;
  optr->Arg_Car[1].array_dim = "1";
  optr->Arg_Car[1].type_sample = "any";
  optr->Arg_Car[1].sample = "any";
  optr->Arg_Car[1].unite = "second";

  /*  X_as */
  optr->Arg_Car[2].direction = DIR_IN;
  optr->Arg_Car[2].categorie = VECTOR;
  optr->Arg_Car[2].typ = ATYC_IF32;
  optr->Arg_Car[2].array_dim = "1";
  optr->Arg_Car[2].NbVal = "$Arg2.NbVal";	/* Pas auto-referent, parceque les $Arg se comptent à partir de 1 */
  optr->Arg_Car[2].type_sample = "any";
  optr->Arg_Car[2].sample = "any";
  optr->Arg_Car[2].unite = "";

  /* size_as */
  optr->Arg_Car[3].direction = DIR_IN;
  optr->Arg_Car[3].categorie = COEFFICIENT;
  optr->Arg_Car[3].typ = ATYC_LOCAL_ULONG;
  optr->Arg_Car[3].array_dim = "1";
  optr->Arg_Car[3].type_sample = "any";
  optr->Arg_Car[3].sample = "any";
  optr->Arg_Car[3].unite = "";

  /* Nb_Sec_interpol */
  optr->Arg_Car[4].direction = DIR_IN;
  optr->Arg_Car[4].categorie = COEFFICIENT;
  optr->Arg_Car[4].typ = ATYC_IF32;
  optr->Arg_Car[4].array_dim = "1";
  optr->Arg_Car[4].unite = "second";

  /* Nb_Sec_extrapol */
  optr->Arg_Car[5].direction = DIR_IN;
  optr->Arg_Car[5].categorie = COEFFICIENT;
  optr->Arg_Car[5].typ = ATYC_IF32;
  optr->Arg_Car[5].array_dim = "1";
  optr->Arg_Car[5].unite = "second";

  /* x_rg */
  optr->Arg_Car[6].direction = DIR_OUT;
  optr->Arg_Car[6].categorie = VECTOR;
  optr->Arg_Car[6].typ = ATYC_IF32;
  optr->Arg_Car[6].array_dim = "1";
  optr->Arg_Car[6].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[6].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[6].sample = "$Arg1.sample";
  optr->Arg_Car[6].ref_time = " $Arg1.nom ";
  optr->Arg_Car[6].unite = "$Arg3.unit";
  optr->Arg_Car[6].famille = "auto";
  optr->Arg_Car[6].misval = "$Arg3.misval";
  optr->Arg_Car[6].name = "$Arg3.name + \" interpolle sur \" + $Arg1.name";
  optr->Arg_Car[6].en_name =
    "$Arg3.english_name + \" interpolated on \" + $Arg1.english_name";
}
