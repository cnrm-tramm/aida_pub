/****************************************************************
* OPERATOR 	correc_pics_angle_auto_unit  FUNCTION  ANSI-C
* 
* PURPOSE	correction of peaks
*
* DESCRIPTION   Cette fonction supprime les pics vers
*	   	le haut ou vers le bas qui se produisent
*		sur une seule valeur et qui sont superieur
*		a un seuil.
*
* VERSION         1.4
*
* ARGUMENTS 	IN 	float 	X   	parametre brut	
*		IN 	float 	seuil	seuil de detection d'un saut
*               IN      char*  unit       "Radian" ou "Degre"  Unité de mesure des angles 
* 		OUT 	float 	Xcor 	parametre corrige
*
* ENTRY		NONE
*
* SUBPROGRAMS 	NONE
* 
* REFERENCES	NONE
*
* CHANGES       1.2   added args' sampling description
* 
* COPYRIGHT 	Meteo-France
*		Centre de Recherches Meteorologiques
*		GMEI/MMA
*		42, av. G. Coriolis
*		31057	TOULOUSE cedex
*
******************************************************************/

#define _POSIX_SOURCE 1
#define _XOPEN_SOURCE 600
/* Le #define _HPUX_SOURCE n'est la que pour "voir" strdup */
#define _HPUX_SOURCE 1


#include <stdio.h>
#include <string.h>
#include <strings.h>
#include <math.h>
#include "struct_oper.h"

int
correc_pics_angle_auto_unit (unsigned long Nloop,
			     const float *X,
			     const float seuil, char *unit, float *Xcor)
{
  long i, j;
  long nbpic;
  double D_to_R;
  float ecart_angle_avant;
  float ecart_angle_apres;
  float z;

  if (!strcasecmp (unit, "degree") || !strcasecmp (unit, "Degree")
      || !strcasecmp (unit, "Degre") || !strcasecmp (unit, "degre"))
    {
      D_to_R = M_PI / 180.0;
    }
  else if (!strcasecmp (unit, "rad") || !strcasecmp (unit, "Rad")
	   || !strcasecmp (unit, "Radian") || !strcasecmp (unit, "radian"))
    {
      D_to_R = 1.0;
    }
  else
    {
      return -1;
    }

  if (seuil < 0.)
    {
      return -2;
    }

  if (seuil > M_PI / D_to_R)
    {
      return -3;
    }

  /* On saute les éventuelles premières valeurs manquantes */
  i = 0;
  while (i < Nloop && !isfinite (X[i]))
    {
      Xcor[i] = X[i];
      i++;
    }
  if (i >= Nloop)
    {
      return 0;
    }

  /* On suppose que le fichier ne démarre pas sur une donnée fausse.
   * à voir... */
  j = i;			/* j est l'indice du dernier "bon" */
  Xcor[j] = X[j];

  nbpic = 0;
  /* i est déjà initialisé */
  for (i = j + 1; i < (Nloop - 1); i++)
    {
      ecart_angle_avant = X[i] - X[j];
      while (ecart_angle_avant > (M_PI / D_to_R))
	ecart_angle_avant -= 2. * M_PI / D_to_R;
      while (ecart_angle_avant < -(M_PI / D_to_R))
	ecart_angle_avant += 2. * M_PI / D_to_R;
      ecart_angle_apres = X[i] - X[i + 1];
      while (ecart_angle_apres > (M_PI / D_to_R))
	ecart_angle_apres -= 2. * M_PI / D_to_R;
      while (ecart_angle_apres < -(M_PI / D_to_R))
	ecart_angle_apres += 2. * M_PI / D_to_R;
      if ((fabs (ecart_angle_avant) < seuil * sqrt (i - j))
	  || (fabs (ecart_angle_apres) < seuil)
	  || (ecart_angle_avant * ecart_angle_apres < 0.))
	{
	  Xcor[i] = X[i];
	  j = i;
	}
      else
	{
	  nbpic++;
	  /* Interpolation */
	  /* Cherchons le modulo 2*pi de x[i+1] tq |X[i+1]-X[j]| soit minimal */
	  z = X[i + 1];
	  while (z - X[j] > (M_PI / D_to_R))
	    z -= 2. * M_PI / D_to_R;
	  while (z - X[j] < -(M_PI / D_to_R))
	    z += 2. * M_PI / D_to_R;
	  Xcor[i] = ((i - j) * X[j] + z) / ((i - j) + 1);
	}
    }

  /* On suppose aussi que la dernière valeur est bonne.
   * Ce n'est pas plus certain que la première... */
  Xcor[Nloop-1] = X[Nloop-1];

  return nbpic;
}

