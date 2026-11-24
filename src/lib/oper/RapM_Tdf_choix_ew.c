/******************************************************************
*
* OPERATOR      RapM_Tdf_choix_ew.c   ANSI-C
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

/* La vraie fonction est dans RapM_Tdf.c */
#include "RapM_Tdf.h"

/* la fonction d'enrobage classique */

int
OP_RapM_Tdf_choix_ew (unsigned long NbVal, void *ArgList[], char *DiagExec)
{
  int CodRet;
  int NCar;

  NCar = sprintf (DiagExec, "RapM_Tdf_choix_ew (%lu echant.), formule = %s ",
		  NbVal, (char *) ArgList[2]);
  if (NCar < 0)
    NCar = 0;
  DiagExec += NCar;

  /* choix explicite des fonctions ew() */
  CodRet = set_ew_formula ((char *) ArgList[2]);
  if (CodRet != 0)
    {
      strcat (DiagExec, " Nom de formule inconnu");
      return OP_FAIL;
    }


  CodRet = RapM_Tdf (NbVal,
		     (float *) ArgList[0],
		     (float *) ArgList[1], (float *) ArgList[3]);

  strcat (DiagExec, unit_raconte (CodRet));

  /* Retour aux fonctions par défaut */
  CodRet = set_ew_formula (NULL);

  return OP_OK;
}

/* la fonction de description de l'operateur et ses arguments */

void
ID_RapM_Tdf_choix_ew (oper * optr)
{
  strcpy (optr->Nom, "RapM_Tdf_choix_ew");
  optr->Version = "$Revision: 4731 $";
  optr->Date = "$Date: 2012-11-26 18:07:53 +0100 (lun. 26 nov. 2012) $";
  optr->fctptr = OP_RapM_Tdf_choix_ew;
  optr->NbArg = 4;

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

  /* formule */
  optr->Arg_Car[2].direction = DIR_IN;
  optr->Arg_Car[2].categorie = COEFFICIENT;
  optr->Arg_Car[2].typ = ATYC_STRING;
  optr->Arg_Car[2].array_dim = "1";

  /* RapM */
  optr->Arg_Car[3].direction = DIR_OUT;
  optr->Arg_Car[3].categorie = VECTOR;
  optr->Arg_Car[3].typ = ATYC_IF32;
  optr->Arg_Car[3].array_dim = "1";
  optr->Arg_Car[3].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[3].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[3].sample = "$Arg1.sample";
  optr->Arg_Car[3].ref_time = "$Arg1.ref_time";
  optr->Arg_Car[3].unite = "gram/kg";
  optr->Arg_Car[3].name =
    " \"Rapport de melange a partir de \"  + $Arg1.name ";
  optr->Arg_Car[3].en_name =
    " \"Water vapor mixing ratio from \" + $Arg1.english_name ";
}
