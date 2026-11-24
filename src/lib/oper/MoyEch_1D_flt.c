/****************************************************
*
* OPERATOR      MoyEch_1D_flt.c   FUNCTION  ANSI-C
*
* PURPOSE       Sum consecutives values of a time serie
*
* DESCRIPTION   Routine de moyenne-échantillonnage, pour variables 1D (float)
*
* VERSION       $Revision$
*
* ARGUMENTS   IN   float  Var_in     any        Original data
*	      IN   int	  NbCol	   without      Number of Columns
*             IN   int    NbSum    without      Number of samples to sum.
*             IN   int    Decal    without     
*             OUT  float  Var_out    same as 1  averaged data
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
/* Le #define _HPUX_SOURCE n'est la que pour "voir" strdup */
#define _HPUX_SOURCE 1

#include <stdio.h>
#include <math.h>
#include <string.h>
#include <stdlib.h>
#include <limits.h>

#include "struct_oper.h"


/* La vraie fonction... */

int
MoyEch_1D_flt (unsigned long NbValIn,
	       const float *Var_in, int NbCol, int NbSum, int Decal,
	       float *Var_out)
{
  unsigned long i;
  unsigned long Ntour, NTourStd;
  long Reste;
  int j, k;
  float *loc_som;

  if (NbSum < 1.0)
    return -1;

  if ((Decal < -NbSum) || (Decal > NbSum))
    return -2;

  /* le cas facile...  */
  if (NbValIn == 0)
    return 0;

  loc_som = malloc (NbCol * sizeof (float));
  if (loc_som == NULL)
    return -3;

  Ntour = NbValIn / NbSum;	/* division entière */
  Reste = NbValIn % NbSum;

  /* Quand Decal est non-nul, les Ntour boucles standard sont remplacées
   * par une boucle non-standard (au début ou à la fin), et Ntour - 1
   * boucles standard.
   */
  if (Decal == 0)
    NTourStd = Ntour;
  else
    NTourStd = Ntour - 1;

  /* Si Decal < 0, la boucle non-standard est au début.           */
  if (Decal < 0)
    {
      if (NbSum + Decal > 0)
	{
	  for (k = 0; k < NbCol; k++)
	    {
	      /* Un jour, on fera une vraie somme */
	      Var_in += ((NbSum + Decal - 1) * NbCol);
	      *Var_out = *(Var_in + k);
	      Var_out++;
	      Var_in++;
	    }
	}
      else
	/* cas où il n'y a rien à faire, on recopie les
	 * premières Var_in plutot que de mettre 0 ou NaN */
	for (k = 0; k < NbCol; k++)
	  {
	    *Var_out = *(Var_in + k);
	    Var_out++;
	  }
    }
  else
    Var_in += (Decal * NbCol);

  for (i = 0; i < NTourStd; i++)
    {
      for (k = 0; k < NbCol; k++)
	loc_som[k] = 0;

      for (j = 0; j < NbSum; j++)
	{
	  for (k = 0; k < NbCol; k++)
	    {
	      loc_som[k] += *Var_in;
	      Var_in++;
	    }
	}
      for (k = 0; k < NbCol; k++)
	{
	  *Var_out = loc_som[k] / NbSum;
	  Var_out++;
	}
    }
  /* Si Decal > 0, la boucle non-standard est a la fin            */
  if (Decal > 0)
    {
    }

  /* Et n'oublions pas le cas où NbValIn n'est pas multiple de NbSum :
   * Y'a un dernier Var_out à remplir. On duplique la précédente valeur */
  if (Reste > 0)
    {
    }

  free (loc_som);
  return 0;
}

/* la fonction d'enrobage classique */

int
OP_MoyEch_1D_flt (unsigned long NbVal, void *ArgList[], char *DiagExec)
{
  int CodRet;
  int NCar;

  NCar =
    sprintf (DiagExec,
	     "MoyEch_1D_flt (%lu echant), NbCol=%d, NbSum=%d, Decal=%d;",
	     NbVal, *((int *) ArgList[1]), *((int *) ArgList[2]),
	     *((int *) ArgList[3]));
  if (NCar < 0)
    NCar = 0;
  DiagExec += NCar;

  CodRet = MoyEch_1D_flt (NbVal,
			  (float *) ArgList[0],
			  *((int *) ArgList[1]),
			  *((int *) ArgList[2]),
			  *((int *) ArgList[3]), (float *) ArgList[4]);

  switch (CodRet)
    {
    case 0:
      sprintf (DiagExec, " OK.");
      return OP_OK;
    case -1:
      sprintf (DiagExec, "ERR: NbSum < 1 !!!");
      return OP_FAIL;
    case -2:
      sprintf (DiagExec, "ERR: Decal Hors-bornes !");
      return OP_FAIL;
    case -3:
      sprintf (DiagExec, "ERR: malloc Error !");
      return OP_FAIL;
    default:
      sprintf (DiagExec, "Erreur %d", CodRet);
      return OP_FAIL;
    }

}

void
ID_MoyEch_1D_flt (oper * optr)
{
  strcpy (optr->Nom, "MoyEch_1D_flt");
  optr->Version = "$Revision$";
  optr->Date = "$Date$";
  optr->fctptr = OP_MoyEch_1D_flt;
  optr->NbArg = 5;

  /* Var_in */
  optr->Arg_Car[0].direction = DIR_IN;
  optr->Arg_Car[0].categorie = VECTOR;
  optr->Arg_Car[0].typ = ATYC_IF32;
/*
   optr->Arg_Car[0].array_dim = "$Arg2"; 
 */
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

  /* NbSum */
  optr->Arg_Car[2].direction = DIR_IN;
  optr->Arg_Car[2].categorie = COEFFICIENT;
  optr->Arg_Car[2].array_dim = "1";
  optr->Arg_Car[2].typ = ATYC_I32;
  optr->Arg_Car[2].unite = "any";

  /* Decal */
  optr->Arg_Car[3].direction = DIR_IN;
  optr->Arg_Car[3].categorie = COEFFICIENT;
  optr->Arg_Car[3].array_dim = "1";
  optr->Arg_Car[3].typ = ATYC_I32;
  optr->Arg_Car[3].unite = "any";

  /* Var_out */
  optr->Arg_Car[4].direction = DIR_OUT;
  optr->Arg_Car[4].categorie = VECTOR;
  optr->Arg_Car[4].typ = ATYC_IF32;
  /*optr->Arg_Car[4].array_dim = "$Arg1.array_dim"); */
  optr->Arg_Car[4].array_dim = "$Arg2";
  optr->Arg_Car[4].bornes = "$Arg1.bornes";	/*   Le sous-échantillonnage ne change pas les bornes   */
  optr->Arg_Car[4].unit_bornes = "$Arg1.unit_bornes";
  optr->Arg_Car[4].NbVal = "$Arg1.NbVal / $Arg3";
  optr->Arg_Car[4].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[4].sample = "$Arg1.sample / $Arg3";
  optr->Arg_Car[4].ref_time = " \"time_\" + $Arg5.sample";
  optr->Arg_Car[4].unite = "$Arg1.unit";
  optr->Arg_Car[4].famille = "$Arg1.famille";
  optr->Arg_Car[4].name =
    "\"Moyenne et echantillonnage regulier de \" + $Arg1.name";
  optr->Arg_Car[4].en_name =
    "\"Regular average and sub-sampling of \" + $Arg1.english_name";
}
