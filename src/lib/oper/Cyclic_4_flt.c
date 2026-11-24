/******************************************************************
*
* OPERATOR      Cyclic_4_flt.c   FUNCTION  ANSI-C
*
* PURPOSE       Compute a four-harmonic function.
*
* DESCRIPTION   C0 + C_1_cos * cos (x) + C_1_sin * sin (x) +  C_2_cos * cos (2*x) + C_2_sin * sin (2*x) + ...
*
* VERSION       1.1
*
* ARGUMENTS   IN   float  Var_in     Any          "X" value
*             IN   float  X_to_rad   Any          Coefficient converting X into radians
*             IN   float  C_0        Any          Constant coefficient
*             IN   float  C_1_cos    Any          coefficient of cos of first wave ()
*             IN   float  C_1_sin    Any          coefficient of sin of first wave ()
*             IN   float  C_2_cos    Any          coefficient of cos of second wave ()
*             IN   float  C_2_sin    Any          coefficient of sin of second wave ()
*             IN   float  C_3_cos    Any          coefficient of cos of third wave ()
*             IN   float  C_3_sin    Any          coefficient of sin of third wave ()
*             IN   float  C_4_cos    Any          coefficient of cos of fourth wave ()
*             IN   float  C_4_sin    Any          coefficient of sin of fourth wave ()
*             IN   string unit_out                Unit of the result
*             IN   string name_out                Name of the result
*             IN   string en_name_out             English name of the result
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
Cyclic_4_flt (unsigned long NLoop,
	      const float *Var_in,
	      const float X_to_rad,
	      const float C_0,
	      const float C_1_cos, const float C_1_sin,
	      const float C_2_cos, const float C_2_sin,
	      const float C_3_cos, const float C_3_sin,
	      const float C_4_cos, const float C_4_sin, float *Var_out)
{
  unsigned long i;
  register double x;

  for (i = 0; i < NLoop; i++)
    {
      x = Var_in[i] * X_to_rad;
      Var_out[i] = C_0 +
	C_1_cos * cos (x) + C_1_sin * sin (x) +
	C_2_cos * cos (2 * x) + C_2_sin * sin (2 * x) +
	C_3_cos * cos (3 * x) + C_3_sin * sin (3 * x) +
	C_4_cos * cos (4 * x) + C_4_sin * sin (4 * x);
    }
  return i;
}


/* la fonction d'enrobage classique */

int
OP_Cyclic_4_flt (unsigned long NbVal, void *ArgList[], char *DiagExec)
{
  unsigned long CodRet;

  (void) sprintf (DiagExec,
		  "Cyclic_4_flt(%lu ech), %g, Cste=%g, 1:(c%g, s%g), ...%s, %s, %s)",
		  NbVal,
		  *((float *) ArgList[1]), *((float *) ArgList[2]),
		  *((float *) ArgList[3]), 
		  *((float *) ArgList[4]), (char *) ArgList[11],
		  (char *) ArgList[12], (char *) ArgList[13]);

/* Le lecteur attentif aura remarqué que les arguments Nr 11, 12, 13 
 * ne sont pas passés à la routine de calcul. En fait, ils ne servent
 * qu'à remplir le champ "unit", "name", "english_name" du vecteur de sortie.
 */
  CodRet = Cyclic_4_flt (NbVal,
			 (float *) ArgList[0],
			 *((float *) ArgList[1]),
			 *((float *) ArgList[2]),
			 *((float *) ArgList[3]),
			 *((float *) ArgList[4]),
			 *((float *) ArgList[5]),
			 *((float *) ArgList[6]),
			 *((float *) ArgList[7]),
			 *((float *) ArgList[8]),
			 *((float *) ArgList[9]),
			 *((float *) ArgList[10]), (float *) ArgList[14]);
  if (CodRet == NbVal)
    return OP_OK;
  else
    return OP_FAIL;
}

/* la fonction de description de l'operateur et ses arguments */

