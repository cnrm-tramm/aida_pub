/******************************************************************
*
* OPERATOR      Hui_Hu.c   ANSI-C
*
* PURPOSE       Compute Relative Humidity above ice from Relative Humidity
*               above water.
*
* DESCRIPTION   The formula is : Hu = 100 * e/ew
*               and Hui = 100 * e/ewi
*               thus  Hui = Hu * ew/ewi
*
* VERSION       $Revision: 4912 $
*
* ARGUMENTS    IN   float  Tempe     Kelvin or deg. Celsius 
*              IN   float  Hu        %
*              OUT  float  Hui       %
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
#include "unit_def.h"

#define T_IN_C (0)
#define T_IN_K (1)

/* La vraie fonction... */

int
Hui_Hu (unsigned long NLoop, const float *Tempe, const float *Hu, float *Hui)
{
  float ewit, ewt, CtoK, T_in_K;
  unsigned long i;
  int flag_info_tempe;

  flag_info_tempe = auto_tempe_unit (NLoop, Tempe, &CtoK);

  for (i = 0; i < NLoop; i++)
    {
      T_in_K = *Tempe + CtoK;
      if (T_in_K < 273.15)
	{
	  ewi (T_in_K, &ewit);
	  ew (T_in_K, &ewt);
	  *Hui = *Hu * ewt / ewit;
	}
      else
	{
	  *Hui = *Hu;
	}

      Tempe++;
      Hu++;
      Hui++;
    }
  return flag_info_tempe;
}


/* la fonction d'enrobage classique */

int
OP_Hui_Hu (unsigned long NbVal, void *ArgList[], char *DiagExec)
{
  int CodRet;

  sprintf (DiagExec, "Hui_Hu(%lu ech)", NbVal);

  CodRet = Hui_Hu (NbVal,
		   (float *) ArgList[0],
		   (float *) ArgList[1], (float *) ArgList[2]);

  if (CodRet == T_EN_C)
    strcat (DiagExec, "; Tempé reconnue en °C");
  else
    strcat (DiagExec, "; Tempé reconnue en K");

  return OP_OK;
}

/* la fonction de description de l'operateur et ses arguments */

void
ID_Hui_Hu (oper * optr)
{
  int idx = 0;
  strcpy (optr->Nom, "Hui_Hu");
  optr->Version = "$Revision: 4912 $";
  optr->Date = "$Date: 2012-11-26 11:05:33 +0100 (lun. 26 nov. 2012) $";
  optr->fctptr = OP_Hui_Hu;
  optr->NbArg = 3;

  /* Tempe */
  optr->Arg_Car[idx].direction = DIR_IN;
  optr->Arg_Car[idx].categorie = VECTOR;
  optr->Arg_Car[idx].typ = ATYC_IF32;
  optr->Arg_Car[idx].array_dim = "1";
  optr->Arg_Car[idx].type_sample = "any";
  optr->Arg_Car[idx].sample = "any";
  optr->Arg_Car[idx].unite = "Kelvin";
  idx++;

  /* Hu */
  optr->Arg_Car[idx].direction = DIR_IN;
  optr->Arg_Car[idx].categorie = VECTOR;
  optr->Arg_Car[idx].typ = ATYC_IF32;
  optr->Arg_Car[idx].array_dim = "1";
  optr->Arg_Car[idx].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[idx].type_sample = "any";
  optr->Arg_Car[idx].sample = "any";
  optr->Arg_Car[idx].unite = "%";
  idx++;

  /* Hui */
  optr->Arg_Car[idx].direction = DIR_OUT;
  optr->Arg_Car[idx].categorie = VECTOR;
  optr->Arg_Car[idx].typ = ATYC_IF32;
  optr->Arg_Car[idx].array_dim = "1";
  optr->Arg_Car[idx].ref_time = "$Arg1.ref_time";
  optr->Arg_Car[idx].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[idx].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[idx].sample = "$Arg1.sample";
  optr->Arg_Car[idx].unite = "%";
  optr->Arg_Car[idx].misval = "$Arg1.misval";
  optr->Arg_Car[idx].famille = " \"eau_vapeur\" ";
  optr->Arg_Car[idx].name = "\"humidité relative à la glace\"";
  optr->Arg_Car[idx].en_name =
    "\"Relative humidity over ice from \" + $Arg2.english_name";
}
