/****************************************************
*
* OPERATOR       Foiss.c   FUNCTION  ANSI-C
*
* PURPOSE        Computes Arg1 * Arg 2, Arg1 est vecteur, Arg2 est scalaire
*
* DESCRIPTION    operation arithmetique "*"
*
* VERSION        1.0
*
* ARGUMENTS    IN   short int *input_1    Any             first value
*              IN   float      input_2    Any             second value
*              OUT  short int *output     same as 1 and 2 Result
*
* ENTRY            
*                 
* SUBPROGRAMS    none
*
* FILES   
*
* REFERENCES   
*
* CHANGES              
*
* COPYRIGHT      Meteo-France
*
* AGREEMENT      The author wishes that .....
*#########################################################################*/

#define _POSIX_SOURCE 1
#define _XOPEN_SOURCE 600
/* Le #define _HPUX_SOURCE n'est la que pour "voir" strdup */
#define _HPUX_SOURCE 1

#include <stdio.h>
#include <string.h>
#include "struct_oper.h"


int
Foiss (const unsigned long int NLoop,
       const short int *input_1,	/* en ... any */
       const float input_2,	/* en ... any  */
       short int *output)
{
  unsigned long int i;

  for (i = 0; i < NLoop; i++)
    {
      *output = (short int) (((float) (*input_1)) * input_2);

      input_1++;
      output++;
    }
}


/* la fonction d'enrobage classique */

int
OP_Foiss (unsigned long int NbVal, void *ArgList[], char *DiagExec)
{
  int CodRet;
  int NCar;

  NCar = sprintf (DiagExec, "Foiss : (%ld echant.) ", NbVal) ;
  if (NCar < 0)
    NCar = 0;
  DiagExec += NCar;

  CodRet = Foiss (NbVal,
		  (short int *) ArgList[0],
		  *((float *) ArgList[1]),
		  (short int *) ArgList[2]);
  
  return OP_OK;
}

void
ID_Foiss (oper * optr)
{
  strcpy (optr->Nom, "Foiss");
  optr->Version = "1.0";
  optr->Date = "06/17/97";
  optr->fctptr = OP_Foiss;
  optr->NbArg = 3;		/* doit rester inf. a FIL_MAX_ARG */
  optr->Arg_Car[0].direction = DIR_IN;
  optr->Arg_Car[0].categorie = VECTOR;
  optr->Arg_Car[0].typ = ATYC_I16;
  optr->Arg_Car[0].array_dim = "1";
  optr->Arg_Car[0].type_sample = "any";
  optr->Arg_Car[0].sample = "any";
  optr->Arg_Car[0].unite = "any";

  optr->Arg_Car[1].direction = DIR_IN;
  optr->Arg_Car[1].categorie = COEFFICIENT;
  optr->Arg_Car[1].typ = ATYC_IF32;
  optr->Arg_Car[1].array_dim = "1";
  optr->Arg_Car[1].type_sample = "any";
  optr->Arg_Car[1].sample = "any";
  optr->Arg_Car[1].unite = "any";

  optr->Arg_Car[2].direction = DIR_OUT;
  optr->Arg_Car[2].categorie = VECTOR;
  optr->Arg_Car[2].typ = ATYC_I16;
  optr->Arg_Car[2].array_dim = "1";
  optr->Arg_Car[2].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[2].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[2].sample = "$Arg1.sample";
  optr->Arg_Car[2].ref_time = "$Arg1.ref_time";
  optr->Arg_Car[2].unite = "unknown";
  optr->Arg_Car[2].misval = "$Arg1.misval";

}
