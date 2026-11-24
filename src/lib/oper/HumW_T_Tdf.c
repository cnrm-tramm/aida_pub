/****************************************************
 *
 * OPERATOR    HumW_T_Tdf.c   FUNCTION  ANSI-C
 *
 * PURPOSE     Compute relative humidity (relative to LIQUID water)
 *             from air temperature and dew/frost point measurement
 *
 * DESCRIPTION   Calcul de l'humidité relative à partir de T et Tdf
 *                Par la formule de définition :
 *                      U = 100 * e / ew(T)
 *                avec  e = ew(Td) si Tdf>=0°c ou ewi(Tf) si Tdf<0°C
 *              ew(T) est toujours calculé en utilisant les formules
 *              relatives à l'eau LIQUIDE quelle que soit la température.
 *              (convention OMM usuelle)
 *              Les formules pour ew(t) et ewi(t) sont celles de 
 *              notre bibliothèque thermo.
 *		       
 * VERSION       $Revision$
 *
 * ARGUMENTS   IN   float  T		K or C  Tempe air
 *             IN   float  Tdf     	K or C  Tempe pt de rosée ou givre.
 *             OUT  float  *hu       	%       Humidité relative.
 *
 * ENTRY            
 *                 
 * FILES   
 *
 * REFERENCES   N'importe quel bouquin de base en physique de l'atmosphère.
 *	       Par exemple Triplet-Roche, p 59 de l'édition de 1971.
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
#include "unit_def.h"

long
HumW_T_Tdf (unsigned long NLoop, const float *T,	/* en Kelvin ou Celsius  */
	    const float *Tdf,	/* en Kelvin ou Celsius  */
	    float *Hu,		/* en % */
	    float borne, int *flag_info_T, int *flag_info_Tdf)
{
  unsigned long i;
  long nb_inv = 0;

  float CnvtoK_T, CnvtoK_Tdf;
  float ewt, ewtdf;
  register float l_T, l_Tdf;

  *flag_info_T = auto_tempe_unit (NLoop, T, &CnvtoK_T);
  *flag_info_Tdf = auto_tempe_unit (NLoop, Tdf, &CnvtoK_Tdf);

  for (i = 0; i < NLoop; i++)
    {
      l_T = *T + CnvtoK_T;
      l_Tdf = *Tdf + CnvtoK_Tdf;

      ew (l_T, &ewt);
      if (l_Tdf > 273.15)
	ew (l_Tdf, &ewtdf);
      else
	ewi (l_Tdf, &ewtdf);

      *Hu = 100.0 * ewtdf / ewt;
      if (*Hu > borne)
	{
	  *Hu = borne + 1;
	  nb_inv++;
	}
      else if (*Hu < 0)
	{			/* Petite protection contre les erreurs de mesure. */
	  *Hu = K_NaN;
	  nb_inv++;
	}

      T++;
      Tdf++;
      Hu++;
    }

  return nb_inv;
}


/* la fonction d'enrobage classique */

int
OP_HumW_T_Tdf (unsigned long NbVal, void *ArgList[], char *DiagExec)
{
  long CodRet;
  int flag_info_T, flag_info_Tdf;
  const float borne = 102.0;

  sprintf (DiagExec, "%s NbVal=%ld ", "HumW_T_Td", NbVal);

  CodRet =
    HumW_T_Tdf (NbVal, (float *) ArgList[0], (float *) ArgList[1],
		(float *) ArgList[2], borne, &flag_info_T, &flag_info_Tdf);

  strcat (DiagExec, unit_raconte (flag_info_T));
  strcat (DiagExec, " ");
  strcat (DiagExec, unit_raconte (flag_info_Tdf));
  sprintf (DiagExec + strlen (DiagExec), " %ld Hu>%g%% ou <0", CodRet, borne);
  if ((flag_info_T == MANQUANTES) || (flag_info_Tdf == MANQUANTES))
    return OP_FAIL;
  else
    return OP_OK;
}

void
ID_HumW_T_Tdf (oper * optr)
{
  strcpy (optr->Nom, "HumW_T_Tdf");
  optr->Version = "$Revision$";
  optr->Date = "$Date$";
  optr->fctptr = OP_HumW_T_Tdf;
  optr->NbArg = 3;

  /* T */
  optr->Arg_Car[0].direction = DIR_IN;
  optr->Arg_Car[0].categorie = VECTOR;
  optr->Arg_Car[0].typ = ATYC_IF32;
  optr->Arg_Car[0].array_dim = "1";
  optr->Arg_Car[0].type_sample = "any";
  optr->Arg_Car[0].sample = "any";
  optr->Arg_Car[0].unite = "any";

  /* Tdf */
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
  optr->Arg_Car[2].name = "\"humidité relative à partir de \"+ $Arg2.name";
  optr->Arg_Car[2].en_name =
    "\"Relative humidity from \" + $Arg2.english_name";
}
