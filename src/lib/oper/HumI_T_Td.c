 /****************************************************
 *
 * OPERATOR    HumI_T_Td.c   FUNCTION  ANSI-C
 *
 * PURPOSE     Compute humidity (relative to ICE) from T/Td measurements.
 *
 * DESCRIPTION   Calcul de l'humidité relative à la glace, à partir de T et Td
 *                Par la formule de définition :
 *                       U = 100 * e / ewi(T)
 *                       avec e = ew(Td) qqsoit Td (on suppose donc que
 *                            td est toujours un point de rosée pas un
 *                            point de givre)
 *               Les formules pour ewi(t) et ew(t) sont celle de notre bibliothèque thermo.
 *               Les résultats supérieurs à 115 % sont ramenés à 115%.
 *               Rappel : pour les mesures météorologiques opérationnelles 
 *               (par ex. : radiosondages), l'humidité relative se calcule toujours
 *               par rapport à l'eau liquide, même si Td<0.
 *		       
 * VERSION       $Revision$
 *
 * ARGUMENTS   IN   float  T		K or C  Tempe Air
 *             IN   float  Td      	K or C  Tempe pt de rosee.
 *             OUT  float  *hu       	%       Humidité relative.
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
#define _HPUX_SOURCE 1
#define _XOPEN_SOURCE_EXTENDED 1


#include <stdio.h>
#include <string.h>
#include "struct_oper.h"
#include "unit.h"
#include "thermo.h"

long
HumI_T_Td (unsigned long NLoop, const float *T,	/* en Kelvin ou Celsius  */
	   const float *Td,	/* en Kelvin ou Celsius  */
	   float *Hu)		/* en % */
{
  unsigned long i;
  int flag_info_T;
  int flag_info_Td;

  float CnvtoK_T, CnvtoK_Td;
  float ewit, ewtd;
  register float l_T, l_Td;

  flag_info_T = auto_tempe_unit (NLoop, T, &CnvtoK_T);
  flag_info_Td = auto_tempe_unit (NLoop, Td, &CnvtoK_Td);

  for (i = 0; i < NLoop; i++)
    {
      l_T = *T + CnvtoK_T;
      l_Td = *Td + CnvtoK_Td;

      ewi (l_T, &ewit);
      ew (l_Td, &ewtd);

      /* La tension de vapeur par rapport à la glace est inférieure
       * à la tension de vapeur par rapport à l'au liquide. L'air peut
       * être sur-saturé par rapport à la glace, mais sous-saturé par 
       * rapport à l'eau. ->  on borne à 115 % au lieu de 101 %
       */
      if (ewtd > 1.14 * ewit)
	*Hu = 115.0;
      else
	{
	  *Hu = 100.0 * ewtd / ewit;
	}
      T++;
      Td++;
      Hu++;
    }

  return 0;
}


/* la fonction d'enrobage classique */

int
OP_HumI_T_Td (unsigned long NbVal, void *ArgList[], char *DiagExec)
{
  long CodRet;

  sprintf (DiagExec, "%s%ld", "HumI_T_Td NbVal=", NbVal);

  CodRet = HumI_T_Td (NbVal, (float *) ArgList[0], (float *) ArgList[1],
		      (float *) ArgList[2]);

  sprintf (DiagExec + strlen (DiagExec), ", %ld Td>T", CodRet);
  
  return OP_OK;
}

void
ID_HumI_T_Td (oper * optr)
{
  strcpy (optr->Nom, "HumI_T_Td");
  optr->Version = "$Revision$";
  optr->Date = "$Date$";
  optr->fctptr = OP_HumI_T_Td;
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
  optr->Arg_Car[2].name = "\"humidité relative à la glace\"";
  optr->Arg_Car[2].en_name = 
    "\"Relative humidity over ice from \" + $Arg2.english_name";
}
