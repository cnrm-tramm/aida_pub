/******************************************************************
*
* OPERATOR      Correc_rep_sonique.c   FUNCTION  ANSI-C
*
* PURPOSE       Changement de repere: repere sonique --> repere bateau      
*
* DESCRIPTION   calcul des composantes du vent dans le repere du bateau par
*               une rotation de 30 degres
*
* VERSION       1.1
*
* ARGUMENTS   IN   float  UU         Any          Vitesse u sonique.
*             IN   float  VV         Any          Vitesse v sonique
*
*             OUT  float  UU_long   same as 1     composante longitudinale du vent 
*             OUT  float  VV_tran   same as 1     composante transversale du vent 
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
Correc_rep_sonique (unsigned long NLoop,
	     const float *UU,
	     const float *VV,
	     float *UU_cor,
	     float *VV_cor)
{
  unsigned long i;

  for (i = 0; i < NLoop; i++)
    {
      UU_cor[i] = 0.866 * UU[i] - 0.5 * VV[i];
      VV_cor[i] = 0.5 * UU[i] + 0.866 * VV[i];
    }
  return i;
}


/* la fonction d'enrobage classique */

int
OP_Correc_rep_sonique (unsigned long NbVal, void *ArgList[], char *DiagExec)
{
  unsigned long CodRet;
  int NCar;

  NCar = sprintf (DiagExec, "Correc_rep_sonique : (%ld echant.) ", NbVal) ;
  if (NCar < 0)
    NCar = 0;
  DiagExec += NCar;

  CodRet = Correc_rep_sonique (NbVal,
			(float *) ArgList[0],
			(float *) ArgList[1],
			(float *) ArgList[2],
			(float *) ArgList[3]);
  if (CodRet == NbVal)
    return OP_OK;
  else
    return OP_FAIL;
}

/* la fonction de description de l'operateur et ses arguments */

void
ID_Correc_rep_sonique (oper * optr)
{
  strcpy (optr->Nom, "Correc_rep_sonique");
  optr->Version = "1.5";
  optr->Date = "08/26/96";
  optr->fctptr = OP_Correc_rep_sonique;
  optr->NbArg = 4;
  /* UU */
  optr->Arg_Car[0].direction = DIR_IN;
  optr->Arg_Car[0].categorie = VECTOR;
  optr->Arg_Car[0].typ = ATYC_IF32;
  optr->Arg_Car[0].array_dim = "1";
  optr->Arg_Car[0].type_sample = "any";
  optr->Arg_Car[0].sample = "any";
  optr->Arg_Car[0].unite = "any";

  /* VV */
  optr->Arg_Car[1].direction = DIR_IN;
  optr->Arg_Car[1].categorie = VECTOR;
  optr->Arg_Car[1].typ = ATYC_IF32;
  optr->Arg_Car[1].array_dim = "1";
  optr->Arg_Car[1].type_sample = "any";
  optr->Arg_Car[1].sample = "any";
  optr->Arg_Car[1].unite = "any";

  optr->Arg_Car[2].direction = DIR_OUT;
  optr->Arg_Car[2].categorie = VECTOR;
  optr->Arg_Car[2].typ = ATYC_IF32;
  optr->Arg_Car[2].array_dim = "1";
  optr->Arg_Car[2].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[2].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[2].sample = "$Arg1.sample";
  optr->Arg_Car[2].ref_time = "$Arg1.ref_time";
  optr->Arg_Car[2].misval = "$Arg1.misval";
  optr->Arg_Car[2].unite = "$Arg1.unit";
  optr->Arg_Car[2].famille = "$Arg1.famille";

  optr->Arg_Car[3].direction = DIR_OUT;
  optr->Arg_Car[3].categorie = VECTOR;
  optr->Arg_Car[3].typ = ATYC_IF32;
  optr->Arg_Car[3].array_dim = "1";
  optr->Arg_Car[3].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[3].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[3].sample = "$Arg1.sample";
  optr->Arg_Car[3].ref_time = "$Arg1.ref_time";
  optr->Arg_Car[3].misval = "$Arg1.misval";
  optr->Arg_Car[3].unite = "$Arg1.unit";
  optr->Arg_Car[3].famille = "$Arg1.famille";
}