/* fonction d'enrobage */

int
OP_correc_pics_angle_auto_unit (unsigned long Nbval,
				void *ArgList[], char *DiagExec)
{
  int CodRet;
  sprintf (DiagExec,
	   "correc_pics_angle_auto_unit (seuil = %g, unit=%s)",
	   *((float *) ArgList[1]), (char *) ArgList[2]);
  CodRet =
    correc_pics_angle_auto_unit (Nbval, (float *) ArgList[0],
				 *((float *) ArgList[1]),
				 (char *) ArgList[2], (float *) ArgList[3]);
  if (CodRet == -1)
    {
      strcat (DiagExec, "; Unité d'angle non reconnue");
      return OP_FAIL;
    }
  else if (CodRet == -2)
    {
      strcat (DiagExec, "; seuil negatif");
      return OP_FAIL;
    }
  else if (CodRet == -3)
    {
      strcat (DiagExec, "; seuil > 180 deg (ou Pi radians)");
      return OP_FAIL;
    }
  else if (CodRet >= 0)
    {
      sprintf (DiagExec + strlen (DiagExec),
	       "; Nombre de saut(s) corrige(s) : %d", CodRet);
    }
  return OP_OK;
}

void
ID_correc_pics_angle_auto_unit (oper * optr)
{
  strcpy (optr->Nom, "correc_pics_angle_auto_unit");
  optr->Version = "$Revision$";
  optr->Date = "$Date$";
  optr->fctptr = OP_correc_pics_angle_auto_unit;
  optr->NbArg = 4;

  /* X */
  optr->Arg_Car[0].direction = DIR_IN;
  optr->Arg_Car[0].categorie = VECTOR;
  optr->Arg_Car[0].typ = ATYC_IF32;
  optr->Arg_Car[0].array_dim = "1";
  optr->Arg_Car[0].unite = "";
  optr->Arg_Car[0].type_sample = "any";
  optr->Arg_Car[0].sample = "any";

  /* seuil */
  optr->Arg_Car[1].direction = DIR_IN;
  optr->Arg_Car[1].categorie = COEFFICIENT;
  optr->Arg_Car[1].typ = ATYC_IF32;
  optr->Arg_Car[1].array_dim = "1";
  optr->Arg_Car[1].unite = "";
  optr->Arg_Car[1].type_sample = NULL;
  optr->Arg_Car[1].sample = NULL;

  /* unit */
  optr->Arg_Car[2].direction = DIR_IN;
  optr->Arg_Car[2].categorie = COEFFICIENT;
  optr->Arg_Car[2].typ = ATYC_STRING;
  optr->Arg_Car[2].array_dim = "1";
  optr->Arg_Car[2].type_sample = NULL;
  optr->Arg_Car[2].sample = NULL;
  optr->Arg_Car[2].unite = "";

  /* XCor */
  optr->Arg_Car[3].direction = DIR_OUT;
  optr->Arg_Car[3].categorie = VECTOR;
  optr->Arg_Car[3].typ = ATYC_IF32;
  optr->Arg_Car[3].array_dim = "1";
  optr->Arg_Car[3].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[3].sample = "$Arg1.sample";
  optr->Arg_Car[3].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[3].ref_time = "$Arg1.ref_time";
  optr->Arg_Car[3].unite = "$Arg1.unit";
  optr->Arg_Car[3].famille = "$Arg1.famille";
  optr->Arg_Car[3].misval = "$Arg1.misval";
  optr->Arg_Car[3].name = "$Arg1.name + \"sans pics\" ";
  optr->Arg_Car[3].en_name = "$Arg1.english_name + \"without peeks\" ";
}
