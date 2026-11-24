/****************************************************
*
* OPERATOR     Tsoni.c   FUNCTION ANSI-C
*
* PURPOSE      Calcul de la temperature sonique à partir de la vitesse du son
*
* DESCRIPTION  
*
* VERSION      1.0
*
* ARGUMENTS    IN   float  Cson        m/s     Vitesse du son
*          
*              OUT  float  Tair     Celsius       Temperature sonique 
*          
* ENTRY        
*          
* SUBPROGRAMS    
*
* FILES     
*
* REFERENCES 
*
* CHANGES 
*
* COPYRIGHT    Meteo-France
*
* AGREEMENT    The author wishes that .....
*#########################################################################*/

#define _POSIX_SOURCE 1
#define _XOPEN_SOURCE 600

#include <math.h>
#include <stdio.h>
#include <string.h>

#include "struct_oper.h"
#ifndef K_Ra
#define K_Ra (8.314510 / 0.028964)
#endif
#ifndef K_cpa
#define K_cpa (1004.685)
#endif
#ifndef K_cva
#define K_cva (717.64)
#endif
#ifndef K_T_0
#define K_T_0 (273.15)
#endif

void
Tsoni (const unsigned long NLoop, const float *Cson, float *Tsoni)
{
  double gamma_fois_Ra;
  unsigned long i;

  gamma_fois_Ra = K_Ra * (K_cpa / K_cva);

  for (i = 0; i < NLoop; i++)
    {
      if (isfinite (Cson[i]))
	{
	  Tsoni[i] = Cson[i] * Cson[i] / gamma_fois_Ra - K_T_0;
	}
      else
	{
	  Tsoni[i] = 0. / 0.;
	}

    }

}

/* la fonction d'enrobage classique */

int
OP_Tsoni (unsigned long NbVal, void *ArgList[], char *DiagExec)
{
  sprintf (DiagExec, "T_soni, (%lu ech.)", NbVal);

  Tsoni (NbVal, (float *) ArgList[0], (float *) ArgList[1]);

  return OP_OK;
}

void
ID_Tsoni (oper * optr)
{
  strcpy (optr->Nom, "Tsoni");
  optr->Version = "1.0";
  optr->Date = "16/06/2014";
  optr->fctptr = OP_Tsoni;
  optr->NbArg = 2;

  optr->Arg_Car[0].direction = DIR_IN;
  optr->Arg_Car[0].categorie = VECTOR;
  optr->Arg_Car[0].typ = ATYC_IF32;
  optr->Arg_Car[0].array_dim = "1";
  optr->Arg_Car[0].type_sample = "any";
  optr->Arg_Car[0].sample = "any";
  optr->Arg_Car[0].unite = "m/s";

  optr->Arg_Car[1].direction = DIR_OUT;
  optr->Arg_Car[1].categorie = VECTOR;
  optr->Arg_Car[1].typ = ATYC_IF32;
  optr->Arg_Car[1].array_dim = " 1 ";
  optr->Arg_Car[1].NbVal = " $Arg1.NbVal ";
  optr->Arg_Car[1].type_sample = " $Arg1.type_sample ";
  optr->Arg_Car[1].sample = " $Arg1.sample ";
  optr->Arg_Car[1].ref_time = " $Arg1.ref_time ";
  optr->Arg_Car[1].misval = " $Arg1.misval ";
  optr->Arg_Car[1].unite = " Celsius ";
  optr->Arg_Car[1].famille = "\"temperature\" ";
  optr->Arg_Car[1].name =
    " \"temperature sonique a partir de \" + $Arg1.name";

}
