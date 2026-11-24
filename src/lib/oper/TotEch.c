/****************************************************
*
* OPERATOR      TotEch.c   FUNCTION  ANSI-C
*
* PURPOSE       Somme et echantillonnage dans une serie temporelle
*
* DESCRIPTION   Routine de somme pour variables "float".
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
*             IN   double RapFreq    whithout   frequency ratio
*             OUT  float  Var_out    same as 1  Somme de Var_in
*
* REFERENCES
*
* CHANGES       
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

/* La vraie fonction... */

long
TotEch (unsigned long NbValIn,
	const float *Var_in,
	const double RapFreq,
	float *Var_out,
	long TabStat[4])
{
  long i, NbValOut;
  long Ntour, Reste;
  int j, NSom, NSomfin;
  register float loc_som;

  if (RapFreq > 1.0)
    return -1;

  NSom = floor ((1.0 / RapFreq) + 0.5);
  /* faudrait verifier que |Nsom - 1/RapFreq| < EPSILON */

  /* Réglons immédiatement le cas ou y'a rien a faire : "NbValIn = 0" */
  if (NbValIn == 0)
    return 0;

  Ntour = NbValIn / NSom;	/* division entière */
  Reste = NbValIn % NSom;

/*
 * Normalement, il y a Ntour calculs "standards" à faire.
 */

  for (i = 0; i < Ntour - 1; i++)
    {
      loc_som = 0.0;
      for (j = 0; j < NSom; j++)
	{
	  loc_som += *Var_in;
	  Var_in++;
	}
      *Var_out = loc_som;
      Var_out++;
    }

/* 
 * La dernière somme se doit pas dépasser NbValIn.
 */

  NbValOut = Ntour;

  TabStat[0] = NSom;
  TabStat[1] = Ntour;
  TabStat[2] = Reste;
  TabStat[3] = NSomfin;
  return NbValOut;
}

/* la fonction d'enrobage classique */

int
OP_TotEch (unsigned long NbVal, void *ArgList[], char *DiagExec)
{
  long CodRet;
  long TabStat[4];
  int NCar;

  NCar = sprintf (DiagExec, "TotEch : (%ld echant.) ", NbVal) ;
  if (NCar < 0)
    NCar = 0;
  DiagExec += NCar;

  CodRet = TotEch (NbVal,
		   (float *) ArgList[0],
		   *((double *) ArgList[1]),
		   (float *) ArgList[3],
		   TabStat);

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
ID_TotEch (oper * optr)
{
  strcpy (optr->Nom, "TotEch");
  optr->Version = "$Revision$";
  optr->Date = "$Date$";
  optr->fctptr = OP_TotEch;
  optr->NbArg = 3;
  optr->misval_auto = 1;	/* On s'en remet au mécanisme automatique.  */
  optr->Arg_Car[0].direction = DIR_IN;
  optr->Arg_Car[0].categorie = VECTOR;
  optr->Arg_Car[0].typ = ATYC_IF32;
  optr->Arg_Car[0].array_dim = "1";
  optr->Arg_Car[0].type_sample = "any";
  optr->Arg_Car[0].sample = "any";
  optr->Arg_Car[0].unite = "any";
  optr->Arg_Car[0].famille = "any";

  optr->Arg_Car[1].direction = DIR_IN;
  optr->Arg_Car[1].categorie = COEFFICIENT;
  optr->Arg_Car[1].array_dim = "1";
  optr->Arg_Car[1].typ = ATYC_IF64;
  optr->Arg_Car[1].unite = "any";
  optr->Arg_Car[1].type_sample = NULL;
  optr->Arg_Car[1].sample = NULL;

  optr->Arg_Car[2].direction = DIR_OUT;
  optr->Arg_Car[2].categorie = VECTOR;
  optr->Arg_Car[2].typ = ATYC_IF32;
  optr->Arg_Car[2].array_dim = "1";
  optr->Arg_Car[2].name = "$Arg1.name";
  /* Les routines d'interpolations "universelles" obligent à utiliser */
  /* une  formule pour calculer le nombre d'elements du vecteur de sortie. */
  optr->Arg_Car[2].NbVal = "$Arg1.NbVal * $Arg2";
  optr->Arg_Car[2].sample = "$Arg1.sample * $Arg2";
  /* Par contre, l'unite est simple... */
  optr->Arg_Car[2].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[2].ref_time = " \"time_\" + $Arg4.sample";
  optr->Arg_Car[2].misval = "$Arg1.misval";
  optr->Arg_Car[2].unite = "$Arg1.unit";
  optr->Arg_Car[2].famille = "$Arg1.famille";
}
