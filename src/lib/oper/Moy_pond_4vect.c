/****************************************************
*
* OPERATOR       Moy_pond_4vect   FUNCTION  ANSI-C
*
* PURPOSE        Computes weighted mean of 4 parameters
*
* DESCRIPTION    
*
* VERSION        1.0
*
* ARGUMENTS    IN   float  X1    Any             first value
*              IN   float  X2    Any             second value
*              IN   float  X3    Any             third value
*              IN   float  X4    Any             fourth value
*              IN   float  C1    Any             weight of C1
*              IN   float  C2    Any             weight of C2
*              IN   float  C3    Any             weight of C3
*              IN   float  C4    Any             weight of C4
*              IN   string name_out                Name of the result
*              IN   string en_name_out             English name of the result
*
*              OUT  float  output   same as 1    weighted mean
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

void
Moy_pond_4vect (unsigned long NLoop,
      const float *X1,	
      const float *X2,
      const float *X3,
      const float *X4,
      const float C1,
      const float C2,
      const float C3,
      const float C4,
      float *output)
{
  unsigned long i;
  float som_C;

  som_C = C1 + C2 + C3 + C4; 

  for (i = 0; i < NLoop; i++)
    {
      output[i] = ( C1*X1[i] + C2*X2[i] + C3*X3[i] + C4*X4[i] ) / som_C ; 

    }
}


/* la fonction d'enrobage classique */

int
OP_Moy_pond_4vect (unsigned long NbVal, void *ArgList[], char *DiagExec)
{

  (void) sprintf (DiagExec, "Moy_pond_4vect, %lu echant., creation de %s (\"%s\")",
		  NbVal, (char *) ArgList[8], (char *) ArgList[9]);

  Moy_pond_4vect (NbVal,
	(float *) ArgList[0], 
	(float *) ArgList[1],
	(float *) ArgList[2],
	(float *) ArgList[3],
	*((float *) ArgList[4]),
	*((float *) ArgList[5]),
	*((float *) ArgList[6]),
	*((float *) ArgList[7]),
       	(float *) ArgList[10]);

  return OP_OK;
}

