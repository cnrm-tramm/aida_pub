/******************************************************************
*
* OPERATOR      Cal_angl_inc.c   FUNCTION  ANSI-C
*
* PURPOSE       Obtenir le vecteur angle d'incidence mesure entre l'ecoulement
*               et le mat pour ensuite corriger de la distortion       
*
* DESCRIPTION   l'angle d'incidence entre l'ecoulement et le mat vaut i_m = Arctan(w/u) 
*
* VERSION       1.2
*
* ARGUMENTS   IN   float  UU         Any          vent moyen dans l'axe moyen.
*             IN   float  WW         Any          composante w verticale.

*             OUT  float  i_m       degree        angle d'incidence mesure
*
* ENTRY
*
* SUBPROGRAMS   none
*
* FILES
*
* REFERENCES
*
* CHANGES       1
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

/* La vraie fonction... */
unsigned long
Cal_angl_inc (unsigned long NLoop,
	      const float *UU,
	      const float *WW,
	      float *i_m)
{
  unsigned long i;


  for (i = 0; i < NLoop; i++)
    {
      if (UU[i] != 0)
	i_m[i] = atan (WW[i] / UU[i]) * 180. / M_PI;
      else
	i_m[i] = K_NaN;
    }
  return i;
}


/* la fonction d'enrobage classique */

int
OP_Cal_angl_inc (unsigned long NbVal, void *ArgList[], char *DiagExec)
{
  unsigned long CodRet;

  (void) sprintf (DiagExec, "Cal_angl_inc(%ld ech)", NbVal);

  CodRet = Cal_angl_inc (NbVal,
			 (float *) ArgList[0],
			 (float *) ArgList[1],
			 (float *) ArgList[2]);
  if (CodRet == NbVal)
    return OP_OK;
  else
    return OP_FAIL;
}

/* la fonction de description de l'operateur et ses arguments */

void
ID_Cal_angl_inc (oper * optr)
{
  strcpy (optr->Nom, "Cal_angl_inc");
  optr->Version = "$Revision:$";
  optr->Date = "$Date:$";
  optr->fctptr = OP_Cal_angl_inc;
  optr->repl_oper = "Atan2";
  optr->repl_cause =
    "Nom trop specifique; ne permet pas de choisir l’unite du parametre calcule";

  optr->NbArg = 3;

  /* UU */
  optr->Arg_Car[0].direction = DIR_IN;
  optr->Arg_Car[0].categorie = VECTOR;
  optr->Arg_Car[0].typ = ATYC_IF32;
  optr->Arg_Car[0].array_dim = "1";
  optr->Arg_Car[0].type_sample = "any";
  optr->Arg_Car[0].sample = "any";
  optr->Arg_Car[0].unite = "any";

  /* WW */
  optr->Arg_Car[1].direction = DIR_IN;
  optr->Arg_Car[1].categorie = VECTOR;
  optr->Arg_Car[1].typ = ATYC_IF32;
  optr->Arg_Car[1].array_dim = "1";
  optr->Arg_Car[1].type_sample = "any";
  optr->Arg_Car[1].sample = "any";
  optr->Arg_Car[1].unite = "any";

  /* i_m */
  optr->Arg_Car[2].direction = DIR_OUT;
  optr->Arg_Car[2].categorie = VECTOR;
  optr->Arg_Car[2].typ = ATYC_IF32;
  optr->Arg_Car[2].array_dim = "1";
  optr->Arg_Car[2].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[2].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[2].sample = "$Arg1.sample";
  optr->Arg_Car[2].ref_time = "$Arg1.ref_time";
  optr->Arg_Car[2].misval = "$Arg1.misval";
  optr->Arg_Car[2].unite = "degres";
  optr->Arg_Car[2].famille = "$Arg1.famille";
}
