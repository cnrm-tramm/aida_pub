/****************************************************************
* OPERATOR 	correc_saut  FUNCTION  ANSI-C
* 
* PURPOSE	correction of peaks
*
* DESCRIPTION   Cette fonction supprime les pics vers
*	   	le haut ou vers le bas qui se produisent
*		sur une seule valeur et qui sont superieur
*		a un seuil.
*
* VERSION         1.5
*
* ARGUMENTS 	IN 	float 	X   	parametre brut	
*		IN 	float 	seuil	seuil de detection d'un saut
* 		OUT 	float 	Xcor 	parametre corrige
*
* ENTRY		NONE
*
* SUBPROGRAMS 	NONE
* 
* REFERENCES	NONE
*
* CHANGES       1.2   added args' sampling description
*               1.5   C.Berne 27/10/2005 : fabsf() remplace par fabs()
*               car fabsf renvoyait des NaN et des valeurs aberrantes (?)
* 
* COPYRIGHT 	Meteo-France
*		Centre de Recherches Meteorologiques
*		GMEI/MMA
*		42, av. G. Coriolis
*		31057	TOULOUSE cedex
*
******************************************************************/

#define _POSIX_SOURCE 1
#define _XOPEN_SOURCE 600

#include <stdio.h>
#include <string.h>
#include <math.h>
#include "struct_oper.h"

long
correc_saut (unsigned long Nloop,
	     const float *X, const float seuil, float *Xcor)
{
  unsigned long i;
  signed long nbsaut;
  /* Même si i parcourt toute l'étendue des "unsigned", on peut utiliser 
   * nbsaut en "signed", car il est limité à Nloop/3. */

  if (seuil <= 0.0)
    return LONG_MIN;

  if (Nloop == 0)
    return 0;

  Xcor[0] = X[0];

  nbsaut = 0;

  for (i = 1; i < (Nloop - 1); i++)
    {
      if ((fabs (X[i] - X[i - 1]) > seuil) &&
	  (fabs (X[i] - X[i + 1]) > seuil) &&
	  ((X[i] - X[i - 1]) * (X[i] - X[i + 1]) > 0))
	{
	  /*fprintf (stderr, "dX%ld=%g , dXi+1=%g \n",
		   i, X[i] - X[i - 1], X[i + 1] - X[i]); */
	  Xcor[i] = (X[i + 1] + X[i - 1]) / 2;
	  nbsaut = nbsaut + 1;
	  i++;			/* On se décale d'un cran de plus, pour que
				   le X[i-1] du test suivant ne soit pas la 
				   valeur fausse actuelle. */
	  Xcor[i] = X[i];	/* Et on suppose donc que la valeur suivante
				   est "OK" */
	}
      else
	{
	  Xcor[i] = X[i];
	}

      if (nbsaut >= Nloop / 3)
	{
	  /* ce qu'on est en train de faire n'a pas beaucoup de sens. */
	  /* ==> On annule tout !! */
	  for (i = 1; i < (Nloop); i++)
	    {
	      Xcor[i] = X[i];
	    }
	  return -nbsaut;
	}
    }

  Xcor[Nloop - 1] = X[Nloop - 1];

  return nbsaut;
}

/* fonction d'enrobage */

int
OP_correc_saut (unsigned long Nbval, void *ArgList[], char *DiagExec)
{
  long CodRet;
  int N;

  N = sprintf (DiagExec, "seuil = %f", *((float *) ArgList[1]));
  if (N > 0)
    DiagExec += N;

  CodRet = correc_saut (Nbval,
			(float *) ArgList[0],
			*((float *) ArgList[1]), (float *) ArgList[2]);

  if (CodRet == LONG_MIN)
    {
      (void) sprintf (DiagExec, "; seuil negatif");
      return OP_FAIL;
    }
  else if (CodRet < 0)
    {
      (void) sprintf (DiagExec,
		      "; Trop grand nombre de sauts (%ld) : Abandon",
		      -CodRet);
    }
  else if (CodRet >= 0)
    {
      (void) sprintf (DiagExec, "; Nb saut(s) corrige(s) : %ld", CodRet);
    }
  return OP_OK;
}

void
ID_correc_saut (oper * optr)
{
  strcpy (optr->Nom, "correc_saut");
  optr->Version = "$Revision$";
  optr->Date = "$Date$";
  optr->fctptr = OP_correc_saut;
  optr->NbArg = 3;

  /* X */
  optr->Arg_Car[0].direction = DIR_IN;
  optr->Arg_Car[0].categorie = VECTOR;
  optr->Arg_Car[0].typ = ATYC_IF32;
  optr->Arg_Car[0].array_dim = "1";
  optr->Arg_Car[0].unite = "";
  optr->Arg_Car[0].type_sample = "any";
  optr->Arg_Car[0].sample = "any";

  /* seuil */
  optr->Arg_Car[1].direction = DIR_IN;
  optr->Arg_Car[1].categorie = COEFFICIENT;
  optr->Arg_Car[1].typ = ATYC_IF32;
  optr->Arg_Car[1].array_dim = "1";
  optr->Arg_Car[1].unite = "";
  optr->Arg_Car[1].type_sample = NULL;
  optr->Arg_Car[1].sample = NULL;

  /* Xcor */
  optr->Arg_Car[2].direction = DIR_OUT;
  optr->Arg_Car[2].categorie = VECTOR;
  optr->Arg_Car[2].typ = ATYC_IF32;
  optr->Arg_Car[2].array_dim = "1";
  optr->Arg_Car[2].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[2].sample = "$Arg1.sample";
  optr->Arg_Car[2].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[2].ref_time = "$Arg1.ref_time";
  optr->Arg_Car[2].unite = "$Arg1.unit";
  optr->Arg_Car[2].famille = "$Arg1.famille";
  optr->Arg_Car[2].misval = "$Arg1.misval";
  optr->Arg_Car[2].name = "$Arg1.name + \" sans pics isolés\" ";
  optr->Arg_Car[2].en_name =
    "$Arg1.english_name + \", with isolated peaks removed\" ";
}
