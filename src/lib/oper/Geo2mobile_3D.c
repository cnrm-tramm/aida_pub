/*****************************************************
*
* OPERATOR         Geo2mobile_3D.c   FUNCTION  ANSI-C
*
* PURPOSE          rotates geographic coordinates to mobile platform coordinates
*
* DESCRIPTION      Converst coordinates of a 3D-vector expressed in
*                  a Earth-related cartesians "repere" to a mobile platform
*                  referential, according to its heading, roll and pitch.
*
* VERSION          1.1
*
* ARGUMENTS  IN    float   X_e  any           East component, from West
*            IN    float   X_n  same as X_e   North component, from South
*	     IN	   float   X_v  same as X_e   Vertical component, from ground
*            IN    float   Cap  degree        Heading of the platform, 
*                                               (0=Northward, 90=Eastward)
*	     IN	   float   Roul degree        Roll of the platform
*	     IN    float   Tang degree        Pitch of the platform
*            OUT   float   Y_l  same as X_e   Component along platform axe
*                                             (Positif forward)
*            OUT   float   Y_t  same as X_e   Component transverse to
*                                             platform axe (>0 to the right)
*            OUT   float   Y_v  same as X_e   Component along platform vertical 
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
Geo2mobile_3D (unsigned long NLoop,
	   const float *X_e,
	   const float *X_n,
	   const float *X_v,
	   const float *Cap,
	   const float *Roul,
	   const float *Tang,
	   float *Y_l,
	   float *Y_t,
	   float *Y_v)
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

      *Y_l = cota * sica * (*X_e) + cota * coca * (*X_n) + sita * (*X_v);

      *Y_t = (siro * sita * sica + coro * coca) * (*X_e) +
	(siro * sita * coca - coro * sica) * (*X_n) - siro * cota * (*X_v);

      *Y_v = (coro * sita * sica - siro * coca) * (*X_e) +
	(coro * sita * coca + siro * sica) * (*X_n) - coro * cota * (*X_v);


      X_e++;
      X_n++;
      X_v++;
      Cap++;
      Roul++;
      Tang++;
      Y_l++;
      Y_t++;
      Y_v++;
    }
}


/* la fonction d'enrobage classique */

int
OP_Geo2mobile_3D (unsigned long NbVal, void *ArgList[], char *DiagExec)
{

  (void) sprintf (DiagExec, "Geo2mobile_3D, %lu echant.", NbVal);

  Geo2mobile_3D (NbVal,
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
ID_Geo2mobile_3D (oper * optr)
{
  strcpy (optr->Nom, "Geo2mobile_3D");
  optr->Version = "$Revision$";
  optr->Date = "$Date$";
  optr->fctptr = OP_Geo2mobile_3D;
  optr->NbArg = 9;

  /* X_e */
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

  optr->Arg_Car[6].direction = DIR_OUT;
  optr->Arg_Car[6].categorie = VECTOR;
  optr->Arg_Car[6].typ = ATYC_IF32;
  optr->Arg_Car[6].array_dim = "1";
  optr->Arg_Car[6].NbVal = "$Arg1.NbVal";
  /* le sample (mais pas l'unite) se deduit de l'entree  */
  optr->Arg_Car[6].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[6].sample = "$Arg1.sample";
  optr->Arg_Car[6].ref_time = "$Arg1.ref_time";
  optr->Arg_Car[6].unite = "$Arg1.unit";
  optr->Arg_Car[6].famille = "$Arg1.famille";

  optr->Arg_Car[7].direction = DIR_OUT;
  optr->Arg_Car[7].categorie = VECTOR;
  optr->Arg_Car[7].typ = ATYC_IF32;
  optr->Arg_Car[7].array_dim = "1";
  optr->Arg_Car[7].NbVal = "$Arg1.NbVal";
  /* l'unite et le sample se deduisent de l'entree  */
  optr->Arg_Car[7].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[7].sample = "$Arg1.sample";
  optr->Arg_Car[7].ref_time = "$Arg1.ref_time";
  optr->Arg_Car[7].unite = "$Arg1.unit";
  optr->Arg_Car[7].famille = "$Arg1.famille";


  optr->Arg_Car[8].direction = DIR_OUT;
  optr->Arg_Car[8].categorie = VECTOR;
  optr->Arg_Car[8].typ = ATYC_IF32;
  optr->Arg_Car[8].array_dim = "1";
  optr->Arg_Car[8].NbVal = "$Arg1.NbVal";
  /* l'unite et le sample se deduisent de l'entree  */
  optr->Arg_Car[8].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[8].sample = "$Arg1.sample";
  optr->Arg_Car[8].ref_time = "$Arg1.ref_time";
  optr->Arg_Car[8].unite = "$Arg1.unit";
  optr->Arg_Car[8].famille = "$Arg1.famille";

}
