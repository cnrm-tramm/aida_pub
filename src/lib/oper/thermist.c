/****************************************************
*
* OPERATOR      thermist.c   FUNCTION  ANSI-C
*
* PURPOSE       Calcul d'une température à partir de la mesure de résistance
*               d'une thermistance (Loi de Steinhart-Hart). 
*
* DESCRIPTION   La loi de transformation est l'inverse d'un
*               polynome du quatrième degre, appliqué à ln(R), 
*               avec 2 jeux de coefficients qui s'appliquent
*		de part et d'autre d'un seuil. Le coefficient de
*		degré 2 est généralement nul.
*
* VERSION       1.0
*
* ARGUMENTS   IN   float  resist      kOhm     	resistance
*             IN   float  Coef_1[4]   Any	coefficient for resist <= seuil 
*             IN   float  Coef_2[4]   Any	coefficient for resist > seuil
*	      IN   float  seuil       Any	seuil a partir on applique
*						le polynome avec Coef_2.
*
*             OUT  float  Tempe       		Temperature	
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
#define _XOPEN_SOURCE_EXTENDED 1

#include <stdio.h>
#include <string.h>
#include <math.h>
#include "struct_oper.h"

unsigned long
thermist (unsigned long NLoop,
	  const float *resist,
	  const float Coef_1[],
	  const float Coef_2[],
          float seuil, float *tempe)
{
  unsigned long i;

  double y, z;
  unsigned long nb_sup, nb_inf, nb_undef;
  nb_sup = 0;
  nb_inf = 0;
  nb_undef = 0;

  for (i = 0; i < NLoop; i++)
    {
      y = log ((double) resist[i]);	/* y=ln(resist) */

      if (resist[i] > seuil)
	{
	  nb_sup++;
	  z = (Coef_2[3] * y * y * y) +
	    (Coef_2[2] * y * y) + (Coef_2[1] * y) + Coef_2[0];

	  tempe[i] = 1. / z;
	}
      else if (resist[i] <= seuil)
	{
	  nb_inf++;
	  z = (Coef_1[3] * y * y * y) +
	    (Coef_1[2] * y * y) + (Coef_1[1] * y) + Coef_1[0];

	  tempe[i] = 1. / z;
	}
      else			/* cas des NaN, ... */
	{
	  nb_undef++;
	  tempe[i] = resist[i];
	}
    }
  return nb_undef;
}


/* la fonction d'enrobage classique */

int
OP_thermist (unsigned long NbVal, void *ArgList[], char *DiagExec)
{
  unsigned long CodRet;

  float Coef_1[4];
  float Coef_2[4];

  Coef_1[0] = *((float *) ArgList[1]);
  Coef_1[1] = *((float *) ArgList[2]);
  Coef_1[2] = *((float *) ArgList[3]);
  Coef_1[3] = *((float *) ArgList[4]);

  Coef_2[0] = *((float *) ArgList[5]);
  Coef_2[1] = *((float *) ArgList[6]);
  Coef_2[2] = *((float *) ArgList[7]);
  Coef_2[3] = *((float *) ArgList[8]);

  sprintf (DiagExec, "Seuil=%e;", *((float *) ArgList[9]));

  sprintf (DiagExec + strlen (DiagExec), " Coef_1 : [%e, %e, %e, %e],",
		  Coef_1[0], Coef_1[1], Coef_1[2], Coef_1[3]);

  sprintf (DiagExec + strlen (DiagExec), " Coef_2 : [%e, %e, %e, %e]",
		  Coef_2[0], Coef_2[1], Coef_2[2], Coef_2[3]);

  CodRet = thermist (NbVal,
		     (float *) ArgList[0],
		     Coef_1,
		     Coef_2, 
                     *((float *) ArgList[9]), (float *) ArgList[10]);

  sprintf (DiagExec + strlen (DiagExec), " %lu val. manquante(s) sur %lu;",
	   CodRet, NbVal);
  return OP_OK;
}

/* la fonction de description de l'operateur et ses arguments */

