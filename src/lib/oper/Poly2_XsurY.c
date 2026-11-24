/******************************************************************
*
* OPERATOR      Poly2_XsurY.c   FUNCTION  ANSI-C
*
* PURPOSE       Compute a ratio and then a 2nd order polynomial function
*
* DESCRIPTION   Standard calculation.... 
*
* VERSION       $Revision$
*
* ARGUMENTS   IN   float  Var_in_1   Any          "X" value
*             IN   float  Var_in_2   Any          "Y" value
*             IN   float  Coef_0     Any          Constant coefficient
*             IN   float  Coef_1     Any          coefficient of X/Y
*	      IN   float  Coef_2     Any          coefficient of (X/Y)^2
*	      IN   float  ValDef     Any          Taken Value X/Y is not define
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
/* Le #define _HPUX_SOURCE n'est la que pour "voir" strdup */
#define _HPUX_SOURCE 1

#include <stdio.h>
#include <string.h>
#include "struct_oper.h"

/* La vraie fonction... */
unsigned long
Poly2_XsurY (unsigned long NLoop,
	     const float *Var_in_1,
	     const float *Var_in_2,
	     float Coef_0,
	     float Coef_1, float Coef_2, float ValDef, float *Var_out)
{
  unsigned long i;
  unsigned long nb_2_zero = 0;

  double Z;

  for (i = 0; i < NLoop; i++)
    {
      if (*Var_in_2 != 0)
	{
	  Z = *Var_in_1 / *Var_in_2;
	  *Var_out = Coef_0 + Coef_1 * Z + Coef_2 * Z * Z;
	}
      else
	{
	  *Var_out = ValDef;
	  nb_2_zero++;
	}

      Var_in_1++;
      Var_in_2++;
      Var_out++;
    }
  return nb_2_zero;
}


/* la fonction d'enrobage classique */

int
OP_Poly2_XsurY (unsigned long NbVal, void *ArgList[], char *DiagExec)
{
  unsigned long CodRet;
  int NCar;

  NCar = sprintf (DiagExec,
		  "Poly2_XsurY(%lu ech), calcul de %g + %g x/y + %g (x/y)^2, ou %g si y==0",
		  NbVal, *((float *) ArgList[2]),
		  *((float *) ArgList[3]), *((float *) ArgList[4]),
		  *((float *) ArgList[5]));
  if (NCar > 0)
    DiagExec += NCar;


  CodRet = Poly2_XsurY (NbVal,
			(float *) ArgList[0],
			(float *) ArgList[1],
			*((float *) ArgList[2]),
			*((float *) ArgList[3]),
			*((float *) ArgList[4]),
			*((float *) ArgList[5]), (float *) ArgList[6]);

  sprintf (DiagExec, ", %lu div. par zero", CodRet);
  return OP_OK;
}

/* la fonction de description de l'operateur et ses arguments */

void
ID_Poly2_XsurY (oper * optr)
{
  strcpy (optr->Nom, "Poly2_XsurY");
  optr->Version = "$Revision$";
  optr->Date = "$Date$";
  optr->fctptr = OP_Poly2_XsurY;
  optr->NbArg = 7;

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
  optr->Arg_Car[1].famille = "any";

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

  /* Coef_2 */
  optr->Arg_Car[3].direction = DIR_IN;
  optr->Arg_Car[4].direction = DIR_IN;
  optr->Arg_Car[4].categorie = COEFFICIENT;
  optr->Arg_Car[4].array_dim = "1";
  optr->Arg_Car[4].typ = ATYC_IF32;
  optr->Arg_Car[4].unite = "any";
  optr->Arg_Car[4].type_sample = NULL;	/* sans signification pour COEFFICIENT */
  optr->Arg_Car[4].sample = NULL;

  /* ValDef */
  optr->Arg_Car[5].direction = DIR_IN;
  optr->Arg_Car[5].categorie = COEFFICIENT;
  optr->Arg_Car[5].array_dim = "1";
  optr->Arg_Car[5].typ = ATYC_IF32;
  optr->Arg_Car[5].unite = "any";
  optr->Arg_Car[5].type_sample = NULL;	/* sans signification pour COEFFICIENT */
  optr->Arg_Car[5].sample = NULL;

  /* Var_out */
  optr->Arg_Car[6].direction = DIR_OUT;
  optr->Arg_Car[6].categorie = VECTOR;
  optr->Arg_Car[6].typ = ATYC_IF32;
  optr->Arg_Car[6].array_dim = "1";
  optr->Arg_Car[6].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[6].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[6].sample = "$Arg1.sample";
  optr->Arg_Car[6].ref_time = "$Arg1.ref_time";
  optr->Arg_Car[6].unite = "unknown";
  optr->Arg_Car[6].famille = "$Arg1.famille";

}
