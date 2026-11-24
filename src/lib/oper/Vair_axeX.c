/*****************************************************
*
* OPERATOR        Vair_axeX.c   FUNCTION  ANSI-C
*
* PURPOSE         Compute the component along the 
*		  the longitudinal axis (X) of the
*		  air velocity 
*
* DESCRIPTION 	  Use of sideslip and attack angles   
*
* VERSION         1.0
*
* ARGUMENTS  IN   float      Vp 	m/s 	True Air Speed 
*            IN   float      Alpha 	rad	Attack angle	
*            IN   float      Beta	rad	Sideslip angle
*
*            OUT  float      Vair_x	m/s     Air velocity following X-axis 
*                                                
*                                                
* ENTRY           NONE
*               
*
* SUBPROGRAMS     NONE
*
* FILES           NONE
*
* REFERENCES     
*                 Bulletin NCAR/RAF Nr 23, Feb 87, by D. Lenschow and
*                   P. Spyers-Duran
*
* CHANGES        
*
*
* COPYRIGHT       Meteo-France/CNRM
*
* AGREEMENT       
*########################################################################*/

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
Vair_axeX (unsigned long NLoop,
	  const float *Vp,
	  const float *Alpha,
	  const float *Beta,
	  float *Vair_x)
{
  unsigned long i;
  double D, tan2a, tan2b;

  for (i = 0; i < NLoop; i++)
    {
     tan2a = tan(Alpha[i]) * tan(Alpha[i]);
     tan2b = tan(Beta[i]) * tan(Beta[i]);

     D = sqrt( 1. + tan2a + tan2b); 

     Vair_x[i] = Vp[i] / ((float)D);
    }
  return 0;
}


/* la fonction d'enrobage classique */

int
OP_Vair_axeX (unsigned long NbVal, void *ArgList[], char *DiagExec)
{
  int CodRet;

  CodRet = sprintf (DiagExec, "OP_Vair_axeX, NbVal=%lu;", NbVal);
  DiagExec += CodRet;

  CodRet = Vair_axeX (NbVal,
		     (float *) ArgList[0],
		     (float *) ArgList[1],
		     (float *) ArgList[2],
		     (float *) ArgList[3]);
  return OP_OK;
}

void
ID_Vair_axeX (oper * optr)
{
  strcpy (optr->Nom, "Vair_axeX");
  optr->Version = "1.0";
  optr->Date = "06/17/97";
  optr->fctptr = OP_Vair_axeX;
  optr->NbArg = 4;

  optr->Arg_Car[0].direction = DIR_IN;
  optr->Arg_Car[0].categorie = VECTOR;
  optr->Arg_Car[0].typ = ATYC_IF32;
  optr->Arg_Car[0].array_dim = "1";
  optr->Arg_Car[0].type_sample = "any";
  optr->Arg_Car[0].sample = "any";
  optr->Arg_Car[0].unite = "";

  optr->Arg_Car[1].direction = DIR_IN;
  optr->Arg_Car[1].categorie = VECTOR;
  optr->Arg_Car[1].typ = ATYC_IF32;
  optr->Arg_Car[1].type_sample = "any";
  optr->Arg_Car[1].sample = "any";
  optr->Arg_Car[1].array_dim = "1";
  optr->Arg_Car[1].unite = "hPa";

  optr->Arg_Car[2].direction = DIR_IN;
  optr->Arg_Car[2].categorie = VECTOR;
  optr->Arg_Car[2].typ = ATYC_IF32;
  optr->Arg_Car[2].array_dim = "1";
  optr->Arg_Car[2].type_sample = "any";
  optr->Arg_Car[2].sample = "any";
  optr->Arg_Car[2].unite = "hPa";

/* La variable produite            */
  optr->Arg_Car[3].direction = DIR_OUT;
  optr->Arg_Car[3].categorie = VECTOR;
  optr->Arg_Car[3].typ = ATYC_IF32;
  optr->Arg_Car[3].array_dim = "1";
  optr->Arg_Car[3].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[3].sample = "$Arg1.sample";
  optr->Arg_Car[3].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[3].ref_time = "$Arg1.ref_time";
  optr->Arg_Car[3].unite = "m/s";

}