void
ID_Moy_pond_4vect (oper * optr)
{
  strcpy (optr->Nom, "Moy_pond_4vect");
  optr->Version = "$Revision: 5097 $";
  optr->Date = "$Date: 2013-03-25 13:23:40 +0100 (lun. 25 mars 2013) $";
  optr->fctptr = OP_Moy_pond_4vect;
  optr->NbArg = 11;		/* doit rester inf. a FIL_MAX_ARG */

  /* X1 */
  optr->Arg_Car[0].direction = DIR_IN;
  optr->Arg_Car[0].categorie = VECTOR;
  optr->Arg_Car[0].typ = ATYC_IF32;
  optr->Arg_Car[0].array_dim = "1";
  optr->Arg_Car[0].type_sample = "any";
  optr->Arg_Car[0].sample = "any";
  optr->Arg_Car[0].unite = "any";
  optr->Arg_Car[0].famille = "any";

  /* X2 */
  optr->Arg_Car[1].direction = DIR_IN;
  optr->Arg_Car[1].categorie = VECTOR;
  optr->Arg_Car[1].typ = ATYC_IF32;
  optr->Arg_Car[1].array_dim = "1";
  optr->Arg_Car[1].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[1].type_sample = "any";
  optr->Arg_Car[1].sample = "any";
  optr->Arg_Car[1].unite = "$Arg1.unit";
  optr->Arg_Car[1].famille = "any";

 /* X3 */
  optr->Arg_Car[2].direction = DIR_IN;
  optr->Arg_Car[2].categorie = VECTOR;
  optr->Arg_Car[2].typ = ATYC_IF32;
  optr->Arg_Car[2].array_dim = "1";
  optr->Arg_Car[2].type_sample = "any";
  optr->Arg_Car[2].sample = "any";
  optr->Arg_Car[2].unite = "any";
  optr->Arg_Car[2].famille = "any";

  /* X4 */
  optr->Arg_Car[3].direction = DIR_IN;
  optr->Arg_Car[3].categorie = VECTOR;
  optr->Arg_Car[3].typ = ATYC_IF32;
  optr->Arg_Car[3].array_dim = "1";
  optr->Arg_Car[3].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[3].type_sample = "any";
  optr->Arg_Car[3].sample = "any";
  optr->Arg_Car[3].unite = "$Arg1.unit";
  optr->Arg_Car[3].famille = "any";

/* C1 */
  optr->Arg_Car[4].direction = DIR_IN;
  optr->Arg_Car[4].categorie = COEFFICIENT;
  optr->Arg_Car[4].typ = ATYC_IF32;
  optr->Arg_Car[4].array_dim = "1";
  optr->Arg_Car[4].type_sample = NULL;
  optr->Arg_Car[4].sample = NULL;
  optr->Arg_Car[4].unite = "any";
  optr->Arg_Car[4].famille = "any";

/* C2 */
  optr->Arg_Car[5].direction = DIR_IN;
  optr->Arg_Car[5].categorie = COEFFICIENT;
  optr->Arg_Car[5].typ = ATYC_IF32;
  optr->Arg_Car[5].array_dim = "1";
  optr->Arg_Car[5].type_sample = NULL;
  optr->Arg_Car[5].sample = NULL;
  optr->Arg_Car[5].unite = "any";
  optr->Arg_Car[5].famille = "any";

/* C3 */
  optr->Arg_Car[6].direction = DIR_IN;
  optr->Arg_Car[6].categorie = COEFFICIENT;
  optr->Arg_Car[6].typ = ATYC_IF32;
  optr->Arg_Car[6].array_dim = "1";
  optr->Arg_Car[6].type_sample = NULL;
  optr->Arg_Car[6].sample = NULL;
  optr->Arg_Car[6].unite = "any";
  optr->Arg_Car[6].famille = "any";

/* C4 */
  optr->Arg_Car[7].direction = DIR_IN;
  optr->Arg_Car[7].categorie = COEFFICIENT;
  optr->Arg_Car[7].typ = ATYC_IF32;
  optr->Arg_Car[7].array_dim = "1";
  optr->Arg_Car[7].type_sample = NULL;
  optr->Arg_Car[7].sample = NULL;
  optr->Arg_Car[7].unite = "any";
  optr->Arg_Car[7].famille = "any";

  /* name_out      */
  optr->Arg_Car[8].direction = DIR_IN;
  optr->Arg_Car[8].categorie = COEFFICIENT;
  optr->Arg_Car[8].array_dim = "1";
  optr->Arg_Car[8].typ = ATYC_STRING;
  optr->Arg_Car[8].type_sample = NULL;	/* sans signification pour COEFFICIENT */
  optr->Arg_Car[8].sample = NULL;
  optr->Arg_Car[8].unite = "any";

  /* en_name_out      */
  optr->Arg_Car[9].direction = DIR_IN;
  optr->Arg_Car[9].categorie = COEFFICIENT;
  optr->Arg_Car[9].array_dim = "1";
  optr->Arg_Car[9].typ = ATYC_STRING;
  optr->Arg_Car[9].type_sample = NULL;	/* sans signification pour COEFFICIENT */
  optr->Arg_Car[9].sample = NULL;
  optr->Arg_Car[9].unite = "any";

  /* output */
  optr->Arg_Car[10].direction = DIR_OUT;
  optr->Arg_Car[10].categorie = VECTOR;
  optr->Arg_Car[10].typ = ATYC_IF32;
  optr->Arg_Car[10].array_dim = "1";
  optr->Arg_Car[10].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[10].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[10].sample = "$Arg1.sample";
  optr->Arg_Car[10].ref_time = "$Arg1.ref_time";
  optr->Arg_Car[10].unite = "$Arg1.unit";
  optr->Arg_Car[10].famille = "auto";
  optr->Arg_Car[10].name = "$Arg9";
  optr->Arg_Car[10].en_name = "$Arg10";
  optr->Arg_Car[10].misval = "$Arg1.misval";

}
