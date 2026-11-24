/*****************************************************
*
* OPERATOR        DensAir.c   FUNCTION  ANSI-C
*
* PURPOSE         Compute the dry air density 
*
* DESCRIPTION 	  Application de l'équation d'état des gaz parfait :
*                        Roh=P/RaT +(1-Rv/Ra)*Rov  (Rov : humidite absolue mesuree)
*                      (avec les valeurs usuelle : 1-Rv/Ra = 0.608)
*
*
* VERSION         1.0
*
* ARGUMENTS  IN   float      P  	hPa 	Air Pressure	
*            IN   float      T  	C or K 	Air temperature	
*            IN   float      Rov  	g/m3 	Absolute humidity	
*            IN   float      Ra		J.kg-1.K-1	Specific constant of dry air
*            IN   float      Rv		J.kg-1.K-1	Specific constant of water vapour
*            OUT  float      Roh	g/m3	Air density
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
/* Le #define _HPUX_SOURCE n'est la que pour "voir" isfinite() */
#define _HPUX_SOURCE 1

#include <math.h>
#include <stdio.h>
#include <string.h>

#include "struct_oper.h"

/* Pour reconnaissance auto d'unité */
#include "unit_def.h"

int
DensAir (unsigned long NLoop,
	 const float *P,
	 const float *T,
	 const float *Rov, const double Ra, const double Rv, float *Roh)
{
  unsigned long i;
  int flag_info_tempe;
  float CtoK;

  flag_info_tempe = auto_tempe_unit (NLoop, T, &CtoK);

  if (flag_info_tempe == MANQUANTES)
   {
    for (i = 0; i < NLoop; i++)
      {
       Roh[i] = 0./0.; 
      }
    return flag_info_tempe;
   }

  for (i = 0; i < NLoop; i++)
    {
      /* test valeur physiquement plausible */
      if (((T[i] + CtoK) < 173.) ||
	  ((T[i] + CtoK) > 373.) || (P[i] < 1.) || (P[i] > 1500.0))
	{
	  Roh[i] = K_NaN;
	}
      else
	{
	  /* 100.0 pour transformer le hPa en Pa.    */
	  /* 1/1000.0 pour transformer le g/m3 en kg/m3.    */
	  Roh[i] = ((100. * P[i]) / (Ra * (T[i] + CtoK))) +
	    Rov[i] * (1 - Rv / Ra) / 1000.;
	}
    }

    return flag_info_tempe;
}


/* la fonction d'enrobage classique */

int
OP_DensAir (unsigned long NbVal, void *ArgList[], char *DiagExec)
{
  int CodRet;

  sprintf (DiagExec, "DensAir, NbVal=%lu, Ra = %g, Rv = %g",
	   NbVal, *((double *) ArgList[3]), *((double *) ArgList[4]));

  CodRet = DensAir (NbVal,
		    (float *) ArgList[0],
		    (float *) ArgList[1],
		    (float *) ArgList[2],
		    *((double *) ArgList[3]),
		    *((double *) ArgList[4]), (float *) ArgList[5]);
  switch (CodRet)
    {
    case T_EN_C:
      strcat (DiagExec, "OK : T reconnue en Celsius");
      return OP_OK;
    case T_EN_K:
      strcat (DiagExec, "OK: T reconnue en Kelvin");
      return OP_OK;
    case MANQUANTES:
      strcat (DiagExec,
	      "; Trop de valeurs manquantes : unité de température non reconnue.");
      return OP_OK;
    default:
      sprintf (DiagExec, "ERR: Erreur %d", CodRet);
      return OP_FAIL;
    }
}

void
ID_DensAir (oper * optr)
{
  strcpy (optr->Nom, "DensAir");
  optr->Version = "$Revision$";
  optr->Date = "$Date$";
  optr->fctptr = OP_DensAir;
  optr->misval_auto = 1;	/* Gestion auto des misval */
  optr->NbArg = 6;

  /* P */
  optr->Arg_Car[0].direction = DIR_IN;
  optr->Arg_Car[0].categorie = VECTOR;
  optr->Arg_Car[0].typ = ATYC_IF32;
  optr->Arg_Car[0].array_dim = "1";
  optr->Arg_Car[0].type_sample = "any";
  optr->Arg_Car[0].sample = "any";
  optr->Arg_Car[0].unite = "hPa";
  optr->Arg_Car[0].famille = "pression";

  /* T */
  optr->Arg_Car[1].direction = DIR_IN;
  optr->Arg_Car[1].categorie = VECTOR;
  optr->Arg_Car[1].typ = ATYC_IF32;
  optr->Arg_Car[1].type_sample = "any";
  optr->Arg_Car[1].sample = "any";
  optr->Arg_Car[1].array_dim = "1";
  optr->Arg_Car[1].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[1].unite = "K";
  optr->Arg_Car[1].famille = "\"temperature\"";

  /* Rov */
  optr->Arg_Car[2].direction = DIR_IN;
  optr->Arg_Car[2].categorie = VECTOR;
  optr->Arg_Car[2].typ = ATYC_IF32;
  optr->Arg_Car[2].type_sample = "any";
  optr->Arg_Car[2].sample = "any";
  optr->Arg_Car[2].array_dim = "1";
  optr->Arg_Car[2].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[2].unite = "gram/m3";
  optr->Arg_Car[2].famille = "\"eau_vapeur\"";

  optr->Arg_Car[3].direction = DIR_IN;
  optr->Arg_Car[3].categorie = COEFFICIENT;
  optr->Arg_Car[3].array_dim = "1";
  optr->Arg_Car[3].typ = ATYC_IF64;
  optr->Arg_Car[3].unite = "any";

  optr->Arg_Car[4].direction = DIR_IN;
  optr->Arg_Car[4].categorie = COEFFICIENT;
  optr->Arg_Car[4].array_dim = "1";
  optr->Arg_Car[4].typ = ATYC_IF64;
  optr->Arg_Car[4].unite = "any";

  /* La variable produite : Roh  */
  optr->Arg_Car[5].direction = DIR_OUT;
  optr->Arg_Car[5].categorie = VECTOR;
  optr->Arg_Car[5].typ = ATYC_IF32;
  optr->Arg_Car[5].array_dim = "1";
  optr->Arg_Car[5].type_sample = "$Arg2.type_sample";
  optr->Arg_Car[5].sample = "$Arg2.sample";
  optr->Arg_Car[5].NbVal = "$Arg2.NbVal";
  optr->Arg_Car[5].ref_time = "$Arg2.ref_time";
  optr->Arg_Car[5].misval = "$Arg2.misval";
  optr->Arg_Car[5].unite = "kg/m3";
  optr->Arg_Car[5].famille = " \"thermodynamique\" ";
  optr->Arg_Car[5].name = "Masse volumique de l'air";
  optr->Arg_Car[5].en_name = "Volumic Mass of Air";

}
