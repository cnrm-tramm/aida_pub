/*************************************************
* OPERATOR 	scalar31_to_tab.c 	FUNCTION ANSI-C
*
* PURPOSE       Remplissage d'un vecteur-tableau à 31 colonnes avec les
*               valeurs de 31 vecteurs "scalaires".
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
*  		IN 	float	x31 	variable 31
*
*		OUT	float 	tab 	tableau des 31 variables 	
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
scalar31_to_tab (unsigned long ndata,
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
		 const float *x31,
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
      tab[j++] = x31[i];
    }
}

/* fonction d'enrobage */

int
OP_scalar31_to_tab (unsigned long Nbval, void *ArgList[], char *DiagExec)
{
  DiagExec[0] = 0;      /* Pas de message pour un simple reformattage */

  scalar31_to_tab (Nbval,
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
		   (float *) ArgList[30],
		   (float *) ArgList[31]);

  return OP_OK;
}

void
ID_scalar31_to_tab (oper * optr)
{
  int i;

  strcpy (optr->Nom, "scalar31_to_tab");
  optr->Version = "$Revision: 7056 $";
  optr->Date = "$Date: 2017-12-14 14:03:01 +0100 (jeu. 14 déc. 2017) $";
  optr->fctptr = OP_scalar31_to_tab;
  optr->NbArg = 32;

  for (i = 0; i < 31; i++)
    {
      optr->Arg_Car[i].direction = DIR_IN;
      optr->Arg_Car[i].categorie = VECTOR;
      optr->Arg_Car[i].typ = ATYC_IF32;
      optr->Arg_Car[i].array_dim = "1";
      optr->Arg_Car[i].type_sample = "any";
      optr->Arg_Car[i].sample = "any";
      optr->Arg_Car[i].unite = "";
    }

  /* Du deuxième au trente-et-unième, ils doivent avoir le même
   * nombre d'éléments que le premier. */
  for (i = 1; i < 31; i++)
    {
      optr->Arg_Car[i].NbVal = "$Arg1.NbVal";
    }

  optr->Arg_Car[31].direction = DIR_OUT;
  optr->Arg_Car[31].categorie = VECTOR;
  optr->Arg_Car[31].typ = ATYC_IF32;
  optr->Arg_Car[31].array_dim = "31";
  optr->Arg_Car[31].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[31].ref_time = "$Arg1.ref_time";
  optr->Arg_Car[31].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[31].sample = "$Arg1.sample";
  optr->Arg_Car[31].unite = "$Arg1.unit";
  optr->Arg_Car[31].famille = "$Arg1.famille";
  optr->Arg_Car[31].misval = "$Arg1.misval";
  /*  optr->Arg_Car[31].bornes = "";
  optr->Arg_Car[31].unit_bornes = "";    */
}
