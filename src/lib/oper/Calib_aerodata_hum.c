/*******************************************************************
* OPERATOR      Calib_aerodata_hum.c FUNCTION ANSI-C
*
* PURPOSE       Calibration de l'humidité du capteur aerodata.
*
* DESCRIPTION   Application d'une loi indiquée par Manfred Helten
*               à P. Nedelec, dans un e-mail du 13 oct 2000.
*		 
* VERSION       1.0
*
* ARGUMENTS     IN      float   RHunc	Uncalibrated relative humidity (volt)
*               IN      float   TRT     True recovery temperature in housing (K)
*               IN      float   a1      first "a" coefficient
*               IN      float   a2      second "a" coefficient
*               IN      float   a3      third "a" coefficient
*               IN      float   a4      fourth "a" coefficient
*               IN      float   b1      first "b" coefficient
*               IN      float   b2      second "b" coefficient
*               IN      float   b3      third "b" coefficient
*               IN      float   b4      fourth "b" coefficient
*
*               OUT     float   RH	Calibrated Relative Humidity (%)
*
* ENTRY         NONE
*
* SUBPROGRAMS   NONE
*
* REFERENCES    NONE  
*             
* COPYRIGHT     Meteo-France
*               Centre National de Recherches Meteorologiques
*               GMEI/TRAMM
*               42, av. G. Coriolis
*               31057   TOULOUSE cedex
*              
*******************************************************************/

#define _POSIX_SOURCE 1
#define _XOPEN_SOURCE 600

#include <stdio.h>
#include <string.h>
#include <math.h>
#include "struct_oper.h"
#include "thermo.h"
#include "unit.h"

int
Calib_aerodata_hum (unsigned long ndata, float *RHunc, float *TRT,
		    float a1, float a2, float a3, float a4,
		    float b1, float b2, float b3, float b4, float *RH)
{
  long i;
  float CtoK;			/* Pour la conversion C->K de T_Stat */
  int flag_unit_T;

  flag_unit_T = auto_tempe_unit (ndata, TRT, &CtoK);

  for (i = 0; i < ndata; i++)
    {
      *RH =
	(b2 + (b1 - b2) / (1 + pow ((*TRT + 50 + CtoK) / b3, b4))) * *RHunc +
	(a2 + (a1 - a2) / (1 + pow ((*TRT + 50 + CtoK) / a3, a4)));

      RHunc++;
      TRT++;
      RH++;
    }

  return flag_unit_T;
}

/* fonction d'enrobage */

int
OP_Calib_aerodata_hum (unsigned long Nbval, void *ArgList[], char *DiagExec)
{
  int CodRet = Calib_aerodata_hum (Nbval,
				   (float *) ArgList[0],
				   (float *) ArgList[1],
				   *((float *) ArgList[2]),
				   *((float *) ArgList[3]),
				   *((float *) ArgList[4]),
				   *((float *) ArgList[5]),
				   *((float *) ArgList[6]),
				   *((float *) ArgList[7]),
				   *((float *) ArgList[8]),
				   *((float *) ArgList[9]),
				   (float *) ArgList[10]);

  strcpy (DiagExec, unit_raconte (CodRet));
  return OP_OK;
}

void
ID_Calib_aerodata_hum (oper * optr)
{
  int i;

  strcpy (optr->Nom, "Calib_aerodata_hum");
  optr->Version = "$Revision$";
  optr->Date = "$Date$";
  optr->fctptr = OP_Calib_aerodata_hum;
  optr->NbArg = 11;

  /* Hu */
  optr->Arg_Car[0].direction = DIR_IN;
  optr->Arg_Car[0].categorie = VECTOR;
  optr->Arg_Car[0].typ = ATYC_IF32;
  optr->Arg_Car[0].array_dim = "1";
  optr->Arg_Car[0].type_sample = "any";
  optr->Arg_Car[0].sample = "any";
  optr->Arg_Car[0].unite = "volt";

  /* T */
  optr->Arg_Car[1].direction = DIR_IN;
  optr->Arg_Car[1].categorie = VECTOR;
  optr->Arg_Car[1].typ = ATYC_IF32;
  optr->Arg_Car[1].array_dim = "1";
  optr->Arg_Car[1].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[1].type_sample = "any";
  optr->Arg_Car[1].sample = "any";
  optr->Arg_Car[1].unite = "K";

  /* a1 à a4 et b1 à b4 */
  for (i = 2; i < 10; i++)
    {
      optr->Arg_Car[i].direction = DIR_IN;
      optr->Arg_Car[i].categorie = COEFFICIENT;
      optr->Arg_Car[i].typ = ATYC_IF32;
      optr->Arg_Car[i].array_dim = "1";
      optr->Arg_Car[i].type_sample = NULL;
      optr->Arg_Car[i].sample = NULL;
      optr->Arg_Car[i].unite = NULL;
      optr->Arg_Car[i].famille = NULL;
    }

  /* RH */
  optr->Arg_Car[10].direction = DIR_OUT;
  optr->Arg_Car[10].categorie = VECTOR;
  optr->Arg_Car[10].typ = ATYC_IF32;
  optr->Arg_Car[10].array_dim = "1";
  optr->Arg_Car[10].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[10].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[10].sample = "$Arg1.sample";
  optr->Arg_Car[10].ref_time = "$Arg1.ref_time";
  optr->Arg_Car[10].misval = "$Arg1.misval";
  optr->Arg_Car[10].unite = "%";
  optr->Arg_Car[10].famille = " \"eau_vapeur\" ";
  optr->Arg_Car[10].name = " $Arg1.name ";
  optr->Arg_Car[10].en_name = " $Arg1.english_name ";
}
