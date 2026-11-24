/****************************************************
*
* OPERATOR     Tair.c   FUNCTION ANSI-C
*
* PURPOSE      Computation of air temperature from mesured total tempe
*                and from a dynamical pressure
*
* DESCRIPTION      .....
*                  .....
*
* VERSION      $Revision : 1.2 $
*
* ARGUMENTS    IN   float  Ttc      K or C  temperature totale mesuree
*              IN   float  Qc       hPa     Pression dynamique
*              IN   float  Ps       hPa     Pression statique
*
*              IN   float  rf       :       coeff. de recuperation de la sonde
*              IN   float  r_sur_cp :       Comme son nom l'indique
*          
*              OUT  float  T_air    K or C  temperature statique calculee
*          
* ENTRY        
*          
* SUBPROGRAMS    
*
* FILES     
*
* REFERENCES 
*
* CHANGES      1.3  adapted to changes in categorie's definition
*              1.2  added args' sampling description/switched args' order
*
* COPYRIGHT    Meteo-France
*
* AGREEMENT    The author wishes that .....
*#########################################################################*/

#define _POSIX_SOURCE 1
#define _XOPEN_SOURCE 600
#define _XOPEN_SOURCE_EXTENDED 1

#include <math.h>
#include <stdio.h>
#include <string.h>
#include "struct_oper.h"
#include "unit_def.h"

int
Tair (const unsigned long NLoop, const float *Ttc,	/* Variables d'entree */
      const float *Qc, const float *Ps, float rf,	/* "constante" thermodynamique */
      float r_sur_cp, float seuil_Qc, float *T_air)	/* Variable de sortie */
{
  double a, T;
  float CtoK;
  unsigned long i;
  unsigned long nb_sous_seuil = 0;
  int flag_info_tempe;

  /* Détermination automatique Kelvin/Celsius */
  flag_info_tempe = auto_tempe_unit (NLoop, Ttc, &CtoK);

  for (i = 0; i < NLoop; i++)
    {
      if (*Qc > seuil_Qc)
	{
	  a = 1.0 + *Qc / *Ps;
	  T = *Ttc + CtoK;
	  *T_air = T / (1.0 + rf * (pow (a, r_sur_cp) - 1.0)) - CtoK;
	}
      else
	{
	  *T_air = K_NaN;
	  nb_sous_seuil += 1;
	}

      Ttc++;
      Qc++;
      Ps++;
      T_air++;
    }
  return flag_info_tempe;
}

/* la fonction d'enrobage classique */
int
OP_Tair (unsigned long NbVal, void *ArgList[], char *DiagExec)
{
  int CodRet;

  sprintf (DiagExec, "Tair (%lu ech), rf=%f, R/Cp=%f, seuil_Qc=-1.0e10 : ",
		  NbVal, *((float *) ArgList[3]), *((float *) ArgList[4]));

  /* Appelle Tair avec un seuil de Qc tel que le calcul sera toujours fait */
  CodRet = Tair (NbVal,
		 (float *) ArgList[0],
		 (float *) ArgList[1],
		 (float *) ArgList[2],
		 *((float *) ArgList[3]),
		 *((float *) ArgList[4]),
                 -1.0e10,
                 (float *) ArgList[5]);

  switch (CodRet)
    {
    case T_EN_C:
      strcat (DiagExec, "OK : T reconnue en Celsius");
      return OP_OK;
    case T_EN_K:
      strcat (DiagExec, "OK: T reconnue en Kelvin");
      return OP_OK;
    default:
      sprintf (DiagExec, "ERR: Erreur %d", CodRet);
      return OP_FAIL;
    }
}

