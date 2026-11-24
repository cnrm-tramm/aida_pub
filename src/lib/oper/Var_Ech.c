/****************************************************
*
* OPERATOR      Var_Ech.c   FUNCTION  ANSI-C
*
* PURPOSE       Compute variance on regular sub-sample of a time serie.
*
* DESCRIPTION   Routine de calcul de variance, sur des sous-périodes
*               de taille fixe, pour variables "float".
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
* ARGUMENTS   IN   float  Var_in     any        Original data
*             IN   double RapFreq    whithout   frequency ratio
*             IN   int    Decal      sec/freq   delay between first values
*             IN   int    tolerance_mnq   Tolerance pour le nb maxi de valeurs
*						 manquantes
*             IN   int    flag_method            Methode (brut ou débiaisé par n/(n-1))
*             OUT  float  Var_out    same as 1  small serie of variances.
*
* REFERENCES
*
* CHANGES      Original coding : 20050913 by BP.
*
* COPYRIGHT     Meteo-France/CNRM
*
*#########################################################################*/

#define _POSIX_SOURCE 1
#define _XOPEN_SOURCE 600
#define _XOPEN_SOURCE_EXTENDED

#define _HPUX_SOURCE 1

#include <stdio.h>
#include <math.h>
#include <string.h>
#include <limits.h>

#include "struct_oper.h"

/** 
* @brief Calcul de la variance de N flottants par 
* la formule : var = moy(x^2) - moy(x)^2, qui ne
* nécessite qu'un parcours de l'ensemble des valeurs,
* mais peut être imprécise si le nombre d'échantillons
* est grand.
* 
* @param data_p : pointeur vers le premier échantillon
* @param N : le nombre d'échantillons
* @param tolerance_mnq : le nombre max de valeurs manquantes
*    tolérées (au-dela, pas de calcul et résultat = NaN).
* 
* @return La valeur de la variance, ou un NaN s'il n'est pas 
*   possible de la calculer.
*/
float
var_flt_simple_passe (const float *data_p, long N, int tolerance_mnq)
{
  const float misval_out = K_NaN;
  register double loc_som;
  register double loc_som2;
  long mnq_som;
  long j;
  float variance;

  if (N <= 1)
    return misval_out;

  loc_som = 0.0;
  loc_som2 = 0.0;
  mnq_som = 0;
  for (j = 0; j < N; j++)
    {
      if (!isfinite (*data_p))
	{
	  mnq_som = mnq_som + 1;
	}
      else
	{
	  loc_som += *data_p;
	  loc_som2 += *data_p * *data_p;
	}
      data_p++;
    }

  if (mnq_som <= tolerance_mnq)
    {
      /* printf(" loc_som = %f   NSom = %d   mnq_som = %f \n",loc_som,NSom,mnq_som); */
      loc_som = loc_som / (N - mnq_som);
      loc_som2 = loc_som2 / (N - mnq_som);
      variance = loc_som2 - loc_som * loc_som;
      if (variance < 0)
	variance = 0;
      return variance;
    }
  else
    {
	  /*** SB : Ajout d'un \n pour limiter les output foireux dans ADC ***/
      printf ("-+- boucle principale TROP de misval --> MISVAL\n");
      return misval_out;
    }
}

long
Var_Ech (unsigned long NbValIn,
	 const float *Var_in,
	 const double RapFreq,
	 const int Decal,
	 const int tolerance_mnq, float *Var_out, long TabStat[4])
{
  const float misval_out = K_NaN;
  long i, NbValOut;
  long Ntour, Reste;
  int NSom, NSomfin;

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
	  *Var_out =
	    var_flt_simple_passe (Var_in, NSom + Decal, tolerance_mnq);
	  Var_in += NSom + Decal;
	}
      else
	*Var_out = misval_out;	/* Plutôt que 0... */

      Var_out++;
    }
  else				/* Cas ou Decal est positif */
    Var_in += Decal;
  /* Fin du if sur Decal < ou > 0 */


  /* Ensuite la boucle standard sur les Ntour  */

  for (i = 0; i < Ntour - 1; i++)
    {
      *Var_out = var_flt_simple_passe (Var_in, NSom, tolerance_mnq);
      Var_out++;
      Var_in += NSom;
    }

