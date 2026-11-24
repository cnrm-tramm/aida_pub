/****************************************************
*
* OPERATOR      MoinsI.c   FUNCTION  ANSI-C
*
* PURPOSE       Compute Arg1 - Arg 2 in INT_16
*
* DESCRIPTION   operation arithmetique "-"
*
* VERSION       $Revision$
*
* ARGUMENTS   IN   short int  input_1    Any             first value
*             IN   short int  input_2    Any             second value
*             OUT  short int  output   same as 1 and 2   Result
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
*
* COPYRIGHT     Meteo-France
*
* AGREEMENT
*#########################################################################*/

#define _POSIX_SOURCE 1
#define _XOPEN_SOURCE 600

#include <stdio.h>
#include <string.h>
#include "struct_oper.h"


void
MoinsI (unsigned long NLoop,
	const short int *input_1,	/* en ... any */
	const short int *input_2,	/* en ... any  */
	short int *output)
{
  unsigned long i;

  for (i = 0; i < NLoop; i++)
    {
      *output = *input_1 - *input_2;

      input_1++;
      input_2++;
      output++;
    }
}

/* la fonction d'enrobage classique */

int
OP_MoinsI (unsigned long NbVal, void *ArgList[], char *DiagExec)
{
  int NCar;

  NCar = sprintf (DiagExec, "MoinsI : (%ld echant.) ", NbVal) ;
  if (NCar < 0)
    NCar = 0;
  DiagExec += NCar;

  MoinsI (NbVal,
	  (short int *) ArgList[0],
	  (short int *) ArgList[1],
	  (short int *) ArgList[2]);
  return OP_OK;
}

void
ID_MoinsI (oper * optr)
{
  strcpy (optr->Nom, "MoinsI");
  optr->Version = "$Revision$";
  optr->Date = "$Date$";
  optr->fctptr = OP_MoinsI;
  optr->NbArg = 3;		/* doit rester inf. a FIL_MAX_ARG */
  optr->Arg_Car[0].direction = DIR_IN;
  optr->Arg_Car[0].categorie = VECTOR;
  optr->Arg_Car[0].typ = ATYC_I16;
  optr->Arg_Car[0].array_dim = "1";
  optr->Arg_Car[0].type_sample = "any";
  optr->Arg_Car[0].sample = "any";
  optr->Arg_Car[0].unite = "any";

  optr->Arg_Car[1].direction = DIR_IN;
  optr->Arg_Car[1].categorie = VECTOR;
  optr->Arg_Car[1].typ = ATYC_I16;
  optr->Arg_Car[1].array_dim = "1";
  optr->Arg_Car[1].type_sample = "any";
  optr->Arg_Car[1].sample = "any";
  optr->Arg_Car[1].unite = "any";
  /*  le mieux serait :
  optr->Arg_Car[1].unite = "$Arg1.unit"; */

  optr->Arg_Car[2].direction = DIR_OUT;
  optr->Arg_Car[2].categorie = VECTOR;
  optr->Arg_Car[2].typ = ATYC_I16;
  optr->Arg_Car[2].array_dim = "1";
  optr->Arg_Car[2].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[2].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[2].sample = "$Arg1.sample";
  optr->Arg_Car[2].ref_time = "$Arg1.ref_time";
  optr->Arg_Car[2].unite = "$Arg1.unit";
  optr->Arg_Car[2].famille = "\"auto\"";
  optr->Arg_Car[2].misval = "$Arg1.misval";
}
