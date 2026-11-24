/****************************************************************
* OPERATOR 	correcKingdata  FUNCTION  ANSI-C
* 
* PURPOSE	correction of peaks in king-probe data
*
* DESCRIPTION   Cette fonction supprime la plupart des pics
*               des donnees du king-probe pendant SCMS.
*               Ces pics ont pour caracteristiques d'etre
*               toujours vers le bas et sur une valeur.
*
* VERSION         1.4
*
* ARGUMENTS 	IN 	float 	Pw 	puissance king-probe brute
*		IN 	float 	seuil	seuil de detection d'un saut
* 		OUT 	float 	Pwcor 	puissance corrigee
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
#define _XOPEN_SOURCE_EXTENDED 1


#include <stdio.h>
#include <string.h>
#include "struct_oper.h"

int
correcKingdata (unsigned long Nloop,
		const float *Pw,
		const float seuil,
		float *Pwcor)
{
  unsigned long i;
  float moy;

  Pwcor[0] = Pw[0];

  for (i = 1; i < (Nloop - 1); i++)
    {
      moy = (Pw[i - 1] + Pw[i + 1]) / 2.;

      if ((Pw[i] - moy) < seuil)
	Pwcor[i] = moy;
      else
	Pwcor[i] = Pw[i];
    }

  Pwcor[Nloop - 1] = Pw[Nloop - 1];

  return 0;
}

/* fonction d'enrobage */

int
OP_correcKingdata (unsigned long Nbval, void *ArgList[], char *DiagExec)
{
  int CodRet = correcKingdata (Nbval,
			       (float *) ArgList[0],
			       *((float *) ArgList[1]),
			       (float *) ArgList[2]);

  return OP_OK;
}

void
ID_correcKingdata (oper * optr)
{
  strcpy (optr->Nom, "correcKingdata");
  optr->Version = "1.4";
  optr->Date = "08/26/96";
  optr->fctptr = OP_correcKingdata;
  optr->NbArg = 3;

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
  optr->Arg_Car[1].type_sample = NULL;
  optr->Arg_Car[1].sample = NULL;

  optr->Arg_Car[2].direction = DIR_OUT;
  optr->Arg_Car[2].categorie = VECTOR;
  optr->Arg_Car[2].typ = ATYC_IF32;
  optr->Arg_Car[2].array_dim = "1";
  optr->Arg_Car[2].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[2].sample = "$Arg1.sample";
  optr->Arg_Car[2].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[2].unite = "";
}
