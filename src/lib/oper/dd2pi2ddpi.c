/*****************************************************
*
* OPERATOR         dd2pi2ddpi.c   FUNCTION  ANSI-C
*
* PURPOSE          Convert wind-ship [0;360] direction to [-180;180].
*
* DESCRIPTION      Convert wind-ship [0;360] direction to [-180;180]
*
* VERSION          1.4
*
* ARGUMENTS  IN   float    DDA2  degree       Wind ship Direction FROM where the vector
*                                            starts (0=front of ship) 0 to 360 degrees
*            OUT   float   DDA1  degree       Direction -180 to 180 degrees (0=front of the ship)
*
*                                                
* ENTRY            NONE
*               
* SUBPROGRAMS      NONE
*
* FILES            NONE
*
* REFERENCES       
*
*
* CHANGES          1.3  adapted to follow categorie's definition change
*                  1.2  added args' sampling description
*
*
* COPYRIGHT        Meteo-France/CNRM
*
* AGREEMENT        
*########################################################################*/

#define _POSIX_SOURCE 1
#define _XOPEN_SOURCE 600
/* Le #define _HPUX_SOURCE est la pour utiliser la fonction isfinite */
#define _HPUX_SOURCE 1

#include <math.h>
#include <stdio.h>
#include <string.h>
#include "struct_oper.h"


void
dd2pi2ddpi (unsigned long NLoop, const float *dda2, float *dda1)
{
  unsigned long i;

  for (i = 0; i < NLoop; i++)
    {
      if (*dda2 > 180.)
	{
	  *dda1 = *dda2 - 360.;
	}
      else
	{
	  *dda1 = *dda2;
	}

      dda1++;
      dda2++;
    }
  return;
}


/* la fonction d'enrobage classique */

int
OP_dd2pi2ddpi (unsigned long NbVal, void *ArgList[], char *DiagExec)
{
  int NCar;

  NCar = sprintf (DiagExec, "dd2pi2ddpi : (%ld echant.) ", NbVal) ;
  if (NCar < 0)
    NCar = 0;
  DiagExec += NCar;

  dd2pi2ddpi (NbVal, (float *) ArgList[0], (float *) ArgList[1]);

  return OP_OK;
}

void
ID_dd2pi2ddpi (oper * optr)
{
  strcpy (optr->Nom, "dd2pi2ddpi");
  optr->Version = "1.0";
  optr->Date = "01/28/08";
  optr->fctptr = OP_dd2pi2ddpi;
  optr->misval_auto = 1;	/* gestion auto des misval */
  optr->NbArg = 2;
  optr->repl_oper = "Chang_gam_angl";
  optr->repl_cause = "N'a jamais été documenté, ne fait rien de mieux que Chang_gam_angl";
  /* Sans oublier le nom pas logique, qui rappelle pi alors qu'il travaille sur des degrés. */

  optr->Arg_Car[0].direction = DIR_IN;
  optr->Arg_Car[0].categorie = VECTOR;
  optr->Arg_Car[0].typ = ATYC_IF32;
  optr->Arg_Car[0].array_dim = "1";
  optr->Arg_Car[0].type_sample = "any";
  optr->Arg_Car[0].sample = "any";
  optr->Arg_Car[0].unite = "degree";

  optr->Arg_Car[1].direction = DIR_OUT;
  optr->Arg_Car[1].categorie = VECTOR;
  optr->Arg_Car[1].typ = ATYC_IF32;
  optr->Arg_Car[1].array_dim = "1";
  optr->Arg_Car[1].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[1].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[1].sample = "$Arg1.sample";
  optr->Arg_Car[1].ref_time = "$Arg1.ref_time";
  optr->Arg_Car[1].misval = "$Arg1.misval";
  optr->Arg_Car[1].unite = "degree";
  optr->Arg_Car[1].famille = "$Arg1.famille";
}
