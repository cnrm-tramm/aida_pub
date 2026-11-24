/*****************************************************
*
* OPERATOR         Geo2mobile_2D.c   FUNCTION  ANSI-C
*
* PURPOSE          rotates geographic coordinates to mobile-born coordinates
*
* DESCRIPTION      Converts coordinates of a vector expressed in
*                  a Earth-related cartesians "repere" to a mobile
*                  referential, according to its heading.
*
* VERSION          1.1
*
* ARGUMENTS  IN    float   X_e  any           East component, from West
*            IN    float   X_n  same as X_e   North component, from South
*            IN    float   Cap  degree        Heading of the mobile, 
*                                               (0=Northward, 90=Eastward)
*            OUT   float   Y_t  same as X_e   Component transverse to
*                                             mobile axe (>0 to the right)
*            OUT   float   Y_l  same as X_e   Component along mobile axe
*                                             (Positif forward)
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
* CHANGES          1.1  Initial version
*
* COPYRIGHT        Meteo-France/CNRM
*
* AGREEMENT        
*########################################################################*/

#define _POSIX_SOURCE 1
#define _XOPEN_SOURCE 600

#include <math.h>
#include <stdio.h>
#include <string.h>
#include "struct_oper.h"


void
Geo2mobile_2D (unsigned long NLoop,
	   const float *X_e,
	   const float *X_n,
	   const float *Cap,
	   float *Y_t,
	   float *Y_l)
{
  unsigned long i;
  register double coca, sica;
  register double Deg2Rad = M_PI / 180.0;
  register double Cap_rad;

  for (i = 0; i < NLoop; i++)
    {
      Cap_rad = *Cap * Deg2Rad;
      coca = cos (Cap_rad);
      sica = sin (Cap_rad);

      *Y_t = coca * *X_e - sica * *X_n;
      *Y_l = sica * *X_e + coca * *X_n;

      X_e++;
      X_n++;
      Cap++;
      Y_l++;
      Y_t++;
    }
}


/* la fonction d'enrobage classique */

int
OP_Geo2mobile_2D (unsigned long NbVal, void *ArgList[], char *DiagExec)
{

  (void) sprintf (DiagExec, "Geo2mobile_2D, Nb ech =%lu", NbVal);

  Geo2mobile_2D (NbVal,
		      (float *) ArgList[0],
		      (float *) ArgList[1],
		      (float *) ArgList[2],
		      (float *) ArgList[3],
		      (float *) ArgList[4]);
  return OP_OK;
}

void
ID_Geo2mobile_2D (oper * optr)
{
  strcpy (optr->Nom, "Geo2mobile_2D");
  optr->Version = "$Revision$";
  optr->Date = "$Date$";
  optr->fctptr = OP_Geo2mobile_2D;
  optr->NbArg = 5;

  /* X_e */
  optr->Arg_Car[0].direction = DIR_IN;
  optr->Arg_Car[0].categorie = VECTOR;
  optr->Arg_Car[0].typ = ATYC_IF32;
  optr->Arg_Car[0].array_dim = "1";
  optr->Arg_Car[0].type_sample = "any";
  optr->Arg_Car[0].sample = "any";
  optr->Arg_Car[0].unite = "any";
  optr->Arg_Car[0].famille = "any";

  /* X_n */
  optr->Arg_Car[1].direction = DIR_IN;
  optr->Arg_Car[1].categorie = VECTOR;
  optr->Arg_Car[1].typ = ATYC_IF32;
  optr->Arg_Car[1].array_dim = "1";
  optr->Arg_Car[1].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[1].type_sample = "any";
  optr->Arg_Car[1].sample = "any";
  optr->Arg_Car[1].unite = "$Arg1.unit";
  optr->Arg_Car[1].famille = "any";

  /* Cap */
  optr->Arg_Car[2].direction = DIR_IN;
  optr->Arg_Car[2].categorie = VECTOR;
  optr->Arg_Car[2].typ = ATYC_IF32;
  optr->Arg_Car[2].array_dim = "1";
  optr->Arg_Car[2].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[2].type_sample = "any";
  optr->Arg_Car[2].sample = "any";
  optr->Arg_Car[2].unite = "degree";
  optr->Arg_Car[2].famille = "any";

  /* Y_t */
  optr->Arg_Car[3].direction = DIR_OUT;
  optr->Arg_Car[3].categorie = VECTOR;
  optr->Arg_Car[3].typ = ATYC_IF32;
  optr->Arg_Car[3].array_dim = "1";
  optr->Arg_Car[3].NbVal = "$Arg1.NbVal";
  /* le sample (mais pas l'unite) se deduit de l'entree  */
  optr->Arg_Car[3].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[3].sample = "$Arg1.sample";
  optr->Arg_Car[3].ref_time = "$Arg1.ref_time";
  optr->Arg_Car[3].unite = "$Arg1.unit";
  optr->Arg_Car[3].famille = "$Arg1.famille";

  /* Y_l */
  optr->Arg_Car[4].direction = DIR_OUT;
  optr->Arg_Car[4].categorie = VECTOR;
  optr->Arg_Car[4].typ = ATYC_IF32;
  optr->Arg_Car[4].array_dim = "1";
  optr->Arg_Car[4].NbVal = "$Arg1.NbVal";
  /* l'unite et le sample se deduisent de l'entree  */
  optr->Arg_Car[4].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[4].sample = "$Arg1.sample";
  optr->Arg_Car[4].ref_time = "$Arg1.ref_time";
  optr->Arg_Car[4].unite = "$Arg1.unit";
  optr->Arg_Car[4].famille = "$Arg1.famille";

}
