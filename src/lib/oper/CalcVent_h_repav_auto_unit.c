/*************************************************************************
*
* OPERATOR         CalcVent_h_repav_auto_unit.c  FUNCTION ANSI-C
*
* PURPOSE          approximate computation of horizontal wind 
*
* DESCRIPTION 
*
* Ce programme calcule le vent horizontal simplifie dans 
* le repère géographique terrestre.
*
* Les composantes de la vitesse du mobile par rapport au sol
* doivent être données dans le repère avion (cas du doppler).
*
* This procedure computes the approximate horizontal
* wind with respect to the earth frame.
* 
* The velocity of the aircraft must be given with respect to the
* aircraft frame.
*
*     
* VERSION          1.4 
*
* ARGUMENTS  
*	     IN   float*   ff_ap  ms ou kt            Vitesse du vent apparent const char *unit   
*            IN   float*   dd_ap  rad ou degré         Direction du vent apparent (positive quand le vent apparent vient de la droite)
*            IN   float*   cap	  rad ou degré         Cap de l'avion ou du navire
*            IN   char*    unit   "Radian" ou "Degre"  Unité de mesure des angles 
*            IN   float*   Vx     ms ou kt            Vitesse du mobile par rapport au sol selon l'axe longitudinal de l'avion
*						       (>0 vers l'avant)
*            IN   float*   Vy     ms ou kt            Vitesse du mobile par rapport au sol selon l'axe transversal de l'avion 
*						       (>0 de babord à tribord)	
*            OUT  float*   U	  ms ou kt            Vent vrai composante Est venant de l'Ouest
*            OUT  float*   V      ms ou kt            Vent vrai composante Nord venant du Sud
*	   
*          NOTA les unités doivent rester homogènes  
*        
* ENTRY        NONE
*        
* SUBPROGRAMS  NONE
*
* FILES        NONE
*        
* REFERENCES   Measurements techniques: air motion sensing
*	       D. H. Lenschow and P. Spyers-Duran
*	       NCAR/RAF  bulletin no. 23, 1987 
*
* CHANGES       
*	 
*
* COPYRIGHT    Meteo-France
*	       Centre National de Recherches Meteorologiques 
*	       GMEI/ MMA
*	       42, av G. Coriolis
*	       31057 TOULOUSE cedex  
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
#include <strings.h>
#include "struct_oper.h"

int
CalcVent_h_repav_auto_unit (unsigned long NLoop,
			    const float *ff_ap,
			    const float *dd_ap,
			    const float *cap,
			    const char *unit,
			    const float *Vx,
			    const float *Vy, float *U, float *V)
{
  unsigned long i;
  double U_l, U_t;
  double scap, ccap;
  double D_to_R;
  int Flag_unit;

  if (!strcasecmp (unit, "degree") || !strcasecmp (unit, "Degree")
      || !strcasecmp (unit, "Degre") || !strcasecmp (unit, "degre"))
    {
      D_to_R = M_PI / 180.0;
      Flag_unit = 1;
    }
  else if (!strcasecmp (unit, "rad") || !strcasecmp (unit, "Rad")
	   || !strcasecmp (unit, "Radian") || !strcasecmp (unit, "radian"))
    {
      D_to_R = 1.0;
      Flag_unit = 0;
    }
  else
    {
      Flag_unit = -1;
      return -1;
    }

  for (i = 0; i < NLoop; i++)
    {
      scap = sin (D_to_R * (*cap));
      ccap = cos (D_to_R * (*cap));

      U_l = *Vx - *ff_ap * cos (D_to_R * (*dd_ap));
      U_t = *Vy - *ff_ap * sin (D_to_R * (*dd_ap));

      *U = U_l * scap + U_t * ccap;
      *V = U_l * ccap - U_t * scap;

      ff_ap++;
      dd_ap++;
      cap++;
      Vx++;
      Vy++;

      U++;
      V++;
    }
  return (Flag_unit);
}


/* la fonction d'enrobage classique */

