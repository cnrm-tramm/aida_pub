/****************************************************
*
* OPERATOR      MoyEch_Angl_auto_unit.c   FUNCTION  ANSI-C
*
* PURPOSE       Averaging and sampling of a time serie
*
* DESCRIPTION   Routine de moyenne-echantillon, pour variables "float"
*		et "angulaires" en radians ou degrés.
*               Il faudra penser à gérer les "valabs"...
*
* VERSION       $Revision$
*
* ARGUMENTS   IN   float  Var_in     any        Original data
*             IN   double RapFreq    whithout   frequency ratio
*             IN   int    Decal      sec/freq   delay between first values
*             IN   char*  unit       "Radian" ou "Degre"  Unité de mesure des angles               
*             OUT  float  Var_out    same as 1  Interpolated data
*
* REFERENCES
*
* CHANGES       
*               This function replace the old "Moy_Angl.c" 12/4/1999
*               1.3 followed Categorie definition's change.
*               1.2 added comments/switched arg. orders
*
* COPYRIGHT     Meteo-France
* modif CBerne 05/12/2002 : rajout du transfert de misval dans l'entete
*      du vecteur en sortie
*
*#########################################################################*/

#define _POSIX_SOURCE 1
#define _XOPEN_SOURCE 600
#define _HPUX_SOURCE 1
#define _XOPEN_SOURCE_EXTENDED 1

#include <stdio.h>
#include <math.h>
#include <string.h>
#include <strings.h>
#include <limits.h>

#include "struct_oper.h"
#include "unit_def.h"
#include "unit.h"

/* La vraie fonction... */

