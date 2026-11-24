/******************************************************************
*
* OPERATOR      Ha_Hu.c   ANSI-C
*
* PURPOSE       Compute Absolute Humidity from Relative
*
* DESCRIPTION   The formula is : Ha = e/Rv*Tempe
*               With Rv=461,51 J/Kg/K and e=Hu*ew/100
*
* VERSION       $Revision$
*
* ARGUMENTS    IN   float  Tempe     Kelvin 
*              IN   float  Hu        %
*              IN   float  Rv  
*              OUT  float  Ha        gram/m3 
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
#include "unit_def.h"

/* La vraie fonction... */

int
Ha_Hu (unsigned long NLoop, const float *Tempe, const float *Hu, float Rv,
       float *Ha)
/*** tension de vapeur saturante ew(T) ****/
{
  float ewt, CtoK, T_in_K;
  double e;
  unsigned long i;
  int flag_info_tempe;

  flag_info_tempe = auto_tempe_unit (NLoop, Tempe, &CtoK);

  if (flag_info_tempe == MANQUANTES)
   {
    for (i = 0; i < NLoop; i++)
      {
       Ha[i] = 0./0.; 
      }
    return flag_info_tempe;
   }


  for (i = 0; i < NLoop; i++)
    {
      T_in_K = *Tempe + CtoK;
      ew (T_in_K, &ewt);
      /* e est en hPa... il faut le convertir en Pa */
      /* donc e = *Hu * ewt / 100.0 * 100.0 et les 100 disparaissent */
      e = *Hu * ewt;
      /* conversion de kg/m3 en g/m3 : on multiplie par 1000 */
      *Ha = e / (Rv * T_in_K) * 1000.0;

      Tempe++;
      Hu++;
      Ha++;
    }
  return flag_info_tempe;
}


/* la fonction d'enrobage classique */

int
OP_Ha_Hu (unsigned long NbVal, void *ArgList[], char *DiagExec)
{
  int CodRet;
  const float Rv = 461.51;

  sprintf (DiagExec, "Ha_Hu(%lu ech), Rv=%g J/Kg/K", NbVal, Rv);

  CodRet = Ha_Hu (NbVal,
		  (float *) ArgList[0],
		  (float *) ArgList[1], Rv, (float *) ArgList[2]);

  switch (CodRet)
    {
    case T_EN_C:
      strcat (DiagExec, "; Tempé reconnue en °C.");
      break;
    case T_EN_K:
      strcat (DiagExec, "; Tempé reconnue en K.");
      break;
    case MANQUANTES:
      strcat (DiagExec,
	      "; Trop de valeurs manquantes : unité de température non reconnue.");
      break;
    default:
      strcat (DiagExec, "; BUG!! Code retour inattendu.");
      return OP_FAIL;
    }

  return OP_OK;

}

/* la fonction de description de l'operateur et ses arguments */

void
ID_Ha_Hu (oper * optr)
{
  strcpy (optr->Nom, "Ha_Hu");
  optr->Version = "$Revision$";
  optr->Date = "$Date$";
  optr->fctptr = OP_Ha_Hu;
  optr->NbArg = 3;
  /* Tempe */
  optr->Arg_Car[0].direction = DIR_IN;
  optr->Arg_Car[0].categorie = VECTOR;
  optr->Arg_Car[0].typ = ATYC_IF32;
  optr->Arg_Car[0].array_dim = "1";
  optr->Arg_Car[0].type_sample = "any";
  optr->Arg_Car[0].sample = "any";
  optr->Arg_Car[0].unite = "Kelvin";

  /* Hu */
  optr->Arg_Car[1].direction = DIR_IN;
  optr->Arg_Car[1].categorie = VECTOR;
  optr->Arg_Car[1].typ = ATYC_IF32;
  optr->Arg_Car[1].array_dim = "1";
  optr->Arg_Car[1].type_sample = "any";
  optr->Arg_Car[1].sample = "any";
  optr->Arg_Car[1].unite = "%";

  optr->Arg_Car[2].direction = DIR_OUT;
  optr->Arg_Car[2].categorie = VECTOR;
  optr->Arg_Car[2].typ = ATYC_IF32;
  optr->Arg_Car[2].array_dim = "1";
  optr->Arg_Car[2].ref_time = "$Arg1.ref_time";
  optr->Arg_Car[2].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[2].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[2].sample = "$Arg1.sample";
  optr->Arg_Car[2].unite = "gram/m3";
  optr->Arg_Car[2].misval = "$Arg1.misval";
  optr->Arg_Car[2].famille = " \"eau_vapeur\" ";
  optr->Arg_Car[2].name = " \"Humidité absolue a partir de \" + $Arg2.name";
  optr->Arg_Car[2].en_name =
    " \"Absolute humidity from \" + $Arg2.english_name";

}
