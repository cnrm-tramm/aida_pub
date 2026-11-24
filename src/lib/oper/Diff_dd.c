/*****************************************************
*
* OPERATOR         Diff_dd.c   FUNCTION  ANSI-C
*
* PURPOSE          Calcule la difference de 2 directions (vent) en degres
*
* DESCRIPTION      Traite le cas des angles proches de 360...
*                  Le resultat est un angle compris entre -180 et +180 deg
*                  Si DD2 > DD1 --> DD est positif ...
*
* VERSION          1.1
*
* ARGUMENTS  IN    float    DD1   degres     Vecteur 1 (direction comprise entre 0-360)
*            IN    float    DD2   degres     Vecteur 2 (autre direction comprise entre 0-360)
*            OUT   float    DD    degres     Vecteur correspondant a DD1 - DD2 
*                                                
*
* ENTRY            NONE
*               
* SUBPROGRAMS      NONE
*
* FILES            NONE
*
* REFERENCES       
*
*
* CHANGES          
*
*
* COPYRIGHT        Meteo-France/CNRM
*
* AGREEMENT        
*########################################################################*/

#define _POSIX_SOURCE 1
#define _XOPEN_SOURCE 600
/* Le #define _HPUX_SOURCE est la pour utiliser la fonction isfinite */
#define _HPUX_SOURCE 1

#include <math.h>
#include <stdio.h>
#include <string.h>
#include "struct_oper.h"


void
Diff_dd (unsigned long NLoop,
	 const float *DD1,
	 const float *DD2,
	 float *DD)
{
  unsigned long i;
  float diff, flag;

  for (i = 0; i < NLoop; i++)
    {
      diff = *DD1 - *DD2;
      flag = 1.;
      if (diff < 0.0)
	{
		/* on change (DD2 - DD1) pour rester avec des angles positifs */
		/* et on introduit le flag car on changera de signe... */
      		diff = *DD2 - *DD1;
      		flag = -1.;
	}
      if (diff >= 180.0)
	{
      		*DD = 360. - diff;
	}
      else
	{
	  	*DD = diff;
	}

      /* On utilise le flag ... */
      *DD = flag * *DD;

      DD1++;
      DD2++;
      DD++;
    }
  return;
}


/* la fonction d'enrobage classique */

int
OP_Diff_dd (unsigned long NbVal, void *ArgList[], char *DiagExec)
{
  (void) sprintf (DiagExec, "Diff_dd : %lu Ech.", NbVal);

  Diff_dd (NbVal,
	   (float *) ArgList[0],
	   (float *) ArgList[1],
	   (float *) ArgList[2]);

  return OP_OK;
}

void
ID_Diff_dd (oper * optr)
{
  strcpy (optr->Nom, "Diff_dd");
  optr->Version = "$Revision$";
  optr->Date = "$Date$";
  optr->fctptr = OP_Diff_dd;
  optr->misval_auto = 1;	/* gestion auto des misval */
  optr->NbArg = 3;

  /* DD1 */
  optr->Arg_Car[0].direction = DIR_IN;
  optr->Arg_Car[0].categorie = VECTOR;
  optr->Arg_Car[0].typ = ATYC_IF32;
  optr->Arg_Car[0].array_dim = "1";
  optr->Arg_Car[0].type_sample = "any";
  optr->Arg_Car[0].sample = "any";
  optr->Arg_Car[0].unite = "degree";

  /* DD2 */
  optr->Arg_Car[1].direction = DIR_IN;
  optr->Arg_Car[1].categorie = VECTOR;
  optr->Arg_Car[1].typ = ATYC_IF32;
  optr->Arg_Car[1].array_dim = "1";
  optr->Arg_Car[1].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[1].type_sample = "any";
  optr->Arg_Car[1].sample = "any";
  optr->Arg_Car[1].unite = "degree";

  /* DD */
  optr->Arg_Car[2].direction = DIR_OUT;
  optr->Arg_Car[2].categorie = VECTOR;
  optr->Arg_Car[2].typ = ATYC_IF32;
  optr->Arg_Car[2].array_dim = "1";
  optr->Arg_Car[2].NbVal = "$Arg1.NbVal";
  /* le sample et l'unite se deduisent de l'entree  */
  optr->Arg_Car[2].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[2].sample = "$Arg1.sample";
  optr->Arg_Car[2].ref_time = "$Arg1.ref_time";
  optr->Arg_Car[2].misval = "$Arg1.misval";
  optr->Arg_Car[2].unite = "degree";
  optr->Arg_Car[2].famille = "$Arg1.famille";

}