void
ID_thermist (oper * optr)
{
  strcpy (optr->Nom, "thermist");
  optr->Version = "$Revision$";
  optr->Date = "$Date$";
  optr->fctptr = OP_thermist;
  optr->NbArg = 11;

  /* resist */
  optr->Arg_Car[0].direction = DIR_IN;
  optr->Arg_Car[0].categorie = VECTOR;
  optr->Arg_Car[0].typ = ATYC_IF32;
  optr->Arg_Car[0].array_dim = "1";
  optr->Arg_Car[0].type_sample = "any";
  optr->Arg_Car[0].sample = "any";
  optr->Arg_Car[0].unite = "kohm";

  optr->Arg_Car[1].direction = DIR_IN;
  optr->Arg_Car[1].categorie = COEFFICIENT;
  optr->Arg_Car[1].array_dim = "1";
  optr->Arg_Car[1].typ = ATYC_IF32;
  optr->Arg_Car[1].type_sample = NULL;
  optr->Arg_Car[1].sample = NULL;

  optr->Arg_Car[2].direction = DIR_IN;
  optr->Arg_Car[2].categorie = COEFFICIENT;
  optr->Arg_Car[2].array_dim = "1";
  optr->Arg_Car[2].typ = ATYC_IF32;
  optr->Arg_Car[2].type_sample = NULL;
  optr->Arg_Car[2].sample = NULL;

  optr->Arg_Car[3].direction = DIR_IN;
  optr->Arg_Car[3].categorie = COEFFICIENT;
  optr->Arg_Car[3].array_dim = "1";
  optr->Arg_Car[3].typ = ATYC_IF32;
  optr->Arg_Car[3].type_sample = NULL;
  optr->Arg_Car[3].sample = NULL;

  optr->Arg_Car[4].direction = DIR_IN;
  optr->Arg_Car[4].categorie = COEFFICIENT;
  optr->Arg_Car[4].array_dim = "1";
  optr->Arg_Car[4].typ = ATYC_IF32;
  optr->Arg_Car[4].type_sample = NULL;
  optr->Arg_Car[4].sample = NULL;

  optr->Arg_Car[5].direction = DIR_IN;
  optr->Arg_Car[5].categorie = COEFFICIENT;
  optr->Arg_Car[5].array_dim = "1";
  optr->Arg_Car[5].typ = ATYC_IF32;
  optr->Arg_Car[5].type_sample = NULL;
  optr->Arg_Car[5].sample = NULL;

  optr->Arg_Car[6].direction = DIR_IN;
  optr->Arg_Car[6].categorie = COEFFICIENT;
  optr->Arg_Car[6].array_dim = "1";
  optr->Arg_Car[6].typ = ATYC_IF32;
  optr->Arg_Car[6].type_sample = NULL;
  optr->Arg_Car[6].sample = NULL;

  optr->Arg_Car[7].direction = DIR_IN;
  optr->Arg_Car[7].categorie = COEFFICIENT;
  optr->Arg_Car[7].array_dim = "1";
  optr->Arg_Car[7].typ = ATYC_IF32;
  optr->Arg_Car[7].type_sample = NULL;
  optr->Arg_Car[7].sample = NULL;

  optr->Arg_Car[8].direction = DIR_IN;
  optr->Arg_Car[8].categorie = COEFFICIENT;
  optr->Arg_Car[8].array_dim = "1";
  optr->Arg_Car[8].typ = ATYC_IF32;
  optr->Arg_Car[8].type_sample = NULL;
  optr->Arg_Car[8].sample = NULL;

  /* seuil */
  optr->Arg_Car[9].direction = DIR_IN;
  optr->Arg_Car[9].categorie = COEFFICIENT;
  optr->Arg_Car[9].array_dim = "1";
  optr->Arg_Car[9].typ = ATYC_IF32;
  optr->Arg_Car[9].type_sample = NULL;
  optr->Arg_Car[9].sample = NULL;

  /* tempe */
  optr->Arg_Car[10].direction = DIR_OUT;
  optr->Arg_Car[10].categorie = VECTOR;
  optr->Arg_Car[10].typ = ATYC_IF32;
  optr->Arg_Car[10].array_dim = "1";
  optr->Arg_Car[10].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[10].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[10].sample = "$Arg1.sample";
  optr->Arg_Car[10].ref_time = "$Arg1.ref_time";
  optr->Arg_Car[10].unite = "Kelvin";
  optr->Arg_Car[10].famille = "$Arg1.famille";
  optr->Arg_Car[10].name = "\"Temperature issue de \" + $Arg1.name";
  optr->Arg_Car[10].en_name = "\"Temperature from \" + $Arg1.english_name";
}
