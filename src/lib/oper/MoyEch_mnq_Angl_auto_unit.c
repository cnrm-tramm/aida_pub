/****************************************************
*
* OPERATOR      MoyEch_mnq_Angl_auto_unit.c   FUNCTION  ANSI-C
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
*             IN   int    tolerance_mnq   Tolerance pour le nb maxi de valeurs
*						 manquantes
*             OUT  float  Var_out    same as 1  Interpolated data
*
* REFERENCES
*
* CHANGES       
*               
*
* COPYRIGHT     Meteo-France
*
*#########################################################################*/

#define _POSIX_SOURCE 1
#define _XOPEN_SOURCE 600
#define _HPUX_SOURCE 1

#include <stdio.h>
#include <math.h>
#include <string.h>
#include <strings.h>
#include <limits.h>
#include "struct_oper.h"

/* La vraie fonction... */

long
MoyEch_mnq_Angl_auto_unit (unsigned long NbValIn,
			   float *Var_in,
			   double RapFreq,
			   int Decal,
			   char *unit,
			   const int tolerance_mnq,
			   float *Var_out)
{
  long i, NbValOut;
  long Ntour, Reste;
  int j, NSom, NSomfin;
  /*register float loc_som, X0, X1,dernier_lu_fini;
     register float mnq_som; */
  float loc_som, X0, X1, dernier_lu_fini;
  float mnq_som;
  const float misval_out = K_NaN;

  double D_to_R;

  if (!strcasecmp (unit, "degree") || !strcasecmp (unit, "Degree") || !strcasecmp (unit, "Degre") || !strcasecmp (unit, "degre"))
    {
      D_to_R = M_PI / 180.0;
    }
  else if (!strcasecmp (unit, "rad") || !strcasecmp (unit, "Rad") || !strcasecmp (unit, "Radian") || !strcasecmp (unit, "radian"))
    {
      D_to_R = 1.0;
    }
  else
    {
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
	  loc_som = 0.0;
	  mnq_som = 0.0;
	  dernier_lu_fini = 0.0;

	  for (j = 0; j < NSom + Decal; j++)
	    {
	      if (!isfinite (*Var_in))
		{
		  mnq_som = mnq_som + 1;
		}
	      else
		{
		  X0 = dernier_lu_fini;
		  X1 = *(Var_in);
		  if (fabs (X0 - X1) > M_PI / D_to_R)
		    {
		      if (X1 < X0)
			X1 += 2.0 * M_PI / D_to_R;
		      else
			X1 -= 2.0 * M_PI / D_to_R;
		    }
		  loc_som = loc_som + X1;
		  dernier_lu_fini = X1;

		}
	      Var_in++;
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
  else
    Var_in += Decal;

  /* Ensuite la boucle standard */

  for (i = 0; i < Ntour - 1; i++)
    {
      loc_som = 0.0;
      mnq_som = 0.0;
      dernier_lu_fini = 0.0;
      for (j = 0; j < NSom; j++)
	{
	  if (!isfinite (*Var_in))
	    {
	      mnq_som = mnq_som + 1;
	    }
	  else
	    {
	      X0 = dernier_lu_fini;
	      X1 = *(Var_in);
	      if (fabs (X0 - X1) > M_PI / D_to_R)
		{
		  if (X1 < X0)
		    X1 += 2.0 * M_PI / D_to_R;
		  else
		    X1 -= 2.0 * M_PI / D_to_R;
		}
	      loc_som = loc_som + X1;
	      dernier_lu_fini = X1;
	    }
	  Var_in++;
	}
      if (mnq_som <= tolerance_mnq)
	{
	  /* printf(" loc_som = %f   NSom = %d   mnq_som = %f \n",loc_som,NSom,mnq_som); */
	  *Var_out = loc_som / (NSom - mnq_som);
	  /*  printf("    Var_out = %f \n",*Var_out); */
	}
      else
	{
	  *Var_out = misval_out;
	}
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
	  loc_som = 0.0;
	  mnq_som = 0.0;
	  dernier_lu_fini = 0.0;

	  for (j = 0; j < NSomfin; j++)
	    {
	      if (!isfinite (*Var_in))
		{
		  mnq_som = mnq_som + 1;
		}
	      else
		{
		  X0 = dernier_lu_fini;
		  X1 = *(Var_in);
		  if (fabs (X0 - X1) > M_PI / D_to_R)
		    {
		      if (X1 < X0)
			X1 += 2.0 * M_PI / D_to_R;
		      else
			X1 -= 2.0 * M_PI / D_to_R;
		    }
		  loc_som = loc_som + X1;
		  dernier_lu_fini = X1;
		}
	      Var_in++;
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

	}
      else
	*Var_out = *(Var_in - 1);
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

  return NbValOut;
}

/* la fonction d'enrobage classique */

int
OP_MoyEch_mnq_Angl_auto_unit (unsigned long NbVal, void *ArgList[], char *DiagExec)
{
  long CodRet;
  int NCar;

  NCar = sprintf (DiagExec, "MoyEch_mnq_Angl_auto_unit : (%ld echant.) ", NbVal) ;
  if (NCar < 0)
    NCar = 0;
  DiagExec += NCar;

  CodRet = MoyEch_mnq_Angl_auto_unit (NbVal,
				      (float *) ArgList[0],
				      *((double *) ArgList[1]),
				      *((int *) ArgList[2]),
				      (char *) ArgList[3],
				      *((int *) ArgList[4]),
				      (float *) ArgList[5]);

  if (CodRet >= 0)
    {
      sprintf (DiagExec, "OK: %ld valeurs calculées.", CodRet);
      return OP_OK;
    }
  switch (CodRet)
    {
    case -1:
      sprintf (DiagExec, "ERR: RapFreq > 1 !!!");
    case -2:
      sprintf (DiagExec, "ERR: Decal hors-bornes.");
    case -3:
      sprintf (DiagExec, "ERR: Unité d'angle non reconnue.");
    default:
      sprintf (DiagExec, "ERR: Erreur %ld.", CodRet);
    }
  return OP_FAIL;
}

void
ID_MoyEch_mnq_Angl_auto_unit (oper * optr)
{
  strcpy (optr->Nom, "MoyEch_mnq_Angl_auto_unit");
  optr->Version = "$Revision$";
  optr->Date = "$Date$";
  optr->fctptr = OP_MoyEch_mnq_Angl_auto_unit;
  optr->NbArg = 6;
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

  optr->Arg_Car[2].direction = DIR_IN;
  optr->Arg_Car[2].categorie = COEFFICIENT;
  optr->Arg_Car[2].array_dim = "1";
  optr->Arg_Car[2].typ = ATYC_I32;
  optr->Arg_Car[2].unite = "any";
  optr->Arg_Car[2].type_sample = NULL;
  optr->Arg_Car[2].sample = NULL;

  optr->Arg_Car[3].direction = DIR_IN;
  optr->Arg_Car[3].categorie = COEFFICIENT;
  optr->Arg_Car[3].typ = ATYC_STRING;
  optr->Arg_Car[3].array_dim = "1";
  optr->Arg_Car[3].type_sample = NULL;
  optr->Arg_Car[3].sample = NULL;
  optr->Arg_Car[3].unite = "";

  optr->Arg_Car[4].direction = DIR_IN;
  optr->Arg_Car[4].categorie = COEFFICIENT;
  optr->Arg_Car[4].array_dim = "1";
  optr->Arg_Car[4].typ = ATYC_I32;
  optr->Arg_Car[4].unite = "any";
  optr->Arg_Car[4].type_sample = NULL;
  optr->Arg_Car[4].sample = NULL;

  optr->Arg_Car[5].direction = DIR_OUT;
  optr->Arg_Car[5].categorie = VECTOR;
  optr->Arg_Car[5].typ = ATYC_IF32;
  optr->Arg_Car[5].array_dim = "1";
  /* Les routines d'interpolations "universelles" obligent à utiliser */
  /* une  formule pour calculer le nombre d'elements du vecteur de sortie. */
  optr->Arg_Car[5].NbVal = "$Arg1.NbVal * $Arg2";
  optr->Arg_Car[5].sample = "$Arg1.sample * $Arg2";
  /* Par contre, l'unite est simple... */
  optr->Arg_Car[5].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[5].ref_time = " \"time_\" + $Arg6.sample";
  optr->Arg_Car[5].unite = "$Arg1.unit";
  optr->Arg_Car[5].famille = "$Arg1.famille";
}
