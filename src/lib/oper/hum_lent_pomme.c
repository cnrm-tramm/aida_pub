/*************************************************************************
*
* OPERATOR         hum_lent_pomme.c FUNCTION ANSI-C
*
* PURPOSE          ellabore une humidité lente validée à partir des deux
*                  humidités de la qli
*
* DESCRIPTION      on applique le choix déterminé par Yann Prigent:
*                  on choisit pour POMME1 : hum2 (sauf pour at010061) sur laquelle on effectue
*                  les corrections suivantes:
*                  si hum2 < 85% : hum = hum2 + 1
*                  si hum2 < 85% : hum = hum2 + 1 + (hum2-85)/6
*
*
* VERSION          1.0 
*
* ARGUMENTS  
*            IN   float  hum2  % humidité   qli choisie
*            
*            OUT  float  hum   % humidité validée
*            
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

#include <stdio.h>
#include <string.h>

#include "struct_oper.h"

void
hum_lent_pomme (unsigned long ndata, const float *hum2, float *hum)
{
  unsigned long i;

  for (i = 0; i < ndata; i++)
    {
      hum[i] = K_NaN;
      if (!isfinite (hum2[i]))
	continue;
      else if (hum2[i] <= 85.0)
	hum[i] = hum2[i] + 1.0;
      else if (hum2[i] >= 85.0)
	hum[i] = hum2[i] + 1.0 + (hum2[i] - 85.0) / 6.0;
    }
  return;
}


/* la fonction d'enrobage classique */

int
OP_hum_lent_pomme (unsigned long NbVal, void *ArgList[], char *DiagExec)
{
  sprintf (DiagExec, "hum_lent_pomme : %lu ech.", NbVal);

  hum_lent_pomme (NbVal, (float *) ArgList[0], (float *) ArgList[1]);
  return OP_OK;
}

void
ID_hum_lent_pomme (oper * optr)
{
  strcpy (optr->Nom, "hum_lent_pomme");
  optr->Version = "0.0";
  optr->Date = "17/12/01";
  optr->fctptr = OP_hum_lent_pomme;
  optr->NbArg = 2;		/* doit rester inf. a FIL_MAX_ARG */

  optr->Arg_Car[0].direction = DIR_IN;
  optr->Arg_Car[0].categorie = VECTOR;
  optr->Arg_Car[0].typ = ATYC_IF32;
  optr->Arg_Car[0].array_dim = "1";
  optr->Arg_Car[0].type_sample = "any";
  optr->Arg_Car[0].sample = "any";
  optr->Arg_Car[0].unite = "%";

  optr->Arg_Car[1].direction = DIR_OUT;
  optr->Arg_Car[1].categorie = VECTOR;
  optr->Arg_Car[1].typ = ATYC_IF32;
  optr->Arg_Car[1].array_dim = "1";
  optr->Arg_Car[1].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[1].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[1].sample = "$Arg1.sample";
  optr->Arg_Car[1].ref_time = "$Arg1.ref_time";
  optr->Arg_Car[1].unite = "$Arg1.unit";
  optr->Arg_Car[1].misval = "$Arg1.misval";
}
