/*************************************************
* OPERATOR 	scalar5_to_tab.c 	FUNCTION ANSI-C
*
* PURPOSE	Remplissage d'un vecteur-tableau à 5 colonnes avec les
*               valeurs de 5 vecteurs "scalaires".
*
* ARGUMENTS 	IN 	float	x1 	variable 1	
* 		IN 	float	x2 	variable 2
*  		IN 	float	x3 	variable 3
*  		IN 	float	x4 	variable 4
*  		IN 	float	x5 	variable 5
*
*		OUT	float 	tab 	tableau des 5 variables 	
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

#include <string.h>
#include "struct_oper.h"

void
scalar5_to_tab (unsigned long ndata,
		 const float *x1,
		 const float *x2,
		 const float *x3,
		 const float *x4,
		 const float *x5,
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
    }
}

/* fonction d'enrobage */

int
OP_scalar5_to_tab (unsigned long Nbval, void *ArgList[], char *DiagExec)
{
  DiagExec[0] = 0;      /* Pas de message pour un simple reformattage */

  scalar5_to_tab (Nbval,
		   (float *) ArgList[0],
		   (float *) ArgList[1],
		   (float *) ArgList[2],
		   (float *) ArgList[3],
		   (float *) ArgList[4],
		   (float *) ArgList[5]);

  return OP_OK;
}

void
ID_scalar5_to_tab (oper * optr)
{
  int i;

  strcpy (optr->Nom, "scalar5_to_tab");
  optr->Version = "$Revision: 7055 $";
  optr->Date = "$Date: 2017-12-14 12:28:29 +0100 (jeu. 14 déc. 2017) $";
  optr->fctptr = OP_scalar5_to_tab;
  optr->NbArg = 6;

  for (i = 0; i < 5; i++)
    {
      optr->Arg_Car[i].direction = DIR_IN;
      optr->Arg_Car[i].categorie = VECTOR;
      optr->Arg_Car[i].typ = ATYC_IF32;
      optr->Arg_Car[i].array_dim = "1";
      optr->Arg_Car[i].type_sample = "any";
      optr->Arg_Car[i].sample = "any";
      optr->Arg_Car[i].unite = "";
    }
  /* Du deuxième au cinquième, ils doivent avoir le même
   * nombre d'éléments que le premier. */
  for (i = 1; i < 5; i++)
    {
      optr->Arg_Car[i].NbVal = "$Arg1.NbVal";
    }

  optr->Arg_Car[5].direction = DIR_OUT;
  optr->Arg_Car[5].categorie = VECTOR;
  optr->Arg_Car[5].typ = ATYC_IF32;
  optr->Arg_Car[5].array_dim = "5";
  optr->Arg_Car[5].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[5].ref_time = "$Arg1.ref_time";
  optr->Arg_Car[5].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[5].sample = "$Arg1.sample";
  optr->Arg_Car[5].unite = "$Arg1.unit";
  optr->Arg_Car[5].famille = "$Arg1.famille";
  optr->Arg_Car[5].misval = "$Arg1.misval";
/*  optr->Arg_Car[5].bornes = "(h_niv1, h_niv1)";"(h_niv2, h_niv2)";"(h_niv3, h_niv3)";"(h_niv4, h_niv4)";"(h_niv5, h_niv5)"; 
  optr->Arg_Car[5].unit_bornes = "m";    */
}
