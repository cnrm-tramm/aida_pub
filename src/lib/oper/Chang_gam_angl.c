/*************************************************************************
*
* OPERATOR         Chang_gam_angl.c  FUNCTION ANSI-C
*
* PURPOSE          Changement de gamme de mesure d'angle afin de pouvoir comparer 
*                  différents vecteurs par exemple par des "plotxy"
*
* DESCRIPTION 
*
*                  Ce programme permet de transformer une mesure d'angle faite de 0° à 360° (ou
*                  de 0 rd à 2*PI rd) en une mesure de -180° à +180 (ou -PI rd à +PI rd) et
*                  réciproquement.
* 
*
* VERSION          1.0 
*
* ARGUMENTS  
*            IN   float*   V   rad ou degré   Vecteur contenant des mesures d'angle      
*            IN   char*    unit   "Radian" ou "Degre"  Unité de mesure des angles 
*            IN   float    gam    180 ou 360           
*            OUT  float*   Vs   rad ou degré   Vecteur contenant les angles transformés
*  
* REFERENCES   
*
* CHANGES       
*	 
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
/* Le #define _HPUX_SOURCE n'est la que pour "voir" strdup */
#define _HPUX_SOURCE 1
#define _XOPEN_SOURCE_EXTENDED 1

#include <math.h>
#include <stdio.h>
#include <string.h>

#include "struct_oper.h"
#include "unit_def.h"
#include "unit.h"


int
Chang_gam_angl (unsigned long NLoop,
		const float *V, const char *unit, const float gam, float *Vs)
{
  unsigned long i;
  double Chang_gam;
  float borne_min, borne_max;
  int Flag_unit;

  Flag_unit = reconnait_deg_rad (unit);

  if (Flag_unit == UNIT_IS_DEGREE)
    Chang_gam = 360.0;
  else if (Flag_unit == UNIT_IS_RADIAN)
    Chang_gam = 2 * M_PI;
  else
    return -1;

  if (gam == 360.0)
    {
      borne_max = Chang_gam;
    }
  else if (gam == 180.0)
    {
      borne_max = Chang_gam / 2.0;
    }
  else
    {
      Flag_unit = -2;
      return Flag_unit;
    }

  borne_min = borne_max - Chang_gam;

  for (i = 0; i < NLoop; i++)
    {
      if (*V < borne_min)
	*Vs = *V + Chang_gam;
      else if (*V > borne_max)
	*Vs = *V - Chang_gam;
      else
	*Vs = *V;
      V++;
      Vs++;
    }

  return Flag_unit;
}


/* la fonction d'enrobage classique */

int
OP_Chang_gam_angl (unsigned long NbVal, void *ArgList[], char *DiagExec)
{
  int CodRet;

  sprintf (DiagExec, "Chang_gam_angl vers %s",
	   (*(float *) ArgList[2] > 180 ? "[-180:180]" : "[0:360]"));

  CodRet = Chang_gam_angl (NbVal,
			   (float *) ArgList[0],
			   (char *) ArgList[1],
			   *(float *) ArgList[2], (float *) ArgList[3]);
  switch (CodRet)
    {
    case 1:
      strcat (DiagExec, ", Angles passés en degrés");
      break;
    case 0:
      strcat (DiagExec, ", Angles passés en radians");
      break;
    case -2:
      strcat (DiagExec, ", Gamme non reconnue");
      return OP_FAIL;
    default:
      strcat (DiagExec, ", Unite d'angle non reconnue");
      return OP_FAIL;
    }
  return OP_OK;
}

void
ID_Chang_gam_angl (oper * optr)
{
  strcpy (optr->Nom, "Chang_gam_angl");
  optr->Version = "$Revision$";
  optr->Date = "$Date$";
  optr->fctptr = OP_Chang_gam_angl;
  optr->NbArg = 4;		/* doit rester inf. a FIL_MAX_ARG */

  /* V */
  optr->Arg_Car[0].direction = DIR_IN;
  optr->Arg_Car[0].categorie = VECTOR;
  optr->Arg_Car[0].typ = ATYC_IF32;
  optr->Arg_Car[0].array_dim = "1";
  optr->Arg_Car[0].type_sample = "any";
  optr->Arg_Car[0].sample = "any";
  optr->Arg_Car[0].unite = "any";

  /* unit */
  optr->Arg_Car[1].direction = DIR_IN;
  optr->Arg_Car[1].categorie = COEFFICIENT;
  optr->Arg_Car[1].typ = ATYC_STRING;
  optr->Arg_Car[1].array_dim = "1";
  optr->Arg_Car[1].unite = "";

  /*  gam       */
  optr->Arg_Car[2].direction = DIR_IN;
  optr->Arg_Car[2].categorie = COEFFICIENT;
  optr->Arg_Car[2].typ = ATYC_IF32;
  optr->Arg_Car[2].array_dim = "1";
  optr->Arg_Car[2].unite = "";

  /* Vs */
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
  optr->Arg_Car[3].famille = "$Arg1.famille";
  optr->Arg_Car[3].name = "$Arg1.name";
  optr->Arg_Car[3].en_name = "$Arg1.english_name";
}
