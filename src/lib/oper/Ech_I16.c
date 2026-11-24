/****************************************************
*
* OPERATOR       Ech_I16.c   FUNCTION  ANSI-C
*
* PURPOSE        Sampling of a time serie
*
* DESCRIPTION    Routine d'echantillonnage, pour variables "short". 
*                ressort 1 valeur toutes les (1/RapFreq), en commencant 
*                par la "decal"ieme. 
*
* VERSION        $Revision$
*
* ARGUMENTS  IN   Int_16  Var_in     any        Original data
*            IN   double  RapFreq    whithout   frequency ratio
*            IN   int     Decal      sec/freq   delay between first values
*            OUT  Int_16  Var_out    same as 1  Sampled data
*
* REFERENCES
*
* CHANGES        1.3 adapted to CATEGORIE's definition change
*                1.2 added comments/switched arg. orders
*
* COPYRIGHT      Meteo-France
*
* AGREEMENT      The author wishes that .....
*
*#########################################################################*/

#define _POSIX_SOURCE 1
#define _XOPEN_SOURCE 600
#define _HPUX_SOURCE 1
#define _XOPEN_SOURCE_EXTENDED 1

#include <stdio.h>
#include <math.h>
#include <string.h>

/* La vraie fonction... */

/**     Routine d'echantillonnage, pour variables "short".
  *  Ressort 1 valeur toutes les (1/RapFreq), en commencant
  *  par la "decal"ieme. 
  */
int
Ech_I16 (unsigned long Nloop,
	 short *Var_in, double RapFreq, float Decal, short *Var_out)
{
  unsigned long i;
  int NSom;

  if (RapFreq > 1.0)
    {
      return -1;
    }

  NSom = floor ((1.0 / RapFreq) + 0.5);

  if ((int) Decal > NSom)
    {
      return -2;
    }

  if ((int) Decal < -NSom)
    {
      return -3;
    }
  
  /* Réglons immédiatement le cas où y'a rien a faire. */
  if (Nloop == 0)
    return 0;

  /* Si le premier élément demandé est avant le début,
   * on fournit le premier, en différant le décalage
   * après la première affectation. */
  if (Decal < 0)
    {
      *Var_out = *Var_in;
      Var_in += (int) Decal;
    }
  else
    {
      Var_in += (int) Decal;
      *Var_out = *Var_in;
    }
  Var_in += NSom;
  Var_out++;

  /* Boucle standard pour la suite. */
  for (i = 1; i < (Nloop * RapFreq); i++)
    {
      *Var_out = *Var_in;
      Var_in += NSom;
      Var_out++;
    }

  return 0;
}

/* la fonction d'enrobage classique */
#include "struct_oper.h"

int
OP_Ech_I16 (unsigned long NbVal, void *ArgList[], char *DiagExec)
{
  int CodRet;
  int n_char;

  n_char=sprintf (DiagExec, "Ech_I16, NbVal=%lu\n", NbVal);
  DiagExec +=n_char;

  CodRet = Ech_I16 (NbVal,
		    (short *) ArgList[0],
		    *((double *) ArgList[1]),
		    *((float *) ArgList[2]), (short *) ArgList[3]);
  if (CodRet >= 0)
  {
  	return OP_OK;
  }
  switch (CodRet)
    {
    case -1:
      sprintf (DiagExec, "ERR: RapFreq > 1 !!!");
      break;
    case -2:
      sprintf (DiagExec, "ERR: Valeur Decal sup au max possible.");
      break;
    case -3:
      sprintf (DiagExec, "ERR: Valeur Decal inf au min possible.");
      break;
    default:
      sprintf (DiagExec, "ERR: Erreur %d.", CodRet);
    }
  return OP_FAIL;

}

void
ID_Ech_I16 (oper * optr)
{
  strcpy (optr->Nom, "Ech_I16");
  optr->Version = "$Revision$";
  optr->Date = "$Date$";
  optr->fctptr = OP_Ech_I16;
  optr->NbArg = 4;

  optr->Arg_Car[0].direction = DIR_IN;
  optr->Arg_Car[0].categorie = VECTOR;
  optr->Arg_Car[0].typ = ATYC_I16;
  optr->Arg_Car[0].array_dim = "1";
  optr->Arg_Car[0].type_sample = "any";
  optr->Arg_Car[0].sample = "any";
  optr->Arg_Car[0].famille = "any";
  optr->Arg_Car[0].unite = "any";

  optr->Arg_Car[1].direction = DIR_IN;
  optr->Arg_Car[1].categorie = COEFFICIENT;
  optr->Arg_Car[1].typ = ATYC_IF64;
  optr->Arg_Car[1].array_dim = "1";
  optr->Arg_Car[1].type_sample = NULL;	/* sans objet pour COEFFICIENT */
  optr->Arg_Car[1].sample = NULL;	/* sans objet pour COEFFICIENT */
  optr->Arg_Car[1].unite = "without";

  optr->Arg_Car[2].direction = DIR_IN;
  optr->Arg_Car[2].categorie = COEFFICIENT;
  optr->Arg_Car[2].typ = ATYC_IF32;
  optr->Arg_Car[2].array_dim = "1";
  optr->Arg_Car[2].type_sample = NULL;	/* sans objet pour COEFFICIENT */
  optr->Arg_Car[2].sample = NULL;	/* sans objet pour COEFFICIENT */
  optr->Arg_Car[2].unite = "any";

  optr->Arg_Car[3].direction = DIR_OUT;
  optr->Arg_Car[3].categorie = VECTOR;
  optr->Arg_Car[3].typ = ATYC_I16;
  optr->Arg_Car[3].array_dim = "1";
  optr->Arg_Car[3].NbVal = "$Arg1.NbVal * $Arg2";
  optr->Arg_Car[3].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[3].sample = "$Arg1.sample * $Arg2";
  optr->Arg_Car[3].unite = "$Arg1.unit";
  optr->Arg_Car[3].ref_time = " \"time_\" + $Arg4.sample";
  optr->Arg_Car[3].famille = "$Arg1.famille";

}