int
OP_CalcVent_h_repav_auto_unit (unsigned long NbVal, void *ArgList[],
			       char *DiagExec)
{
  int CodRet;

  CodRet = CalcVent_h_repav_auto_unit (NbVal,
				       (float *) ArgList[0],
				       (float *) ArgList[1],
				       (float *) ArgList[2],
				       (char *) ArgList[3],
				       (float *) ArgList[4],
				       (float *) ArgList[5],
				       (float *) ArgList[6],
				       (float *) ArgList[7]);
  switch (CodRet)
    {
    case 1:
      strcat (DiagExec, "Angles passés en degrés");
      break;
    case 0:
      strcat (DiagExec, "Angles passés en radians");
      break;
    default:
      strcat (DiagExec, "Unite d'angle non reconnue");
      return OP_FAIL;
    }
  return OP_OK;
}

void
ID_CalcVent_h_repav_auto_unit (oper * optr)
{
  strcpy (optr->Nom, "CalcVent_h_repav_auto_unit");
  optr->Version = "$Revision$";
  optr->Date = "$Date$";
  optr->fctptr = OP_CalcVent_h_repav_auto_unit;
  optr->NbArg = 8;		/* doit rester inf. a FIL_MAX_ARG */

  /* ff_ap */
  optr->Arg_Car[0].direction = DIR_IN;
  optr->Arg_Car[0].categorie = VECTOR;
  optr->Arg_Car[0].typ = ATYC_IF32;
  optr->Arg_Car[0].array_dim = "1";
  optr->Arg_Car[0].type_sample = "any";
  optr->Arg_Car[0].sample = "any";
  optr->Arg_Car[0].unite = "any";

  /* dd_ap */
  optr->Arg_Car[1].direction = DIR_IN;
  optr->Arg_Car[1].categorie = VECTOR;
  optr->Arg_Car[1].typ = ATYC_IF32;
  optr->Arg_Car[1].array_dim = "1";
  optr->Arg_Car[1].type_sample = "any";
  optr->Arg_Car[1].sample = "any";
  optr->Arg_Car[1].unite = "any";

  optr->Arg_Car[2].direction = DIR_IN;
  optr->Arg_Car[2].categorie = VECTOR;
  optr->Arg_Car[2].typ = ATYC_IF32;
  optr->Arg_Car[2].array_dim = "1";
  optr->Arg_Car[2].type_sample = "any";
  optr->Arg_Car[2].sample = "any";
  optr->Arg_Car[2].unite = "any";

  optr->Arg_Car[3].direction = DIR_IN;
  optr->Arg_Car[3].categorie = COEFFICIENT;
  optr->Arg_Car[3].typ = ATYC_STRING;
  optr->Arg_Car[3].array_dim = "1";
  optr->Arg_Car[3].type_sample = NULL;
  optr->Arg_Car[3].sample = NULL;
  optr->Arg_Car[3].unite = "";

  optr->Arg_Car[4].direction = DIR_IN;
  optr->Arg_Car[4].categorie = VECTOR;
  optr->Arg_Car[4].typ = ATYC_IF32;
  optr->Arg_Car[4].array_dim = "1";
  optr->Arg_Car[4].type_sample = "any";
  optr->Arg_Car[4].sample = "any";
  optr->Arg_Car[4].unite = "any";

  optr->Arg_Car[5].direction = DIR_IN;
  optr->Arg_Car[5].categorie = VECTOR;
  optr->Arg_Car[5].typ = ATYC_IF32;
  optr->Arg_Car[5].array_dim = "1";
  optr->Arg_Car[5].type_sample = "any";
  optr->Arg_Car[5].sample = "any";
  optr->Arg_Car[5].unite = "any";

  optr->Arg_Car[6].direction = DIR_OUT;
  optr->Arg_Car[6].categorie = VECTOR;
  optr->Arg_Car[6].typ = ATYC_IF32;
  optr->Arg_Car[6].array_dim = "1";
  optr->Arg_Car[6].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[6].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[6].sample = "$Arg1.sample";
  optr->Arg_Car[6].ref_time = "$Arg1.ref_time";
  optr->Arg_Car[6].unite = "$Arg1.unit";
  optr->Arg_Car[6].misval = "$Arg1.misval";

  optr->Arg_Car[7].direction = DIR_OUT;
  optr->Arg_Car[7].categorie = VECTOR;
  optr->Arg_Car[7].typ = ATYC_IF32;
  optr->Arg_Car[7].array_dim = "1";
  optr->Arg_Car[7].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[7].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[7].sample = "$Arg1.sample";
  optr->Arg_Car[7].ref_time = "$Arg1.ref_time";
  optr->Arg_Car[7].unite = "$Arg1.unit";
  optr->Arg_Car[7].misval = "$Arg1.misval";


}
