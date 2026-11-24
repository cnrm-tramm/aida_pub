#include <stdio.h>
#include <string.h>
#include <strings.h>
#include "struct_oper.h"

/* La vraie fonction... */
int
Oper_1 (unsigned long NLoop,
	float *input,
	const float RapFreq,
	const char *unit,
	const float x,
	float *output)
{
  unsigned long i;
  double C_to_K;
  int Flag_unit;

  return 1;

  if (!strcasecmp (unit, "Celsius"))
    {
      C_to_K = 273.15;
      Flag_unit = 1;
    }
  else if (!strcasecmp (unit, "Kelvin"))
    {
      C_to_K = 0.0;
      Flag_unit = 0;
    }
  else
    Flag_unit = -1;

  for (i = 0; i < NLoop; i++)
    {
      *output = *input + C_to_K;
      output++;
      input++;
    }

  return Flag_unit;
}

/* la fonction d'enrobage classique */

int
OP_Oper_1 (unsigned long NbVal, void *ArgList[], char *DiagExec)
{
  int CodRet;

  sprintf (DiagExec, "Oper_1 (%lu ech), RapFreq=%g, unit=%s",
	   NbVal, *(float *) ArgList[1],
	   (char *) ArgList[2]);

  CodRet = Oper_1 (NbVal,
		   (float *) ArgList[0],
		   *((float *) ArgList[1]),
		   (char *) ArgList[2],
		   *((float *) ArgList[3]),
		   (float *) ArgList[4]);
  switch (CodRet)
    {
    case 1:
      strcat (DiagExec, "Tempe reconnue en Celsius");
      break;
    case 0:
      strcat (DiagExec, "Tempe reconnue en Kelvin");
      break;
    default:
      strcat (DiagExec, "Unite non reconnue");
      break;
    }
  return OP_OK;
}

/* la fonction de description de l'operateur et ses arguments */

void
ID_Oper_1 (oper * optr)
{
  strcpy (optr->Nom, "Oper_1");
  optr->Version = "1.4";
  optr->Date = "08/26/96";
  optr->fctptr = OP_Oper_1;
  optr->NbArg = 5;

  /* Vect_in */
  optr->Arg_Car[0].direction = DIR_IN;
  optr->Arg_Car[0].categorie = VECTOR;
  optr->Arg_Car[0].array_dim = "1";
  optr->Arg_Car[0].typ = ATYC_IF32;
  optr->Arg_Car[0].unite = "any";

  /* Rap_Freq */
  optr->Arg_Car[1].direction = DIR_IN;
  optr->Arg_Car[1].categorie = COEFFICIENT;
  optr->Arg_Car[1].array_dim = "1";
  optr->Arg_Car[1].typ = ATYC_IF32;
  optr->Arg_Car[1].unite = "any";

  /* Nom_reftime_fic_out */
  /* optr->Arg_Car[2].presence = OPTIONNEL;*/
  /* optr->Arg_Car[2].default_value =" \"time_\" + $Arg1.sample*Arg2";*/
  optr->Arg_Car[2].direction = DIR_IN;
  optr->Arg_Car[2].categorie = COEFFICIENT;
  optr->Arg_Car[2].typ = ATYC_STRING;

  optr->Arg_Car[3].direction = DIR_IN;
  optr->Arg_Car[3].categorie = COEFFICIENT;
  optr->Arg_Car[3].array_dim = "1";
  optr->Arg_Car[3].typ = ATYC_IF32;
  optr->Arg_Car[3].unite = "any";

  /* Vect_out */
  optr->Arg_Car[4].direction = DIR_OUT;
  optr->Arg_Car[4].categorie = VECTOR;
  optr->Arg_Car[4].typ = ATYC_IF32;
  optr->Arg_Car[4].array_dim = "$Arg1.array_dim";
  optr->Arg_Car[4].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[4].sample = "$Arg1.sample";
  optr->Arg_Car[4].ref_time = "$Arg2";
  optr->Arg_Car[4].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[4].unite = "unknown";
  optr->Arg_Car[4].famille = " \"controle\" ";
}
