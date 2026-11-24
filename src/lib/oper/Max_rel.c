/****************************************************
*
* OPERATOR      Max_rel.c   FUNCTION  ANSI-C
*
* PURPOSE       Relative maximum values of a time serie
*
* DESCRIPTION   Find all maxima and their associated times.
*               with NAN for others data
*
* VERSION       $Revision$
*
* ARGUMENTS   IN   float  Var_in     any        Original data
*             OUT  float  Var_out    same as 1  Maximum value
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
#define _HPUX_SOURCE 1

#include <stdio.h>
#include <math.h>
#include <string.h>
#include <limits.h>

#include "struct_oper.h"


/* La vraie fonction... */

int
Max_rel (unsigned long NbValIn, const float *Var_in, float *Var_out)
{
  unsigned long i;
  double max_rel;


  if (NbValIn == 0)
    return 0;

  /* Les boucles standard */

  /*Initialisation */
  for (i = 0; i < NbValIn; i++)
    {
      Var_out[i] = 0. / 0.;
    }

  /*cas du premier */
  max_rel = Var_in[0];

  for (i = 1; i < NbValIn; i++)
    {
      if (isfinite (Var_in[i]))	/*valeur finie */
	{
	  if (Var_in[i] > max_rel)	/*nouveau max relatif */
	    {
	      if (Var_in[i] > Var_in[i - 1])	/*pente positive : on incremente max_rel */
		{
		  max_rel = Var_in[i];
		}
	    }
	  else
	    {
	      /*sinon, le precedent est effectivement un max rel */
	      Var_out[i - 1] = max_rel;
	      /*on reinitialise le "max_rel" : */
	      max_rel = -MAXFLOAT;
	      /* valeur mini d'un flottant pour initialiser les loc_max */
	    }
	}

    }
  /*cas du dernier */
  if (max_rel > -MAXFLOAT)
    Var_out[i - 1] = max_rel;
  return 0;
}

/* la fonction d'enrobage classique */

int
OP_Max_rel (unsigned long NbVal, void *ArgList[], char *DiagExec)
{
  int CodRet;
  int NCar;

  NCar = sprintf (DiagExec, "Max_rel : (%ld echant.) ", NbVal) ;
  if (NCar < 0)
    NCar = 0;
  DiagExec += NCar;

  CodRet = Max_rel (NbVal, (float *) ArgList[0], (float *) ArgList[1]);

  switch (CodRet)
    {
    case 0:
      sprintf (DiagExec, "OK.");
      return OP_OK;
    case -1:
      sprintf (DiagExec, "ERR:  !!!");
      return OP_FAIL;
    case -2:
      sprintf (DiagExec, "ERR: ");
      return OP_FAIL;
    default:
      sprintf (DiagExec, "ERR: Erreur %d", CodRet);
      return OP_FAIL;
    }
}

void
ID_Max_rel (oper * optr)
{
  strcpy (optr->Nom, "Max_rel");
  optr->Version = "$Revision$";
  optr->Date = "$Date$";
  optr->fctptr = OP_Max_rel;
  optr->NbArg = 2;
  optr->Arg_Car[0].direction = DIR_IN;
  optr->Arg_Car[0].categorie = VECTOR;
  optr->Arg_Car[0].typ = ATYC_IF32;
  optr->Arg_Car[0].array_dim = "1";
  optr->Arg_Car[0].type_sample = "any";
  optr->Arg_Car[0].sample = "any";
  optr->Arg_Car[0].unite = "any";

  optr->Arg_Car[1].direction = DIR_OUT;
  optr->Arg_Car[1].categorie = VECTOR;
  optr->Arg_Car[1].typ = ATYC_IF32;
  optr->Arg_Car[1].array_dim = "1";
  optr->Arg_Car[1].NbVal = "$Arg1.NbVal";	/* */
  optr->Arg_Car[1].ref_time = "$Arg1.ref_time";
  optr->Arg_Car[1].unite = "$Arg1.unit";
  optr->Arg_Car[1].famille = "$Arg1.famille";


}
