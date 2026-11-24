/*************************************************************************
*
* OPERATOR         CalcVent_h_repav.c  FUNCTION ANSI-C
*
* PURPOSE          approximate computation of horizontal wind 
*
* DESCRIPTION 
*
* Ce programme calcule le vent horizontal simplifie dans 
* le repère géographique terrestre.
*
* Les composantes de la vitesse du mobile par rapport au sol
* doivent être données dans le repère lié au mobile (cas du doppler).
*
* This procedure computes the approximate horizontal
* wind with respect to the earth frame.
* 
* The velocity of the aircraft must be given with respect to the
* aircraft frame.
*
*
* VERSION          $Revision$
*
* ARGUMENTS  
*            IN   float   Vp     m/s    True Air Speed     
*            IN   float   Beta   rad   	Angle of Sideslip (positif when
                                        relative winds comes from the right)
*            IN   float   Psi	 rad	Heading
*            IN   float   Vx     m/s    Aircraft velocity along the 
*                                       platform lengthwise axe (>0 forward)
*            IN   float   Vy     m/s   	Aircraft velocity along the platform
*                                       transverse axe (>0 from left to right)
*            OUT  float*  U	 m/s	East component, from West 
*            OUT  float*  V      m/s	North component, from South
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

#include <math.h>
#include <stdio.h>
#include <string.h>
#include "struct_oper.h"


int
CalcVent_h_repav (unsigned long NLoop,
		  const float *Vp,
		  const float *Beta,
		  const float *Psi,
		  const float *Vx,
		  const float *Vy,
		  float *U,
		  float *V)
{
  unsigned long i;
  double U_l, U_t;
  double spsi, cpsi;

  for (i = 0; i < NLoop; i++)
    {
      spsi = sin (*Psi);
      cpsi = cos (*Psi);

      U_l = *Vx - *Vp * cos (*Beta);
      U_t = *Vy - *Vp * sin (*Beta);

      *U = U_l * spsi + U_t * cpsi;
      *V = U_l * cpsi - U_t * spsi;

      Vp++;
      Beta++;
      Psi++;
      Vx++;
      Vy++;

      U++;
      V++;
    }
  return 0;
}


/* la fonction d'enrobage classique */

int
OP_CalcVent_h_repav (unsigned long NbVal, void *ArgList[], char *DiagExec)
{
  int CodRet;

  CodRet = CalcVent_h_repav (NbVal,
			     (float *) ArgList[0],
			     (float *) ArgList[1],
			     (float *) ArgList[2],
			     (float *) ArgList[3],
			     (float *) ArgList[4],
			     (float *) ArgList[5],
			     (float *) ArgList[6]);

  return OP_OK;
}

void
ID_CalcVent_h_repav (oper * optr)
{
  strcpy (optr->Nom, "CalcVent_h_repav");
  optr->Version = "$Revision$";
  optr->Date = "$Date$";
  optr->fctptr = OP_CalcVent_h_repav;
  optr->NbArg = 7;		/* doit rester inf. a FIL_MAX_ARG */

  /* Vp */
  optr->Arg_Car[0].direction = DIR_IN;
  optr->Arg_Car[0].categorie = VECTOR;
  optr->Arg_Car[0].typ = ATYC_IF32;
  optr->Arg_Car[0].array_dim = "1";
  optr->Arg_Car[0].type_sample = "any";
  optr->Arg_Car[0].sample = "any";
  optr->Arg_Car[0].unite = "m/s";
  optr->Arg_Car[0].famille = "\"vitesse\"";

  /* Beta */
  optr->Arg_Car[1].direction = DIR_IN;
  optr->Arg_Car[1].categorie = VECTOR;
  optr->Arg_Car[1].typ = ATYC_IF32;
  optr->Arg_Car[1].array_dim = "1";
  optr->Arg_Car[1].type_sample = "any";
  optr->Arg_Car[1].sample = "any";
  optr->Arg_Car[1].unite = "radian";
  optr->Arg_Car[1].famille = "\"attitude\"";

  /* Psi */
  optr->Arg_Car[2].direction = DIR_IN;
  optr->Arg_Car[2].categorie = VECTOR;
  optr->Arg_Car[2].typ = ATYC_IF32;
  optr->Arg_Car[2].array_dim = "1";
  optr->Arg_Car[2].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[2].type_sample = "any";
  optr->Arg_Car[2].sample = "any";
  optr->Arg_Car[2].unite = "radian";
  optr->Arg_Car[2].famille = "\"attitude\"";

  /* Vx */
  optr->Arg_Car[3].direction = DIR_IN;
  optr->Arg_Car[3].categorie = VECTOR;
  optr->Arg_Car[3].typ = ATYC_IF32;
  optr->Arg_Car[3].array_dim = "1";
  optr->Arg_Car[3].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[3].type_sample = "any";
  optr->Arg_Car[3].sample = "any";
  optr->Arg_Car[3].unite = "m/s";

  /* Vy */
  optr->Arg_Car[4].direction = DIR_IN;
  optr->Arg_Car[4].categorie = VECTOR;
  optr->Arg_Car[4].typ = ATYC_IF32;
  optr->Arg_Car[4].array_dim = "1";
  optr->Arg_Car[4].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[4].type_sample = "any";
  optr->Arg_Car[4].sample = "any";
  optr->Arg_Car[4].unite = "m/s";

  /* U */
  optr->Arg_Car[5].direction = DIR_OUT;
  optr->Arg_Car[5].categorie = VECTOR;
  optr->Arg_Car[5].typ = ATYC_IF32;
  optr->Arg_Car[5].array_dim = "1";
  optr->Arg_Car[5].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[5].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[5].sample = "$Arg1.sample";
  optr->Arg_Car[5].ref_time = "$Arg1.ref_time";
  optr->Arg_Car[5].unite = "$Arg1.unit";
  optr->Arg_Car[5].famille = "\"vent\"";
  optr->Arg_Car[6].name = " \"Composante zonale du vent\" ";

  /* V */
  optr->Arg_Car[6].direction = DIR_OUT;
  optr->Arg_Car[6].categorie = VECTOR;
  optr->Arg_Car[6].typ = ATYC_IF32;
  optr->Arg_Car[6].array_dim = "1";
  optr->Arg_Car[6].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[6].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[6].sample = "$Arg1.sample";
  optr->Arg_Car[6].ref_time = "$Arg1.ref_time";
  optr->Arg_Car[6].unite = "$Arg1.unit";
  optr->Arg_Car[6].famille = "\"vent\"";
  optr->Arg_Car[6].name = " \"Composante meridienne du vent\" ";
}
