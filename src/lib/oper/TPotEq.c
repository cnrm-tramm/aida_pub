/******************************************************************
*
* OPERATOR      TPotEq.c   ANSI-C
*
* PURPOSE       Compute Equivalent Potential temperature
*
* DESCRIPTION   Just a call to our "thermo" library. The formula is :
*                    tpe = tp*(1+rapm*L/(Cp*T)) en kelvin
*                          (L=3136.17 - 2.34 * T)
*
* VERSION       $Revision$
*
* ARGUMENTS    IN   float  Tempe     Kelvin or Celsius
*              IN   float  T_pot     Kelvin        
*              IN   float  RapM      g/Kg
*              IN   float  Cp  
*              OUT  float  T_pot     Kelvin
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
#define _HPUX_SOURCE 1		/* Rajout C.Berne 10/10/2000 */

#include <stdio.h>
#include <string.h>
#include "struct_oper.h"
#include "thermo.h"
#include "unit_def.h"
#ifndef K_T0
#define K_T0 (273.15)
#endif


/* La vraie fonction... */
int
TPotEq (unsigned long NLoop,
	const float *Tempe,
	const float *T_pot,
	const float *RapM,
       	const float Cp,
       	float *T_pot_eq)
{
  unsigned long i;
  float CtoK_T, CtoK_Tp;
  float T, Tp;
#ifdef DEBUG
  fprintf (stderr, "TPotEq(%ld, %g, %g, %g, %p)\n",
	   NLoop, *Tempe, *T_pot, *RapM, T_pot);
#endif
  int flag_info;

  /* Détermination automatique Kelvin/Celsius */
  flag_info = auto_tempe_unit (NLoop, Tempe, &CtoK_T);
  flag_info = auto_tempe_unit (NLoop, T_pot, &CtoK_Tp);

  for (i = 0; i < NLoop; i++)
    {
      /* On fait appel a la fonction tpoteq de notre librairie thermo.. */
      T = *Tempe + CtoK_T;
      Tp = *T_pot + CtoK_Tp;
      tpoteq (T, Tp, *RapM, Cp, T_pot_eq);
      *T_pot_eq -= CtoK_T;

      Tempe++;
      T_pot++;
      RapM++;
      T_pot_eq++;
    }
  return 0;
}


/* la fonction d'enrobage classique */

int
OP_TPotEq (unsigned long NbVal, void *ArgList[], char *DiagExec)
{
  int CodRet;

  sprintf (DiagExec, "TPotEq  : %lu ech, Cp=%g", NbVal, *(float *) ArgList[3]);

  CodRet = TPotEq (NbVal,
		   (float *) ArgList[0],
		   (float *) ArgList[1],
		   (float *) ArgList[2],
		   *(float *) ArgList[3],
		   (float *) ArgList[4]);
  return OP_OK;
}

/* la fonction de description de l'operateur et ses arguments */

void
ID_TPotEq (oper * optr)
{
  strcpy (optr->Nom, "TPotEq");
  optr->Version = "$Revision$";
  optr->Date = "$Date$";
  optr->fctptr = OP_TPotEq;
  optr->NbArg = 5;

  /* Tempe */
  optr->Arg_Car[0].direction = DIR_IN;
  optr->Arg_Car[0].categorie = VECTOR;
  optr->Arg_Car[0].typ = ATYC_IF32;
  optr->Arg_Car[0].array_dim = "1";
  optr->Arg_Car[0].type_sample = "any";
  optr->Arg_Car[0].sample = "any";
  optr->Arg_Car[0].unite = "any";

  /* Tpot */
  optr->Arg_Car[1].direction = DIR_IN;
  optr->Arg_Car[1].categorie = VECTOR;
  optr->Arg_Car[1].typ = ATYC_IF32;
  optr->Arg_Car[1].array_dim = "1";
  optr->Arg_Car[1].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[1].type_sample = "any";
  optr->Arg_Car[1].sample = "any";
  optr->Arg_Car[1].unite = "any";

  optr->Arg_Car[2].direction = DIR_IN;
  optr->Arg_Car[2].categorie = VECTOR;
  optr->Arg_Car[2].typ = ATYC_IF32;
  optr->Arg_Car[2].array_dim = "1";
  optr->Arg_Car[2].type_sample = "any";
  optr->Arg_Car[2].sample = "any";
  optr->Arg_Car[2].unite = "gram/kg";

  optr->Arg_Car[3].direction = DIR_IN;
  optr->Arg_Car[3].categorie = COEFFICIENT;
  optr->Arg_Car[3].typ = ATYC_IF32;
  optr->Arg_Car[3].array_dim = "1";
  optr->Arg_Car[3].type_sample = NULL;
  optr->Arg_Car[3].sample = NULL;
  optr->Arg_Car[3].unite = "";

  optr->Arg_Car[4].direction = DIR_OUT;
  optr->Arg_Car[4].categorie = VECTOR;
  optr->Arg_Car[4].typ = ATYC_IF32;
  optr->Arg_Car[4].array_dim = "1";
  optr->Arg_Car[4].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[4].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[4].sample = "$Arg1.sample";
  optr->Arg_Car[4].ref_time = "$Arg1.ref_time";
  optr->Arg_Car[4].unite = "$Arg1.unit";
  optr->Arg_Car[4].misval = "$Arg1.misval";
}
