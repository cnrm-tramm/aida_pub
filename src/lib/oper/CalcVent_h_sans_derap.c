/*************************************************************************
*
* OPERATOR         CalcVent_h_simple.c  FUNCTION ANSI-C
*
* PURPOSE          approximate computation of horizontal wind 
*
* DESCRIPTION 
*
* Ce programme calcule le vent horizontal simplifie dans 
* le repère géographique terrestre.
*
* Les composantes de la vitesse du mobile par rapport au sol
* doivent être données dans le repère terrestre 
*
* This procedure computes the approximate horizontal
* wind with respect to the earth frame.
* 
* The velocity of the mobile platform must be given with respect to the
* earth frame.
*
*
* VERSION          1.4 
*
* ARGUMENTS  
*            IN   float   Vp     m/s    True Air Speed     
*            IN   float   Psi	 rad	Heading
*            IN   float   Ve     m/s    Aircraft velocity West->East component
*            IN   float   Vn     m/s   	Aircraft velocity South->North component
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


int
CalcVent_h_sans_derap (unsigned long NLoop,
		   const float *Vp,
		   const float *Psi,
		   const float *Ve, const float *Vn, float *U, float *V)
{
  unsigned long i;


  for (i = 0; i < NLoop; i++)
    {

      *U = *Ve - *Vp * sin (*Psi);
      *V = *Vn - *Vp * cos (*Psi);

      Vp++;
      Psi++;
      Vn++;
      Ve++;

      U++;
      V++;

    }
  return 0;
}


/* la fonction d'enrobage classique */

int
OP_CalcVent_h_sans_derap (unsigned long NbVal, void *ArgList[], char *DiagExec)
{
  int CodRet;

  CodRet = CalcVent_h_sans_derap (NbVal,
			      (float *) ArgList[0],
			      (float *) ArgList[1],
			      (float *) ArgList[2],
			      (float *) ArgList[3],
			      (float *) ArgList[4],
			      (float *) ArgList[5]);

  return OP_OK;
}

void
ID_CalcVent_h_sans_derap (oper * optr)
{
  int idx;

  strcpy (optr->Nom, "CalcVent_h_sans_derap");
  optr->Version = "1.0";
  optr->Date = "26/03/2013";
  optr->fctptr = OP_CalcVent_h_sans_derap;
  optr->NbArg = 6;		/* doit rester inf. a FIL_MAX_ARG */

  idx = 0;

  /* Vp */
  optr->Arg_Car[idx].direction = DIR_IN;
  optr->Arg_Car[idx].categorie = VECTOR;
  optr->Arg_Car[idx].typ = ATYC_IF32;
  optr->Arg_Car[idx].array_dim = "1";
  optr->Arg_Car[idx].type_sample = "any";
  optr->Arg_Car[idx].sample = "any";
  optr->Arg_Car[idx].unite = "m/s";
  idx++;

  /* Psi */
  optr->Arg_Car[idx].direction = DIR_IN;
  optr->Arg_Car[idx].categorie = VECTOR;
  optr->Arg_Car[idx].typ = ATYC_IF32;
  optr->Arg_Car[idx].array_dim = "1";
  optr->Arg_Car[idx].type_sample = "any";
  optr->Arg_Car[idx].sample = "any";
  optr->Arg_Car[idx].unite = "radian";
  idx++;

  /* Ve */
  optr->Arg_Car[idx].direction = DIR_IN;
  optr->Arg_Car[idx].categorie = VECTOR;
  optr->Arg_Car[idx].typ = ATYC_IF32;
  optr->Arg_Car[idx].array_dim = "1";
  optr->Arg_Car[idx].type_sample = "any";
  optr->Arg_Car[idx].sample = "any";
  optr->Arg_Car[idx].unite = "m/s";
  idx++;

  /* Vn */
  optr->Arg_Car[idx].direction = DIR_IN;
  optr->Arg_Car[idx].categorie = VECTOR;
  optr->Arg_Car[idx].typ = ATYC_IF32;
  optr->Arg_Car[idx].array_dim = "1";
  optr->Arg_Car[idx].type_sample = "any";
  optr->Arg_Car[idx].sample = "any";
  optr->Arg_Car[idx].unite = "m/s";
  idx++;

  /* U */
  optr->Arg_Car[idx].direction = DIR_OUT;
  optr->Arg_Car[idx].categorie = VECTOR;
  optr->Arg_Car[idx].typ = ATYC_IF32;
  optr->Arg_Car[idx].array_dim = "1";
  optr->Arg_Car[idx].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[idx].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[idx].sample = "$Arg1.sample";
  optr->Arg_Car[idx].ref_time = "$Arg1.ref_time";
  optr->Arg_Car[idx].unite = "$Arg1.unit";
  idx++;

  /* V */
  optr->Arg_Car[idx].direction = DIR_OUT;
  optr->Arg_Car[idx].categorie = VECTOR;
  optr->Arg_Car[idx].typ = ATYC_IF32;
  optr->Arg_Car[idx].array_dim = "1";
  optr->Arg_Car[idx].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[idx].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[idx].sample = "$Arg1.sample";
  optr->Arg_Car[idx].ref_time = "$Arg1.ref_time";
  optr->Arg_Car[idx].unite = "$Arg1.unit";
}
