/*****************************************************
*
* OPERATOR        aero_vit_conv.c   FUNCTION  ANSI-C
*
* PURPOSE         Compute "conventional" speed of air from dynamical pressure
*
* DESCRIPTION     Computes air speed out of dynamical pressure,
*                 assuming standard sea-level atmospheric conditions.
*                 Applied to raw pitot measurement, this gives IAS
*                 Applied to corrected pitot measurement, this gives CAS
*                 
*
* VERSION         $Revision: 4731 $
*
* ARGUMENTS  IN   float    dP    hPa     Dynamical pressure
*            IN   string   unit   -      Unit of the result ("kt" or "m/s")
*
*            OUT  float    Vc    arg2    Air Speed
*                                                
*                                                
* ENTRY           NONE
*               
*
* SUBPROGRAMS     NONE
*
* FILES           NONE
*
* REFERENCES      Norme AFNOR NF X 02-115, parag 5.6.1, page 45
*
* CHANGES         none yet.
*
* COPYRIGHT       Meteo-France/CNRM
*
* AGREEMENT       
*########################################################################*/

#define _POSIX_SOURCE 1
#define _XOPEN_SOURCE 600

#include <math.h>
#include <stdio.h>
#include <string.h>

#include "struct_oper.h"
#include "unit.h"

int
aero_vit_conv (unsigned long NLoop,
	       const float *dP,
               const char *unit_out,
               float *Vc)
{
  unsigned long i;
  int flag_unit;
  const double Vs0_ms = 340.294;
  const double Vs0_kt = 661.479;
  double Vs0 = 0.0;
  const double P0 = 1013.25;

  flag_unit = reconnait_kt_ms (unit_out);
  switch (flag_unit)
    {
    case 0:
      Vs0 = Vs0_ms;
      break;
    case 1:
      Vs0 = Vs0_kt;
      break;
    default:
      return -1;
    }

  for (i = 0; i < NLoop; i++)
    {
      if (*dP < 0.0)
	{
	  *Vc = 0.0;
	}
      else
	{
	  *Vc = Vs0 * sqrt (5.0 * pow (*dP / P0 + 1.0, 2.0 / 7.0));
	}

      dP++;
      Vc++;
    }
  return 0;
}


/* la fonction d'enrobage classique */

int
OP_aero_vit_conv (unsigned long NbVal, void *ArgList[], char *DiagExec)
{
  int CodRet;

  (void) sprintf (DiagExec, "aero_vit_conv, %lu echant.", NbVal);

  CodRet = aero_vit_conv (NbVal,
			  (float *) ArgList[0],
			  (char *) ArgList[1], (float *) ArgList[2]);
  if (CodRet == -1)
    {
      (void) sprintf (DiagExec + strlen(DiagExec), " unite desiree (%s) non reconnue",
           (char *) ArgList[1]);
      return OP_FAIL;
    }
  return OP_OK;
}

void
ID_aero_vit_conv (oper * optr)
{
  int idx = 0;
  strcpy (optr->Nom, "aero_vit_conv");
  optr->Version = "$Revision: 4731 $";
  optr->Date = "$Date: 2012-08-21 18:25:57 +0200 (mar. 21 août 2012) $";
  optr->fctptr = OP_aero_vit_conv;
  optr->NbArg = 3;

  /* dP */
  optr->Arg_Car[idx].direction = DIR_IN;
  optr->Arg_Car[idx].categorie = VECTOR;
  optr->Arg_Car[idx].typ = ATYC_IF32;
  optr->Arg_Car[idx].array_dim = "1";
  optr->Arg_Car[idx].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[idx].type_sample = "any";
  optr->Arg_Car[idx].sample = "any";
  optr->Arg_Car[idx].unite = "hPa";
  idx++;

  /* unit */
  optr->Arg_Car[idx].direction = DIR_IN;
  optr->Arg_Car[idx].categorie = COEFFICIENT;
  optr->Arg_Car[idx].array_dim = "1";
  optr->Arg_Car[idx].typ = ATYC_STRING;
  optr->Arg_Car[idx].unite = NULL;
  idx++;

  /* La variable produite : Vc           */
  optr->Arg_Car[idx].direction = DIR_OUT;
  optr->Arg_Car[idx].categorie = VECTOR;
  optr->Arg_Car[idx].typ = ATYC_IF32;
  optr->Arg_Car[idx].array_dim = "1";
  optr->Arg_Car[idx].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[idx].sample = "$Arg1.sample";
  optr->Arg_Car[idx].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[idx].ref_time = "$Arg1.ref_time";
  optr->Arg_Car[idx].unite = "$Arg2";
  optr->Arg_Car[idx].famille = " \"vitesse\" ";
  optr->Arg_Car[idx].name = " \"vitesse conventionnelle de l'air\" ";
  optr->Arg_Car[idx].en_name = " \"Indicated Air Speed\" ";
  idx++;
}
