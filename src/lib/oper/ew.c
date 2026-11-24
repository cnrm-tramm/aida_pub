/****************************************************
*
* OPERATOR    ew.c   FUNCTION  ANSI-C
*
* PURPOSE     Compute saturation vapour pressure over liquid water at given temperatures
*
* DESCRIPTION   Calcul de la tension de vapeur saturante par rapport à l'eau liquide.
*		       
* VERSION       $Revision$
*
* ARGUMENTS   IN   float  T		K or C  Tempe Air
*             IN   string formula     	        Nom de la formule utilisee
*             OUT  float   ew       	hPa     Tension de vapeur saturante
*
* ENTRY            
*                 
* FILES         thermo.c
*
* REFERENCES   
*	       
*
* CHANGES       
*
* COPYRIGHT    Meteo-France
*
* AGREEMENT    The author wishes that .....
*#########################################################################*/

#define _POSIX_SOURCE 1
#define _XOPEN_SOURCE 600
#define _XOPEN_SOURCE_EXTENDED 1

#include <stdio.h>
#include <string.h>


#include "struct_oper.h"
#include "thermo.h"
#include "thermo_extra.h"
#include "unit_def.h"

int
ew_local (unsigned long NLoop, const float *T,	/* en Kelvin ou Celsius  */
	  const char *formule_name, float *result)	/* en hPa */
{
  unsigned long i;
  int flag_info;
  void (*fct_ptr) (const float, float *);

  float CnvtoK_T;
  register float l_T;

  flag_info = auto_tempe_unit (NLoop, T, &CnvtoK_T);
  fct_ptr = ew_function (formule_name);
  if (fct_ptr == NULL)
    return -1;

  for (i = 0; i < NLoop; i++)
    {
      l_T = *T + CnvtoK_T;
      fct_ptr (l_T, result);
      T++;
      result++;
    }

  return flag_info;
}


/* la fonction d'enrobage classique */

int
OP_ew (unsigned long NbVal, void *ArgList[], char *DiagExec)
{
  int CodRet;

  sprintf (DiagExec, "%s%ld%s%s", "ew NbVal=", NbVal, ", formule=",
	   (char *) ArgList[1]);

  CodRet = ew_local (NbVal,
		     (float *) ArgList[0],
		     (char *) ArgList[1], (float *) ArgList[2]);

  if (CodRet == -1)
    {
      strcat (DiagExec, "; ERREUR : Nom de formule inconnue");
      return OP_FAIL;
    }
  strcat (DiagExec, unit_raconte (CodRet));
  return OP_OK;
}

void
ID_ew (oper * optr)
{
  strcpy (optr->Nom, "ew");
  optr->Version = "$Revision$";
  optr->Date = "$Date: 2011-03-29 14:44:09 $";
  optr->fctptr = OP_ew;
  optr->NbArg = 3;

  /* T */
  optr->Arg_Car[0].direction = DIR_IN;
  optr->Arg_Car[0].categorie = VECTOR;
  optr->Arg_Car[0].typ = ATYC_IF32;
  optr->Arg_Car[0].array_dim = "1";
  optr->Arg_Car[0].type_sample = "any";
  optr->Arg_Car[0].sample = "any";
  optr->Arg_Car[0].unite = "any";

  /* nom_formule */
  optr->Arg_Car[1].direction = DIR_IN;
  optr->Arg_Car[1].categorie = COEFFICIENT;
  optr->Arg_Car[1].typ = ATYC_STRING;
  optr->Arg_Car[1].array_dim = "1";

  /* Hu */
  optr->Arg_Car[2].direction = DIR_OUT;
  optr->Arg_Car[2].categorie = VECTOR;
  optr->Arg_Car[2].typ = ATYC_IF32;
  optr->Arg_Car[2].array_dim = "1";
  optr->Arg_Car[2].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[2].sample = "$Arg1.sample";
  optr->Arg_Car[2].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[2].ref_time = "$Arg1.ref_time";
  optr->Arg_Car[2].unite = "hPa";
  optr->Arg_Car[2].famille = "\"eau_vapeur\"";
  optr->Arg_Car[2].name =
    "\"tension de vapeur saturante /eau liquide a T=\"+ $Arg1.name";
  optr->Arg_Car[2].en_name =
    "\" saturation vapour pressure over liquid water at T=\" + $Arg1.english_name";
}
