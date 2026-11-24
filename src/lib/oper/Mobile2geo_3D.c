/*****************************************************
*
* OPERATOR         Mobile2geo_3D.c   FUNCTION  ANSI-C
*
* PURPOSE          rotates geographic coordinates to a mobile platform
*                  coordinates
*
* DESCRIPTION      Converst coordinates of a 3D-vector expressed in
*                  a Earth-related cartesians "repere" to a mobile platform
*                  referential, according to its heading, roll and pitch.
*
* VERSION          1.1
*
* ARGUMENTS  
*            IN   float   X_l  any           Component along the platform axe 
*                                             (Positif forward)
*            IN   float   X_t  same as X_l   Component transverse to the 
*                                             platform axe (>0 toward 
*                                             the right/starboard side)
*            IN   float   X_v  same as X_l   Component along "downward"
*                                             axe (>0 to the bottom)
*            IN    float   Cap  degree        Heading of the platform, 
*                                               (0=Northward, 90=Eastward)
*	     IN	   float   Roul degree        Roll angle of the platform
*	                                         (positive when right/starboard
*	                                         side is sunken)
*	     IN    float   Tang degree        Pitch angle of the platform
*	                                         (positive when the nose is risen)
*
*            OUT   float   X_e  same as X_l   East component, from West
*            OUT   float   X_n  same as X_l   North component, from South
*	     OUT   float   X_v  same as X_l   Vertical component, from ground
*                                             axe (>0 up)
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
Mobile2geo_3D (unsigned long NLoop,
	       const float *X_l,
	       const float *X_t,
	       const float *X_v,
	       const float *Cap,
	       const float *Roul,
	       const float *Tang, float *Y_e, float *Y_n, float *Y_v)
{
  unsigned long i;
  register double coca, sica, coro, siro, cota, sita;
  register double Deg2Rad = M_PI / 180.0;
  register double Cap_rad, Roul_rad, Tang_rad;


  for (i = 0; i < NLoop; i++)
    {
      Cap_rad = *Cap * Deg2Rad;
      Roul_rad = *Roul * Deg2Rad;
      Tang_rad = *Tang * Deg2Rad;

      coca = cos (Cap_rad);
      sica = sin (Cap_rad);

      coro = cos (Roul_rad);
      siro = sin (Roul_rad);

      cota = cos (Tang_rad);
      sita = sin (Tang_rad);

      *Y_e =
	(*X_l) * sica * cota + (*X_t) * (coca * coro + sica * sita * siro) +
	(*X_v) * (sica * sita * coro - coca * siro);

      *Y_n =
	(*X_l) * coca * cota - (*X_t) * (sica * coro - coca * sita * siro) +
	(*X_v) * (coca * sita * coro + sica * siro);

      *Y_v = (*X_l) * sita - (*X_t) * cota * siro - (*X_v) * cota * coro;

      X_l++;
      X_t++;
      X_v++;
      Cap++;
      Roul++;
      Tang++;
      Y_e++;
      Y_n++;
      Y_v++;
    }
}


/* la fonction d'enrobage classique */

int
OP_Mobile2geo_3D (unsigned long NbVal, void *ArgList[], char *DiagExec)
{

  (void) sprintf (DiagExec, "Mobile2geo_3D, NbVal=%lu", NbVal);

  Mobile2geo_3D (NbVal,
		 (float *) ArgList[0],
		 (float *) ArgList[1],
		 (float *) ArgList[2],
		 (float *) ArgList[3],
		 (float *) ArgList[4],
		 (float *) ArgList[5],
		 (float *) ArgList[6],
		 (float *) ArgList[7],
         (float *) ArgList[8]);
  return OP_OK;
}

