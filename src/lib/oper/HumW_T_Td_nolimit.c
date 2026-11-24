/****************************************************
*
* OPERATOR    HumW_T_Td_nolimit.c   FUNCTION  ANSI-C
*
* PURPOSE     Compute humidity (relative to LIQUID water) from T/Td measurements
*
* DESCRIPTION   Calcul de l'humidite a partir de T et Td
*                Par la formule de definition :
*                       U = 100 * e / ew(T)  et  e = ew(Td)
*               En utilisant les formules relatives à l'eau LIQUIDE
*               quelque soit la temperature.
*               la formule pour ew(t) est celle de notre librairie thermo.
*               L'humidité n'est pas plafonnée à 101%
*		       
* VERSION       $Revision$
*
* ARGUMENTS   IN   float  T		K or C  Tempe Air
*             IN   float  Td      	K or C  Tempe pt de rosee.
*             OUT  float  *hu       	%       HumiditÅ relative.
*
* ENTRY            
*                 
* FILES   
*
* REFERENCES   N'importe quel bouquin de base en physique de l'atmosphere.
*	       Par exemple Triplet-Roche, p 59 de l'edition de 1971.
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
#include "unit.h"

int
HumW_T_Td_nolimit (unsigned long NLoop,
	   const float *T,	/* en Kelvin ou Celsius  */
	   const float *Td,	/* en Kelvin ou Celsius  */
	   float *Hu)		/* en % */
{
  unsigned long i;
  int flag_info;

  float CnvtoK_T, CnvtoK_Td;
  float ewt, ewtd;
  register float l_T, l_Td;

  flag_info  = auto_tempe_unit (NLoop, T, &CnvtoK_T);
  flag_info  = auto_tempe_unit (NLoop, Td, &CnvtoK_Td);

  for (i = 0; i < NLoop; i++)
    {
      l_T = *T + CnvtoK_T;
      l_Td = *Td + CnvtoK_Td;
	  ew (l_T, &ewt);
	  ew (l_Td, &ewtd);
	  *Hu = 100.0 * ewtd / ewt;
      T++;
      Td++;
      Hu++;
    }

  return 0;
}


/* la fonction d'enrobage classique */

int
OP_HumW_T_Td_nolimit (unsigned long NbVal, void *ArgList[], char *DiagExec)
{
  int CodRet;

  sprintf (DiagExec, "%s%ld", "HumW_T_Td_nolimit NbVal=", NbVal);
  sprintf (&DiagExec[strlen(DiagExec)], "%s%f", "T (0) =", *(float *) ArgList[0]);
  sprintf (&DiagExec[strlen(DiagExec)], "%s%f", "Td(0) =", *(float *) ArgList[1]);
  CodRet = HumW_T_Td_nolimit (NbVal,
		      (float *) ArgList[0],
		      (float *) ArgList[1],
		      (float *) ArgList[2]);
  return OP_OK;
}

void
ID_HumW_T_Td_nolimit (oper * optr)
{
  strcpy (optr->Nom, "HumW_T_Td_nolimit");
  optr->Version = "$Revision$";
  optr->Date = "$Date$";
  optr->fctptr = OP_HumW_T_Td_nolimit;
  optr->NbArg = 3;

  /* T */
  optr->Arg_Car[0].direction = DIR_IN;
  optr->Arg_Car[0].categorie = VECTOR;
  optr->Arg_Car[0].typ = ATYC_IF32;
  optr->Arg_Car[0].array_dim = "1";
  optr->Arg_Car[0].type_sample = "any";
  optr->Arg_Car[0].sample = "any";
  optr->Arg_Car[0].unite = "any";

  /* Td */
  optr->Arg_Car[1].direction = DIR_IN;
  optr->Arg_Car[1].categorie = VECTOR;
  optr->Arg_Car[1].typ = ATYC_IF32;
  optr->Arg_Car[1].array_dim = "1";
  optr->Arg_Car[1].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[1].type_sample = "any";
  optr->Arg_Car[1].sample = "any";
  optr->Arg_Car[1].unite = "any";

  /* Hu */
  optr->Arg_Car[2].direction = DIR_OUT;
  optr->Arg_Car[2].categorie = VECTOR;
  optr->Arg_Car[2].typ = ATYC_IF32;
  optr->Arg_Car[2].array_dim = "1";
  optr->Arg_Car[2].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[2].sample = "$Arg1.sample";
  optr->Arg_Car[2].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[2].ref_time = "$Arg1.ref_time";
  optr->Arg_Car[2].unite = "%";
  optr->Arg_Car[2].famille = "\"eau_vapeur\"";
  optr->Arg_Car[2].name = "\"humidite relative a partir de \"+$Arg2.name";
  optr->Arg_Car[2].en_name = "\"Relative humidity from \"+$Arg2.english_name";
}
