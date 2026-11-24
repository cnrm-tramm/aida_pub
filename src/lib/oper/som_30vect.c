/*************************************************
* OPERATOR 	som_30vect.c 	FUNCTION ANSI-C
*
* PURPOSE	calcul de la somme de 30 vecteurs
*
* ARGUMENTS 	IN 	float	x1 	variable 1	
*  		IN 	float	x2 	variable 2
*                               .       .
*                               .       .
*                               .       .
*                               .       .
*                               .       .
*  		IN 	float	x30 	variable 30
*
*		OUT	float 	som 	somme des 30 variables 	
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
#define _XOPEN_SOURCE_EXTENDED 1

#include <stdio.h>
#include <string.h>

#include "struct_oper.h"


void
som_30vect (unsigned long ndata,
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
	    const float *x16,
	    const float *x17,
	    const float *x18,
	    const float *x19,
	    const float *x20,
	    const float *x21,
	    const float *x22,
	    const float *x23,
	    const float *x24,
	    const float *x25,
	    const float *x26,
	    const float *x27,
	    const float *x28,
	    const float *x29,
	    const float *x30,
	    float *som)

{
  unsigned long i;

  for (i = 0; i < ndata; i++)
    {
      som[i] = x1[i] +
	x2[i] +
	x3[i] +
	x4[i] +
	x5[i] +
	x6[i] +
	x7[i] +
	x8[i] +
	x9[i] +
	x10[i] +
	x11[i] +
	x12[i] +
	x13[i] +
	x14[i] +
	x15[i] +
	x16[i] +
	x17[i] +
	x18[i] +
	x19[i] +
	x20[i] +
	x21[i] +
	x22[i] +
	x23[i] +
	x24[i] +
	x25[i] +
	x26[i] +
	x27[i] +
	x28[i] +
	x29[i] +
	x30[i];
    }

  return;
}

/* fonction d'enrobage */

int
OP_som_30vect (unsigned long NbVal, void *ArgList[], char *DiagExec)
{

  sprintf (DiagExec, "som_30vect (%lu ech)", NbVal);

  som_30vect (NbVal,
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
		   (float *) ArgList[15],
		   (float *) ArgList[16],
		   (float *) ArgList[17],
		   (float *) ArgList[18],
		   (float *) ArgList[19],
		   (float *) ArgList[20],
		   (float *) ArgList[21],
		   (float *) ArgList[22],
		   (float *) ArgList[23],
		   (float *) ArgList[24],
		   (float *) ArgList[25],
		   (float *) ArgList[26],
		   (float *) ArgList[27],
		   (float *) ArgList[28],
		   (float *) ArgList[29],
		   (float *) ArgList[30]);

  return OP_OK;
}

void
ID_som_30vect (oper * optr)
{
  int i;

  strcpy (optr->Nom, "som_30vect");
  optr->Version = "1.0";
  optr->Date = "10/21/96";
  optr->fctptr = OP_som_30vect;
  optr->NbArg = 31;

  for (i = 0; i < 30; i++)
    {
      optr->Arg_Car[i].direction = DIR_IN;
      optr->Arg_Car[i].categorie = VECTOR;
      optr->Arg_Car[i].typ = ATYC_IF32;
      optr->Arg_Car[i].array_dim = "1";
      optr->Arg_Car[i].type_sample = "any";
      optr->Arg_Car[i].sample = "any";
      optr->Arg_Car[i].unite = "";
    }

  for (i = 1; i < 30; i++)
    {
      optr->Arg_Car[i].NbVal = "$Arg1.NbVal";
    }

  optr->Arg_Car[30].direction = DIR_OUT;
  optr->Arg_Car[30].categorie = VECTOR;
  optr->Arg_Car[30].typ = ATYC_IF32;
  optr->Arg_Car[30].array_dim = "1";
  optr->Arg_Car[30].ref_time = "$Arg1.ref_time";
  optr->Arg_Car[30].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[30].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[30].sample = "$Arg1.sample";
  optr->Arg_Car[30].unite = "$Arg1.unit";
}
