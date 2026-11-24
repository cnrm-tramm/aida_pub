/****************************************************************
* OPERATOR 	correc_saut_angle_auto_unit  FUNCTION  ANSI-C
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

long
correc_saut_angle_auto_unit (unsigned long Nloop,
	     const float *X,
	     const float seuil,
	     char*  unit,
	     float *Xcor)
{
  unsigned long i;
  long j;
  long nbsaut;
  double D_to_R;
  float ecart_angle;

 if (!strcasecmp (unit, "degree") || !strcasecmp (unit, "Degree") || !strcasecmp (unit, "Degre") || !strcasecmp (unit, "degre"))
    {
      D_to_R = M_PI/180.0;
    }
  else if (!strcasecmp (unit, "rad") ||!strcasecmp (unit, "Rad") ||!strcasecmp (unit, "Radian") || !strcasecmp (unit, "radian"))
    {
      D_to_R = 1.0;
    }
  else
    {
    return -1;
    }
    
  /*on suppose que le fichier ne démarre pas sur une donnée fausse  */
  /* à voir */
  Xcor[0] = X[0];

  nbsaut = 0;
  j = 0; /* j est l'indice du dernier "bon" */
  
  for (i = 1; i < (Nloop - 1); i++)
  {
     ecart_angle = (int)fabsf (X[i] - X[j]) % (int)(2.0 * M_PI/D_to_R);
     if ((ecart_angle < seuil*(i-j)) || (ecart_angle > (2.0 * M_PI/D_to_R) - (seuil*(i-j))))
     {
        Xcor[i] = X[i];
	j =i ;
     }
     else
     {
        if ( sqrt(i-j) * seuil > 360 )  /* bof! on va considérer que la dernière valeur est ok ce qui peut
	être totalement faux */
	{
           Xcor[i] = X[i];
	   j =i ;
	}
	else
	{
	   Xcor[i] = K_NaN;
	   ++nbsaut;
	}
     }

  }

  return nbsaut;
}

/* fonction d'enrobage */

int
OP_correc_saut_angle_auto_unit (unsigned long Nbval, void *ArgList[], char *DiagExec)
{
  long CodRet;

  sprintf (DiagExec, "seuil = %f", *((float *) ArgList[1]));

  CodRet = correc_saut_angle_auto_unit (Nbval,
			(float *) ArgList[0],
			*((float *) ArgList[1]),
			(char  *) ArgList[2],
			(float *) ArgList[3]);
  if (CodRet == -1)
    {
      strcat (DiagExec, "Unité d'angle non reconnue\n");
    }

  else if (CodRet > 0)
    {
      sprintf (DiagExec + strlen (DiagExec),
	       "; Nombre de saut(s) corrige(s) : %ld", CodRet);
    }
  return OP_OK;
}

void
ID_correc_saut_angle_auto_unit (oper * optr)
{
  strcpy (optr->Nom, "correc_saut_angle_auto_unit");
  optr->Version = "1.0";
  optr->Date = "18/05/01";
  optr->fctptr = OP_correc_saut_angle_auto_unit;
  optr->NbArg = 4;

  /*  X */
  optr->Arg_Car[0].direction = DIR_IN;
  optr->Arg_Car[0].categorie = VECTOR;
  optr->Arg_Car[0].typ = ATYC_IF32;
  optr->Arg_Car[0].array_dim = "1";
  optr->Arg_Car[0].unite = "";
  optr->Arg_Car[0].type_sample = "any";
  optr->Arg_Car[0].sample = "any";

  optr->Arg_Car[1].direction = DIR_IN;
  optr->Arg_Car[1].categorie = COEFFICIENT;
  optr->Arg_Car[1].typ = ATYC_IF32;
  optr->Arg_Car[1].array_dim = "1";
  optr->Arg_Car[1].unite = "";
  
  optr->Arg_Car[2].direction = DIR_IN;
  optr->Arg_Car[2].categorie = COEFFICIENT;
  optr->Arg_Car[2].typ = ATYC_STRING;
  optr->Arg_Car[2].array_dim = "1";
  optr->Arg_Car[2].unite = "";
  
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
}
