/******************************************************************
*
* OPERATOR      TPotBolton.c   ANSI-C
*
* PURPOSE       Calcul de la temperature potentielle de l'air
*               humide d'une particule donnee 
*               definie par : pression, temperature , humidite .
*
* DESCRIPTION   Just a call to our "thermo" library. 
*
* VERSION       $Revision$
*
* ARGUMENTS    ENTREE   float  Pression     hPa
*              ENTREE   float  Temperature  deg.Kelvin ou Celsius
*              ENTREE   float  Humidite     %
*              SORTIE   float  T_potBolton  deg.Kelvin ou Celsius 
*                                           (idem Temperature)
*
* SUBPROGRAMS  Appels a la Librairie thermo ainsi que la Librairie
*	       struct_oper 
*
* FILES
*
* REFERENCES   Bolton Volume 108 equation (7)
*
* CHANGES      10/05/2000 C.Berne : premiere version 
*
* COPYRIGHT    Meteo-France
*
* AGREEMENT     
*#########################################################################*/

#define _POSIX_SOURCE 1
#define _XOPEN_SOURCE 600

#include <stdio.h>
#include <string.h>
#include "struct_oper.h"
#include "thermo.h"
#include "unit_def.h"

#define T_IN_C (0)
#define T_IN_K (1)
#define R_IN_G (0)
#define R_IN_KG (2)
#define R_POS (0)
#define R_NEG (4)

#define TPOT_BOLTON_ECHEC (-999.)

/* La vraie fonction... */
int
TPotBolton (unsigned long NLoop,
	 const float *Ps,
	 const float *Tempe,
	 const float *Hum,
	 float *T_potBolton)
{
  unsigned long i;
  int flag_info;
  float CtoK;
  const float misval_out = K_NaN;

  /* Détermination automatique Kelvin/Celsius */
  flag_info = auto_tempe_unit (NLoop, Tempe, &CtoK);

  for (i = 0; i < NLoop; i++)
    {
	  /*                                                                  */
	  /* On fait appel a la fonction de notre librairie thermo    */
	  /* tpot_Bolton                                              */
	  /* Pas d'utilisation des pointeurs mais des indices de tableaux!    */

	  tpot_Bolton (Ps[i], (Tempe[i] + CtoK), Hum[i], &T_potBolton[i]);
          if (T_potBolton[i] == TPOT_BOLTON_ECHEC)
	    T_potBolton[i] = misval_out;
          else
	    T_potBolton[i] = T_potBolton[i] - CtoK;
    }

  return flag_info;
}

/* la fonction d'enrobage classique */

int
OP_TPotBolton (unsigned long NbVal, void *ArgList[], char *DiagExec)
{
  int CodRet;

  sprintf (DiagExec, "OP_TPotBolton(%lu, %f, %f, %f, %f)", NbVal,
	   *((float *) ArgList[0]),
	   *((float *) ArgList[1]),
	   *((float *) ArgList[2]),
	   *((float *) ArgList[3]));

  CodRet = TPotBolton (NbVal,
		    (float *) ArgList[0],
		    (float *) ArgList[1],
		    (float *) ArgList[2],
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
      return OP_FAIL;
    default:
      strcat (DiagExec, "; BUG!! Code retour inattendu.");
      return OP_FAIL;
    }


  return OP_OK;
}

/* la fonction de description de l'operateur et ses arguments */

void
ID_TPotBolton (oper * optr)
{
  strcpy (optr->Nom, "TPotBolton");
  optr->Version = "$Revision$";
  optr->Date = "$Date$";
  optr->fctptr = OP_TPotBolton;
  optr->misval_auto = 1;
  optr->NbArg = 4;

  optr->Arg_Car[0].direction = DIR_IN;
  optr->Arg_Car[0].categorie = VECTOR;
  optr->Arg_Car[0].typ = ATYC_IF32;
  optr->Arg_Car[0].array_dim = "1";
  optr->Arg_Car[0].type_sample = "any";
  optr->Arg_Car[0].sample = "any";
  optr->Arg_Car[0].unite = "hPa";

  optr->Arg_Car[1].direction = DIR_IN;
  optr->Arg_Car[1].categorie = VECTOR;
  optr->Arg_Car[1].typ = ATYC_IF32;
  optr->Arg_Car[1].array_dim = "1";
  optr->Arg_Car[1].type_sample = "any";
  optr->Arg_Car[1].sample = "any";
  optr->Arg_Car[1].unite = "";

  optr->Arg_Car[2].direction = DIR_IN;
  optr->Arg_Car[2].categorie = VECTOR;
  optr->Arg_Car[2].typ = ATYC_IF32;
  optr->Arg_Car[2].array_dim = "1";
  optr->Arg_Car[2].type_sample = "any";
  optr->Arg_Car[2].sample = "any";
  optr->Arg_Car[2].unite = "%";

  optr->Arg_Car[3].direction = DIR_OUT;
  optr->Arg_Car[3].categorie = VECTOR;
  optr->Arg_Car[3].typ = ATYC_IF32;
  optr->Arg_Car[3].array_dim = "1";
  optr->Arg_Car[3].ref_time = "$Arg1.ref_time";
  optr->Arg_Car[3].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[3].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[3].sample = "$Arg1.sample";
  optr->Arg_Car[3].unite = "$Arg2.unit";
  optr->Arg_Car[3].misval = "$Arg2.misval";
  optr->Arg_Car[3].famille = " \"temperature\" ";

}
