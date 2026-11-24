/****************************************************
*
* OPERATOR      MoyEch.c   FUNCTION  ANSI-C
*
* PURPOSE       Averaging and sampling of a regularly-sampled time serie
*
* DESCRIPTION   Routine de moyenne-echantillon, pour variables "float".
*               Les valeurs absentes sont gérées par le mécanisme
*               automatique (système des NaN). Il suffit donc qu'une
*               valeur sur une somme soit absente pour que le résultat
*               ne soit pas calculé. 
*               Attention, cette routine ne fonctione bien que si RapFreq
*               est l'inverse d'un entier !
*               Dans les autres cas, on utilisera l'entier le plus proche,
*               ce qui risque de ne pas donner exactement le résultat
*               attendu.
*
* VERSION       $Revision$
*
* ARGUMENTS   IN   float  Var_in     any        Original data
*             IN   double RapFreq    whithout   frequency ratio (out/in)
*             IN   int    Decal      sec/freq   delay between first values
*             OUT  float  Var_out    same as 1  Averaged and sub-sampled data
*
* REFERENCES
*
* CHANGES       
*               This function replace the old "Moy.c" 12/4/1999
*               1.3 followed Categorie definition's change.
*               1.2 added comments/switched arg. orders
*
* COPYRIGHT     Meteo-France
*
*#########################################################################*/

#define _POSIX_SOURCE 1
#define _XOPEN_SOURCE 600

#include <stdio.h>
#include <math.h>
#include <string.h>
#include <limits.h>

#include "struct_oper.h"

/** 
* @brief Calcul de la moyenne de N flottants
* 
* 
* @param data_p : pointeur vers le premier échantillon
* @param N : le nombre d'échantillons
* @param tolerance_mnq : Inutilisé (présent pour compatibilité
*   avec syntaxe d'appel d'autres fonctions semblables).
*
* @return La valeur de la moyenne, ou un NaN s'il n'est pas 
*   possible de la calculer.
*/
float
moy_flt_simple_passe (const float *data_p, long N, int tolerance_mnq)
{
  long j;
  register double loc_som;

  loc_som = 0.0;
  for (j = 0; j < N; j++)
    {
      loc_som += *data_p;
      data_p++;
    }
  return loc_som / N;
}

/* La vraie fonction... */
long
MoyEch (unsigned long NbValIn,
	const float *Var_in,
	const double RapFreq,
	const int Decal, float *Var_out, long TabStat[4])
{
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
      if ((NSom + Decal) > 0)
	{
	  *Var_out = moy_flt_simple_passe (Var_in, NSom + Decal, 0);
	  Var_in += NSom + Decal;
	}
      else
	*Var_out = *Var_in;	/* Plutôt que 0 ou ValAbs... */
      Var_out++;
    }
  else				/* Cas ou Decal est positif */
    {
      Var_in += Decal;
    }
  /* Fin du if sur Decal < ou > 0 */

  /* Ensuite la boucle standard sur les Ntour  */

  for (i = 0; i < Ntour - 1; i++)
    {
      *Var_out = moy_flt_simple_passe (Var_in, NSom, 0);
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
	  *Var_out = moy_flt_simple_passe (Var_in, NSomfin, 0);
	  Var_in += NSomfin;
	}
      else			/* Cas ou NSomfin == 0 */
	*Var_out = *(Var_in - 1);

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
	*Var_out = *(Var_out - 1);	/* Duplication de la fin */
      else
	{
	  *Var_out = moy_flt_simple_passe (Var_in, NSomfin, 0);
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
OP_MoyEch (unsigned long NbVal, void *ArgList[], char *DiagExec)
{
  long CodRet;
  int NCar;
  long TabStat[4];

  NCar = sprintf (DiagExec, "MoyEch (%lu ech), F_out/F_in = %g, decal = %d; ",
		  NbVal, *((double *) ArgList[1]), *((int *) ArgList[2]));
  if (NCar < 0)
    NCar = 0;
  DiagExec += NCar;

  CodRet = MoyEch (NbVal,
		   (float *) ArgList[0],
		   *((double *) ArgList[1]),
		   *((int *) ArgList[2]), (float *) ArgList[3], TabStat);

  if (CodRet >= 0)
    {
      if (fabs (TabStat[0] - (1.0 / *((double *) ArgList[1]))) < 1.0e-6)
	{
	  sprintf (DiagExec,
		   "OK: %ld val. calculées,  (%lu = %ld * %ld + %ld).",
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
ID_MoyEch (oper * optr)
{
  strcpy (optr->Nom, "MoyEch");
  optr->Version = "$Revision$";
  optr->Date = "$Date$";
  optr->fctptr = OP_MoyEch;
  optr->NbArg = 4;
  optr->misval_auto = 1;	/* On s'en remet au mécanisme automatique.  */

  /* Var_in */
  optr->Arg_Car[0].direction = DIR_IN;
  optr->Arg_Car[0].categorie = VECTOR;
  optr->Arg_Car[0].typ = ATYC_IF32;
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

  /* Var_out */
  optr->Arg_Car[3].direction = DIR_OUT;
  optr->Arg_Car[3].categorie = VECTOR;
  optr->Arg_Car[3].typ = ATYC_IF32;
  optr->Arg_Car[3].array_dim = "1";
  optr->Arg_Car[3].name = "$Arg1.name";
  /* Les routines d'interpolations "universelles" obligent à utiliser */
  /* une  formule pour calculer le nombre d'elements du vecteur de sortie. */
  optr->Arg_Car[3].NbVal = "$Arg1.NbVal * $Arg2";
  optr->Arg_Car[3].sample = "$Arg1.sample * $Arg2";
  optr->Arg_Car[3].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[3].ref_time = " \"time_\" + $Arg4.sample";
  optr->Arg_Car[3].misval = "$Arg1.misval";
  /* Par contre, l'unite est simple... */
  optr->Arg_Car[3].unite = "$Arg1.unit";
  optr->Arg_Car[3].famille = "$Arg1.famille";
  /* On considere que le moyenne et le sous-echantillonnage ne change */
  optr->Arg_Car[3].name =
    "$Arg1.name + \" moyenne a \" + $Arg4.sample + \"Hz\"";
  optr->Arg_Car[3].en_name =
    "$Arg1.english_name + \" averaged at \" + $Arg4.sample + \"Hz\"";
}
