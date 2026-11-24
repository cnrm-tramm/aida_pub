/*****************************************************
*
* OPERATOR         Rotat_horiz_auto.c   FUNCTION  ANSI-C
*
* PURPOSE          Rotates geographic coordinates to mobile-born coordinates
*
* DESCRIPTION      Converts coordinates of a vector expressed in
*                  a Earth-related cartesians "repere" to a mobile
*                  referential, according to its heading.
*
* VERSION          1.1
*
* ARGUMENTS  IN    float   X_e  any           East component, from West
*            IN    float   X_n  same as X_e   North component, from South
*            IN    float   Cap  degree ou radian       Heading of the mobile, 
*                                               (0=Northward, 90=Eastward)
*            IN    char*   unit "Radian" ou "Degre"  Unité de mesure des angles 
*            IN    float   flag  1.0 ou -1.0   1.0 pour geo2mobile
*                                             -1.0 pour mobile2geo
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
#include "unit_def.h"


int
Rotat_horiz_auto (unsigned long NLoop,
	   const float *X_e,
	   const float *X_n,
	   const float *Cap,
	   const char  *unit, 
	   const float flag,
	   float *Y_t,
	   float *Y_l)
{
  unsigned long i;
  register double coca, sica;
  register double Deg2Rad;
  register double Cap_rad;
  int Flag_unit;

  if (flag != 1.0 && flag != -1.0)
    return -1;

  Flag_unit = reconnait_deg_rad (unit);
  switch (Flag_unit)
    {
    case UNIT_IS_RADIAN:
      Deg2Rad = 1.0;
      break;
    case UNIT_IS_DEGREE:
      Deg2Rad = flag * M_PI / 180.0;
      break;
    default:
      return -1;
    }

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
  return Flag_unit;
}


/* la fonction d'enrobage classique */

int
OP_Rotat_horiz_auto (unsigned long NbVal, void *ArgList[], char *DiagExec)
{
  int CodRet;

  (void) sprintf (DiagExec,
		  "Rotat_horiz_auto, NbVal=%lu, Angles en %s, flag = %g (%s))",
		  NbVal,
		  (char *) ArgList[3],
		  *(float *) ArgList[4],
		  (*(float *) ArgList[4] == 1.0 ? 
                         "geo vers mobile" : "mobile vers geo"));

  CodRet = Rotat_horiz_auto (NbVal,
			     (float *) ArgList[0],
			     (float *) ArgList[1],
			     (float *) ArgList[2],
			     (char *) ArgList[3],
			     *(float *) ArgList[4],
			     (float *) ArgList[5],
                 (float *) ArgList[6]);

  switch (CodRet)
    {
    case UNIT_IS_DEGREE:
      strcat (DiagExec, "Cap passés en degrés");
      break;
    case UNIT_IS_RADIAN:
      strcat (DiagExec, "Cap passés en radians");
      break;
    default:
      strcat (DiagExec,
	      "Unite d'angle de cap non reconnue ou sens de transformation non défini");
      return OP_FAIL;
    }

  return OP_OK;
}

void
ID_Rotat_horiz_auto (oper * optr)
{
  strcpy (optr->Nom, "Rotat_horiz_auto");
  optr->Version = "1.4";
  optr->Date = "$Date: 2015-08-17 13:59:12 +0200 (lun. 17 oct. 2015) $";
  optr->fctptr = OP_Rotat_horiz_auto;
  optr->NbArg = 7;

  /* X_e */
/*   Pour l'instant, les specifications d'unites et de sample sont
 * approximatives. L'ideal serait : Arg1.unit = "m/s OR kt".
 * Helas, l'interpreteur actuel ne sait pas gérer ça.  */
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
  optr->Arg_Car[2].unite = "any";
  optr->Arg_Car[2].famille = "any";

  /* unit */
  optr->Arg_Car[3].direction = DIR_IN;
  optr->Arg_Car[3].categorie = COEFFICIENT;
  optr->Arg_Car[3].typ = ATYC_STRING;
  optr->Arg_Car[3].array_dim = "1";
  optr->Arg_Car[3].type_sample = NULL;
  optr->Arg_Car[3].sample = NULL;
  optr->Arg_Car[3].unite = "";

  /* flag */
  optr->Arg_Car[4].direction = DIR_IN;
  optr->Arg_Car[4].categorie = COEFFICIENT;
  optr->Arg_Car[4].typ = ATYC_IF32;
  optr->Arg_Car[4].array_dim = "1";
  optr->Arg_Car[4].type_sample = NULL;
  optr->Arg_Car[4].sample = NULL;
  optr->Arg_Car[4].unite = "";

  /* Y_t */
  optr->Arg_Car[5].direction = DIR_OUT;
  optr->Arg_Car[5].categorie = VECTOR;
  optr->Arg_Car[5].typ = ATYC_IF32;
  optr->Arg_Car[5].array_dim = "1";
  optr->Arg_Car[5].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[5].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[5].sample = "$Arg1.sample";
  optr->Arg_Car[5].ref_time = "$Arg1.ref_time";
  optr->Arg_Car[5].unite = "$Arg1.unit";
  optr->Arg_Car[5].famille = "$Arg1.famille";
  optr->Arg_Car[5].misval = "$Arg1.misval";

  /* Y_l */
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
  optr->Arg_Car[6].misval = "$Arg1.misval";

}
