/******************************************************************
*
* OPERATOR      Poly1_XsurY.c   FUNCTION  ANSI-C
*
* PURPOSE       Compute a ratio and then a 1rst order polynomial function
*
* DESCRIPTION   Standard calculation.... 
*
* VERSION       $Revision$
*
* ARGUMENTS   IN   float  Var_in_1   Any          "X" value
*             IN   float  Var_in_2   Any          "Y" value
*             IN   float  Coef_0     Any          Constant coefficient
*             IN   float  Coef_1     Any          coefficient of X
*             IN   float  Val_Def    Any          Value when y=0
*             OUT  float  Var_out  same as 2      Result
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

/* La vraie fonction... */
unsigned long
Poly1_XsurY (unsigned long NLoop,
	     const float *Var_in_1,
	     const float *Var_in_2,
	     float Coef_0,
	     float Coef_1,
	     float ValDef,
	     float *Var_out)
{
  unsigned long i, Nb_0;

  Nb_0 = 0;

  for (i = 0; i < NLoop; i++)
    {
      if (*Var_in_2 != 0)
	*Var_out = Coef_0 + Coef_1 * *Var_in_1 / *Var_in_2;
      else
	{
	  *Var_out = ValDef;
	  Nb_0++;
	}
      Var_in_1++;
      Var_in_2++;
      Var_out++;
    }

  return Nb_0;
}


/* la fonction d'enrobage classique */

int
OP_Poly1_XsurY (unsigned long NbVal, void *ArgList[], char *DiagExec)
{
  unsigned long CodRet;
  char TmpStr[48];

  (void) sprintf (DiagExec,
     "Poly1_XsurY, %lu echant., C0 = %g, C1 = %g (res = c0 + c1*X/Y), defval=%g",
		  NbVal,
		  *((float *) ArgList[2]),
		  *((float *) ArgList[3]),
		  *((float *) ArgList[4]));

  CodRet = Poly1_XsurY (NbVal,
			(float *) ArgList[0],
			(float *) ArgList[1],
			*((float *) ArgList[2]),
			*((float *) ArgList[3]),
			*((float *) ArgList[4]),
			(float *) ArgList[5]);

  if (CodRet != 0)
    {
      (void) sprintf (TmpStr, ", %lu", CodRet);
      strcat (DiagExec, TmpStr);
      strcat (DiagExec, " denominateurs nuls");
    }
  return OP_OK;
}

/* la fonction de description de l'operateur et ses arguments */

void
ID_Poly1_XsurY (oper * optr)
{
  strcpy (optr->Nom, "Poly1_XsurY");
  optr->Version = "$Revision$";
  optr->Date = "$Date$";
  optr->fctptr = OP_Poly1_XsurY;
  optr->repl_oper = "Poly1_XsurY_flt";
  optr->repl_cause = "ne permet pas de fixer l'unite du parametre calcule";
  optr->NbArg = 6;

  /* X */
  optr->Arg_Car[0].direction = DIR_IN;
  optr->Arg_Car[0].categorie = VECTOR;
  optr->Arg_Car[0].typ = ATYC_IF32;
  optr->Arg_Car[0].array_dim = "1";
  optr->Arg_Car[0].type_sample = "any";
  optr->Arg_Car[0].sample = "any";
  optr->Arg_Car[0].unite = "any";
  optr->Arg_Car[0].famille = "any";

  /* Y */
  optr->Arg_Car[1].direction = DIR_IN;
  optr->Arg_Car[1].categorie = VECTOR;
  optr->Arg_Car[1].typ = ATYC_IF32;
  optr->Arg_Car[1].array_dim = "1";
  optr->Arg_Car[1].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[1].type_sample = "any";
  optr->Arg_Car[1].sample = "any";
  optr->Arg_Car[1].unite = "any";

 /* Coef_0 */
  optr->Arg_Car[2].direction = DIR_IN;
  optr->Arg_Car[2].categorie = COEFFICIENT;
  optr->Arg_Car[2].array_dim = "1";
  optr->Arg_Car[2].typ = ATYC_IF32;
  optr->Arg_Car[2].unite = "any";
  optr->Arg_Car[2].type_sample = NULL;	/* sans signification pour COEFFICIENT */
  optr->Arg_Car[2].sample = NULL;

 /* Coef_1 */
  optr->Arg_Car[3].direction = DIR_IN;
  optr->Arg_Car[3].categorie = COEFFICIENT;
  optr->Arg_Car[3].array_dim = "1";
  optr->Arg_Car[3].typ = ATYC_IF32;
  optr->Arg_Car[3].unite = "any";
  optr->Arg_Car[3].type_sample = NULL;	/* sans signification pour COEFFICIENT */
  optr->Arg_Car[3].sample = NULL;

  optr->Arg_Car[4].direction = DIR_IN;
  optr->Arg_Car[4].categorie = COEFFICIENT;
  optr->Arg_Car[4].array_dim = "1";
  optr->Arg_Car[4].typ = ATYC_IF32;
  optr->Arg_Car[4].unite = "any";
  optr->Arg_Car[4].type_sample = NULL;	/* sans signification pour COEFFICIENT */
  optr->Arg_Car[4].sample = NULL;

  /* Var_out */
  optr->Arg_Car[5].direction = DIR_OUT;
  optr->Arg_Car[5].categorie = VECTOR;
  optr->Arg_Car[5].typ = ATYC_IF32;
  optr->Arg_Car[5].array_dim = "1";
  optr->Arg_Car[5].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[5].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[5].sample = "$Arg1.sample";
  optr->Arg_Car[5].ref_time = "$Arg1.ref_time";
  optr->Arg_Car[5].unite = "unknown";
  optr->Arg_Car[5].famille = " \"auto\" ";

}
