/******************************************************************
*
* OPERATOR      Humspec_Hu.c   ANSI-C
*
* PURPOSE       Compute specific humidity  
*
* DESCRIPTION   Formulas used :
*		   e = Hu * ew(ts) 
*                  q = Ra/Rv * e / (Ps - e (1-Ra/Rv) )
*                  Ra/Rv = 0.622
*
* VERSION       $Revision$
*
* ARGUMENTS    IN   float  Hu        %                 Relative Humidity
*              IN   float  Ts        Kelvin or Celsius Static Temperature
*              IN   float  Ps        hPa               Static Pressure
*              OUT  float  q         g/Kg              Specific humidity 
*
* ENTRY
*
* SUBPROGRAMS   none
*
* FILES
*
* REFERENCES
*
* CHANGES       
*
* COPYRIGHT     Meteo-France
*
* AGREEMENT     The author wishes that .....
*#########################################################################*/

#define _POSIX_SOURCE 1
#define _XOPEN_SOURCE 600

#include <stdio.h>
#include <string.h>
#include "struct_oper.h"
#include "thermo.h"
#include "unit.h"

/* La vraie fonction... */
int
Humspec_Hu (unsigned long NLoop,
	    const float *Hu, const float *Ts, const float *Ps, float *q)
{
  unsigned long i;

  float CtoK, TsK, ewts;
  double ets;
  float  flag_info_tempe; 


  /* Détermination automatique Kelvin/Celsius */
  flag_info_tempe = auto_tempe_unit (NLoop, Ts, &CtoK);

  for (i = 0; i < NLoop; i++)
    {
      if ((Ts[i] < -100.) || (Ps[i] < 0.1) || (Hu[i] < 0.))
	{
	  q[i] = -9999.;
	  continue;
	}

      TsK = Ts[i] + CtoK;
      ew (TsK, &ewts);

      ets = Hu[i] * ewts / 100.;

      q[i] = 622. * ets / (Ps[i] - ets * (1. - 0.622));

    }

  if (CtoK == 0.0)
    return 0;
  else
    return 1;
}


/* la fonction d'enrobage classique */

int
OP_Humspec_Hu (unsigned long NbVal, void *ArgList[], char *DiagExec)
{
  int CodRet;

  sprintf (DiagExec, "Humspec_Hu (%lu ech); ", NbVal);

  CodRet = Humspec_Hu (NbVal,
		       (float *) ArgList[0],
		       (float *) ArgList[1],
		       (float *) ArgList[2], (float *) ArgList[3]);

  switch (CodRet)
    {
    case 0:
      strcat (DiagExec, "Ts reconnu en Kelvin");
      break;
    case 1:
      strcat (DiagExec, "Ts reconnu en Celsius");
      break;
    default:
      strcat (DiagExec, "Erreur Interne");
      break;
    }

  return OP_OK;
}

/* la fonction de description de l'operateur et ses arguments */

void
ID_Humspec_Hu (oper * optr)
{
  strcpy (optr->Nom, "Humspec_Hu");
  optr->Version = "$Revision$";
  optr->Date = "$Date$";
  optr->fctptr = OP_Humspec_Hu;
  optr->NbArg = 4;

  /* Hu */
  optr->Arg_Car[0].direction = DIR_IN;
  optr->Arg_Car[0].categorie = VECTOR;
  optr->Arg_Car[0].typ = ATYC_IF32;
  optr->Arg_Car[0].array_dim = "1";
  optr->Arg_Car[0].type_sample = "any";
  optr->Arg_Car[0].sample = "any";
  optr->Arg_Car[0].unite = "%";

  /* Ts */
  optr->Arg_Car[1].direction = DIR_IN;
  optr->Arg_Car[1].categorie = VECTOR;
  optr->Arg_Car[1].typ = ATYC_IF32;
  optr->Arg_Car[1].array_dim = "1";
  optr->Arg_Car[1].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[1].type_sample = "any";
  optr->Arg_Car[1].sample = "any";
  optr->Arg_Car[1].unite = "any";

  /* Ps */
  optr->Arg_Car[2].direction = DIR_IN;
  optr->Arg_Car[2].categorie = VECTOR;
  optr->Arg_Car[2].typ = ATYC_IF32;
  optr->Arg_Car[2].array_dim = "1";
  optr->Arg_Car[2].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[2].type_sample = "any";
  optr->Arg_Car[2].sample = "any";
  optr->Arg_Car[2].unite = "hPa";

  /* q */
  optr->Arg_Car[3].direction = DIR_OUT;
  optr->Arg_Car[3].categorie = VECTOR;
  optr->Arg_Car[3].typ = ATYC_IF32;
  optr->Arg_Car[3].array_dim = "1";
  optr->Arg_Car[3].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[3].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[3].sample = "$Arg1.sample";
  optr->Arg_Car[3].ref_time = "$Arg1.ref_time";
  optr->Arg_Car[3].misval = "$Arg1.misval";
  optr->Arg_Car[3].unite = "gram/kg";
  optr->Arg_Car[3].famille = " \"eau_vapeur\" ";
  optr->Arg_Car[3].name = " \"humidite specifique a partir de \" + $Arg1.name";
  optr->Arg_Car[3].en_name = " \"specific humidity from \" + $Arg1.english_name";
}
