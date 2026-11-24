/******************************************************************
*
* OPERATOR      RapM_Tdf.c   ANSI-C
*
* PURPOSE       Compute WaterVapour mixing ratio
*
* DESCRIPTION   Just a call to the "thermo" library. The formula is :
*                  ew_tdf = ew(tdf) or ewi(tdf) if tdf<0°C
*                  rapm = 622. * ew_tdf / (Ps - ew_tdf)
*
* VERSION       $Revision: 4731 $
*
* ARGUMENTS    IN   float  Tdf      Kelvin or Celsius  Dew or Frost point temp..
*              IN   float  Ps       hPa                Static pressure
*              OUT  float  RapM     g/Kg               mixing ratio
*
* ENTRY
*
* SUBPROGRAMS   none
*
* FILES
*
* REFERENCES    N'importe quel bouquin de thermodynamique applique
*               a l'atmosphere. Par exemple Triplet-Roche; page 55
*               de l'edition de 1971.
*
* CHANGES       
*
* COPYRIGHT     Meteo-France
*
* AGREEMENT     The author wishes that .....
*#########################################################################*/

#define _POSIX_SOURCE 1
#define _XOPEN_SOURCE 600
#define _XOPEN_SOURCE_EXTENDED 1

#include <stdio.h>
#include <string.h>
#include "struct_oper.h"
#include "thermo.h"
#include "unit.h"

/* La vraie fonction... */
int
RapM_Tdf (unsigned long NLoop,
	 const float *Tdf,
	 const float *Ps,
	 float *RapM)
{
  unsigned long i;
  int flag_info;

  float TdfK, CtoK;

  flag_info  = auto_tempe_unit (NLoop, Tdf, &CtoK);

  for (i = 0; i < NLoop; i++)
    {
      TdfK = *Tdf + CtoK;
      /* On fait appel a la fonction de notre librairie thermo.. */
      rmel_Td_hybride (TdfK, *Ps, RapM);

      Tdf++;
      Ps++;
      RapM++;
    }

  return flag_info;
}


/* la fonction d'enrobage classique */

int
OP_RapM_Tdf (unsigned long NbVal, void *ArgList[], char *DiagExec)
{
  int CodRet;
  int NCar;

  NCar = sprintf (DiagExec, "RapM_Tdf (%lu echant.) ", NbVal);
  if (NCar < 0)
    NCar = 0;
  DiagExec += NCar;

  CodRet = RapM_Tdf (NbVal,
		    (float *) ArgList[0],
		    (float *) ArgList[1],
		    (float *) ArgList[2]);

  strcat (DiagExec, unit_raconte (CodRet));

  return OP_OK;
}

/* la fonction de description de l'operateur et ses arguments */

void
ID_RapM_Tdf (oper * optr)
{
  strcpy (optr->Nom, "RapM_Tdf");
  optr->Version = "$Revision: 4731 $";
  optr->Date = "$Date$";
  optr->fctptr = OP_RapM_Tdf;
  optr->NbArg = 3;

  /* Tdf */
  optr->Arg_Car[0].direction = DIR_IN;
  optr->Arg_Car[0].categorie = VECTOR;
  optr->Arg_Car[0].typ = ATYC_IF32;
  optr->Arg_Car[0].array_dim = "1";
  optr->Arg_Car[0].type_sample = "any";
  optr->Arg_Car[0].sample = "any";
  optr->Arg_Car[0].unite = "any";

  /* Ps */
  optr->Arg_Car[1].direction = DIR_IN;
  optr->Arg_Car[1].categorie = VECTOR;
  optr->Arg_Car[1].typ = ATYC_IF32;
  optr->Arg_Car[1].array_dim = "1";
  optr->Arg_Car[1].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[1].type_sample = "any";
  optr->Arg_Car[1].sample = "any";
  optr->Arg_Car[1].unite = "hPa";

  /* RapM */
  optr->Arg_Car[2].direction = DIR_OUT;
  optr->Arg_Car[2].categorie = VECTOR;
  optr->Arg_Car[2].typ = ATYC_IF32;
  optr->Arg_Car[2].array_dim = "1";
  optr->Arg_Car[2].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[2].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[2].sample = "$Arg1.sample";
  optr->Arg_Car[2].ref_time = "$Arg1.ref_time";
  optr->Arg_Car[2].unite = "gram/kg";
  optr->Arg_Car[2].famille = "\"eau_vapeur\"";
  optr->Arg_Car[2].name = " \"Rapport de melange a partir de \"  + $Arg1.name ";
  optr->Arg_Car[2].en_name = " \"Water vapor mixing ratio from \" + $Arg1.english_name ";
}
