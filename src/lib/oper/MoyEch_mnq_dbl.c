/****************************************************
*
* OPERATOR      MoyEch_mnq_dbl.c   FUNCTION  ANSI-C
*
* PURPOSE       Averaging and sampling of a time serie
* OBJECTIF      Moyenne d'une serie-temporelle de flottants doubles
*
* DESCRIPTION   Routine de moyenne-echantillon, pour variables "double".
*               Les valeurs absentes sont gérées par le mécanisme
*               automatique (système des NaN). 
*               Les valeurs manquantes (NaN) sont eliminees et decomptees
*		afin que le nombre de valeurs manquantes soit < a tolerance_mnq.
*               Attention, cette routine ne fonctionne bien que si RapFreq
*               est l'inverse d'un entier !
*               Dans les autres cas, on utilisera l'entier le plus proche,
*               ce qui risque de ne pas donner exactement le résultat
*               attendu.
*
* VERSION       $Revision$
*
* ARGUMENTS   IN   double  Var_in     any        Original data
*             IN   double  RapFreq    whithout   frequency ratio
*             IN   int     Decal      sec/freq   delay between first values
*             IN   int     tolerance_mnq   Tolerance pour le nb maxi de valeurs
*						 manquantes
*             OUT  double  Var_out    same as 1  Averaged data
*
* REFERENCES
*
* CHANGES       
*               Cette fonction est identique a la fonction MoyEch_mnq.c
*               avec des flottants double en entree/sortie
*
* COPYRIGHT     Meteo-France
*
*#########################################################################*/

#define _POSIX_SOURCE 1
#define _XOPEN_SOURCE 600
#define _XOPEN_SOURCE_EXTENDED

#include <stdio.h>
#include <math.h>
#include <string.h>
#include <limits.h>
#include "struct_oper.h"

