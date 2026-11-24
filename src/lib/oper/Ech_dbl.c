/****************************************************
*
* OPERATOR       Ech_dbl.c   FUNCTION  ANSI-C
*
* PURPOSE        Sampling of a time serie
*
* DESCRIPTION    Routine d'echantillonnage, pour variables "double". 
*                ressort 1 valeur toutes les (1/RapFreq), en commencant 
*                par la "decal"ieme. 
*
* VERSION        $Revision$
*
* ARGUMENTS  IN   double  Var_in     any        Original data
*            IN   double  RapFreq    whithout   frequency ratio
*            IN   int     Decal      sec/freq   delay between first values
*            OUT  double  Var_out    same as 1  Sampled data
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

#include "struct_oper.h"
/* La vraie fonction... */

long
Ech_dbl (unsigned long Nloop,
	 const double *Var_in,
	 double RapFreq, 
	 int Decal, 
	 double *Var_out, 
	 long TabStat[3])
/**    Routine d'echantillonnage, pour variables "double".
 *  Ressort 1 valeur toutes les (1/RapFreq), en commencant
 *  par la "Decal"ieme. 
 */
{
  unsigned long i;
  long NbValOut;
  int NSom;
  long Ntour, Reste;

  if (RapFreq > 1.0)
    {
      return -1;
    }

  NSom = floor ((1.0 / RapFreq) + 0.5);

  if (Decal > NSom)
    {
      return -2;
    }
  if (Decal < -NSom)
    {
      return -3;
    }

  /* Réglons immédiatement le cas où y'a rien a faire. */
  if (Nloop == 0)
    return 0;

  Ntour = Nloop / NSom;		/* division entière */
  Reste = Nloop % NSom;

  NbValOut = 0;
  /* Si le premier élément demandé est avant le début,
   * on fournit le premier, en différant le décalage
   * après la première affectation. */
  if (Decal < 0)
    {
      *Var_out = *Var_in;
      Var_in += Decal;
      NbValOut++;
    }
  else
    {
      Var_in += Decal;
      *Var_out = *Var_in;
      NbValOut++;
    }
  Var_in += NSom;
  Var_out++;

  /* Boucle standard pour la suite. */
  for (i = 1; i < Ntour; i++)
    {
      *Var_out = *Var_in;
      Var_in += NSom;
      Var_out++;
      NbValOut++;
    }


  if (Reste > 0)
    {
      if (Decal < Reste)
	{
	  *Var_out = *Var_in;
	}
      else
	{
	  /* Pour être cohérent avec le cas Decal<0,
	   * on pourraît, peut-être, recopier la dernière valeur. */
	  *Var_out = K_NaN;
	}
      NbValOut++;
    }

  TabStat[0] = NSom;
  TabStat[1] = Ntour;
  TabStat[2] = Reste;
  return NbValOut;
}

/* la fonction d'enrobage classique */

int
OP_Ech_dbl (unsigned long NbVal, void *ArgList[], char *DiagExec)
{
  long CodRet;
  int n_char;
  long TabStat[3];

  n_char = sprintf (DiagExec, "Ech_dbl, NbVal=%ld;", NbVal);
  DiagExec += n_char;

  CodRet = Ech_dbl (NbVal,
		    (double *) ArgList[0],
		    *((double *) ArgList[1]),
		    *((int *) ArgList[2]), 
		    (double *) ArgList[3], 
		    TabStat);
  if (CodRet >= 0)
    {
      sprintf (DiagExec,
	       "OK: %ld val. calculées,  (%ld = %ld * %ld + %ld).",
	       CodRet, NbVal, TabStat[1], TabStat[0], TabStat[2]);
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
      sprintf (DiagExec, "ERR: Erreur %ld.", CodRet);
    }
  return OP_FAIL;

}

void
ID_Ech_dbl (oper * optr)
{
  strcpy (optr->Nom, "Ech_dbl");
  optr->Version = "$Revision$";
  optr->Date = "$Date$";
  optr->fctptr = OP_Ech_dbl;
  optr->NbArg = 4;

  optr->Arg_Car[0].direction = DIR_IN;
  optr->Arg_Car[0].categorie = VECTOR;
  optr->Arg_Car[0].typ = ATYC_IF64;
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
  optr->Arg_Car[2].typ = ATYC_I32;
  optr->Arg_Car[2].array_dim = "1";
  optr->Arg_Car[2].type_sample = NULL;	/* sans objet pour COEFFICIENT */
  optr->Arg_Car[2].sample = NULL;	/* sans objet pour COEFFICIENT */
  optr->Arg_Car[2].unite = "any";

  optr->Arg_Car[3].direction = DIR_OUT;
  optr->Arg_Car[3].categorie = VECTOR;
  optr->Arg_Car[3].typ = ATYC_IF64;
  optr->Arg_Car[3].array_dim = "1";
  optr->Arg_Car[3].NbVal = "$Arg1.NbVal * $Arg2";
  optr->Arg_Car[3].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[3].sample = "$Arg1.sample * $Arg2";
  optr->Arg_Car[3].unite = "$Arg1.unit";
  optr->Arg_Car[3].ref_time = " \"time_\" + $Arg4.sample";
  optr->Arg_Car[3].famille = "$Arg1.famille";

}
