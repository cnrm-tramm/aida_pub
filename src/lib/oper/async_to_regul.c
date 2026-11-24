/*******************************************************************
* OPERATOR      async_to_regul.c FUNCTION ANSI-C
*
* PURPOSE 	Interpolation d'une variable sur une autre base de temps. 
*
*		Par exemple, transformation d'une serie temporelle asynchrone  
*		en une serie reguliere. 
*		
* DESCRIPTION	Cette fonction interpole une variable "x_as"
*		qui est date par le vecteur temps "time_as" sur une 
*		autre base de temps "time_rg".
*		La variable resultat est "x_rg"		
*		L'interpolation est lineaire.	
*		On suppose que time_as est "a peu pres" trié par ordre
*               croissant.
*		 
* VERSION       1.1  
*
* ARGUMENTS     IN   double  time_rg  second  base de temps d'arrivee
*               IN   double  time_as  second  base de temps de depart
*               IN   float   x_as     any      variable de depart a interpoler 
*
*               OUT  float   x_rg   same as "x_as"  variable "x-as" interpolee 
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

/* Pour le moment les "time_rg" et "time_as" doivent avoir
   la meme taille. */

int
async_to_regul (unsigned long size,
		double *time_rg, double *time_as, float *x_as, float *x_rg)
{
  long i, jinf, jinf2, jsup, jsup2;

  double min_delta_T;
  double d_x_sup, d_x_inf, d_time_inf, d_time_sup;
  double a, b;
  const double epsilon = 10.0 * DBL_MIN;

  jsup = 1;
  jinf = 0;

/********************************************************
 * On incremente le time_rg (regulier) et on cherche
 * les 2 valeurs de time_as qui l'encadrent.
 * On interpole lineairement la valeur entre les 2 points
 *********************************************************
 */

  for (i = 1; i < size; i++)
    {
      /* Etape 1 : */
      /* Recherche d'un temps asynchone plus grand que time_rg[i] */

      /* Pour éviter de parcourir toute les valeurs, voire de */
      /* les trier, on estime j_sup */
      if (jinf < size - 1)
	jsup = jinf + 1;
      else
	jsup = 0;

      while ((time_as[jsup] <= time_rg[i]) && (jsup < (size - 1)))
	{
	  jsup = jsup + 1;
	}
      /* Dans certains cas, on peut vouloir chercher */
      /* plus loin une valeur convenable.            */
      min_delta_T = time_as[jsup] - time_rg[i];
      jsup2 = jsup + 1;
      while ((time_as[jsup2] - time_rg[i] <= min_delta_T)
	     && (jsup2 <= (size - 1)))
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

      while ((time_rg[i] < time_as[jinf]) && (jinf > 0))
	{
	/** ceci est pour prendre en compte le cas ou 
           (time_as[jsup] < time_as[jsup-1]) 
        **/
	  jinf = jinf - 1;
	}
      /* Comme pour la recherche de valeur plus grande, */
      /* il faut aller voir si il n'y a pas "avant" une */
      /* valeur plus proche du temps recherché */
      /* (le temps asynchrone n'est pas forcement trié).  */
      min_delta_T = time_rg[i] - time_as[jinf];
      jinf2 = jinf - 1;
      while (((time_rg[i] - time_as[jinf2]) <= min_delta_T) && (jinf2 >= 0))
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

      /* question soulevee lors d'une relecture de code le 22/02/1999 : */
      /*  pourquoi ne pas coder plus simplement l'interpolation lineaire ? */
      /* du genre :     */
      /* x_rg = x_as[jinf] +                 */
      /*   (time_rg[i]-time_as[jinf]) * (x_as[jsup]-x_as[jinf])/(time_as[jsup]-time_as[jinf]) */

      d_x_inf = (double) x_as[jinf];
      d_x_sup = (double) x_as[jsup];

      d_time_inf = time_as[jinf];
      d_time_sup = time_as[jsup];

      if (fabs (d_time_inf - d_time_sup) > epsilon)
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

  /* Est-ce utile ??? */
  x_rg[0] = x_rg[1];

  return 0;
}

/* fonction d'enrobage */

int
OP_async_to_regul (unsigned long Nbval, void *ArgList[], char *DiagExec)
{
  int NCar;
  int CodRet;

  NCar = sprintf (DiagExec, "async_to_regul (%lu ech), ", Nbval);
  DiagExec += NCar;
  DiagExec = ecrit_bornes_temps (DiagExec, "Time_rg", (double *) ArgList[0],
                                 Nbval);
  DiagExec = ecrit_bornes_temps (DiagExec, "Time_as", (double *) ArgList[1],
                                 Nbval);

  CodRet = async_to_regul (Nbval,
			   (double *) ArgList[0],
			   (double *) ArgList[1],
			   (float *) ArgList[2],
			   (float *) ArgList[3]);

  return OP_OK;
}

void
ID_async_to_regul (oper * optr)
{
  strcpy (optr->Nom, "async_to_regul");
  optr->Version = "$Revision$";
  optr->Date = "$Date$";
  optr->fctptr = OP_async_to_regul;
  optr->NbArg = 4;

  /* time_rg */
  optr->Arg_Car[0].direction = DIR_IN;
  optr->Arg_Car[0].categorie = VECTOR;
  optr->Arg_Car[0].typ = ATYC_IF64;
  optr->Arg_Car[0].array_dim = "1";
  optr->Arg_Car[0].type_sample = "any";
  optr->Arg_Car[0].sample = "any";
  optr->Arg_Car[0].unite = "second";

  /* time_as */
  optr->Arg_Car[1].direction = DIR_IN;
  optr->Arg_Car[1].categorie = VECTOR;
  optr->Arg_Car[1].typ = ATYC_IF64;
  optr->Arg_Car[1].array_dim = "1";
  optr->Arg_Car[1].NbVal = "$Arg1.NbVal";	/*  Doit avoir autant d'échantillon que l'autre temps ! */
  optr->Arg_Car[1].type_sample = "any";
  optr->Arg_Car[1].sample = "any";
  optr->Arg_Car[1].unite = "second";

  /* x_as */
  optr->Arg_Car[2].direction = DIR_IN;
  optr->Arg_Car[2].categorie = VECTOR;
  optr->Arg_Car[2].typ = ATYC_IF32;
  optr->Arg_Car[2].array_dim = "1";
  optr->Arg_Car[2].NbVal = "$Arg2.NbVal";	/* Doit avoir autant d'échantillon que son ref_time.  */
  optr->Arg_Car[2].type_sample = "any";
  optr->Arg_Car[2].sample = "any";
  optr->Arg_Car[2].unite = "";

  /* x_rg */
  optr->Arg_Car[3].direction = DIR_OUT;
  optr->Arg_Car[3].categorie = VECTOR;
  optr->Arg_Car[3].typ = ATYC_IF32;
  optr->Arg_Car[3].array_dim = "1";
  optr->Arg_Car[3].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[3].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[3].sample = "$Arg1.sample";
  optr->Arg_Car[3].ref_time = " $Arg1.nom ";
  optr->Arg_Car[3].unite = "$Arg3.unit";
  optr->Arg_Car[3].famille = "$Arg3.famille";
  optr->Arg_Car[3].name = "$Arg3.name";
  optr->Arg_Car[3].en_name = "$Arg3.english_name";
}
