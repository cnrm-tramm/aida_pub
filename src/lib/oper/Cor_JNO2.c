/******************************************************************
*
* OPERATOR      Cor_JNO2.c   FUNCTION  ANSI-C
*
* PURPOSE       Corrects JNO2 measurements.
*
* DESCRIPTION   JNO2
*
* VERSION       $Revision$
*
* ARGUMENTS   IN   float  JNO2_brut  s-1         raw measuremenst
*             IN   float  T_s        K or °C     ambiant temperature
*             IN   float  Coef_0     Any         First coefficient
*             IN   float  Coef_1     Any         Second coefficient
*	      IN   float  Coef_2     Any         Third coefficient
*	      IN   float  MisVal     Any         special value for missing
*             OUT  float  J_NO2_cor  s-1         Result
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

#define T_IN_C (0)
#define T_IN_K (1)

/* La vraie fonction... */
int
Cor_JNO2 (unsigned long NLoop,
	  const float *JNO2_brut,
	  const float *T_s,
	  float Coef_0,
	  float Coef_1,
	  float Coef_2,
	  float MisVal,
	  float *J_NO2_cor)
{
  unsigned long i;

  float KtoC;
  double Z;

  /* On devine l'unite Celsius/Kelvins */
  if (T_s[NLoop / 2] > 100.)
    /* Kelvin */
    KtoC = -273.15;
  else
    /* Celsius */
    KtoC = 0.0;

  for (i = 0; i < NLoop; i++)
    {
      if (*JNO2_brut != MisVal)
	{
	  Z = Coef_0 - Coef_1 / (Coef_2 - (*T_s + KtoC));
	  *J_NO2_cor = *JNO2_brut * Z;
	}
      else
	*J_NO2_cor = MisVal;

      JNO2_brut++;
      T_s++;
      J_NO2_cor++;
    }
 
  if ( KtoC == 0.0)
    return T_IN_C;
  else
    return T_IN_K;
}


/* la fonction d'enrobage classique */

int
OP_Cor_JNO2 (unsigned long NbVal, void *ArgList[], char *DiagExec)
{
  int CodRet;
  int NCar;

  NCar = sprintf (DiagExec, "Cor_JNO2 : (%ld echant.) ", NbVal) ;
  if (NCar < 0)
    NCar = 0;
  DiagExec += NCar;

  CodRet = Cor_JNO2 (NbVal,
		     (float *) ArgList[0],
		     (float *) ArgList[1],
		     *((float *) ArgList[2]),
		     *((float *) ArgList[3]),
		     *((float *) ArgList[4]),
		     *((float *) ArgList[5]),
		     (float *) ArgList[6]);

  switch (CodRet)
    {
      case T_IN_C: strcat (DiagExec, " Tempé reconnue en °C;");
                   break;
      case T_IN_K: strcat (DiagExec, " Tempé reconnue en K;");
                   break;
    }
  return OP_OK;
}

/* la fonction de description de l'operateur et ses arguments */

void
ID_Cor_JNO2 (oper * optr)
{
  strcpy (optr->Nom, "Cor_JNO2");
  optr->Version = "$Revision$";
  optr->Date = "$Date$";
  optr->fctptr = OP_Cor_JNO2;
  optr->NbArg = 7;
  optr->Arg_Car[0].direction = DIR_IN;
  optr->Arg_Car[0].categorie = VECTOR;
  optr->Arg_Car[0].typ = ATYC_IF32;
  optr->Arg_Car[0].array_dim = "1";
  optr->Arg_Car[0].type_sample = "any";
  optr->Arg_Car[0].sample = "any";
  optr->Arg_Car[0].unite = "s-1";
  optr->Arg_Car[0].famille = "\"physicochimie\"";

  optr->Arg_Car[1].direction = DIR_IN;
  optr->Arg_Car[1].categorie = VECTOR;
  optr->Arg_Car[1].typ = ATYC_IF32;
  optr->Arg_Car[1].array_dim = "1";
  optr->Arg_Car[1].type_sample = "any";
  optr->Arg_Car[1].sample = "any";
  optr->Arg_Car[1].unite = "K";
  optr->Arg_Car[1].famille = "\"temperature\"";

  optr->Arg_Car[2].direction = DIR_IN;
  optr->Arg_Car[2].categorie = COEFFICIENT;
  optr->Arg_Car[2].array_dim = "1";
  optr->Arg_Car[2].typ = ATYC_IF32;
  optr->Arg_Car[2].unite = "any";
  optr->Arg_Car[2].type_sample = NULL;	/* sans signification pour COEFFICIENT */
  optr->Arg_Car[2].sample = NULL;

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

  optr->Arg_Car[5].direction = DIR_IN;
  optr->Arg_Car[5].categorie = COEFFICIENT;
  optr->Arg_Car[5].array_dim = "1";
  optr->Arg_Car[5].typ = ATYC_IF32;
  optr->Arg_Car[5].unite = "any";
  optr->Arg_Car[5].type_sample = NULL;	/* sans signification pour COEFFICIENT */
  optr->Arg_Car[5].sample = NULL;

  optr->Arg_Car[6].direction = DIR_OUT;
  optr->Arg_Car[6].categorie = VECTOR;
  optr->Arg_Car[6].typ = ATYC_IF32;
  optr->Arg_Car[6].array_dim = "1";
  optr->Arg_Car[6].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[6].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[6].sample = "$Arg1.sample";
  optr->Arg_Car[6].ref_time = "$Arg1.ref_time";
  optr->Arg_Car[6].unite = "s-1";
  optr->Arg_Car[6].famille = " \"physicochimie\" ";
}
