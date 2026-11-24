/*****************************************************
*
* OPERATOR        aero_inv_vit_conv.c   FUNCTION  ANSI-C
*
* PURPOSE         Reciprocal function of "conventionnal" speed of 
*                 air from dynamical pressure
*
* DESCRIPTION     Computes the dynamical pressure correponding to a 
*                 conventionnal air velocity (which is computed 
*                 assuming standard sea-level atmospheric conditions).
*                 Given a IAS or CAS, this gives the raw or corrected pitot measurement.
*                 
*
* VERSION         $Revision: 4731 $
*
* ARGUMENTS  IN   float    Vc            Conventional Air Speed (IAS ou CAS)
*            IN   string   unit   -      Unit of the velocity ("kt" or "m/s")
*
*            OUT  float    dP    hPa     Dynamical pressure corresponding to Vc
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
*
* CHANGES         none yet.
*
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
aero_inv_vit_conv (unsigned long NLoop,
		   const float *Vc, const char *unit, float *dP)
{
  unsigned long i;
  int flag_unit;
  const double Vs0_ms = 340.294;
  const double Vs0_kt = 661.479;
  double Vs0_sq = 0.0;
  const double P0 = 1013.25;

  flag_unit = reconnait_kt_ms (unit);
  switch (flag_unit)
    {
    case 0:
      Vs0_sq = Vs0_ms * Vs0_ms;
      break;
    case 1:
      Vs0_sq = Vs0_kt * Vs0_kt;
      break;
    default:
      return -1;
    }

  for (i = 0; i < NLoop; i++)
    {
      if (*Vc < 0.0)
	{
	  *dP = 0.0;
	}
      else
	{
	  *dP = P0 * (pow (1 + 0.2 * (*Vc * *Vc) / Vs0_sq, 7. / 2.) - 1.);
	}

      dP++;
      Vc++;
    }
  return 0;
}


/* la fonction d'enrobage classique */

int
OP_aero_inv_vit_conv (unsigned long NbVal, void *ArgList[], char *DiagExec)
{
  int CodRet;

  (void) sprintf (DiagExec, "aero_inv_vit_conv, %lu echant.", NbVal);

  CodRet = aero_inv_vit_conv (NbVal,
			      (float *) ArgList[0],
			      (char *) ArgList[1], (float *) ArgList[2]);
  if (CodRet == -1)
    {
      (void) sprintf (DiagExec + strlen (DiagExec),
		      " unite fournie (%s) non reconnue",
		      (char *) ArgList[1]);
      return OP_FAIL;
    }
  return OP_OK;
}

void
ID_aero_inv_vit_conv (oper * optr)
{
  int idx = 0;
  strcpy (optr->Nom, "aero_inv_vit_conv");
  optr->Version = "$Revision: 4731 $";
  optr->Date = "$Date: 2012-08-21 18:25:57 +0200 (mar. 21 août 2012) $";
  optr->fctptr = OP_aero_inv_vit_conv;
  optr->NbArg = 3;

  /* Vc */
  optr->Arg_Car[idx].direction = DIR_IN;
  optr->Arg_Car[idx].categorie = VECTOR;
  optr->Arg_Car[idx].typ = ATYC_IF32;
  optr->Arg_Car[idx].array_dim = "1";
  optr->Arg_Car[idx].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[idx].type_sample = "any";
  optr->Arg_Car[idx].sample = "any";
  optr->Arg_Car[idx].unite = "any";
  idx++;

  /* unit */
  optr->Arg_Car[idx].direction = DIR_IN;
  optr->Arg_Car[idx].categorie = COEFFICIENT;
  optr->Arg_Car[idx].array_dim = "1";
  optr->Arg_Car[idx].typ = ATYC_STRING;
  optr->Arg_Car[idx].unite = NULL;
  idx++;

  /* La variable produite : dP           */
  optr->Arg_Car[idx].direction = DIR_OUT;
  optr->Arg_Car[idx].categorie = VECTOR;
  optr->Arg_Car[idx].typ = ATYC_IF32;
  optr->Arg_Car[idx].array_dim = "1";
  optr->Arg_Car[idx].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[idx].sample = "$Arg1.sample";
  optr->Arg_Car[idx].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[idx].ref_time = "$Arg1.ref_time";
  optr->Arg_Car[idx].unite = "hPa";
  optr->Arg_Car[idx].famille = " \"vitesse\" ";
  optr->Arg_Car[idx].name =
    " \"Pression dynamique correspondant à \" + $Arg1.name";
  optr->Arg_Car[idx].en_name =
    " \"Dynamic Pressure corresponding to \" +  $Arg1.english_name";
  idx++;
}
