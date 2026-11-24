/*************************************************
* OPERATOR 	scalar30_to_tab.c 	FUNCTION ANSI-C
*
* PURPOSE       Remplissage d'un vecteur-tableau à 30 colonnes avec les
*               valeurs de 30 vecteurs "scalaires".
*
* ARGUMENTS 	IN 	float	x1 	variable 1	
* 		IN 	float	x2 	variable 2
*  		IN 	float	x3 	variable 3
*  		IN 	float	x4 	variable 4
*  		.        .      .       .
*  		.        .      .       .
*  		.        .      .       .
*  		.        .      .       .
*  		IN 	float	x30 	variable 30
*
*		OUT	float 	tab 	tableau des 30 variables 	
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

#include <stdio.h>
#include <string.h>
#include "struct_oper.h"

void
scalar30_to_tab (unsigned long ndata,
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
		 float *tab)	/* tab est en fait un tableau 2D */

{
  unsigned long i, j;

  for (i = 0, j = 0; i < ndata; i++)
    {
      tab[j++] = x1[i];
      tab[j++] = x2[i];
      tab[j++] = x3[i];
      tab[j++] = x4[i];
      tab[j++] = x5[i];
      tab[j++] = x6[i];
      tab[j++] = x7[i];
      tab[j++] = x8[i];
      tab[j++] = x9[i];
      tab[j++] = x10[i];
      tab[j++] = x11[i];
      tab[j++] = x12[i];
      tab[j++] = x13[i];
      tab[j++] = x14[i];
      tab[j++] = x15[i];
      tab[j++] = x16[i];
      tab[j++] = x17[i];
      tab[j++] = x18[i];
      tab[j++] = x19[i];
      tab[j++] = x20[i];
      tab[j++] = x21[i];
      tab[j++] = x22[i];
      tab[j++] = x23[i];
      tab[j++] = x24[i];
      tab[j++] = x25[i];
      tab[j++] = x26[i];
      tab[j++] = x27[i];
      tab[j++] = x28[i];
      tab[j++] = x29[i];
      tab[j++] = x30[i];
    }
}

/* fonction d'enrobage */

int
OP_scalar30_to_tab (unsigned long Nbval, void *ArgList[], char *DiagExec)
{
  DiagExec[0] = 0;      /* Pas de message pour un simple reformattage */
  
  scalar30_to_tab (Nbval,
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
ID_scalar30_to_tab (oper * optr)
{
  int i;

  strcpy (optr->Nom, "scalar30_to_tab");
  optr->Version = "$Revision$";
  optr->Date = "$Date$";
  optr->fctptr = OP_scalar30_to_tab;
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

  /* Du deuxième au trentième, ils doivent avoir le même
   * nombre d'éléments que le premier. */
  for (i = 1; i < 30; i++)
    {
      optr->Arg_Car[i].NbVal = "$Arg1.NbVal";
    }

  optr->Arg_Car[30].direction = DIR_OUT;
  optr->Arg_Car[30].categorie = VECTOR;
  optr->Arg_Car[30].typ = ATYC_IF32;
  optr->Arg_Car[30].array_dim = "30";
  optr->Arg_Car[30].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[30].ref_time = "$Arg1.ref_time";
  optr->Arg_Car[30].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[30].sample = "$Arg1.sample";
  optr->Arg_Car[30].unite = "$Arg1.unit";
  optr->Arg_Car[30].famille = "$Arg1.famille";
  optr->Arg_Car[30].misval = "$Arg1.misval";
  /*  optr->Arg_Car[30].bornes = "";
  optr->Arg_Car[30].unit_bornes = "";    */
}
