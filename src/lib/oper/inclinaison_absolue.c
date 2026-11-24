/*************************************************************************
*
* OPERATOR         inclinaison_absolue.c FUNCTION ANSI-C
*
* PURPOSE          Donne l'inclinaison en valeur absolue d'un mobile par
*                  rapport à la verticale.
*
* DESCRIPTION      Calcule l'inclinaison absolue du bateau en des valeurs de
* 		   roulis et tangage selon la formule:
*		   inclinaison_absolue = atan ( sqrt( (tan(roulis)**2) + (tan(tangage)**2) )
*	  	    	
*
*
* VERSION          1.0 
*
* ARGUMENTS  
*            IN   float   vect1	 degre ou rd   vecteur roulis
*            IN   float   vect2  degre ou rd   vecteur tangage
*            IN   string  unit   degre ou rd   unité des angles
*
*            OUT  float   vect3  degre ou rd   vecteur inclinaison_absolue
*            
*            
*
* ENTRY        NONE
*        
* SUBPROGRAMS  NONE
*        
* REFERENCES   
*
* COPYRIGHT    Meteo-France
*	       Centre National de Recherches Meteorologiques 
*	       GMEI/ TRAMM
*	       42, av G. Coriolis
*	       31057 TOULOUSE cedex  
*
*
*############################################################################*/

#define _POSIX_SOURCE 1
#define _XOPEN_SOURCE 600
#define _HPUX_SOURCE 1

#include <math.h>
#include <stdio.h>
#include <string.h>
#include <math.h>

#include "struct_oper.h"
#include "unit_def.h"
#include "unit.h"

int
inclinaison_absolue (unsigned long ndata,
		     const float *vect1,
		     const float *vect2, const char *unit, float *vect3)
{
  unsigned long i;
  double D_to_R;
  double tan1, tan2;
  double arctan;
  int Flag_unit;

  Flag_unit = reconnait_deg_rad (unit);

  switch (Flag_unit)
    {
    case UNIT_IS_DEGREE:
      D_to_R = M_PI / 180.0;
      break;
    case UNIT_IS_RADIAN:
      D_to_R = 1.0;
      break;
    default:
      Flag_unit = -1;
      return -1;
    }

  for (i = 0; i < ndata; i++)
    {
      vect3[i] = K_NaN;
      if (!isfinite (vect1[i]) || !isfinite (vect2[i]))
	continue;
      tan1 = tan (D_to_R * vect1[i]);
      tan2 = tan (D_to_R * vect2[i]);
      arctan = atan (sqrt (pow (tan1, 2) + pow (tan2, 2)));
      vect3[i] = (float) arctan / D_to_R;
    }

  return Flag_unit;
}


/* la fonction d'enrobage classique */

int
OP_inclinaison_absolue (unsigned long NbVal, void *ArgList[], char *DiagExec)
{
  int CodRet;
  sprintf (DiagExec, "inclinaison_absolue, Nb_ech = %lu, unite indiquee = %s",
	   NbVal, (char *) ArgList[2]);
  CodRet =
    inclinaison_absolue (NbVal, (float *) ArgList[0], (float *) ArgList[1],
			 (char *) ArgList[2], (float *) ArgList[3]);
  switch (CodRet)
    {
    case UNIT_IS_DEGREE:
      strcat (DiagExec, "Angles passés en degrés");
      break;
    case UNIT_IS_RADIAN:
      strcat (DiagExec, "Angles passés en radians");
      break;
    default:
      strcat (DiagExec, "Unite d'angle non reconnue");
      return OP_FAIL;
    }
  return OP_OK;
}

void
ID_inclinaison_absolue (oper * optr)
{
  strcpy (optr->Nom, "inclinaison_absolue");
  optr->Date = "$Date$";
  optr->Version = "$Revision$";
  optr->fctptr = OP_inclinaison_absolue;
  optr->NbArg = 4;		/* doit rester inf. a FIL_MAX_ARG */

  /* vect1 */
  optr->Arg_Car[0].direction = DIR_IN;
  optr->Arg_Car[0].categorie = VECTOR;
  optr->Arg_Car[0].typ = ATYC_IF32;
  optr->Arg_Car[0].array_dim = "1";
  optr->Arg_Car[0].type_sample = "any";
  optr->Arg_Car[0].sample = "any";
  optr->Arg_Car[0].unite = "any";

  /* vect2 */
  optr->Arg_Car[1].direction = DIR_IN;
  optr->Arg_Car[1].categorie = VECTOR;
  optr->Arg_Car[1].typ = ATYC_IF32;
  optr->Arg_Car[1].array_dim = "1";
  optr->Arg_Car[1].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[1].type_sample = "any";
  optr->Arg_Car[1].sample = "any";
  optr->Arg_Car[1].unite = "any";

  /* unit */
  optr->Arg_Car[2].direction = DIR_IN;
  optr->Arg_Car[2].categorie = COEFFICIENT;
  optr->Arg_Car[2].typ = ATYC_STRING;
  optr->Arg_Car[2].array_dim = "1";
  optr->Arg_Car[2].type_sample = NULL;
  optr->Arg_Car[2].sample = NULL;
  optr->Arg_Car[2].unite = "";

  /* vect3 */
  optr->Arg_Car[3].direction = DIR_OUT;
  optr->Arg_Car[3].categorie = VECTOR;
  optr->Arg_Car[3].typ = ATYC_IF32;
  optr->Arg_Car[3].array_dim = "1";
  optr->Arg_Car[3].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[3].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[3].sample = "$Arg1.sample";
  optr->Arg_Car[3].ref_time = "$Arg1.ref_time";
  optr->Arg_Car[3].unite = "$Arg1.unit";
  optr->Arg_Car[3].misval = "$Arg1.misval";
}
