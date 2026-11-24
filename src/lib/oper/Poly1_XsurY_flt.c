/******************************************************************
*
* OPERATOR      Poly1_XsurY_flt.c   FUNCTION  ANSI-C
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
*             IN   char	  unit_out   			  Unit of result
*             IN   char   name                    Name of result
*             IN   char   en_name                 English_name of result
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
Poly1_XsurY_flt (unsigned long NLoop,
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
OP_Poly1_XsurY_flt (unsigned long NbVal, void *ArgList[], char *DiagExec)
{
  unsigned long CodRet;
  char TmpStr[48];

  (void) sprintf (DiagExec,
		  "Poly_1_XsurY_flt, %lu echant., calcul de  z = %g + %g x / y",
		  NbVal, *((float *) ArgList[2]), *((float *) ArgList[3]));

  CodRet = Poly1_XsurY_flt (NbVal,
			(float *) ArgList[0],
			(float *) ArgList[1],
			*((float *) ArgList[2]),
			*((float *) ArgList[3]),
			*((float *) ArgList[4]),
			(float *) ArgList[8]);

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
ID_Poly1_XsurY_flt (oper * optr)
{
  strcpy (optr->Nom, "Poly1_XsurY_flt");
  optr->Version = "$Revision$";
  optr->Date = "$Date$";
  optr->fctptr = OP_Poly1_XsurY_flt;
  optr->NbArg = 9;

  /* Var_in_1 */
  optr->Arg_Car[0].direction = DIR_IN;
  optr->Arg_Car[0].categorie = VECTOR;
  optr->Arg_Car[0].typ = ATYC_IF32;
  optr->Arg_Car[0].array_dim = "1";
  optr->Arg_Car[0].type_sample = "any";
  optr->Arg_Car[0].sample = "any";
  optr->Arg_Car[0].unite = "any";
  optr->Arg_Car[0].famille = "any";

  /* Var_in_2 */
  optr->Arg_Car[1].direction = DIR_IN;
  optr->Arg_Car[1].categorie = VECTOR;
  optr->Arg_Car[1].typ = ATYC_IF32;
  optr->Arg_Car[1].array_dim = "1";
  optr->Arg_Car[1].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[1].type_sample = "any";
  optr->Arg_Car[1].sample = "any";
  optr->Arg_Car[1].unite = "any";

  /* C0 */
  optr->Arg_Car[2].direction = DIR_IN;
  optr->Arg_Car[2].categorie = COEFFICIENT;
  optr->Arg_Car[2].array_dim = "1";
  optr->Arg_Car[2].typ = ATYC_IF32;
  optr->Arg_Car[2].unite = "any";
  optr->Arg_Car[2].type_sample = NULL;	/* sans signification pour COEFFICIENT */
  optr->Arg_Car[2].sample = NULL;

  /* C1 */
  optr->Arg_Car[3].direction = DIR_IN;
  optr->Arg_Car[3].categorie = COEFFICIENT;
  optr->Arg_Car[3].array_dim = "1";
  optr->Arg_Car[3].typ = ATYC_IF32;
  optr->Arg_Car[3].unite = "any";

  /* ValDef */
  optr->Arg_Car[4].direction = DIR_IN;
  optr->Arg_Car[4].categorie = COEFFICIENT;
  optr->Arg_Car[4].array_dim = "1";
  optr->Arg_Car[4].typ = ATYC_IF32;
  optr->Arg_Car[4].unite = "any";

  /* Unit */
  optr->Arg_Car[5].direction = DIR_IN;
  optr->Arg_Car[5].categorie = COEFFICIENT;
  optr->Arg_Car[5].array_dim = "1";
  optr->Arg_Car[5].typ = ATYC_STRING;

  /* Name */
  optr->Arg_Car[6].direction = DIR_IN;
  optr->Arg_Car[6].categorie = COEFFICIENT;
  optr->Arg_Car[6].array_dim = "1";
  optr->Arg_Car[6].typ = ATYC_STRING;

  /* English_name */
  optr->Arg_Car[7].direction = DIR_IN;
  optr->Arg_Car[7].categorie = COEFFICIENT;
  optr->Arg_Car[7].array_dim = "1";
  optr->Arg_Car[7].typ = ATYC_STRING;

  /* Var_out */
  optr->Arg_Car[8].direction = DIR_OUT;
  optr->Arg_Car[8].categorie = VECTOR;
  optr->Arg_Car[8].typ = ATYC_IF32;
  optr->Arg_Car[8].array_dim = "1";
  optr->Arg_Car[8].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[8].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[8].sample = "$Arg1.sample";
  optr->Arg_Car[8].ref_time = "$Arg1.ref_time";
  optr->Arg_Car[8].unite = "$Arg6";
  optr->Arg_Car[8].name = "$Arg7";
  optr->Arg_Car[8].en_name = "$Arg8";
  optr->Arg_Car[8].famille = "auto";
}