long
MoyEch_mnq_dbl (unsigned long NbValIn,
		const double *Var_in,
		const double RapFreq,
		const int Decal,
		const int tolerance_mnq, double *Var_out, long TabStat[4])
{
  long i, NbValOut;
  long Ntour, Reste;
  int j, NSom, NSomfin;
  register double loc_som;
  register double mnq_som;
  const double misval_out = K_NaN;

  if (RapFreq > 1.0)
    return -1;

  NSom = floor ((1.0 / RapFreq) + 0.5);
/* faudrait verifier que |Nsom - 1/RapFreq| < EPSILON */

  if ((Decal < -NSom) || (Decal > NSom))
    return -2;

/* Réglons immédiatement le cas ou y'a rien a faire : "NbValIn = 0" */
  if (NbValIn == 0)
    return 0;

/*
 * Normalement, il y a Ntour calculs "standards" à faire.
 *  Si on tient compte de Decal, le premier ou le dernier peut ne
 * plus être standard--> traitement des cas-particulier, et boucle sur
 * (Ntour - 1) cas.
 */

  Ntour = NbValIn / NSom;	/* division entière */
  Reste = NbValIn % NSom;

/* 
 * La première somme se fait de Decal à Decal+Nsom-1, mais si 
 * Decal est negatif, on commence à zero.
 * Si Decal est positif, cette première somme se fait dans la boucle standard.
 */

  if (Decal < 0)
    {
      if (NSom + Decal > 0)
	{
	  loc_som = 0.0;
	  mnq_som = 0.0;
	  for (j = 0; j < NSom + Decal; j++)
	    {
	      if (!isfinite (*Var_in))
		{
		  mnq_som = mnq_som + 1;
		  Var_in++;
		}
	      else
		{
		  loc_som += *Var_in;
		  Var_in++;
		}
	    }
	  if (mnq_som <= tolerance_mnq)
	    {
	      *Var_out = loc_som / (NSom + Decal - mnq_som);
	    }
	  else
	    {
	      *Var_out = misval_out;
	    }
	}
      else
	*Var_out = *Var_in;	/* Plutôt que 0 ou misval... */

      Var_out++;
    }
  else				/* Cas ou Decal est positif */
    Var_in += Decal;
/* Fin du if sur Decal < ou > 0 */


  /* Ensuite la boucle standard sur les Ntour 
     Si le nb de misval est >= tolerance_mnq :
     -pas de moyenne (misval)
     Sinon moyenne sur les (NSom - mnq_som) valeurs de Var_in */

  for (i = 0; i < Ntour - 1; i++)
    {
      loc_som = 0.0;
      mnq_som = 0.0;
      for (j = 0; j < NSom; j++)
	{
	  if (!isfinite (*Var_in))
	    {
	      mnq_som = mnq_som + 1;
	      Var_in++;
	    }
	  else
	    {
	      loc_som += *Var_in;
	      Var_in++;
	    }
	}
      if (mnq_som <= tolerance_mnq)
	{
	  /* printf(" loc_som = %f   NSom = %d   mnq_som = %f \n",loc_som,NSom,mnq_som); */
	  *Var_out = loc_som / (NSom - mnq_som);
	  /*  printf("    Var_out = %f \n",*Var_out); */
	}
      else
	{
	  /*** SB : Ajout d'un \n pour limiter les output foireux dans ADC ***/
      printf ("-+- boucle principale TROP de misval --> MISVAL\n");
	  *Var_out = misval_out;
	}
      Var_out++;
    }

/* 
 * La dernière somme se doit pas dépasser NbValIn.
 * Si Decal est négatif, y'a pas de Pb, ça a été fait dans la boucle standard.
 * Si Decal est positif, le nombre normal de sommes peut être réduit
 * si (Nsom + Reste - Decal) est plus petit que Nsom.
 */

  if (Decal >= 0)
    {
      NSomfin = NSom + Reste - Decal;
      if (NSomfin > NSom)
	NSomfin = NSom;
      if (NSomfin > 0)
	{
	  loc_som = 0.0;
	  mnq_som = 0.0;
	  for (j = 0; j < NSomfin; j++)
	    {
	      if (!isfinite (*Var_in))
		{
		  mnq_som = mnq_som + 1;
		  Var_in++;
		}
	      else
		{
		  loc_som += *Var_in;
		  Var_in++;
		}
	    }
	  if (mnq_som <= tolerance_mnq)
	    {
	      *Var_out = loc_som / (NSomfin - mnq_som);
	    }
	  else
	    {
	      *Var_out = misval_out;
	    }
	}
      else			/* Cas ou NSomfin = 0 */
	*Var_out = *(Var_in - 1);

      Var_out++;
    }

  NbValOut = Ntour;

  /* Et si Reste > 0, Y'a encore une valeur a remplir, indépendament */
  /* de la valeur de Decal.             */
  /* Le nombre de valeurs qu'il reste à sommer est Reste - Decal,   */
  /* si ce terme est positif.           */

  if (Reste > 0)
    {
      NbValOut++;
      NSomfin = Reste - Decal;
      if (NSomfin < 0)
	*Var_out = *(Var_out - 1);	/* Duplication de la fin */
      else
	{
	  *Var_out = *(Var_in);	/* On ne fait pas de somme.... */
	}
    }

  TabStat[0] = NSom;
  TabStat[1] = Ntour;
  TabStat[2] = Reste;
  TabStat[3] = NSomfin;
  return NbValOut;
}

/* la fonction d'enrobage classique */

