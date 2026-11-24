/*************************************************************************
*
* OPERATOR         remplace_valeur.c  FUNCTION ANSI-C
*
* PURPOSE          remplace dans un vecteur une donnée positionnée à l'indice
*                  passé en argument par la valeur de remplacement passée en argument.
*
* DESCRIPTION      
*
* VERSION          1.0 
*
* ARGUMENTS  
*            IN   float   vect		vecteur de données quelconque
*            IN   int     indice        de 0 à ndata-1
*            IN   float   val           valeur de remplacement ou misval
*
*            OUT  float   vect_cor      vecteur corrigé
*            
*            
*
* ENTRY        NONE
*        
* SUBPROGRAMS  NONE
*        
* REFERENCES   
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

#include <stdio.h>
#include <string.h>

#include "struct_oper.h"

int
remplace_valeur (unsigned long ndata,
		 const float *vect,
		 int indice, float val, float *vect_cor)
{
  unsigned long i;

  if (indice < 0)
    return -1;

  if (indice >= ndata)
    return -2;

  for (i = 0; i < ndata; i++)
    {
      vect_cor[i] = vect[i];
    }
  vect_cor[indice] = val;
  return 0;
}


/* la fonction d'enrobage classique */

int
OP_remplace_valeur (unsigned long NbVal, void *ArgList[], char *DiagExec)
{
  int CodRet;
  sprintf (DiagExec, "remplace_valeur: num %d par %g", *(int *) ArgList[1],
	   *(float *) ArgList[2]);

  CodRet = remplace_valeur (NbVal,
			    (float *) ArgList[0],
			    *(int *) ArgList[1],
			    *(float *) ArgList[2],
			    (float *) ArgList[3]);

  if (CodRet == 0)
    return OP_OK;
  else
    return OP_FAIL;
}

void
ID_remplace_valeur (oper * optr)
{
  strcpy (optr->Nom, "remplace_valeur");
  optr->Version = "2.0";
  optr->Date = "17/05/00";
  optr->fctptr = OP_remplace_valeur;
  optr->NbArg = 4;		/* doit rester inf. a FIL_MAX_ARG */

  optr->Arg_Car[0].direction = DIR_IN;
  optr->Arg_Car[0].categorie = VECTOR;
  optr->Arg_Car[0].typ = ATYC_IF32;
  optr->Arg_Car[0].array_dim = "1";
  optr->Arg_Car[0].type_sample = "any";
  optr->Arg_Car[0].sample = "any";
  optr->Arg_Car[0].unite = "any";

  optr->Arg_Car[1].direction = DIR_IN;
  optr->Arg_Car[1].categorie = COEFFICIENT;
  optr->Arg_Car[1].typ = ATYC_I32;
  optr->Arg_Car[1].array_dim = "1";
  optr->Arg_Car[1].type_sample = NULL;
  optr->Arg_Car[1].sample = NULL;
  optr->Arg_Car[1].unite = "";

  optr->Arg_Car[2].direction = DIR_IN;
  optr->Arg_Car[2].categorie = COEFFICIENT;
  optr->Arg_Car[2].typ = ATYC_IF32;
  optr->Arg_Car[2].array_dim = "1";
  optr->Arg_Car[2].type_sample = NULL;
  optr->Arg_Car[2].sample = NULL;
  optr->Arg_Car[2].unite = "";

  optr->Arg_Car[3].direction = DIR_OUT;
  optr->Arg_Car[3].categorie = VECTOR;
  optr->Arg_Car[3].typ = ATYC_IF32;
  optr->Arg_Car[3].array_dim = "1";
  optr->Arg_Car[3].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[3].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[3].sample = "$Arg1.sample";
  optr->Arg_Car[3].ref_time = "$Arg1.ref_time";
  optr->Arg_Car[3].unite = "$Arg1.unit";
  optr->Arg_Car[3].misval = "$Arg1.misval";
  optr->Arg_Car[3].famille = "$Arg1.famille";
}
