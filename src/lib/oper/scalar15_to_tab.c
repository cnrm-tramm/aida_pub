/*************************************************
* OPERATOR 	scalar15_to_tab.c 	FUNCTION ANSI-C
*
* PURPOSE	Remplissage d'un vecteur-tableau à 15 colonnes avec les
*               valeurs de 15 vecteurs "scalaires".
*
* ARGUMENTS 	IN 	float	x1 	variable 1	
* 		IN 	float	x2 	variable 2
*  		IN 	float	x3 	variable 3
*               .
*               .
*               .
*               .
*  		IN 	float	x14 	variable 14
*  		IN 	float	x15 	variable 15
*
*		OUT	float 	tab 	tableau des 15 variables 	
*		
* ENTRY		NONE
*
* SUBPROGRAMS 	NONE
*
* REFERENCE	NONE
*
* COPYRIGHT	Meteo-France
*		Centre National de Recherches Meteorologiques
*		GMEI/ TRAMM
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
scalar15_to_tab (unsigned long ndata, const float *x1, const float *x2, const float *x3, const float *x4, const float *x5, const float *x6, const float *x7, const float *x8, const float *x9, const float *x10, const float *x11, const float *x12, const float *x13, const float *x14, const float *x15, float *tab)	/* tab est en fait un tableau 2D */
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
    }

}

/* fonction d'enrobage */

int
OP_scalar15_to_tab (unsigned long Nbval, void *ArgList[], char *DiagExec)
{
  DiagExec[0] = 0;      /* Pas de message pour un simple reformattage */
  scalar15_to_tab (Nbval,
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
		   (float *) ArgList[14], (float *) ArgList[15]);

  return OP_OK;
}

void
ID_scalar15_to_tab (oper * optr)
{
  int i;
  strcpy (optr->Nom, "scalar15_to_tab");
  optr->Version = "$Revision$";
  optr->Date = "$Date$";
  optr->fctptr = OP_scalar15_to_tab;

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

  /* Du deuxième au quinzième, ils doivent avoir le même
   * nombre d'éléments que le premier. */
  for (i = 1; i < 15; i++)
    {
      optr->Arg_Car[i].NbVal = "$Arg1.NbVal";
    }

  optr->Arg_Car[15].direction = DIR_OUT;
  optr->Arg_Car[15].categorie = VECTOR;
  optr->Arg_Car[15].typ = ATYC_IF32;
  optr->Arg_Car[15].array_dim = "15";
  optr->Arg_Car[15].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[15].ref_time = "$Arg1.ref_time";
  optr->Arg_Car[15].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[15].sample = "$Arg1.sample";
  optr->Arg_Car[15].unite = "$Arg1.unit";
  optr->Arg_Car[15].famille = "$Arg1.famille";
  optr->Arg_Car[15].misval = "$Arg1.misval";
  /*  optr->Arg_Car[15].bornes = "";
  optr->Arg_Car[15].unit_bornes = "";    */
}
