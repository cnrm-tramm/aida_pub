/******************************************************************
*
* OPERATOR      Humspec_RapM.c   ANSI-C
*
* PURPOSE       Compute specific humidity  
*
* DESCRIPTION   Formulas used :
*               RapM = mv / ma
*		   q = mv / ( ma + mv )
*                  q = RapM / ( 1 + RapM ) 
*                  en tenant compte des unités (g/kg au lieu de kg/kg) :
*                  q = RapM / ( 1 + RapM / 1000 ) 
*
* VERSION       $Revision$
*
* ARGUMENTS    IN   float  RapM      g/Kg              Mixing Ratio
*              OUT  float  q         g/Kg              Specific humidity 
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
#define _HPUX_SOURCE 1

#include <math.h>

#include <stdio.h>
#include <string.h>
#include "struct_oper.h"

#define R_UNKNOWN (0)
#define R_IN_G (1)
#define R_IN_KG (2)


/* La vraie fonction... */
int
Humspec_RapM (unsigned long NLoop, const float *RapM, float *q)
{
  unsigned long i;
  int flag_info;

  /* On essaie de verifier l'unite du rapport de mélange */
  flag_info = R_UNKNOWN;
  i = NLoop / 5;
  while ((i < NLoop) & !isfinite (RapM[i]) & (RapM[i] < 0))
    i++;

  if (i < NLoop)
    {
      if ((RapM[i] < 0.03))
	flag_info = R_IN_KG;	/* C'est pas bon.. */
      else if (RapM[i] < 50.0)
	flag_info = R_IN_G;
    }

  for (i = 0; i < NLoop; i++)
    {
      if (isfinite (RapM[i]))
	{
	  q[i] = RapM[i] / (1 + (RapM[i] / 1000.));
	}
      else
	{
	  q[i] = K_NaN;
	}
    }
  return flag_info;
}


/* la fonction d'enrobage classique */

int
OP_Humspec_RapM (unsigned long NbVal, void *ArgList[], char *DiagExec)
{
  int CodRet;

  sprintf (DiagExec, "Humspec_RapM (%lu ech); ", NbVal);

  CodRet = Humspec_RapM (NbVal, (float *) ArgList[0], (float *) ArgList[1]);

  switch (CodRet)
    {
    case R_IN_G:
      strcat (DiagExec, "RapM reconnu en g/kg");
      break;
    case R_IN_KG:
      strcat (DiagExec, "RapM reconnu en kg/kg");
      break;
    case R_UNKNOWN:
      strcat (DiagExec, "Unite RapM non reconnue !!!");
      return OP_FAIL;
      break;
    default:
      strcat (DiagExec, "Erreur Interne");
      return OP_FAIL;
      break;
    }

  return OP_OK;
}

/* la fonction de description de l'operateur et ses arguments */

void
ID_Humspec_RapM (oper * optr)
{
  strcpy (optr->Nom, "Humspec_RapM");
  optr->Version = "$Revision$";
  optr->Date = "$Date$";
  optr->fctptr = OP_Humspec_RapM;
  optr->NbArg = 2;

  /* RapM */
  optr->Arg_Car[0].direction = DIR_IN;
  optr->Arg_Car[0].categorie = VECTOR;
  optr->Arg_Car[0].typ = ATYC_IF32;
  optr->Arg_Car[0].array_dim = "1";
  optr->Arg_Car[0].type_sample = "any";
  optr->Arg_Car[0].sample = "any";
  optr->Arg_Car[0].unite = "gram/kg";

  /* q */
  optr->Arg_Car[1].direction = DIR_OUT;
  optr->Arg_Car[1].categorie = VECTOR;
  optr->Arg_Car[1].typ = ATYC_IF32;
  optr->Arg_Car[1].array_dim = "1";
  optr->Arg_Car[1].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[1].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[1].sample = "$Arg1.sample";
  optr->Arg_Car[1].ref_time = "$Arg1.ref_time";
  optr->Arg_Car[1].misval = "$Arg1.misval";
  optr->Arg_Car[1].unite = "gram/kg";
  optr->Arg_Car[1].famille = " \"eau_vapeur\" ";
  optr->Arg_Car[1].name = "\"Humidite specifique a partir de \" + $Arg1.name ";

}
