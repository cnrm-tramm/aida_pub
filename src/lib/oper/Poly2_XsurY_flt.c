/******************************************************************
*
* OPERATOR      Poly2_XsurY_flt.c   FUNCTION  ANSI-C
*
* PURPOSE       Compute a ratio and then a 2nd order polynomial function
*
* DESCRIPTION   Standard calculation.... 
*
* VERSION       $Revision$
*
* ARGUMENTS   IN  float  Var_in_1   Any      "X" value
*             IN  float  Var_in_2   Any      "Y" value
*             IN  float  Coef_0     Any      Constant coefficient
*             IN  float  Coef_1     Any      coefficient of X/Y
*	      IN  float  Coef_2     Any      coefficient of (X/Y)^2
*	      IN  float  ValDef     Any      Returned value if X/Y is not defined
*	      IN  char   unit_out            Unit of the result
*
*             OUT float  Var_out   unit_out  Result
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
Poly2_XsurY_flt (unsigned long NLoop,
		 const float *Var_in_1,
		 const float *Var_in_2,
		 float Coef_0,
		 float Coef_1,
                 float Coef_2,
                 float ValDef,
                 float *Var_out)
{
  unsigned long i;
  unsigned long nb_undef = 0;
  double Z;

  for (i = 0; i < NLoop; i++)
    {
      if (*Var_in_2 != 0.0)
	{
	  Z = *Var_in_1 / *Var_in_2;
	  *Var_out = Coef_0 + Z * (Coef_1 + Z * Coef_2);
	}
      else
	{
	  *Var_out = ValDef;
	  nb_undef++;
	}

      Var_in_1++;
      Var_in_2++;
      Var_out++;
    }
  return nb_undef;
}


/* la fonction d'enrobage classique */

int
OP_Poly2_XsurY_flt (unsigned long NbVal, void *ArgList[], char *DiagExec)
{
  unsigned long CodRet;
  int NCar;

  NCar = sprintf (DiagExec, "Poly2_XsurY_flt : (%ld echant.) ", NbVal) ;
  if (NCar < 0)
    NCar = 0;
  DiagExec += NCar;

  /* L'argument Nr 6 n'est pas passé à la routine de calcul : il ne
   * sert qu'à remplir le champ "unit" du vecteur de sortie. */
  CodRet = Poly2_XsurY_flt (NbVal,
			    (float *) ArgList[0],
			    (float *) ArgList[1],
			    *((float *) ArgList[2]),
			    *((float *) ArgList[3]),
			    *((float *) ArgList[4]),
			    *((float *) ArgList[5]),
                            (float *) ArgList[7]);
  if (CodRet > 0)
    {
      sprintf (DiagExec, "%lu val. undef remplacee par %f", CodRet,
	       *((float *) ArgList[5]));
    }

  return OP_OK;
}

/* la fonction de description de l'operateur et ses arguments */

void
ID_Poly2_XsurY_flt (oper * optr)
{
  strcpy (optr->Nom, "Poly2_XsurY_flt");
  optr->Version = "$Revision$";
  optr->Date = "$Date$";
  optr->fctptr = OP_Poly2_XsurY_flt;
  optr->NbArg = 8;

  /*  Var_in_1 */
  optr->Arg_Car[0].direction = DIR_IN;
  optr->Arg_Car[0].categorie = VECTOR;
  optr->Arg_Car[0].typ = ATYC_IF32;
  optr->Arg_Car[0].array_dim = "1";
  optr->Arg_Car[0].type_sample = "any";
  optr->Arg_Car[0].sample = "any";
  optr->Arg_Car[0].unite = "any";
  optr->Arg_Car[0].famille = "any";

  /*  Var_in_2 */
  optr->Arg_Car[1].direction = DIR_IN;
  optr->Arg_Car[1].categorie = VECTOR;
  optr->Arg_Car[1].typ = ATYC_IF32;
  optr->Arg_Car[1].array_dim = "1";
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
  optr->Arg_Car[4].direction = DIR_IN;
  optr->Arg_Car[4].categorie = COEFFICIENT;
  optr->Arg_Car[4].array_dim = "1";
  optr->Arg_Car[4].typ = ATYC_IF32;
  optr->Arg_Car[4].unite = "any";
  optr->Arg_Car[4].type_sample = NULL;	/* sans signification pour COEFFICIENT */
  optr->Arg_Car[4].sample = NULL;

  optr->Arg_Car[5].direction = DIR_IN;
  optr->Arg_Car[5].categorie = COEFFICIENT;
  optr->Arg_Car[5].array_dim = "1";
  optr->Arg_Car[5].typ = ATYC_IF32;
  optr->Arg_Car[5].unite = "any";
  optr->Arg_Car[5].type_sample = NULL;	/* sans signification pour COEFFICIENT */
  optr->Arg_Car[5].sample = NULL;

  optr->Arg_Car[6].direction = DIR_IN;
  optr->Arg_Car[6].categorie = COEFFICIENT;
  optr->Arg_Car[6].array_dim = "1";
  optr->Arg_Car[6].typ = ATYC_STRING;
  optr->Arg_Car[6].type_sample = NULL;
  optr->Arg_Car[6].sample = NULL;
  optr->Arg_Car[6].unite = "any";

  optr->Arg_Car[7].direction = DIR_OUT;
  optr->Arg_Car[7].categorie = VECTOR;
  optr->Arg_Car[7].typ = ATYC_IF32;
  optr->Arg_Car[7].array_dim = "1";
  optr->Arg_Car[7].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[7].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[7].sample = "$Arg1.sample";
  optr->Arg_Car[7].ref_time = "$Arg1.ref_time";
  optr->Arg_Car[7].unite = "$Arg7";
  optr->Arg_Car[7].famille = "$Arg1.famille";
}
