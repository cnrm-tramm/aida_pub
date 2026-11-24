/******************************************************************
*
* OPERATOR      TVirt.c   ANSI-C
*
* PURPOSE       Compute Virtual temperature
*
* DESCRIPTION   Just a call to our "thermo" library. The formula is :
*                        tvir = t*(1+1.608rapm)/(1+rapm)
*
* VERSION       $Revision$
*
* ARGUMENTS    IN   float  Tempe     Kelvin          "
*              IN   float  RapM      g/Kg
*              OUT  float  Var_out   Kelvin
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
#include "unit.h"
#include "thermo.h"

#define T_IN_C (0)
#define T_IN_K (1)
#define R_IN_G (0)
#define R_IN_KG (2)
#define R_POS (0)
#define R_NEG (4)

/* La vraie fonction... */
int
TVirt (unsigned long NLoop,
       const float *Tempe, const float *RapM, float *Var_out)
{
  unsigned long i;
  int flag_info;
  float tmp_Rapm;
  float CtoK;

  /* On devine l'unite Celsius/Kelvins */
  flag_info = auto_tempe_unit (NLoop, Tempe, &CtoK);

  /* On essaie de verifier l'unite du rapport de mélange */
  if ((RapM[NLoop / 2] < 0.03) && (RapM[NLoop / 2] >= 0.0))
    flag_info += R_IN_KG;	/* C'est pas bon.. */
  if (RapM[NLoop / 2] < 0.0)
    flag_info += R_NEG;		/* C'est pas bon.. */

  for (i = 0; i < NLoop; i++)
    {
      /* On fait appel a la fonction tvir de notre librairie thermo.. 
       * Conversion des g/kg en kg/kg */
      tmp_Rapm = *RapM / 1000.0;
      tvir ((*Tempe + CtoK), tmp_Rapm, Var_out);
      *Var_out -= CtoK;

      Tempe++;
      RapM++;
      Var_out++;
    }

  return flag_info;
}


/* la fonction d'enrobage classique */

int
OP_TVirt (unsigned long NbVal, void *ArgList[], char *DiagExec)
{
  int CodRet;

  sprintf (DiagExec, "TVirt(%lu echant.)", NbVal);

  CodRet = TVirt (NbVal,
		  (float *) ArgList[0],
		  (float *) ArgList[1], (float *) ArgList[2]);

  if (CodRet & T_IN_K)
    strcat (DiagExec, "; Tempé reconnue en K");
  else
    strcat (DiagExec, "; Tempé reconnue en °C");


  if (CodRet & R_IN_KG)
    strcat (DiagExec, "; BUG ..... RapM reconnu en kg/kg");
  else
    strcat (DiagExec, "; RapM reconnu en g/kg <OK>");


  if (CodRet & R_NEG)
    strcat (DiagExec, "; BIG BUG : RapM Negatif....");

  return OP_OK;
}

/* la fonction de description de l'operateur et ses arguments */

void
ID_TVirt (oper * optr)
{
  strcpy (optr->Nom, "TVirt");
  optr->Version = "$Revision:";
  optr->Date = "$Date$";
  optr->fctptr = OP_TVirt;
  optr->NbArg = 3;

  /* Tempe */
  optr->Arg_Car[0].direction = DIR_IN;
  optr->Arg_Car[0].categorie = VECTOR;
  optr->Arg_Car[0].typ = ATYC_IF32;
  optr->Arg_Car[0].array_dim = "1";
  optr->Arg_Car[0].type_sample = "any";
  optr->Arg_Car[0].sample = "any";
  optr->Arg_Car[0].unite = "Kelvin";

  /* RapM */
  optr->Arg_Car[1].direction = DIR_IN;
  optr->Arg_Car[1].categorie = VECTOR;
  optr->Arg_Car[1].typ = ATYC_IF32;
  optr->Arg_Car[1].array_dim = "1";
  optr->Arg_Car[1].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[1].type_sample = "any";
  optr->Arg_Car[1].sample = "any";
  optr->Arg_Car[1].unite = "gram/kg";

  optr->Arg_Car[2].direction = DIR_OUT;
  optr->Arg_Car[2].categorie = VECTOR;
  optr->Arg_Car[2].typ = ATYC_IF32;
  optr->Arg_Car[2].array_dim = "1";
  optr->Arg_Car[2].ref_time = "$Arg1.ref_time";
  optr->Arg_Car[2].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[2].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[2].sample = "$Arg1.sample";
  optr->Arg_Car[2].unite = "$Arg1.unit";
  optr->Arg_Car[2].misval = "$Arg1.misval";
  optr->Arg_Car[2].famille = " \"temperature\" ";
  optr->Arg_Car[2].name = "\"Température virtuelle (\"+$Arg1.name+\")\"";
  optr->Arg_Car[2].en_name =
    "\"Virtual temperature from \"+$Arg1.english_name+\" and \"+$Arg2.english_name";

}