long
MoyEch_Angl_auto_unit (unsigned long NbValIn,
		       const float *Var_in,
		       double RapFreq,
		       int Decal, const char *unit, float *Var_out,
		       long TabStat[4])
{
  long i, NbValOut;
  long Ntour, Reste;
  int j, NSom, NSomfin;
  register float loc_som, X0, X1;
  double D_to_R;
  int Flag_unit;

  Flag_unit = reconnait_deg_rad (unit);
  switch (Flag_unit)
    {
    case UNIT_IS_DEGREE:
      D_to_R = M_PI / 180.0;
      break;
    case UNIT_IS_RADIAN:
      D_to_R = 1.0;
      break;
    default:
      return -3;
    }


  if (RapFreq > 1.0)
    return -1;

  NSom = floor ((1.0 / RapFreq) + 0.5);

  if ((Decal < -NSom) || (Decal > NSom))
    return -2;

  /* Réglons immédiatement le cas ou y'a rien a faire : "NbValIn = 0" */
  if (NbValIn == 0)
    return 0;

  Ntour = NbValIn / NSom;	/* division entière */
  Reste = NbValIn % NSom;

/*
 * Normalement, il y a Ntour calculs "standards" à faire.
 *  Si on tient compte de Decal, le premier ou le dernier peut ne
 * plus être standard--> traitement des cas-particulier, et boucle sur
 * (Ntour - 1) cas.
 */

/* 
 * La première somme se fait de Decal à Decal+Nsom-1, mais si 
 * Decal est negatif, on commence à zero.
 * Si Decal est positif, cette première somme se fait dans la boucle standard.
 */

  if (Decal < 0)
    {
      if (NSom + Decal > 0)
	{
	  X1 = *Var_in;
	  loc_som = X1;
	  Var_in++;
	  for (j = 1; j < NSom + Decal; j++)
	    {
	      X0 = X1;
	      X1 = *(Var_in);
	      if (fabs (X0 - X1) > M_PI / D_to_R)
		{
		  if (X1 < X0)
		    X1 += 2.0 * M_PI / D_to_R;
		  else
		    X1 -= 2.0 * M_PI / D_to_R;
		}
	      loc_som = loc_som + X1;
	      Var_in++;
	    }
	  *Var_out = loc_som / (NSom + Decal);
	}
      else
	*Var_out = Var_in[0];	/* Plutôt que 0 ou ValAbs... */
      Var_out++;
    }
  else
    Var_in += Decal;

  /* Ensuite la boucle standard */

  for (i = 0; i < Ntour - 1; i++)
    {
      X1 = *Var_in;
      loc_som = X1;
      Var_in++;
      for (j = 1; j < NSom; j++)
	{
	  X0 = X1;
	  X1 = *(Var_in);
	  if (fabs (X0 - X1) > M_PI / D_to_R)
	    {
	      if (X1 < X0)
		X1 += 2.0 * M_PI / D_to_R;
	      else
		X1 -= 2.0 * M_PI / D_to_R;
	    }
	  loc_som = loc_som + X1;
	  Var_in++;
	}
      *Var_out = loc_som * RapFreq;
      Var_out++;
    }

/* 
 * La dernière somme se doit pas dépasser NbValIn.
 * Si Decal est négatif, Y'a pas de Pb, ça a été fait dans la boucle standard.
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
	  X1 = *Var_in;
	  loc_som = X1;
	  Var_in++;
	  for (j = 1; j < NSomfin; j++)
	    {
	      X0 = X1;
	      X1 = *(Var_in);
	      if (fabs (X0 - X1) > M_PI / D_to_R)
		{
		  if (X1 < X0)
		    X1 += 2.0 * M_PI / D_to_R;
		  else
		    X1 -= 2.0 * M_PI / D_to_R;
		}
	      loc_som = loc_som + X1;
	      Var_in++;
	    }
	  *Var_out = loc_som / NSomfin;
	}
      else
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
OP_MoyEch_Angl_auto_unit (unsigned long NbVal, void *ArgList[],
			  char *DiagExec)
{
  long CodRet;
  int NCar;
  long TabStat[4];

  NCar = sprintf (DiagExec,
		  "MoyEch_Angl_auto_unit (%ld ech), f_out/f_in = %g, decal = %d, unit=%s, ",
		  NbVal, *((double *) ArgList[1]),
		  *((int *) ArgList[2]), (char *) ArgList[3]);
  if (NCar < 0)
    NCar = 0;
  DiagExec += NCar;

  CodRet = MoyEch_Angl_auto_unit (NbVal,
				  (float *) ArgList[0],
				  *((double *) ArgList[1]),
				  *((int *) ArgList[2]),
				  (char *) ArgList[3],
				  (float *) ArgList[4], TabStat);

  if (CodRet >= 0)
    {
      sprintf (DiagExec, "OK: %ld valeurs calculées.", CodRet);
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
    case -3:
      sprintf (DiagExec, "ERR: Unité d'angle non reconnue.");
      break;
    default:
      sprintf (DiagExec, "ERR: Erreur %ld.", CodRet);
      break;
    }
  return OP_FAIL;
}

void
ID_MoyEch_Angl_auto_unit (oper * optr)
{
  strcpy (optr->Nom, "MoyEch_Angl_auto_unit");
  optr->Version = "$Revision$";
  optr->Date = "$Date$";
  optr->fctptr = OP_MoyEch_Angl_auto_unit;
  optr->NbArg = 5;

  /* Var_in */
  optr->Arg_Car[0].direction = DIR_IN;
  optr->Arg_Car[0].categorie = VECTOR;
  optr->Arg_Car[0].typ = ATYC_IF32;
  optr->Arg_Car[0].array_dim = "1";
  optr->Arg_Car[0].type_sample = "any";
  optr->Arg_Car[0].sample = "any";
  optr->Arg_Car[0].unite = "any";
  optr->Arg_Car[0].famille = "any";

  /* RapFreq (sortie/entree) */
  optr->Arg_Car[1].direction = DIR_IN;
  optr->Arg_Car[1].categorie = COEFFICIENT;
  optr->Arg_Car[1].array_dim = "1";
  optr->Arg_Car[1].typ = ATYC_IF64;
  optr->Arg_Car[1].unite = "any";
  optr->Arg_Car[1].type_sample = NULL;
  optr->Arg_Car[1].sample = NULL;

  /* Decal */
  optr->Arg_Car[2].direction = DIR_IN;
  optr->Arg_Car[2].categorie = COEFFICIENT;
  optr->Arg_Car[2].array_dim = "1";
  optr->Arg_Car[2].typ = ATYC_I32;
  optr->Arg_Car[2].unite = "any";
  optr->Arg_Car[2].type_sample = NULL;
  optr->Arg_Car[2].sample = NULL;

  /* unit */
  optr->Arg_Car[3].direction = DIR_IN;
  optr->Arg_Car[3].categorie = COEFFICIENT;
  optr->Arg_Car[3].typ = ATYC_STRING;
  optr->Arg_Car[3].array_dim = "1";
  optr->Arg_Car[3].type_sample = NULL;
  optr->Arg_Car[3].sample = NULL;
  optr->Arg_Car[3].unite = "";

  /* Var_out */
  optr->Arg_Car[4].direction = DIR_OUT;
  optr->Arg_Car[4].categorie = VECTOR;
  optr->Arg_Car[4].typ = ATYC_IF32;
  optr->Arg_Car[4].array_dim = "1";
  /* Les routines d'interpolations "universelles" obligent à utiliser */
  /* une  formule pour calculer le nombre d'elements du vecteur de sortie. */
  optr->Arg_Car[4].NbVal = "$Arg1.NbVal * $Arg2";
  optr->Arg_Car[4].sample = "$Arg1.sample * $Arg2";
  /* Par contre, l'unite est simple... */
  optr->Arg_Car[4].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[4].ref_time = " \"time_\" + $Arg5.sample";
  optr->Arg_Car[4].unite = "$Arg1.unit";
  optr->Arg_Car[4].famille = "$Arg1.famille";
  optr->Arg_Car[4].misval = "$Arg1.misval";
  optr->Arg_Car[4].name = "$Arg1.name + \" moyenne et echantillonne \" ";
  optr->Arg_Car[4].en_name = "$Arg1.english_name + \" averaged and sampled\" ";
}
