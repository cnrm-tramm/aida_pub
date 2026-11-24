/*************************************************************************
*
* OPERATOR         Calc_sst.c  FUNCTION ANSI-C
*
* PURPOSE          Calcul de la température de la mer (sst) à partir des données
*                  du thermosalinomètre.
* DESCRIPTION     Calcul à partir de la température interne,(donnée fournie par
*                 le thermosalinomètre et passée en fréquence absolue) et des
*                 coefficients d'étalonnage.
*
* VERSION          1.0 
*
* ARGUMENTS  
*            IN   float   T_INT_THSAL	température interne en fréquence absolue
*            IN   float   coef_a	coefficient d'étalonnage
*            IN   float   coef_b	coefficient d'étalonnage
*            IN   float   coef_c        coefficient d'étalonnage  
*            IN   float   coef_d	coefficient d'étalonnage
*            IN   float   coef_f0       coefficient d'étalonnage 
*                                       
*
*            OUT  float   SST           température en degrés Celsius
*            
*            
*
* ENTRY        NONE
*        
* SUBPROGRAMS  NONE
*        
* REFERENCES   Document IFREMER (spécifications fonctionnelles du logiciel
*              TS_TERMES)
*
* COPYRIGHT    Meteo-France
*	       Centre National de Recherches Meteorologiques 
*	       GMEI/ TRAMM
*	       42, av G. Coriolis
*	       31057 TOULOUSE cedex  
*
*
*############################################################################*/

#define _POSIX_SOURCE 1
#define _XOPEN_SOURCE 600
#define _HPUX_SOURCE 1
#ifndef K_T0
#define K_T0 273.15
#endif

#include <math.h>
#include <stdio.h>
#include <string.h>
#include <math.h>
#include "struct_oper.h"


int
Calc_sst (unsigned long ndata,
	  const float *T_INT_THSAL,
	  const float coef_a,
	  const float coef_b,
	  const float coef_c,
	  const float coef_d,
      const float coef_f0,
      float *SST)
{
  unsigned long i;
  double x;

  for (i = 0; i < ndata; i++)
    {
      if (!isfinite (*T_INT_THSAL) || *T_INT_THSAL < 0)
	*SST = K_NaN;
      else
	{
	  x = log (coef_f0 / *T_INT_THSAL);
	  *SST =
	    1.0 / (coef_a + coef_b * x + coef_c * x * x + coef_d * x * x * x) -
	    K_T0;
	}
      T_INT_THSAL++;
      SST++;
    }

  return 0;
}


/* la fonction d'enrobage classique */

int
OP_Calc_sst (unsigned long NbVal, void *ArgList[], char *DiagExec)
{
  (void) sprintf (DiagExec, "Calc_sst, %lu echant.", NbVal);

  Calc_sst (NbVal,
	    (float *) ArgList[0],
	    *(float *) ArgList[1],
	    *(float *) ArgList[2],
	    *(float *) ArgList[3],
	    *(float *) ArgList[4],
	    *(float *) ArgList[5],
        (float *) ArgList[6]);

  return OP_OK;
}

void
ID_Calc_sst (oper * optr)
{
  strcpy (optr->Nom, "Calc_sst");
  optr->Version = "$Revision$";
  optr->Date = "$Date$";
  optr->fctptr = OP_Calc_sst;
  optr->NbArg = 7;		/* doit rester inf. a FIL_MAX_ARG */

  /* T_INT_THSAL */
  optr->Arg_Car[0].direction = DIR_IN;
  optr->Arg_Car[0].categorie = VECTOR;
  optr->Arg_Car[0].typ = ATYC_IF32;
  optr->Arg_Car[0].array_dim = "1";
  optr->Arg_Car[0].type_sample = "any";
  optr->Arg_Car[0].sample = "any";
  optr->Arg_Car[0].unite = "hertz";

  /* coef_a */
  optr->Arg_Car[1].direction = DIR_IN;
  optr->Arg_Car[1].categorie = COEFFICIENT;
  optr->Arg_Car[1].typ = ATYC_IF32;
  optr->Arg_Car[1].array_dim = "1";
  optr->Arg_Car[1].unite = "";

  /* coef_b */
  optr->Arg_Car[2].direction = DIR_IN;
  optr->Arg_Car[2].categorie = COEFFICIENT;
  optr->Arg_Car[2].typ = ATYC_IF32;
  optr->Arg_Car[2].array_dim = "1";
  optr->Arg_Car[2].unite = "";

  /* coef_c */
  optr->Arg_Car[3].direction = DIR_IN;
  optr->Arg_Car[3].categorie = COEFFICIENT;
  optr->Arg_Car[3].typ = ATYC_IF32;
  optr->Arg_Car[3].array_dim = "1";
  optr->Arg_Car[3].unite = "";

  /* coef_d */
  optr->Arg_Car[4].direction = DIR_IN;
  optr->Arg_Car[4].categorie = COEFFICIENT;
  optr->Arg_Car[4].typ = ATYC_IF32;
  optr->Arg_Car[4].array_dim = "1";
  optr->Arg_Car[4].unite = "";

  /* coef_f0 */
  optr->Arg_Car[5].direction = DIR_IN;
  optr->Arg_Car[5].categorie = COEFFICIENT;
  optr->Arg_Car[5].typ = ATYC_IF32;
  optr->Arg_Car[5].array_dim = "1";
  optr->Arg_Car[5].unite = "";

  /* SST */
  optr->Arg_Car[6].direction = DIR_OUT;
  optr->Arg_Car[6].categorie = VECTOR;
  optr->Arg_Car[6].typ = ATYC_IF32;
  optr->Arg_Car[6].array_dim = "1";
  optr->Arg_Car[6].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[6].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[6].sample = "$Arg1.sample";
  optr->Arg_Car[6].ref_time = "$Arg1.ref_time";
  optr->Arg_Car[6].unite = "celsius";
  optr->Arg_Car[6].misval = "$Arg1.misval";
  optr->Arg_Car[6].name = "$Arg1.name";
  optr->Arg_Car[6].en_name = "$Arg1.english_name";
}
