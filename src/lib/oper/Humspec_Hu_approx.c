/******************************************************************
*
* OPERATOR      Humspec_Hu_approx.c   ANSI-C
*
* PURPOSE       Compute specific humidity  
*
* DESCRIPTION   Formulas used :
*		   e = Hu/100 * ew(ts) 
*                  q = 622. * e / Ps (Approximate formula).
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

/* La vraie fonction... */
int
Humspec_Hu_approx (unsigned long NLoop,
		   const float *Hu,
		   const float *Ts, const float *Ps, float *q)
{
  unsigned long i;

  float CtoK, TsK, ewts, ets;

  if (Ts[NLoop / 2] < 100.)
    CtoK = 273.15;
  else
    CtoK = 0.;

  for (i = 0; i < NLoop; i++)
    {
      if ((Ts[i] < -100.) || (Ps[i] < 0.) || (Hu[i] < 0.))
	{
	  q[i] = -9999.;
	  continue;
	}

      TsK = Ts[i] + CtoK;
      ew (TsK, &ewts);

      ets = Hu[i] * ewts / 100.;

      q[i] = 622. * ets / Ps[i];

    }

  if (CtoK == 0.0)
    return 0;
  else
    return 1;
}


/* la fonction d'enrobage classique */

int
OP_Humspec_Hu_approx (unsigned long NbVal, void *ArgList[], char *DiagExec)
{
  int CodRet;
  int NCar;

  NCar = sprintf (DiagExec, "Humspec_Hu_approx : (%ld echant.) ", NbVal) ;
  if (NCar < 0)
    NCar = 0;
  DiagExec += NCar;

  CodRet = Humspec_Hu_approx (NbVal,
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
ID_Humspec_Hu_approx (oper * optr)
{
  strcpy (optr->Nom, "Humspec_Hu_approx");
  optr->Version = "$Revision$";
  optr->Date = "$Date$";
  optr->fctptr = OP_Humspec_Hu_approx;
  optr->NbArg = 4;

  optr->Arg_Car[0].direction = DIR_IN;
  optr->Arg_Car[0].categorie = VECTOR;
  optr->Arg_Car[0].typ = ATYC_IF32;
  optr->Arg_Car[0].array_dim = "1";
  optr->Arg_Car[0].type_sample = "any";
  optr->Arg_Car[0].sample = "any";
  optr->Arg_Car[0].unite = "%";

  optr->Arg_Car[1].direction = DIR_IN;
  optr->Arg_Car[1].categorie = VECTOR;
  optr->Arg_Car[1].typ = ATYC_IF32;
  optr->Arg_Car[1].array_dim = "1";
  optr->Arg_Car[1].type_sample = "any";
  optr->Arg_Car[1].sample = "any";
  optr->Arg_Car[1].unite = "any";

  optr->Arg_Car[2].direction = DIR_IN;
  optr->Arg_Car[2].categorie = VECTOR;
  optr->Arg_Car[2].typ = ATYC_IF32;
  optr->Arg_Car[2].array_dim = "1";
  optr->Arg_Car[2].type_sample = "any";
  optr->Arg_Car[2].sample = "any";
  optr->Arg_Car[2].unite = "hPa";

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

}