/* Et une autre version */
int
OP_Tair_avion (unsigned long NbVal, void *ArgList[], char *DiagExec)
{
  int CodRet;

  sprintf (DiagExec, "Tair_avion (%lu ech), rf=%f, R/Cp=%f seuil_Qc=6.0 : ",
		  NbVal, *((float *) ArgList[3]), *((float *) ArgList[4]));

  /* Appelle Tair avec un seuil de Qc à 6 hPa, parce que, sur 
   *  un avion, les Qc trop faibles correspondent à une sonde
   *  mal ventilée et des mesures fausses. */
  CodRet = Tair (NbVal,
		 (float *) ArgList[0],
		 (float *) ArgList[1],
		 (float *) ArgList[2],
		 *((float *) ArgList[3]),
		 *((float *) ArgList[4]),
                 6.0,
                 (float *) ArgList[5]);

  switch (CodRet)
    {
    case T_EN_C:
      strcat (DiagExec, "OK : T reconnue en Celsius");
      return OP_OK;
    case T_EN_K:
      strcat (DiagExec, "OK: T reconnue en Kelvin");
      return OP_OK;
    default:
      sprintf (DiagExec, "ERR: Erreur %d", CodRet);
      return OP_FAIL;
    }
}

void
ID_Tair (oper * optr)
{
  int idx = 0;
  strcpy (optr->Nom, "Tair");
  optr->Version = "$Revision$";
  optr->Date = "$Date$";
  optr->fctptr = OP_Tair;
  optr->NbArg = 6;

  /* Ttc */
  optr->Arg_Car[idx].direction = DIR_IN;
  optr->Arg_Car[idx].categorie = VECTOR;
  optr->Arg_Car[idx].typ = ATYC_IF32;
  optr->Arg_Car[idx].array_dim = "1";
  optr->Arg_Car[idx].type_sample = "any";
  optr->Arg_Car[idx].sample = "any";
  optr->Arg_Car[idx].unite = "";
  idx++;

  /* Qc */
  optr->Arg_Car[idx].direction = DIR_IN;
  optr->Arg_Car[idx].categorie = VECTOR;
  optr->Arg_Car[idx].typ = ATYC_IF32;
  optr->Arg_Car[idx].array_dim = "1";
  optr->Arg_Car[idx].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[idx].type_sample = "any";
  optr->Arg_Car[idx].sample = "any";
  optr->Arg_Car[idx].unite = "hPa";
  idx++;

  /* Ps */
  optr->Arg_Car[idx].direction = DIR_IN;
  optr->Arg_Car[idx].categorie = VECTOR;
  optr->Arg_Car[idx].typ = ATYC_IF32;
  optr->Arg_Car[idx].array_dim = "1";
  optr->Arg_Car[idx].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[idx].type_sample = "any";
  optr->Arg_Car[idx].sample = "any";
  optr->Arg_Car[idx].unite = "hPa";
  idx++;

  /* rf */
  optr->Arg_Car[idx].direction = DIR_IN;
  optr->Arg_Car[idx].categorie = COEFFICIENT;
  optr->Arg_Car[idx].array_dim = "1";
  optr->Arg_Car[idx].typ = ATYC_IF32;
  idx++;

  /* r_sur_cp */
  optr->Arg_Car[idx].direction = DIR_IN;
  optr->Arg_Car[idx].categorie = COEFFICIENT;
  optr->Arg_Car[idx].array_dim = "1";
  optr->Arg_Car[idx].typ = ATYC_IF32;
  idx++;

  /* T_air */
  optr->Arg_Car[idx].direction = DIR_OUT;
  optr->Arg_Car[idx].categorie = VECTOR;
  optr->Arg_Car[idx].typ = ATYC_IF32;
  optr->Arg_Car[idx].array_dim = "1";
  optr->Arg_Car[idx].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[idx].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[idx].sample = "$Arg1.sample";
  optr->Arg_Car[idx].ref_time = "$Arg1.ref_time";
  /* l'unite se deduit de l'entree  */
  optr->Arg_Car[idx].unite = "$Arg1.unit";
  optr->Arg_Car[idx].famille = " \"temperature\" ";
  optr->Arg_Car[idx].misval = "$Arg1.misval";
  optr->Arg_Car[idx].name =
    " \"temperature statique a partir de \" + $Arg1.name";
  optr->Arg_Car[idx].en_name =
    " \"Static air temperature from \" + $Arg1.english_name";
  idx++;

}

/* Et le second opérateur est quasi-identique au premier */
void
ID_Tair_avion (oper * optr)
{
  ID_Tair (optr);
  strcpy (optr->Nom, "Tair_avion");
  optr->fctptr = OP_Tair_avion;
}