void
ID_Mobile2geo_3D (oper * optr)
{
  strcpy (optr->Nom, "Mobile2geo_3D");
  optr->Version = "$Revision$";
  optr->Date = "$Date$";
  optr->fctptr = OP_Mobile2geo_3D;
  optr->NbArg = 9;

  /* X_l */
/*  Pour l'instant, les specifications d'unites et de sample sont
 * approximatives. L'ideal serait : Arg1.unit = "m/s OR kt"
 * Hélas, l'interpreteur actuel ne sait pas gérer ça.
 */
  optr->Arg_Car[0].direction = DIR_IN;
  optr->Arg_Car[0].categorie = VECTOR;
  optr->Arg_Car[0].typ = ATYC_IF32;
  optr->Arg_Car[0].array_dim = "1";
  optr->Arg_Car[0].type_sample = "any";
  optr->Arg_Car[0].sample = "any";
  optr->Arg_Car[0].unite = "any";
  optr->Arg_Car[0].famille = "any";

  /* X_t */
  optr->Arg_Car[1].direction = DIR_IN;
  optr->Arg_Car[1].categorie = VECTOR;
  optr->Arg_Car[1].typ = ATYC_IF32;
  optr->Arg_Car[1].array_dim = "1";
  optr->Arg_Car[1].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[1].type_sample = "any";
  optr->Arg_Car[1].sample = "any";
  optr->Arg_Car[1].unite = "$Arg1.unit";
  optr->Arg_Car[1].famille = "any";

  /* X_v */
  optr->Arg_Car[2].direction = DIR_IN;
  optr->Arg_Car[2].categorie = VECTOR;
  optr->Arg_Car[2].typ = ATYC_IF32;
  optr->Arg_Car[2].array_dim = "1";
  optr->Arg_Car[2].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[2].type_sample = "any";
  optr->Arg_Car[2].sample = "any";
  optr->Arg_Car[2].unite = "$Arg1.unit";
  optr->Arg_Car[2].famille = "any";

  /* Cap */
  optr->Arg_Car[3].direction = DIR_IN;
  optr->Arg_Car[3].categorie = VECTOR;
  optr->Arg_Car[3].typ = ATYC_IF32;
  optr->Arg_Car[3].array_dim = "1";
  optr->Arg_Car[3].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[3].type_sample = "any";
  optr->Arg_Car[3].sample = "any";
  optr->Arg_Car[3].unite = "degree";
  optr->Arg_Car[3].famille = "any";

  /* Roul */
  optr->Arg_Car[4].direction = DIR_IN;
  optr->Arg_Car[4].categorie = VECTOR;
  optr->Arg_Car[4].typ = ATYC_IF32;
  optr->Arg_Car[4].array_dim = "1";
  optr->Arg_Car[4].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[4].type_sample = "any";
  optr->Arg_Car[4].sample = "any";
  optr->Arg_Car[4].unite = "degree";
  optr->Arg_Car[4].famille = "any";

  /* Tang */
  optr->Arg_Car[5].direction = DIR_IN;
  optr->Arg_Car[5].categorie = VECTOR;
  optr->Arg_Car[5].typ = ATYC_IF32;
  optr->Arg_Car[5].array_dim = "1";
  optr->Arg_Car[5].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[5].type_sample = "any";
  optr->Arg_Car[5].sample = "any";
  optr->Arg_Car[5].unite = "degree";
  optr->Arg_Car[5].famille = "any";

  /* X_e */
  optr->Arg_Car[6].direction = DIR_OUT;
  optr->Arg_Car[6].categorie = VECTOR;
  optr->Arg_Car[6].typ = ATYC_IF32;
  optr->Arg_Car[6].array_dim = "1";
  optr->Arg_Car[6].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[6].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[6].sample = "$Arg1.sample";
  optr->Arg_Car[6].ref_time = "$Arg1.ref_time";
  optr->Arg_Car[6].unite = "$Arg1.unit";
  optr->Arg_Car[6].famille = "$Arg1.famille";

  /* X_n */
  optr->Arg_Car[7].direction = DIR_OUT;
  optr->Arg_Car[7].categorie = VECTOR;
  optr->Arg_Car[7].typ = ATYC_IF32;
  optr->Arg_Car[7].array_dim = "1";
  optr->Arg_Car[7].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[7].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[7].sample = "$Arg1.sample";
  optr->Arg_Car[7].ref_time = "$Arg1.ref_time";
  optr->Arg_Car[7].unite = "$Arg1.unit";
  optr->Arg_Car[7].famille = "$Arg1.famille";

  /* X_v */
  optr->Arg_Car[8].direction = DIR_OUT;
  optr->Arg_Car[8].categorie = VECTOR;
  optr->Arg_Car[8].typ = ATYC_IF32;
  optr->Arg_Car[8].array_dim = "1";
  optr->Arg_Car[8].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[8].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[8].sample = "$Arg1.sample";
  optr->Arg_Car[8].ref_time = "$Arg1.ref_time";
  optr->Arg_Car[8].unite = "$Arg1.unit";
  optr->Arg_Car[8].famille = "$Arg1.famille";
}