int
OP_MoyEch_mnq_dbl (unsigned long NbVal, void *ArgList[], char *DiagExec)
{
  long CodRet;
  int NCar;
  long TabStat[4];

  NCar =
    sprintf (DiagExec,
	     "MoyEch_mnq_dbl (%lu ech), F_out/F_in = %g, decal = %d; toler_mnq=%d ech.",
	     NbVal, *((double *) ArgList[1]), *((int *) ArgList[2]),
	     *((int *) ArgList[3]));
  if (NCar < 0)
    NCar = 0;
  DiagExec += NCar;

  CodRet = MoyEch_mnq_dbl (NbVal,
			   (double *) ArgList[0],
			   *((double *) ArgList[1]),
			   *((int *) ArgList[2]),
			   *((int *) ArgList[3]),
			   (double *) ArgList[4], TabStat);

  if (CodRet >= 0)
    {
      if (fabs (TabStat[0] - (1.0 / *((double *) ArgList[1]))) < 1.0e-6)
	{
	  sprintf (DiagExec,
		   "OK: %ld val. calculées,  (%ld = %ld * %ld + %ld).",
		   CodRet, NbVal, TabStat[1], TabStat[0], TabStat[2]);
	}
      else
	{
	  sprintf (DiagExec,
		   "WARN: %g arrondi en %g. %ld val. calculées (%ld*%ld+%ld).",
		   *((double *) ArgList[1]), 1.0 / TabStat[0], CodRet,
		   TabStat[1], TabStat[0], TabStat[2]);
	}
      return OP_OK;
    }
  switch (CodRet)
    {
    case -1:
      sprintf (DiagExec, "ERR: RapFreq > 1 !!!");
      break;
    case -2:
      sprintf (DiagExec, "ERR: Decal hors-bornes.");
      break;
    default:
      sprintf (DiagExec, "ERR: Erreur %ld.", CodRet);
    }
  return OP_FAIL;
}

void
ID_MoyEch_mnq_dbl (oper * optr)
{
  strcpy (optr->Nom, "MoyEch_mnq_dbl");
  optr->Version = "$Revision$";
  optr->Date = "$Date$";
  optr->fctptr = OP_MoyEch_mnq_dbl;
  optr->NbArg = 5;
  optr->misval_auto = 1;	/* On s'en remet au mécanisme automatique.  */

  /* Var_in */
  optr->Arg_Car[0].direction = DIR_IN;
  optr->Arg_Car[0].categorie = VECTOR;
  optr->Arg_Car[0].typ = ATYC_IF64;
  optr->Arg_Car[0].array_dim = "1";
  optr->Arg_Car[0].type_sample = "any";
  optr->Arg_Car[0].sample = "any";
  optr->Arg_Car[0].unite = "any";
  optr->Arg_Car[0].famille = "any";

  /* RapFreq */
  optr->Arg_Car[1].direction = DIR_IN;
  optr->Arg_Car[1].categorie = COEFFICIENT;
  optr->Arg_Car[1].array_dim = "1";
  optr->Arg_Car[1].typ = ATYC_IF64;
  optr->Arg_Car[1].unite = "any";

  /* Decal */
  optr->Arg_Car[2].direction = DIR_IN;
  optr->Arg_Car[2].categorie = COEFFICIENT;
  optr->Arg_Car[2].array_dim = "1";
  optr->Arg_Car[2].typ = ATYC_I32;
  optr->Arg_Car[2].unite = "any";

  /* tolerance_mnq */
  optr->Arg_Car[3].direction = DIR_IN;
  optr->Arg_Car[3].categorie = COEFFICIENT;
  optr->Arg_Car[3].array_dim = "1";
  optr->Arg_Car[3].typ = ATYC_I32;
  optr->Arg_Car[3].unite = "any";

  /* Var_out */
  optr->Arg_Car[4].direction = DIR_OUT;
  optr->Arg_Car[4].categorie = VECTOR;
  optr->Arg_Car[4].typ = ATYC_IF64;
  optr->Arg_Car[4].array_dim = "1";
  optr->Arg_Car[4].name = "$Arg1.name";
  /* Les routines d'interpolations "universelles" obligent à utiliser */
  /* une  formule pour calculer le nombre d'elements du vecteur de sortie. */
  optr->Arg_Car[4].NbVal = "$Arg1.NbVal * $Arg2";
  optr->Arg_Car[4].sample = "$Arg1.sample * $Arg2";
  /* Par contre, l'unite est simple... */
  optr->Arg_Car[4].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[4].ref_time = " \"time_\" + $Arg5.sample";
  optr->Arg_Car[4].misval = "$Arg1.misval";
  optr->Arg_Car[4].unite = "$Arg1.unit";
  optr->Arg_Car[4].famille = "$Arg1.famille";
  optr->Arg_Car[4].name =
    "$Arg1.name + \" moyenne a \" + $Arg5.sample + \"Hz\"";
  optr->Arg_Car[4].en_name =
    "$Arg1.english_name + \" averaged at \" + $Arg5.sample + \"Hz\"";
}
