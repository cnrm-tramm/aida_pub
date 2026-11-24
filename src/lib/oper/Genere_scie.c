/****************************************************
*
* OPERATOR       Genere_scie.c   FUNCTION  ANSI-C
*
* PURPOSE        Genere un signal en dents de scie 
*
* DESCRIPTION    
*
* VERSION        $Revision$
*
* ARGUMENTS    IN   double time       Any             reference time 
*              IN   float  min        Any             min value 
*              IN   float  max        Any             max value 
*              IN   float  N          Any             length of of one tooth
*							(number of points) 
*
*              OUT  float  X                          Result 
*
* ENTRY            
*                 
* SUBPROGRAMS    none
*
* FILES   
*
* REFERENCES   
*
* CHANGES        
*
* COPYRIGHT      Meteo-France
*
* AGREEMENT      The author wishes that .....
*#########################################################################*/

#define _POSIX_SOURCE 1
#define _XOPEN_SOURCE 600
/* Le #define _HPUX_SOURCE n'est la que pour "voir" strdup */
#define _HPUX_SOURCE 1
#define _XOPEN_SOURCE_EXTENDED 1

#include <stdio.h>
#include <string.h>
#include "struct_oper.h"


void
Genere_scie (unsigned long NLoop,
	     const double *time,
	     const float min, 
	     const float max, 
	     const int N, 
	     float *X)
{
  unsigned long i, j;

  float a, b;

  a = (max - min) / ((float) (N - 1));
  b = min;

  i = 0;
  j = 0;
  for (i = 0; i < NLoop; i++)
    {
      if (i - j > N)
      {
	j += N;
      }
      X[i] = a * ((float) (i - j)) + b;
    }
}


/* la fonction d'enrobage classique */

int
OP_Genere_scie (unsigned long NbVal, void *ArgList[], char *DiagExec)
{

  (void) sprintf (DiagExec,
		  "Genere_scie, NbVal=%lu, entre %g et %g, periode %d ech.", 
		  NbVal,
		  *((float *) ArgList[1]), 
		  *((float *) ArgList[2]),
		  *((int *) ArgList[3]));

  Genere_scie (NbVal,
	       (double *) ArgList[0],
	       *((float *) ArgList[1]),
	       *((float *) ArgList[2]),
	       *((int *) ArgList[3]), (float *) ArgList[4]);

  return OP_OK;
}

void
ID_Genere_scie (oper * optr)
{
  strcpy (optr->Nom, "Genere_scie");
  optr->Version = "$Revision$";
  optr->Date = "$Date$";
  optr->fctptr = OP_Genere_scie;
  optr->NbArg = 5;		/* doit rester inf. a FIL_MAX_ARG */

  /* time */
  optr->Arg_Car[0].direction = DIR_IN;
  optr->Arg_Car[0].categorie = VECTOR;
  optr->Arg_Car[0].typ = ATYC_IF64;
  optr->Arg_Car[0].array_dim = "1";
  optr->Arg_Car[0].type_sample = "any";
  optr->Arg_Car[0].sample = "any";
  optr->Arg_Car[0].unite = "any";
  optr->Arg_Car[0].famille = "any";

  /* min */
  optr->Arg_Car[1].direction = DIR_IN;
  optr->Arg_Car[1].categorie = COEFFICIENT;
  optr->Arg_Car[1].typ = ATYC_IF32;
  optr->Arg_Car[1].array_dim = "1";
  optr->Arg_Car[1].type_sample = NULL;
  optr->Arg_Car[1].sample = NULL;
  optr->Arg_Car[1].unite = NULL;
  optr->Arg_Car[1].famille = NULL;

  /* max */
  optr->Arg_Car[2].direction = DIR_IN;
  optr->Arg_Car[2].categorie = COEFFICIENT;
  optr->Arg_Car[2].typ = ATYC_IF32;
  optr->Arg_Car[2].array_dim = "1";
  optr->Arg_Car[2].type_sample = NULL;
  optr->Arg_Car[2].sample = NULL;
  optr->Arg_Car[2].unite = NULL;
  optr->Arg_Car[2].famille = NULL;

  /* N */
  optr->Arg_Car[3].direction = DIR_IN;
  optr->Arg_Car[3].categorie = COEFFICIENT;
  optr->Arg_Car[3].typ = ATYC_I32;
  optr->Arg_Car[3].array_dim = "1";
  optr->Arg_Car[3].type_sample = NULL;
  optr->Arg_Car[3].sample = NULL;
  optr->Arg_Car[3].unite = NULL;
  optr->Arg_Car[3].famille = NULL;

  optr->Arg_Car[4].direction = DIR_OUT;
  optr->Arg_Car[4].categorie = VECTOR;
  optr->Arg_Car[4].typ = ATYC_IF32;
  optr->Arg_Car[4].array_dim = "1";
  optr->Arg_Car[4].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[4].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[4].sample = "$Arg1.sample";
  optr->Arg_Car[4].ref_time = "$Arg1.nom";
  optr->Arg_Car[4].unite = "unknown";
  optr->Arg_Car[4].famille = " \"auto\" ";
  optr->Arg_Car[4].name = "\"Signal en dent de scie\"";
  optr->Arg_Car[4].en_name = "\"Sawtooth wave\" ";

}
