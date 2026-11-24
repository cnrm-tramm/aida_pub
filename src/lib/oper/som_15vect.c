/*************************************************
* OPERATOR 	som_15vect.c 	FUNCTION ANSI-C
*
* PURPOSE	Somme terme à terme de 15 vecteurs
*
* ARGUMENTS 	IN 	float	x1 	variable 1	
* 		IN 	float	x2 	variable 2
*  		IN 	float	x3 	variable 3
*  		IN 	float	x4 	variable 4
*  		IN 	float	x5 	variable 5
*  		IN 	float	x6 	variable 6
*  		IN 	float	x7 	variable 7
*  		IN 	float	x8 	variable 8
*  		IN 	float	x9 	variable 9
*  		IN 	float	x10 	variable 10
*  		IN 	float	x11 	variable 11
*  		IN 	float	x12 	variable 12
*  		IN 	float	x13 	variable 13
*  		IN 	float	x14 	variable 14
*  		IN 	float	x15 	variable 15
*
*		OUT	float 	som 	somme des 15 variables 	
*		
* ENTRY		NONE
*
* SUBPROGRAMS 	NONE
*
* REFERENCE	NONE
*
* COPYRIGHT	Meteo-France
*		Centre National de Recherches Meteorologiques
*		GMEI/ MMA
*		42, av G. Coriolis 
*		31057	TOULOUSE cedex
*
*****************************************************************/

#define _POSIX_SOURCE 1
#define _XOPEN_SOURCE 600
/* Le #define _HPUX_SOURCE n'est la que pour "voir" strdup */
#define _HPUX_SOURCE 1
#define _XOPEN_SOURCE_EXTENDED 1

#include <stdio.h>
#include <string.h>

#include "struct_oper.h"


void
som_15vect (unsigned long ndata,
	    const float *x1,
	    const float *x2,
	    const float *x3,
	    const float *x4,
	    const float *x5,
	    const float *x6,
	    const float *x7,
	    const float *x8,
	    const float *x9,
	    const float *x10,
	    const float *x11,
	    const float *x12,
	    const float *x13,
	    const float *x14,
	    const float *x15,
	    float *som)

{
  unsigned long i;

  for (i = 0; i < ndata; i++)
    {
      som[i] = x1[i] + x2[i] + x3[i] + x4[i] +
	       x5[i] + x6[i] + x7[i] + x8[i] +
	       x9[i] + x10[i] + x11[i] + x12[i] +
 	       x13[i] + x14[i] + x15[i];
    }

  return;
}

/* fonction d'enrobage */

int
OP_som_15vect (unsigned long Nbval, void *ArgList[], char *DiagExec)
{
  som_15vect (Nbval,
	      (float *) ArgList[0],
	      (float *) ArgList[1],
	      (float *) ArgList[2],
	      (float *) ArgList[3],
	      (float *) ArgList[4],
	      (float *) ArgList[5],
	      (float *) ArgList[6],
	      (float *) ArgList[7],
	      (float *) ArgList[8],
	      (float *) ArgList[9],
	      (float *) ArgList[10],
	      (float *) ArgList[11],
	      (float *) ArgList[12],
	      (float *) ArgList[13],
	      (float *) ArgList[14],
	      (float *) ArgList[15]);

  DiagExec[0] = 0;              /* Rien à dire */

  return OP_OK;
}

void
ID_som_15vect (oper * optr)
{
  int i;

  strcpy (optr->Nom, "som_15vect");
  optr->Version = "$Revision$";
  optr->Date = "$Date$";
  optr->fctptr = OP_som_15vect;
  optr->NbArg = 16;

  for (i = 0; i < 15; i++)
    {
      optr->Arg_Car[i].direction = DIR_IN;
      optr->Arg_Car[i].categorie = VECTOR;
      optr->Arg_Car[i].typ = ATYC_IF32;
      optr->Arg_Car[i].array_dim = "1";
      optr->Arg_Car[i].type_sample = "any";
      optr->Arg_Car[i].sample = "any";
      optr->Arg_Car[i].unite = "";
    }
  for (i = 1; i < 15; i++)
    {
      optr->Arg_Car[i].NbVal = "$Arg1.NbVal";
    }

  optr->Arg_Car[15].direction = DIR_OUT;
  optr->Arg_Car[15].categorie = VECTOR;
  optr->Arg_Car[15].typ = ATYC_IF32;
  optr->Arg_Car[15].array_dim = "1";
  optr->Arg_Car[15].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[15].ref_time = "$Arg1.ref_time";
  optr->Arg_Car[15].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[15].sample = "$Arg1.sample";
  optr->Arg_Car[15].unite = "$Arg1.unit";
}
