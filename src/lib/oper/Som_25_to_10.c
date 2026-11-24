/****************************************************
*
* OPERATOR      Som_25_to_10.c   FUNCTION  ANSI-C
*
* PURPOSE       Sum consecutives values of a time serie from 25 to 10 Hz
*
* DESCRIPTION   Routine de sommation de 25 a 10 Hz, pour variables "float".
*               schema temporel retenu :              
*                 Variable origine      | | | | | | | | | | | | | | |
*                 Variable Destination  0  |    |    |    |    |    |
*               C'est a dire que l'algorithme est des plus simples    ... 
*                Dans une version future, on gerera l'argument Decal qui 
*               indique a quelle valeur interpollee correspond la 
*               premiere valeur d'origine. 
*               Il faudra aussi gerer les "valabs"...
*
* VERSION       $Revision$
*
* ARGUMENTS   IN   float  Var_in     any        Original data
*             IN   int    Decal      sec/freq   delay between first values
*             OUT  float  Var_out    same as 1  Interpolated data
*
* REFERENCES
*
* CHANGES       1.3 followed Categorie definition's change.
*               1.2 added comments/switched arg. orders
*
* COPYRIGHT     Meteo-France
*
*#########################################################################*/

#define _POSIX_SOURCE 1
#define _XOPEN_SOURCE 600

#include <string.h>
#include <limits.h>

#include "struct_oper.h"

/* La vraie fonction... */

unsigned long
Som_25_to_10 (unsigned long NbValIn,
     const float *Var_in,
     int Decal,
     float *Var_out)
{
  unsigned long i, NbValOut;
  long j;

  if (Decal != 0)
    return ULONG_MAX;

  if (NbValIn == 0)
    return 0;

  /* Normalement NbValIn correspond a un nbre entier de secondes */
  NbValOut = NbValIn * 10 / 25 ;

  /* on cumule donc la 1ere data de sortie est indefinie */
  *Var_out = 0 ;

  /* la boucle */
  j = 0 ;
  for (i = 0; i < NbValOut-1; i++)
    {
      Var_out++;

      if (i % 2 == 0)
          *Var_out = Var_in[j] + Var_in[j+1] + Var_in[j+2] /2.;
      else
        {
          *Var_out = Var_in[j+2] / 2. + Var_in[j+3] + Var_in[j+4];
          j += 5;
        }
    }

  return NbValOut;
}

/* la fonction d'enrobage classique */

int
OP_Som_25_to_10 (unsigned long NbVal, void *ArgList[], char *DiagExec)
{
  unsigned long CodRet;
  int NCar;

  NCar = sprintf (DiagExec, "Som_25_to_10 (%ld ech), Decal=%d",
		  NbVal, *((int *) ArgList[1]));
  if (NCar < 0)
    NCar = 0;
  DiagExec += NCar;

  CodRet = Som_25_to_10 (NbVal,
		(float *) ArgList[0],
		*((int *) ArgList[1]),
		(float *) ArgList[2]);

  switch (CodRet)
    {
    case ULONG_MAX:
      sprintf (DiagExec, "ERR: Decal hors-bornes");
      return OP_FAIL;
    default:
      sprintf (DiagExec, "OK. Le resultat a %lu echant.", CodRet);
      return OP_OK;
    }
}

void
ID_Som_25_to_10 (oper * optr)
{
  strcpy (optr->Nom, "Som_25_to_10");
  optr->Version = "$Revision$";
  optr->Date = "$Date$";
  optr->fctptr = OP_Som_25_to_10;
  optr->NbArg = 3;

  /* Var_in  */
  optr->Arg_Car[0].direction = DIR_IN;
  optr->Arg_Car[0].categorie = VECTOR;
  optr->Arg_Car[0].typ = ATYC_IF32;
  optr->Arg_Car[0].array_dim = "1";
  optr->Arg_Car[0].type_sample = "any";
  optr->Arg_Car[0].sample = "any";
  optr->Arg_Car[0].unite = "any";

  /*  Decal */
  optr->Arg_Car[1].direction = DIR_IN;
  optr->Arg_Car[1].categorie = COEFFICIENT;
  optr->Arg_Car[1].array_dim = "1";
  optr->Arg_Car[1].typ = ATYC_I32;
  optr->Arg_Car[1].unite = "any";
  optr->Arg_Car[1].type_sample = NULL;
  optr->Arg_Car[1].sample = NULL;

  /* Var_out  */
  optr->Arg_Car[2].direction = DIR_OUT;
  optr->Arg_Car[2].categorie = VECTOR;
  optr->Arg_Car[2].typ = ATYC_IF32;
  optr->Arg_Car[2].array_dim = "1";
  optr->Arg_Car[2].NbVal = "$Arg1.NbVal * 10 / 25";
  optr->Arg_Car[2].sample = "10";
  optr->Arg_Car[2].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[2].ref_time = " \"time_\" + $Arg3.sample";
  optr->Arg_Car[2].unite = "$Arg1.unit";
  optr->Arg_Car[2].famille = "$Arg1.famille";
}
