/****************************************************
*
* OPERATOR      Som.c   FUNCTION  ANSI-C
*
* PURPOSE       Sum consecutives values of a time serie
*
* DESCRIPTION   Routine de sommation, pour variables "float".
*               schema temporel retenu :              
*                 Variable origine      | | | | | | | | | | | | | | | | 
*                 Variable Destination     |       |       |       |  
*               C'est a dire que l'algorithme est des plus simples    ... 
*                Dans une version future, on gerera l'argument Decal qui 
*               indique a quelle valeur interpolee correspond la 
*               premiere valeur d'origine. 
*               Il faudra aussi gerer les "valabs"...
*               On prevoit le cas où le nb de valeurs en entrée est <
*               a NbSum --> on renvoie un NaN
*
*
* VERSION       $Revision$
*
* ARGUMENTS   IN   float  Var_in     any        Original data
*             IN   float  NbSum    whithout   frequency ratio
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
/* Le #define _HPUX_SOURCE n'est la que pour "voir" strdup */
#define _HPUX_SOURCE 1

#include <stdio.h>
#include <math.h>
#include <string.h>
#include <limits.h>
#include "struct_oper.h"

/* La vraie fonction... */

int
Som (unsigned long NbValIn,
     const float *Var_in,
     int NbSum,
     int Decal,
     float *Var_out,
     long TabStat[2])
{
  long i;
  long Ntour, NTourStd, Reste;
  int j;
  register float loc_som;

  TabStat[0] = -1;
  TabStat[1] = -1;

  if (NbSum < 1.0)
    return -1;

  if ((Decal < -NbSum) || (Decal > NbSum))
    return -2;

  if (NbValIn == 0)
    return 0;

  Ntour = NbValIn / NbSum;	/* division entière */
  Reste = NbValIn % NbSum;

  /* Quand Decal est non-nul, les Ntour boucles standard sont remplacées
   * par une boucle non-standard (au début ou à la fin), et Ntour - 1
   * boucles standard.  */
  if (Decal == 0)
    NTourStd = Ntour;
  else
    NTourStd = Ntour - 1;

  /* Si Decal < 0, la boucle non-standard est au début.           */
  if (Decal < 0)
    {
      /* On ne s'embète pas à faire des sommes partielles... */
      /* on prend N fois la première valeur.                */
      *Var_out = *Var_in * NbSum;
      Var_out++;
      /* Et on se déplace pour la première boucle standard  */
      Var_in += NbSum + Decal;
    }
  else
    Var_in += Decal;

  /* Les boucles standard */
  for (i = 0; i < NTourStd; i++)
    {
      loc_som = 0.0;
      for (j = 0; j < NbSum; j++)
	{
	  loc_som += *Var_in;
	  Var_in++;
	}
      *Var_out = loc_som;
      Var_out++;
    }

  /* Si Decal > 0, la boucle non-standard est a la fin            */
  if (Decal > 0)
    {
      /* On ne s'embète pas à faire des sommes partielles... */
      /* on prend N fois une des dernières valeurs.         */
      if (NbSum - Decal > 0)
	*Var_out = *Var_in * NbSum;
      else
	*Var_out = *(Var_in - 1) * NbSum;
      Var_out++;
    }

  /* Si Reste n'est pas nul ..... */
  if (Reste != 0)
    {
      /* et Si NbValIn est inferieur à NbSum */
      /* Le nb de points n'est pas suffisant pour faire un "tour" ! */
      /*  On n'a rien fait et on renvoie un NaN ! */
      if (Ntour == 0)
	*Var_out = K_NaN;
      else
	/* Et n'oublions pas le cas où NbValIn n'est pas multiple de NbSum */
	/* Y'a un dernier Var_out à remplir. On duplique la précédente valeur */
	/* uniquement dans le cas ou Ntour != 0 (il faut que la valeur precedente existe!) */
	*Var_out = *(Var_out - 1);
    }

  TabStat[0] = Ntour;
  TabStat[1] = Reste;
  return 0;
}

/* la fonction d'enrobage classique */

int
OP_Som (unsigned long NbVal, void *ArgList[], char *DiagExec)
{
  int CodRet;
  int NCar;
  long TabStat[2];

  NCar = sprintf (DiagExec, "Som, Nb echant. : %lu,  %d, decalage : %d.",
		  NbVal, *((int *) ArgList[1]), *((int *) ArgList[2]));
  if (NCar < 0)
    NCar = 0;
  DiagExec += NCar;

  CodRet = Som (NbVal,
		(float *) ArgList[0],
		*((int *) ArgList[1]),
		*((int *) ArgList[2]),
		(float *) ArgList[3],
                TabStat);

  switch (CodRet)
    {
    case 0:
      sprintf (DiagExec, "OK: Nb de tours : %ld , Reste : %ld ",
	       TabStat[0], TabStat[1]);
      return OP_OK;
    case -1:
      sprintf (DiagExec, "ERR: NbSum < 1 ! (%d)", *(int *) ArgList[1]);
      return OP_FAIL;
    case -2:
      sprintf (DiagExec, "ERR: Decal hors-bornes (%d)", *(int *) ArgList[2]);
      return OP_FAIL;
    default:
      sprintf (DiagExec, "ERR: Erreur %d", CodRet);
      return OP_FAIL;
    }

}

void
ID_Som (oper * optr)
{
  strcpy (optr->Nom, "Som");
  optr->Version = "$Revision$";
  optr->Date = "$Date$";
  optr->fctptr = OP_Som;
  optr->NbArg = 4;

  /* Var_in */
  optr->Arg_Car[0].direction = DIR_IN;
  optr->Arg_Car[0].categorie = VECTOR;
  optr->Arg_Car[0].typ = ATYC_IF32;
  optr->Arg_Car[0].array_dim = "1";
  optr->Arg_Car[0].type_sample = "any";
  optr->Arg_Car[0].sample = "any";
  optr->Arg_Car[0].unite = "any";

  /* NbSum */
  optr->Arg_Car[1].direction = DIR_IN;
  optr->Arg_Car[1].categorie = COEFFICIENT;
  optr->Arg_Car[1].array_dim = "1";
  optr->Arg_Car[1].typ = ATYC_I32;
  optr->Arg_Car[1].unite = "any";
  optr->Arg_Car[1].type_sample = NULL;
  optr->Arg_Car[1].sample = NULL;

  /* Decal */
  optr->Arg_Car[2].direction = DIR_IN;
  optr->Arg_Car[2].categorie = COEFFICIENT;
  optr->Arg_Car[2].array_dim = "1";
  optr->Arg_Car[2].typ = ATYC_I32;
  optr->Arg_Car[2].unite = "any";
  optr->Arg_Car[2].type_sample = NULL;
  optr->Arg_Car[2].sample = NULL;

  /* Var_out */
  optr->Arg_Car[3].direction = DIR_OUT;
  optr->Arg_Car[3].categorie = VECTOR;
  optr->Arg_Car[3].typ = ATYC_IF32;
  optr->Arg_Car[3].array_dim = "1";
  optr->Arg_Car[3].NbVal = "$Arg1.NbVal / $Arg2";
  optr->Arg_Car[3].sample = "$Arg1.sample / $Arg2";
  optr->Arg_Car[3].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[3].ref_time = " \"time_\" + $Arg4.sample";
  optr->Arg_Car[3].unite = "$Arg1.unit";
  optr->Arg_Car[3].famille = "$Arg1.famille";

}
