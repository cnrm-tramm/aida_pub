/****************************************************
*
* OPERATOR       Arrondi.c   FUNCTION  ANSI-C
*
* PURPOSE      	 Arrondi le parametre X  
*
* DESCRIPTION    Arrondi le parametre X a la valeur de 
* 		 l'argument "arrondi" près. 
* 		 Le type d'arrondi est défini par l'argument type_arrondi
*
* VERSION        1.0
*
* ARGUMENTS    IN    float   X    	any    La variable d'entree
*              IN    float   arrondi           Valeur de l'arrondi 
*              IN    float   type_arrondi      Type arrondi (-1: en dessous, 0: plus proche, 1 : au dessus) 
*              OUT   float   X_arr             Variable X arrondie 
*          
* ENTRY        
*          
* SUBPROGRAMS    
*
* FILES     
*
* REFERENCES 
*
* CHANGES        1.1 Initial release
*
* COPYRIGHT      Meteo-France
*
* AGREEMENT      The author wishes that .....
*#########################################################################*/

#define _POSIX_SOURCE 1
#define _XOPEN_SOURCE 600

#include <math.h>
#include <stdio.h>
#include <string.h>
#include "struct_oper.h"

void
Arrondi (const unsigned long NLoop,
       const float *X,	/* Variable d'entree */
       const double arrondi,
       const int type_arrondi,
       float *X_arr)		/* Variable resultat */
{
  unsigned long i;

  for (i = 0; i < NLoop; i++)
    {
      if (isfinite (X[i]))
	{
	  if (type_arrondi == 0)
	    X_arr[i] = arrondi * ((int) (0.5 + X[i] / arrondi));
	  else if (type_arrondi == -1)
	    X_arr[i] = arrondi * floor (X[i] / arrondi);
	  else if (type_arrondi == 1)
	    X_arr[i] = arrondi * ceil (X[i] / arrondi);
	}
      else
	{
	  X_arr[i] = X[i];
	}
    }
  return;
}

/* la fonction d'enrobage classique */

int
OP_Arrondi (unsigned long NbVal, void *ArgList[], char *DiagExec)
{
  sprintf (DiagExec,
	   "Arrondi, NbVal=%lu, Arrondi a : %f de type %d ",
	   NbVal, *((double *) ArgList[1]), *((int *) ArgList[2]));

  Arrondi (NbVal,
	   (float *) ArgList[0],
	   *((double *) ArgList[1]),
	   *((int *) ArgList[2]), (float *) ArgList[3]);
  return OP_OK;
}

void
ID_Arrondi (oper * optr)
{
  strcpy (optr->Nom, "Arrondi");
  optr->Version = "1.0";
  optr->Date = "$Date$";
  optr->fctptr = OP_Arrondi;
  optr->NbArg = 4;

  /* X */
  optr->Arg_Car[0].direction = DIR_IN;
  optr->Arg_Car[0].categorie = VECTOR;
  optr->Arg_Car[0].typ = ATYC_IF32;
  optr->Arg_Car[0].array_dim = "1";
  optr->Arg_Car[0].type_sample = "any";
  optr->Arg_Car[0].sample = "any";
  optr->Arg_Car[0].unite = "";
  optr->Arg_Car[0].famille = "any";

  /* arrondi */
  optr->Arg_Car[1].direction = DIR_IN;
  optr->Arg_Car[1].categorie = COEFFICIENT;
  optr->Arg_Car[1].typ = ATYC_IF64;
  optr->Arg_Car[1].array_dim = "1";
  optr->Arg_Car[1].unite = "";

  /* type_arrondi */

  optr->Arg_Car[2].direction = DIR_IN;
  optr->Arg_Car[2].categorie = COEFFICIENT;
  optr->Arg_Car[2].typ = ATYC_I32;
  optr->Arg_Car[2].array_dim = "1";
  optr->Arg_Car[2].unite = "";

  /* X_arr */
  optr->Arg_Car[3].direction = DIR_OUT;
  optr->Arg_Car[3].categorie = VECTOR;
  optr->Arg_Car[3].typ = ATYC_IF32;
  optr->Arg_Car[3].array_dim = "1";
  optr->Arg_Car[3].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[3].ref_time = "$Arg1.ref_time";
  optr->Arg_Car[3].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[3].sample = "$Arg1.sample";
  optr->Arg_Car[3].unite = "$Arg1.unit";
  optr->Arg_Car[3].famille = "$Arg1.famille";

}
