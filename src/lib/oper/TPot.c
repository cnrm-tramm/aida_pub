/******************************************************************
*
* OPERATOR      TPot.c   ANSI-C
*
* PURPOSE       Compute Potential temperature
*
* DESCRIPTION   Just a call to our "thermo" library. The formula is :
*                         tp=t*(1000/ps) **(r/Cp)
*
* VERSION       $Revision$
*
* ARGUMENTS    IN   float  Tempe     Kelvin or Celsius          "
*              IN   float  Pression  hPa
*              IN   float  R_sur_Cp  
*              OUT  float  T_pot     same unit as Tempe 
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
TPot (unsigned long NLoop,
      const float *Tempe,
      const float *Pression,
      const float R_sur_Cp,
      float *T_pot)
{
  unsigned long i;
  float T;
  float CtoK;
  int flag_info_tempe;

  /* Détermination automatique Kelvin/Celsius */
  flag_info_tempe = auto_tempe_unit (NLoop, Tempe, &CtoK);

  if (flag_info_tempe == MANQUANTES)
   {
    for (i = 0; i < NLoop; i++)
      {
       T_pot[i] = 0./0.; 
      }
    return flag_info_tempe;
   }


  for (i = 0; i < NLoop; i++)
    {
      T = *Tempe + CtoK;
      /* On fait appel a la fonction tpot de notre librairie thermo.. */
      if ((T >= 0.) && (*Pression > 0.))
	{
	  tpot (T, *Pression, R_sur_Cp, T_pot);
	  *T_pot = *T_pot - CtoK;
	}
      else
	{
	  *T_pot = K_NaN; 	/* Nan */
	}

      Tempe++;
      Pression++;
      T_pot++;
    }
  return flag_info_tempe;
}


/* la fonction d'enrobage classique */

int
OP_TPot (unsigned long NbVal, void *ArgList[], char *DiagExec)
{
  int CodRet;

  sprintf (DiagExec, "TPot(%lu ech.)", NbVal);

  CodRet = TPot (NbVal,
		 (float *) ArgList[0],
		 (float *) ArgList[1],
		 *(float *) ArgList[2],
		 (float *) ArgList[3]);

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
ID_TPot (oper * optr)
{
  strcpy (optr->Nom, "TPot");
  optr->Version = "$Revision$";
  optr->Date = "$Date$";
  optr->fctptr = OP_TPot;
  optr->NbArg = 4;
  optr->misval_auto = 1;

  /* Tempe */
  optr->Arg_Car[0].direction = DIR_IN;
  optr->Arg_Car[0].categorie = VECTOR;
  optr->Arg_Car[0].typ = ATYC_IF32;
  optr->Arg_Car[0].array_dim = "1";
  optr->Arg_Car[0].type_sample = "any";
  optr->Arg_Car[0].sample = "any";
  optr->Arg_Car[0].unite = "any";

  /* Pression */
  optr->Arg_Car[1].direction = DIR_IN;
  optr->Arg_Car[1].categorie = VECTOR;
  optr->Arg_Car[1].typ = ATYC_IF32;
  optr->Arg_Car[1].array_dim = "1";
  optr->Arg_Car[1].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[1].sample = "any";
  optr->Arg_Car[1].unite = "hPa";

  /*  R_sur_Cp */
  optr->Arg_Car[2].direction = DIR_IN;
  optr->Arg_Car[2].categorie = COEFFICIENT;
  optr->Arg_Car[2].typ = ATYC_IF32;
  optr->Arg_Car[2].array_dim = "1";
  optr->Arg_Car[2].unite = "";

  /* T_pot */
  optr->Arg_Car[3].direction = DIR_OUT;
  optr->Arg_Car[3].categorie = VECTOR;
  optr->Arg_Car[3].typ = ATYC_IF32;
  optr->Arg_Car[3].array_dim = "1";
  optr->Arg_Car[3].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[3].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[3].sample = "$Arg1.sample";
  optr->Arg_Car[3].ref_time = "$Arg1.ref_time";
  optr->Arg_Car[3].unite = "$Arg1.unit";
  optr->Arg_Car[3].famille = " \"temperature\" ";
  optr->Arg_Car[3].misval = "$Arg1.misval";
  optr->Arg_Car[3].name = "\"T. Potentielle  a partir de \" + $Arg1.name";
  optr->Arg_Car[3].en_name = "\"Potential temp. from \" + $Arg1.english_name";
}
