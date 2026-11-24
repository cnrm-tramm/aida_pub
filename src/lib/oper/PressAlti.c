/*********************************************************
*
* OPERATOR       PressAlti.c  ANSI-C
*
* PURPOSE        Calculation of pressure at altitude Z with a pressure P0 measured at altitude Z0.
*
* DESCRIPTION      
*
* 
* VERSION        $Revision$
*
* ARGUMENTS      
*                IN   float   P0      hPa             Pressure at level Z0 
*                IN   float   Tv      Kelvin          Virtual Temp. moyenne de la couche
*                IN   float   Z0      m               Altitude of level Z0 
*                IN   float   Z      m               Altitude of level Z0 
*                IN   float   rsurg                   "constante" r/g
*
*                OUT  float   P       same as P0      Pressure at level Z 
*
* FILES          NONE
*
* REFERENCES       
*              
* Fomule de Laplace - Triplet-Roche
*
* COPYRIGHT      Meteo-France
*
* AGREEMENT      Nothing special
*#########################################################################*/

#define _POSIX_SOURCE 1
#define _XOPEN_SOURCE 600

#include <string.h>
#include <stdio.h>
#include <math.h>
#include "struct_oper.h"
#include "unit_def.h"

int
PressAlti (unsigned long NLoop,
	   const float *P0, 
	   const float *Tv,
	   const float Z0, 
	   const float Z, 
	   const float rsurg, 
	   float *P)
{
  unsigned long i;
  int flag_info_tempe;
  float CtoK;

  /* Détermination automatique Kelvin/Celsius */
  flag_info_tempe = auto_tempe_unit (NLoop, Tv, &CtoK);

  /*fprintf(stderr, "CtoK : %f\n", CtoK);*/

  for (i = 0; i < NLoop; i++)
    {
      *P = *P0 / exp ( ( Z - Z0 ) / ( rsurg * (*Tv + CtoK) ) );

      Tv++;
      P0++;
      P++;
    }

  return flag_info_tempe;
}

/* la fonction d'enrobage classique */

int
OP_PressAlti (unsigned long NbVal, void *ArgList[], char *DiagExec)
{
  int CodRet;

  sprintf (DiagExec, "OP_PressAlti (%lu ech.), Z0=%f, Z= %f, R/g = %f", NbVal,
	   *((float *) ArgList[2]), *((float *) ArgList[3]), *((float *) ArgList[4]));

  CodRet = PressAlti (NbVal,
		      (float *) ArgList[0],
		      (float *) ArgList[1],
		      *((float *) ArgList[2]),
		      *((float *) ArgList[3]), 
		      *((float *) ArgList[4]), 
		      (float *) ArgList[5]);

  switch (CodRet)
    {
    case -1:
      strcat (DiagExec, "ERR : Tempé Ni Kelvin Ni Celsius");
      return OP_FAIL;
    case T_EN_K :
      strcat (DiagExec, "Unité Température reconnue : Kelvin;");
      return OP_OK;
    case T_EN_C :
      strcat (DiagExec, "Unité Température reconnue : Degrés Celsius");
      return OP_OK;
    case MANQUANTES :
      strcat (DiagExec, "Données de température manquantes");
      return OP_OK;
    default:
      strcat (DiagExec, "Erreur inattendue");
      return OP_FAIL;
    }
}

/* la fonction de description de l'operateur et ses arguments */

void
ID_PressAlti (oper * optr)
{
  strcpy (optr->Nom, "PressAlti");
  optr->Version = "$Revision$";
  optr->Date = "$Date$";
  optr->fctptr = OP_PressAlti;
  optr->NbArg = 6;

  /* P0 */
  optr->Arg_Car[0].direction = DIR_IN;
  optr->Arg_Car[0].categorie = VECTOR;
  optr->Arg_Car[0].typ = ATYC_IF32;
  optr->Arg_Car[0].array_dim = "1";
  optr->Arg_Car[0].type_sample = "any";
  optr->Arg_Car[0].sample = "any";
  optr->Arg_Car[0].unite = "hPa";

  /* Tv */
  optr->Arg_Car[1].direction = DIR_IN;
  optr->Arg_Car[1].categorie = VECTOR;
  optr->Arg_Car[1].typ = ATYC_IF32;
  optr->Arg_Car[1].array_dim = "1";
  optr->Arg_Car[1].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[1].type_sample = "any";
  optr->Arg_Car[1].sample = "any";
  optr->Arg_Car[1].unite = "Kelvin";

  /* Z0  */
  optr->Arg_Car[2].direction = DIR_IN;
  optr->Arg_Car[2].categorie = COEFFICIENT;
  optr->Arg_Car[2].typ = ATYC_IF32;
  optr->Arg_Car[2].array_dim = "1";
  optr->Arg_Car[2].type_sample = NULL;
  optr->Arg_Car[2].sample = NULL;
  optr->Arg_Car[2].unite = "m";

  /* Z */
  optr->Arg_Car[3].direction = DIR_IN;
  optr->Arg_Car[3].categorie = COEFFICIENT;
  optr->Arg_Car[3].typ = ATYC_IF32;
  optr->Arg_Car[3].array_dim = "1";
  optr->Arg_Car[3].type_sample = NULL;
  optr->Arg_Car[3].sample = NULL;
  optr->Arg_Car[3].unite = "m";

  /* rsurg */
  optr->Arg_Car[4].direction = DIR_IN;
  optr->Arg_Car[4].categorie = COEFFICIENT;
  optr->Arg_Car[4].typ = ATYC_IF32;
  optr->Arg_Car[4].array_dim = "1";
  optr->Arg_Car[4].type_sample = NULL;
  optr->Arg_Car[4].sample = NULL;
  optr->Arg_Car[4].unite = "any";

  /* P */
  optr->Arg_Car[5].direction = DIR_OUT;
  optr->Arg_Car[5].categorie = VECTOR;
  optr->Arg_Car[5].typ = ATYC_IF32;
  optr->Arg_Car[5].array_dim = "1";
  optr->Arg_Car[5].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[5].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[5].sample = "$Arg1.sample";
  optr->Arg_Car[5].ref_time = "$Arg1.ref_time";
  optr->Arg_Car[5].unite = "$Arg1.unit";
  optr->Arg_Car[5].name = " \"Pression calculee a partir de \" +$Arg1.name";
  optr->Arg_Car[5].en_name = " \"Pressure computed with \"+$Arg1.english_name";
  optr->Arg_Car[5].famille = " \"pression\" ";
}
