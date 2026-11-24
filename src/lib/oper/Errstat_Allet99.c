/****************************************************
*
* OPERATOR      Errstat_Allet99.c   FUNCTION  ANSI-C
*
* PURPOSE       Calcul de l'erreur de pression statique
*		
* DESCRIPTION   L'erreur de statique est calculee 
*               en fonction de :
*			- la pression statique 
*			- le tangage 
*			- le roulis
*			- la supression dynamique
*
* VERSION       1.0
*
* ARGUMENTS   IN   float  Ps          hPa	Pression statique brute
*             IN   float  Tang	      degres	Angle de Tangage de l'avion
*             IN   float  Roul        degres	Angle de Roulis de l'avion
*	      IN   float  DP          hPa	Surpression dynamique
*	      IN   float  C0	       -	Coefficient
*	      IN   float  C2	       -	Coefficient
*	      IN   float  C3	       -	Coefficient
*	      IN   float  C4	       -	Coefficient
*	      IN   float  C5	       -	Coefficient
*
*             OUT  float  Errstat     hPa	Erreur de statique
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
#define _XOPEN_SOURCE_EXTENDED 1

#include <stdio.h>
#include <string.h>
#include <math.h>
#include "struct_oper.h"

int
Errstat_Allet99 (unsigned long NLoop,
	  const float *Ps,
	  const float *Tang,
	  const float *Roul,
	  const float *DP,
	  const float C0,
	  const float C1,
	  const float C2,
	  const float C3,
	  const float C4,
	  float *Errstat )
{
  unsigned long i;

  fprintf (stderr, " Coef_1 : %e %e %e %e %e\n",
	   C0,C1,C2,C3,C4);

  for (i = 0; i < NLoop; i++)
    {
      Errstat[i] = C0 +
                   C1 * Ps[i] +
                   C2 * Tang[i] +
                   C3 * Roul[i] +
                   C4 * DP[i] ;
    }
  return OP_OK;
}


/* la fonction d'enrobage classique */

int
OP_Errstat_Allet99 (unsigned long NbVal, void *ArgList[], char *DiagExec)
{
  int CodRet;

  CodRet = Errstat_Allet99 (NbVal,
		     (float *) ArgList[0],
		     (float *) ArgList[1],
		     (float *) ArgList[2],
		     (float *) ArgList[3],
		     *((float *) ArgList[4]),
		     *((float *) ArgList[5]),
		     *((float *) ArgList[6]),
		     *((float *) ArgList[7]),
		     *((float *) ArgList[8]),
		     (float *) ArgList[9]);

  return 0;
}

/* la fonction de description de l'operateur et ses arguments */

void
ID_Errstat_Allet99 (oper * optr)
{
  int k;
  
  strcpy (optr->Nom, "Errstat_Allet99");
  optr->Version = "$Revision$";
  optr->Date = "$Date$";
  optr->fctptr = OP_Errstat_Allet99;
  optr->NbArg = 10;

  k = 0;        /* Ps */
  optr->Arg_Car[k].direction = DIR_IN;
  optr->Arg_Car[k].categorie = VECTOR;
  optr->Arg_Car[k].typ = ATYC_IF32;
  optr->Arg_Car[k].array_dim = "1";
  optr->Arg_Car[k].type_sample = "any";
  optr->Arg_Car[k].sample = "any";
  optr->Arg_Car[k].unite = "hPa";

  k = 1;       /* Tang */
  optr->Arg_Car[k].direction = DIR_IN;
  optr->Arg_Car[k].categorie = VECTOR;
  optr->Arg_Car[k].typ = ATYC_IF32;
  optr->Arg_Car[k].array_dim = "1";
  optr->Arg_Car[k].type_sample = "any";
  optr->Arg_Car[k].sample = "any";
  optr->Arg_Car[k].unite = "degres";
  
  k = 2;       /* Roul */
  optr->Arg_Car[k].direction = DIR_IN;
  optr->Arg_Car[k].categorie = VECTOR;
  optr->Arg_Car[k].typ = ATYC_IF32;
  optr->Arg_Car[k].array_dim = "1";
  optr->Arg_Car[k].type_sample = "any";
  optr->Arg_Car[k].sample = "any";
  optr->Arg_Car[k].unite = "degres";
  
  k = 3;       /* dP */
  optr->Arg_Car[k].direction = DIR_IN;
  optr->Arg_Car[k].categorie = VECTOR;
  optr->Arg_Car[k].typ = ATYC_IF32;
  optr->Arg_Car[k].array_dim = "1";
  optr->Arg_Car[k].type_sample = "any";
  optr->Arg_Car[k].sample = "any";
  optr->Arg_Car[k].unite = "hPa";

  k = 4;
  optr->Arg_Car[k].direction = DIR_IN;
  optr->Arg_Car[k].categorie = COEFFICIENT;
  optr->Arg_Car[k].array_dim = "1";
  optr->Arg_Car[k].typ = ATYC_IF32;
  optr->Arg_Car[k].type_sample = NULL;
  optr->Arg_Car[k].sample = NULL;

  k = 5;
  optr->Arg_Car[k].direction = DIR_IN;
  optr->Arg_Car[k].categorie = COEFFICIENT;
  optr->Arg_Car[k].array_dim = "1";
  optr->Arg_Car[k].typ = ATYC_IF32;
  optr->Arg_Car[k].type_sample = NULL;
  optr->Arg_Car[k].sample = NULL;

  k = 6;
  optr->Arg_Car[k].direction = DIR_IN;
  optr->Arg_Car[k].categorie = COEFFICIENT;
  optr->Arg_Car[k].array_dim = "1";
  optr->Arg_Car[k].typ = ATYC_IF32;
  optr->Arg_Car[k].type_sample = NULL;
  optr->Arg_Car[k].sample = NULL;
  
  k = 7;
  optr->Arg_Car[k].direction = DIR_IN;
  optr->Arg_Car[k].categorie = COEFFICIENT;
  optr->Arg_Car[k].array_dim = "1";
  optr->Arg_Car[k].typ = ATYC_IF32;
  optr->Arg_Car[k].type_sample = NULL;
  optr->Arg_Car[k].sample = NULL;
  
  k = 8;
  optr->Arg_Car[k].direction = DIR_IN;
  optr->Arg_Car[k].categorie = COEFFICIENT;
  optr->Arg_Car[k].array_dim = "1";
  optr->Arg_Car[k].typ = ATYC_IF32;
  optr->Arg_Car[k].type_sample = NULL;
  optr->Arg_Car[k].sample = NULL;

  k = 9;
  optr->Arg_Car[k].direction = DIR_OUT;
  optr->Arg_Car[k].categorie = VECTOR;
  optr->Arg_Car[k].typ = ATYC_IF32;
  optr->Arg_Car[k].array_dim = "1";
  optr->Arg_Car[k].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[k].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[k].sample = "$Arg1.sample";
  optr->Arg_Car[k].ref_time = "$Arg1.ref_time";
  optr->Arg_Car[k].unite = "hPa";
}
