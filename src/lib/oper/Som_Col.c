/****************************************************
*
* OPERATOR      Som_Col.c   FUNCTION  ANSI-C
*
* PURPOSE       Sum several colums of a 1D parameter. 
*		It sums from column number "col_Deb" to 
*		column number "col_Fin". 
*		(the first column is number 0 )
*
* DESCRIPTION   Sommation de plusieurs colonnes
*		d'une variable 1D (Int16)
*
* VERSION       $Revision$
*
* ARGUMENTS   IN   int    Var_in     any        Original data
*	      IN   int	  NbCol	     without	Number of Column of Var_in
*	      IN   int	  Col_deb    without    First column  	
*             IN   int    Col_fin    without    Last column
*             OUT  float  Var_out    same as 1  Summed data
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
#define _XOPEN_SOURCE_EXTENDED 1

#include <stdio.h>
#include <math.h>
#include <string.h>
#include <stdlib.h>
#include <limits.h>
#include "struct_oper.h"


/* La vraie fonction... */

int
Som_Col (unsigned long NbValIn,
	 short *Var_in,
	 int NbCol,
	 int Col_deb,
	 int Col_fin,
	 float *Var_out)

{
  unsigned long i;
  int k;

  if ((Col_deb < 0) || (Col_deb >= NbCol) ||
      (Col_fin < 0) || (Col_fin >= NbCol) ||
      (Col_deb > Col_fin))
    return -1;

  for (i = 0; i < NbValIn; i++)
    {
      Var_out[i] = 0.;
      for (k = Col_deb; k <= Col_fin; k++)
	{
	  Var_out[i] = Var_out[i] + ((float) Var_in[i * NbCol + k]);
	}
    }
  return 0;
}

/* la fonction d'enrobage classique */

int
OP_Som_Col (unsigned long NbVal, void *ArgList[], char *DiagExec)
{
  int CodRet;
  int NCar;

  NCar = sprintf (DiagExec, "Som_Col (%ld ech), nb_col=%d, col_deb=%d, col_fin=%d",
	 NbVal, *((int *)ArgList[1]), *((int *) ArgList[2]),
         *((int *)ArgList[3]));
  if (NCar < 0)
    NCar = 0;
  DiagExec += NCar;

  CodRet = Som_Col (NbVal,
		    (short *) ArgList[0],
		    *((int *) ArgList[1]),
		    *((int *) ArgList[2]),
		    *((int *) ArgList[3]),
		    (float *) ArgList[4]);
  switch (CodRet)
    {
    case 0:
      sprintf (DiagExec, "OK.");
      return OP_OK;
    case -1:
      sprintf (DiagExec, "ERR: Valeur de numero de colonne incorrecte !!!");
      return OP_FAIL;
    default:
      sprintf (DiagExec, "Erreur %d", CodRet);
      return OP_FAIL;
    }
}

void
ID_Som_Col (oper * optr)
{
  strcpy (optr->Nom, "Som_Col");
  optr->Version = "$Revision$";
  optr->Date = "$Date$";
  optr->fctptr = OP_Som_Col;
  optr->NbArg = 5;

  optr->Arg_Car[0].direction = DIR_IN;
  optr->Arg_Car[0].categorie = VECTOR;
  optr->Arg_Car[0].typ = ATYC_I16;
  optr->Arg_Car[0].array_dim = "*";
  optr->Arg_Car[0].type_sample = "any";
  optr->Arg_Car[0].sample = "any";
  optr->Arg_Car[0].unite = "any";
  optr->Arg_Car[0].famille = "any";

  /* NbCol */
  optr->Arg_Car[1].direction = DIR_IN;
  optr->Arg_Car[1].categorie = COEFFICIENT;
  optr->Arg_Car[1].array_dim = "1";
  optr->Arg_Car[1].typ = ATYC_I32;
  optr->Arg_Car[1].unite = "any";

  /* Col_deb */
  optr->Arg_Car[2].direction = DIR_IN;
  optr->Arg_Car[2].categorie = COEFFICIENT;
  optr->Arg_Car[2].array_dim = "1";
  optr->Arg_Car[2].typ = ATYC_I32;
  optr->Arg_Car[2].unite = "any";

  /* Col_fin */
  optr->Arg_Car[3].direction = DIR_IN;
  optr->Arg_Car[3].categorie = COEFFICIENT;
  optr->Arg_Car[3].array_dim = "1";
  optr->Arg_Car[3].typ = ATYC_I32;
  optr->Arg_Car[3].unite = "any";

  optr->Arg_Car[4].direction = DIR_OUT;
  optr->Arg_Car[4].categorie = VECTOR;
  optr->Arg_Car[4].typ = ATYC_IF32;
  optr->Arg_Car[4].array_dim = "1";
  optr->Arg_Car[4].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[4].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[4].sample = "$Arg1.sample";
  optr->Arg_Car[4].ref_time = "$Arg1.ref_time";
  optr->Arg_Car[4].unite = "$Arg1.unit";
  optr->Arg_Car[4].famille = "$Arg1.famille";

}
