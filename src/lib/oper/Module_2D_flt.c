/*****************************************************
*
* OPERATOR         Module_2D_flt.c   FUNCTION  ANSI-C
*
* PURPOSE          Compute the module of a vector given its 2 components
*
* DESCRIPTION      
*
* VERSION          $Revision: 4731 $
*
* ARGUMENTS  IN   float   C1      any           First component
*            IN   float   C2      same as C1    Second component
*            IN   string  name_out              Name of the result
*            IN   string  en_name_out           English name of the result
*            OUT  float   M       same as C1    Module of the vector
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
* CHANGES          1.3  adapted to follow categorie's definition change
*                  1.2  added args' sampling description
*
*
* COPYRIGHT        Meteo-France/CNRM
*
* AGREEMENT        
*########################################################################*/

#define _POSIX_SOURCE 1
#define _XOPEN_SOURCE 600

#include <math.h>
#include <stdio.h>
#include <string.h>
#include "struct_oper.h"


void
Module_2D_flt (unsigned long NLoop, const float *C1, const float *C2,
	       float *M)
{
  unsigned long i;

  for (i = 0; i < NLoop; i++)
    {
      *M = sqrt (*C1 * *C1 + *C2 * *C2);

      C1++;
      C2++;
      M++;
    }
  return;
}


/* la fonction d'enrobage classique */

int
OP_Module_2D_flt (unsigned long NbVal, void *ArgList[], char *DiagExec)
{
  (void) sprintf (DiagExec, "Module_2D_flt, NbVal=%lu", NbVal);

  Module_2D_flt (NbVal,
		 (float *) ArgList[0],
		 (float *) ArgList[1], (float *) ArgList[4]);
  return OP_OK;
}

void
ID_Module_2D_flt (oper * optr)
{
  int idx = 0;
  strcpy (optr->Nom, "Module_2D_flt");
  optr->Version = "$Revision: 4731 $";
  optr->Date = "$Date: 2012-08-21 18:25:57 +0200 (mar. 21 août 2012) $";
  optr->fctptr = OP_Module_2D_flt;
  optr->misval_auto = 1;	/* gestion auto des misval */
  optr->NbArg = 5;


  /* C1 */
  optr->Arg_Car[idx].direction = DIR_IN;
  optr->Arg_Car[idx].categorie = VECTOR;
  optr->Arg_Car[idx].typ = ATYC_IF32;
  optr->Arg_Car[idx].array_dim = "1";
  optr->Arg_Car[idx].type_sample = "any";
  optr->Arg_Car[idx].sample = "any";
  optr->Arg_Car[idx].unite = "any";
  idx++;

  /* C2 */
  optr->Arg_Car[idx].direction = DIR_IN;
  optr->Arg_Car[idx].categorie = VECTOR;
  optr->Arg_Car[idx].typ = ATYC_IF32;
  optr->Arg_Car[idx].array_dim = "1";
  optr->Arg_Car[idx].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[idx].type_sample = "any";
  optr->Arg_Car[idx].sample = "any";
  optr->Arg_Car[idx].unite = "$Arg1.unit";
  idx++;

  /* name_out      */
  optr->Arg_Car[idx].direction = DIR_IN;
  optr->Arg_Car[idx].categorie = COEFFICIENT;
  optr->Arg_Car[idx].array_dim = "1";
  optr->Arg_Car[idx].typ = ATYC_STRING;
  optr->Arg_Car[idx].unite = "any";
  idx++;

  /* en_name_out      */
  optr->Arg_Car[idx].direction = DIR_IN;
  optr->Arg_Car[idx].categorie = COEFFICIENT;
  optr->Arg_Car[idx].array_dim = "1";
  optr->Arg_Car[idx].typ = ATYC_STRING;
  optr->Arg_Car[idx].unite = "any";
  idx++;

  /* M */
  optr->Arg_Car[idx].direction = DIR_OUT;
  optr->Arg_Car[idx].categorie = VECTOR;
  optr->Arg_Car[idx].typ = ATYC_IF32;
  optr->Arg_Car[idx].array_dim = "1";
  optr->Arg_Car[idx].NbVal = "$Arg1.NbVal";
  /* l'unite et le sample se deduisent de l'entree  */
  optr->Arg_Car[idx].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[idx].sample = "$Arg1.sample";
  optr->Arg_Car[idx].ref_time = "$Arg1.ref_time";
  optr->Arg_Car[idx].misval = "$Arg1.misval";
  optr->Arg_Car[idx].unite = "$Arg1.unit";
  optr->Arg_Car[idx].famille = "$Arg1.famille";
  optr->Arg_Car[idx].name = "$Arg3";
  optr->Arg_Car[idx].en_name = "$Arg4";
}
