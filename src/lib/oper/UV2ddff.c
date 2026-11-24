/*****************************************************
*
* OPERATOR         UV2ddff.c   FUNCTION  ANSI-C
*
* PURPOSE          Convert Cartesian coordinates to polar.
*
* DESCRIPTION      Converts coordinates of a vector expressed in
*                  a Earth-related cartesians "repere" to the polar
*                  referential used for meteorological winds, 
*                  with angles counting from North and corresponding 
*                  to the origin of the wind.
*
* VERSION          $Revision$
*
* ARGUMENTS  IN    float    U   any           East component, from West
*            IN    float    V   same as U     North component, from South
*            OUT   float    DD  degree        Direction FROM where the vector
*                                             points (0=North)
*            OUT   float    FF  same as U, V  Module of the vector
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
UV2ddff (unsigned long NLoop,
	 const float *U,
	 const float *V,
	 float *DD,
	 float *FF)
{
  unsigned long i;

  for (i = 0; i < NLoop; i++)
    {
      *FF = sqrt (*U * *U + *V * *V);
      if (*V == 0.0)
	{
	  if (*U == 0.0)
	    *DD = 0.0;
	  else if (*U > 0.0)
	    *DD = -M_PI / 2.;
	  else
	    *DD = M_PI / 2.;
	}
      else if (*V > 0.0)
	{
	  *DD = atan (*U / *V) + M_PI;
	}
      else
	{
	  *DD = atan (*U / *V);
	}

      /* Passage de [-PI:PI]  a  [0:2*PI]  */

      if (*DD < 0.0)
	*DD += 2.0 * M_PI;

      /* Puis conversion en degres  */

      *DD = *DD * 180.0 / M_PI;

      U++;
      V++;
      DD++;
      FF++;
    }
  return;
}


/* la fonction d'enrobage classique */
int
OP_UV2ddff (unsigned long NbVal, void *ArgList[], char *DiagExec)
{
  (void) sprintf (DiagExec, "UV2ddff, NbVal=%lu", NbVal);

  UV2ddff (NbVal,
	   (float *) ArgList[0],
	   (float *) ArgList[1],
	   (float *) ArgList[2],
	   (float *) ArgList[3]);
  return OP_OK;
}

void
ID_UV2ddff (oper * optr)
{
  strcpy (optr->Nom, "UV2ddff");
  optr->Version = "$Revision$";
  optr->Date = "$Date$";
  optr->fctptr = OP_UV2ddff;
  optr->misval_auto = 1;	/* gestion auto des misval */
  optr->NbArg = 4;

/*  Pour l'instant, les specifications d'unites sont
 * approximatives. L'ideal serait : Arg1.unit = "m/s OR kt" et
 * Arg2.unit = "$Arg1.unit". Helas; l'interpreteur actuel ne sait
 * pas gérer ça.     */

  /* U */
  optr->Arg_Car[0].direction = DIR_IN;
  optr->Arg_Car[0].categorie = VECTOR;
  optr->Arg_Car[0].typ = ATYC_IF32;
  optr->Arg_Car[0].array_dim = "1";
  optr->Arg_Car[0].type_sample = "any";
  optr->Arg_Car[0].sample = "any";
  optr->Arg_Car[0].unite = "m/s";

  /* V */
  optr->Arg_Car[1].direction = DIR_IN;
  optr->Arg_Car[1].categorie = VECTOR;
  optr->Arg_Car[1].typ = ATYC_IF32;
  optr->Arg_Car[1].array_dim = "1";
  optr->Arg_Car[1].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[1].type_sample = "any";
  optr->Arg_Car[1].sample = "any";
  optr->Arg_Car[1].unite = "$Arg1.unit";

  /* DD */
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
  optr->Arg_Car[2].unite = "degree";
  optr->Arg_Car[2].famille = "$Arg1.famille";
  optr->Arg_Car[2].name = " \"Direction du vent\" ";
  optr->Arg_Car[2].en_name = " \"Wind direction\" ";

  /* FF */
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
  optr->Arg_Car[3].unite = "$Arg1.unit";
  optr->Arg_Car[3].famille = "$Arg1.famille";
  optr->Arg_Car[3].name = " \"Vitesse du vent\" ";
  optr->Arg_Car[3].en_name = " \"Wind speed\" ";

}