/* 
 * La dernière somme se doit pas dépasser NbValIn.
 * Si Decal est négatif, y'a pas de Pb, ça a été fait dans la boucle standard.
 * Si Decal est positif, le nombre normal de sommes peut être réduit
 * si (Nsom + Reste - Decal) est plus petit que Nsom.
 */

  NSomfin = 0;
  if (Decal >= 0)
    {
      NSomfin = NSom + Reste - Decal;
      if (NSomfin > NSom)
	NSomfin = NSom;
      if (NSomfin > 0)
	{
	  *Var_out = var_flt_simple_passe (Var_in, NSomfin, tolerance_mnq);
	  Var_in += NSomfin;
	}
      else			/* Cas ou NSomfin == 0 */
	*Var_out = misval_out;

      Var_out++;
    }

  NbValOut = Ntour;

  /* Et si Reste > 0, Y'a encore une valeur a remplir, indépendament
   * de la valeur de Decal.
   * Le nombre de valeurs qu'il reste à sommer est Reste - Decal,
   * si ce terme est positif.
   */

  if (Reste > 0)
    {
      NbValOut++;
      NSomfin = Reste - Decal;
      if (NSomfin <= 0)
	*Var_out = misval_out;
      else
	{
	  *Var_out = var_flt_simple_passe (Var_in, NSomfin, tolerance_mnq);
	  /* Pas d'incrémentation Var_out++; Var_in +=xxx parce que c'est la fin */
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
OP_Var_Ech (unsigned long NbVal, void *ArgList[], char *DiagExec)
{
  long CodRet;
  int NCar;
  long TabStat[4];

  NCar =
    sprintf (DiagExec, "Var_Ech (%lu ech), F_out/F_in = %g, decal = %d; ",
	     NbVal, *((double *) ArgList[1]), *((int *) ArgList[2]));
  if (NCar < 0)
    NCar = 0;
  DiagExec += NCar;

  CodRet = Var_Ech (NbVal,
		    (float *) ArgList[0],
		    *((double *) ArgList[1]),
		    *((int *) ArgList[2]),
		    *((int *) ArgList[3]), (float *) ArgList[5], TabStat);

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
ID_Var_Ech (oper * optr)
{
  strcpy (optr->Nom, "Var_Ech");
  optr->Version = "$Revision$";
  optr->Date = "$Date$";
  optr->fctptr = OP_Var_Ech;
  optr->NbArg = 6;
  optr->misval_auto = 1;	/* On s'en remet au mécanisme automatique.  */

  /* X */
  optr->Arg_Car[0].direction = DIR_IN;
  optr->Arg_Car[0].categorie = VECTOR;
  optr->Arg_Car[0].typ = ATYC_IF32;
  optr->Arg_Car[0].array_dim = "1";
  optr->Arg_Car[0].type_sample = "any";
  optr->Arg_Car[0].sample = "any";
  optr->Arg_Car[0].unite = "any";
  optr->Arg_Car[0].famille = "any";

  /* Rf */
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

  /* Toler_mnq */
  optr->Arg_Car[3].direction = DIR_IN;
  optr->Arg_Car[3].categorie = COEFFICIENT;
  optr->Arg_Car[3].array_dim = "1";
  optr->Arg_Car[3].typ = ATYC_I32;
  optr->Arg_Car[3].unite = "any";

  /* Flag (future use) */
  optr->Arg_Car[4].direction = DIR_IN;
  optr->Arg_Car[4].categorie = COEFFICIENT;
  optr->Arg_Car[4].array_dim = "1";
  optr->Arg_Car[4].typ = ATYC_I32;
  optr->Arg_Car[4].unite = "any";
  optr->Arg_Car[4].type_sample = NULL;
  optr->Arg_Car[4].sample = NULL;

  /* Var_out (=Variance) */
  optr->Arg_Car[5].direction = DIR_OUT;
  optr->Arg_Car[5].categorie = VECTOR;
  optr->Arg_Car[5].typ = ATYC_IF32;
  optr->Arg_Car[5].array_dim = "1";
  /* Les routines faisant une transformation temporelle obligent à utiliser
   * une  formule pour calculer le nombre d'elements du vecteur de sortie. */
  optr->Arg_Car[5].NbVal = "$Arg1.NbVal * $Arg2";
  optr->Arg_Car[5].sample = "$Arg1.sample * $Arg2";
  optr->Arg_Car[5].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[5].ref_time = " \"rft_time_\" + $Arg6.sample";
  /* optr->Arg_Car[5].ref_time = "$Arg1.ref_time+\"_Med_\"+$Arg6.sample"; */
  optr->Arg_Car[5].misval = "$Arg1.misval";
  optr->Arg_Car[5].unite = "$Arg1.unit $Arg1.unit";	/* une des syntaxe de multiplication d'unité */
  /* cela permet de déclarer le vecteur en trb */
  optr->Arg_Car[5].famille = "auto";
  optr->Arg_Car[5].name = "\"Variance de \"+$Arg1.name";
  optr->Arg_Car[5].en_name = "\"Variance of \"+$Arg1.english_name";
}
