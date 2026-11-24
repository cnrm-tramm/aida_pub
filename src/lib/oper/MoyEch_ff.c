/****************************************************
*
* OPERATOR      MoyEch_ff.c   FUNCTION  ANSI-C
*
* PURPOSE       Averaging and sampling of a time serie
*
* DESCRIPTION   Routine de moyenne-echantillon, pour variables "float".
*               schema temporel retenu :              
*                 Variable origine      | | | | | | | | | | | | | | | | 
*                 Variable Destination     |       |       |       |  
*
* VERSION       $Revision$
*
* ARGUMENTS   IN   float  datai      any        	Original data
*             IN   float  fi	     Hz   		Original data frequency
*             IN   float  fo         Hz   	
*             OUT  float  datao      same as datai	Averaging and sampling data
*
* REFERENCES
*
* MODIFICATIONS :
*	- 26/02/01 (W. Maurel) 
*		- passage de fréquence "float" en arguments
*
* COPYRIGHT     Meteo-France
*
*#########################################################################*/

#define _POSIX_SOURCE 1
#define _XOPEN_SOURCE 600
/* Le #define _HPUX_SOURCE n'est la que pour "voir" strdup */
#define _HPUX_SOURCE 1
#define _XOPEN_SOURCE_EXTENDED 1

#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <string.h>
#include <limits.h>

#include "struct_oper.h"

/* La vraie fonction... */

int
MoyEch_ff (unsigned long ndatai,
	   float *datai,
	   double fi,
	   double fo,
	   float *datao,
	   int *finter,
	   long *ndatainter,
	   long *ndatao)

{
  int i, j, Ni, No, ai, r;
  float *datainter;
  double c, fr, mean;

  if (fo > fi)
    {
      return -1;
    }

/* determination du ppcm */

  ai = 1;
  r = (int)( ((double)ai * fi) / fo );
  fr = ((double)ai * fi) / fo;
  while ((fr > r) || (fr < r))
    {
      ai = ai + 1;
      r = (int)((double)ai * fi) / fo;
      fr = ((double)ai * fi) / fo;
    }
  Ni = ai;
  *finter = (double)Ni * fi;
  *ndatainter = Ni * ndatai;

/* allocation de datainter */

  datainter = malloc (*ndatainter * sizeof (float));
  if (datainter == NULL)
    {
      return -2;
    }

/* interpolation */

  for (i = 0; i < ndatai - 1; i++)
    {
      datainter[i * Ni] = datai[i];
      for (j = i * Ni + 1; j < (i + 1) * Ni; j++)
	{
	  c = ((double) (j - (i * Ni))) /
	    ((double) Ni);
	  datainter[j] = (c * (datai[i + 1] - datai[i])) + datai[i];
	}
    }

  for (j = (ndatai - 1) * Ni; j < (ndatai) * Ni; j++)
    {
      datainter[j] = datai[ndatai - 1];
    }

/* moyennage et sous-echantillonnage */

  No = *finter / fo;
  *ndatao = (*ndatainter * fo) / *finter;

  for (i = 0; i < *ndatao; i++)
    {
      mean = 0.;
      for (j = i * No; j < (i + 1) * No; j++)
	{
	  mean = mean + (double)datainter[j];
	}
      datao[i] = (float)(mean/((double)No));
    }

  /* On nettoie avant de sortir */
  free (datainter);
  return 0;
}

/* la fonction d'enrobage classique */

int
OP_MoyEch_ff (unsigned long NbVal, void *ArgList[], char *DiagExec)
{
  int CodRet;
  /* Les variables de calcul intermédiaire de MoyEch_ff */
  long ndatainter, ndatao;
  int finter;
  int NCar;

  NCar = sprintf (DiagExec, "MoyEch_ff : (%ld echant.) ", NbVal) ;
  if (NCar < 0)
    NCar = 0;
  DiagExec += NCar;

  CodRet = MoyEch_ff (NbVal,
		      (float *) ArgList[0],
		      *((double *) ArgList[1]),
		      *((double *) ArgList[2]),
		      (float *) ArgList[3],
		      &finter,
		      &ndatainter,
		      &ndatao);

  switch (CodRet)
    {
    case 0:
      sprintf (DiagExec, 
	       "OK. freq intermediaire d'interpol : %d (%ld éch) et %ld ech finaux",
	       finter, ndatainter, ndatao);
      return OP_OK;
    case -1:
      sprintf (DiagExec, "ERR: freq. sortie > freq. entree, pas de moyenne.");
      return OP_FAIL;
    case -2:
      sprintf (DiagExec, "ERR: Allocation impossible de datainter \n");
      return OP_FAIL;
    default:
      sprintf (DiagExec, "ERR: Erreur %d", CodRet);
      return OP_FAIL;
    }
}

void
ID_MoyEch_ff (oper * optr)
{
  strcpy (optr->Nom, "MoyEch_ff");
  optr->Version = "$Revision$";
  optr->Date = "$Date$";
  optr->fctptr = OP_MoyEch_ff;
  optr->NbArg = 4;

 /* datai */
  optr->Arg_Car[0].direction = DIR_IN;
  optr->Arg_Car[0].categorie = VECTOR;
  optr->Arg_Car[0].typ = ATYC_IF32;
  optr->Arg_Car[0].array_dim = "1";
  optr->Arg_Car[0].type_sample = "any";
  optr->Arg_Car[0].sample = "any";
  optr->Arg_Car[0].unite = "any";

 /* fi */
  optr->Arg_Car[1].direction = DIR_IN;
  optr->Arg_Car[1].categorie = COEFFICIENT;
  optr->Arg_Car[1].array_dim = "1";
  optr->Arg_Car[1].typ = ATYC_IF64;
  optr->Arg_Car[1].unite = "any";
  optr->Arg_Car[1].type_sample = NULL;
  optr->Arg_Car[1].sample = NULL;

 /* fo */
  optr->Arg_Car[2].direction = DIR_IN;
  optr->Arg_Car[2].categorie = COEFFICIENT;
  optr->Arg_Car[2].array_dim = "1";
  optr->Arg_Car[2].typ = ATYC_IF64;
  optr->Arg_Car[2].unite = "any";
  optr->Arg_Car[2].type_sample = NULL;
  optr->Arg_Car[2].sample = NULL;

 /* datao */
  optr->Arg_Car[3].direction = DIR_OUT;
  optr->Arg_Car[3].categorie = VECTOR;
  optr->Arg_Car[3].typ = ATYC_IF32;
  optr->Arg_Car[3].array_dim = "1";
  optr->Arg_Car[3].NbVal = "$Arg1.NbVal * $Arg3 / $Arg2 ";
  /* Par contre, l'unite est simple... */
  optr->Arg_Car[3].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[3].sample = "$Arg1.sample * $Arg3 / $Arg2 ";
  optr->Arg_Car[3].ref_time = " \"time_\" + $Arg4.sample";
  optr->Arg_Car[3].unite = "$Arg1.unit";
  optr->Arg_Car[3].misval = "$Arg1.misval";
  optr->Arg_Car[3].name = 
            "$Arg1.name + \"sous-echantillonne a \" + $Arg3 + \"Hz\"";
  optr->Arg_Car[3].en_name = 
            "$Arg1.english_name + \"sub-sampled at\" + $Arg3 + \"Hz\"";
}
