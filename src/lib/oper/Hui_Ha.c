/******************************************************************
*
* OPERATOR      Hui_Ha.c   ANSI-C
*
* PURPOSE       Compute Relative Humidity from Absolute.
*
* DESCRIPTION   The formula is : Hu = 100 * e/ew
*               With Rv=461,51 J/Kg/K and e = Ha*Rv*Tempe
*
* VERSION       $Revision$
*
* ARGUMENTS    IN   float  Tempe     Kelvin or deg. Celsius 
*              IN   float  Ha        g/m3 
*              IN   float  Rv  
*              OUT  float  Hu        %
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
Hui_Ha (unsigned long NLoop, const float *Tempe, const float *Ha, float Rv,
	float *Hu)
{
  float ewit, CtoK, T_in_K;
  double e;
  unsigned long i;
  int flag_info_tempe;

  flag_info_tempe = auto_tempe_unit (NLoop, Tempe, &CtoK);

  for (i = 0; i < NLoop; i++)
    {
      T_in_K = *Tempe + CtoK;
      ewi (T_in_K, &ewit);
      /* e est en hPa... il faut le convertir en Pa 
       * donc e = *Hu * ewt / 100.0 * 100.0 et les 100 disparaissent.
       * Conversion de g/m3 en kg/m3 : on divise par 1000 */
      e = (*Ha / 1000.0) * Rv * T_in_K;
      *Hu = e / ewit;

      Tempe++;
      Hu++;
      Ha++;
    }
  return flag_info_tempe;
}


/* la fonction d'enrobage classique */

int
OP_Hui_Ha (unsigned long NbVal, void *ArgList[], char *DiagExec)
{
  int CodRet;
  /* Rv n'est pas encore un argument de l'opérateur, il est 
   * défini ici. Si on a vraiment besoin d'une autre valeur,
   * il faudra rajouter cet argument à l'opérateur. */
  const float Rv = 461.51;

  sprintf (DiagExec, "Hui_Ha (%lu ech, Rv=%g J/kg/K)", NbVal, Rv);

  CodRet = Hui_Ha (NbVal,
		   (float *) ArgList[0],
		   (float *) ArgList[1], Rv, (float *) ArgList[2]);

  if (CodRet == 0)
    strcat (DiagExec, "; Tempé reconnue en °C");
  else
    strcat (DiagExec, "; Tempé reconnue en K");

  return OP_OK;
}

/* la fonction de description de l'operateur et ses arguments */

void
ID_Hui_Ha (oper * optr)
{
  int idx = 0;
  strcpy (optr->Nom, "Hui_Ha");
  optr->Version = "$Revision$";
  optr->Date = "$Date$";
  optr->fctptr = OP_Hui_Ha;
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

  /* Ha */
  optr->Arg_Car[idx].direction = DIR_IN;
  optr->Arg_Car[idx].categorie = VECTOR;
  optr->Arg_Car[idx].typ = ATYC_IF32;
  optr->Arg_Car[idx].array_dim = "1";
  optr->Arg_Car[idx].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[idx].type_sample = "any";
  optr->Arg_Car[idx].sample = "any";
  optr->Arg_Car[idx].unite = "gram/m3";
  idx++;

  /* Hu */
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
  optr->Arg_Car[idx].name =
    " \"Humidite relative a partir de \" + $Arg2.name";
  optr->Arg_Car[idx].en_name =
    " \"Relative Humidity from \" + $Arg2.english_name";
}