void
ID_Cyclic_4_flt (oper * optr)
{
  int i;
  strcpy (optr->Nom, "Cyclic_4_flt");
  optr->Version = "$Revision$";
  optr->Date = "$Date$";
  optr->fctptr = OP_Cyclic_4_flt;
  optr->NbArg = 15;

  /* Var_in  */
  optr->Arg_Car[0].direction = DIR_IN;
  optr->Arg_Car[0].categorie = VECTOR;
  optr->Arg_Car[0].typ = ATYC_IF32;
  optr->Arg_Car[0].array_dim = "1";
  optr->Arg_Car[0].type_sample = "any";
  optr->Arg_Car[0].sample = "any";
  optr->Arg_Car[0].unite = "any";

  /*  X_to_rad  */
  optr->Arg_Car[1].direction = DIR_IN;
  optr->Arg_Car[1].categorie = COEFFICIENT;
  optr->Arg_Car[1].array_dim = "1";
  optr->Arg_Car[1].typ = ATYC_IF32;
  optr->Arg_Car[1].type_sample = NULL;	/* sans signification pour COEFFICIENT */
  optr->Arg_Car[1].sample = NULL;
  optr->Arg_Car[1].unite = "any";

  /*  C_0, C_1_cos, C_1_sin, ... C_4_sin  */
  for (i = 2; i < 11; i++)
    {
      optr->Arg_Car[i].direction = DIR_IN;
      optr->Arg_Car[i].categorie = COEFFICIENT;
      optr->Arg_Car[i].array_dim = "1";
      optr->Arg_Car[i].typ = ATYC_IF32;
      optr->Arg_Car[i].type_sample = NULL;	/* sans signification pour COEFFICIENT */
      optr->Arg_Car[i].sample = NULL;
      optr->Arg_Car[i].unite = "any";
    }

  /*  unit_out  */
  optr->Arg_Car[11].direction = DIR_IN;
  optr->Arg_Car[11].categorie = COEFFICIENT;
  optr->Arg_Car[11].array_dim = "1";
  optr->Arg_Car[11].typ = ATYC_STRING;
  optr->Arg_Car[11].type_sample = NULL;	/* sans signification pour COEFFICIENT */
  optr->Arg_Car[11].sample = NULL;
  optr->Arg_Car[11].unite = "any";

  /*  name_out  */
  optr->Arg_Car[12].direction = DIR_IN;
  optr->Arg_Car[12].categorie = COEFFICIENT;
  optr->Arg_Car[12].array_dim = "1";
  optr->Arg_Car[12].typ = ATYC_STRING;
  optr->Arg_Car[12].type_sample = NULL;	/* sans signification pour COEFFICIENT */
  optr->Arg_Car[12].sample = NULL;
  optr->Arg_Car[12].unite = "any";

  /*  en_name_out  */
  optr->Arg_Car[13].direction = DIR_IN;
  optr->Arg_Car[13].categorie = COEFFICIENT;
  optr->Arg_Car[13].array_dim = "1";
  optr->Arg_Car[13].typ = ATYC_STRING;
  optr->Arg_Car[13].type_sample = NULL;	/* sans signification pour COEFFICIENT */
  optr->Arg_Car[13].sample = NULL;
  optr->Arg_Car[13].unite = "any";

  /* Var_out  */
  optr->Arg_Car[14].direction = DIR_OUT;
  optr->Arg_Car[14].categorie = VECTOR;
  optr->Arg_Car[14].typ = ATYC_IF32;
  optr->Arg_Car[14].array_dim = "1";
  optr->Arg_Car[14].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[14].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[14].sample = "$Arg1.sample";
  optr->Arg_Car[14].ref_time = "$Arg1.ref_time";
  optr->Arg_Car[14].misval = "$Arg1.misval";
  optr->Arg_Car[14].unite = "$Arg12";
  optr->Arg_Car[14].name = "$Arg13";
  optr->Arg_Car[14].en_name = "$Arg14";
  optr->Arg_Car[14].famille = " \"auto\" ";

}
