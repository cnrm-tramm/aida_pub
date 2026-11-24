/*****************************************************
*
* OPERATOR         ddff2UV.c   FUNCTION  ANSI-C
*
* PURPOSE          Convert polar coordinates to cartesian.
*
* DESCRIPTION      Converts coordinates in a vector expressed in
*                  a Earth-related cartesians "repere", from a polar
*                  referential, with angles counting from North.
*
* VERSION          1.4
*
* ARGUMENTS  IN   float    DD  degree        Direction FROM where the vector
*                                             starts (0=North)
*            IN   float    FF  same as U, V  Module of the vector
*            OUT  float    U   any           East component, from West
*            OUT  float    V   same as U     North component, from South
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


int
ddff2UV (unsigned long NLoop,
	 const float *DD, const float *FF, float *U, float *V)
{
  unsigned long i;
  register double Deg2Rad;
  register double dir;

  /* entree de l'angle en degres, donc conversion en radians */
  Deg2Rad = M_PI / 180.0;

  for (i = 0; i < NLoop; i++)
    {
      dir = *DD * Deg2Rad;
      *U = sin (dir) * (-1) * *FF;
      *V = cos (dir) * (-1) * *FF;
      DD++;
      FF++;
      U++;
      V++;
    }
  return 0;
}


/* la fonction d'enrobage classique */

int
OP_ddff2UV (unsigned long NbVal, void *ArgList[], char *DiagExec)
{
  int CodRet;

  (void) sprintf (DiagExec, "ddff2UV, %lu Ech", NbVal);

  CodRet = ddff2UV (NbVal,
		   (float *) ArgList[0],
		   (float *) ArgList[1],
		   (float *) ArgList[2], (float *) ArgList[3]);
  return OP_OK;
}

void
ID_ddff2UV (oper * optr)
{
  strcpy (optr->Nom, "ddff2UV");
  optr->Version = "$Revision$";
  optr->Date = "$Date$";
  optr->fctptr = OP_ddff2UV;
  optr->misval_auto = 1;	/* gestion auto des misval */
  optr->NbArg = 4;

  /* DD */
  optr->Arg_Car[0].direction = DIR_IN;
  optr->Arg_Car[0].categorie = VECTOR;
  optr->Arg_Car[0].typ = ATYC_IF32;
  optr->Arg_Car[0].array_dim = "1";
  optr->Arg_Car[0].type_sample = "any";
  optr->Arg_Car[0].sample = "any";
  optr->Arg_Car[0].unite = "degree";

  /* FF */
  optr->Arg_Car[1].direction = DIR_IN;
  optr->Arg_Car[1].categorie = VECTOR;
  optr->Arg_Car[1].typ = ATYC_IF32;
  optr->Arg_Car[1].array_dim = "1";
  optr->Arg_Car[1].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[1].type_sample = "any";
  optr->Arg_Car[1].sample = "any";
  optr->Arg_Car[1].unite = "any";

  /* U */
  optr->Arg_Car[2].direction = DIR_OUT;
  optr->Arg_Car[2].categorie = VECTOR;
  optr->Arg_Car[2].typ = ATYC_IF32;
  optr->Arg_Car[2].array_dim = "1";
  optr->Arg_Car[2].NbVal = "$Arg1.NbVal";
  /* le sample (mais pas l'unite) se deduit de l'entree  */
  optr->Arg_Car[2].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[2].sample = "$Arg1.sample";
  optr->Arg_Car[2].ref_time = "$Arg1.ref_time";
  optr->Arg_Car[2].misval = "$Arg1.misval";
  optr->Arg_Car[2].unite = "$Arg2.unit";
  optr->Arg_Car[2].famille = "$Arg1.famille";

  /* V */
  optr->Arg_Car[3].direction = DIR_OUT;
  optr->Arg_Car[3].categorie = VECTOR;
  optr->Arg_Car[3].typ = ATYC_IF32;
  optr->Arg_Car[3].array_dim = "1";
  optr->Arg_Car[3].NbVal = "$Arg1.NbVal";
  /* l'unite et le sample se deduisent de l'entree  */
  optr->Arg_Car[3].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[3].sample = "$Arg1.sample";
  optr->Arg_Car[3].ref_time = "$Arg1.ref_time";
  optr->Arg_Car[3].misval = "$Arg1.misval";
  optr->Arg_Car[3].unite = "$Arg2.unit";
  optr->Arg_Car[3].famille = "$Arg1.famille";

}
