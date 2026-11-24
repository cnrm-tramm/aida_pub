/*********************************************************
* OPERATOR 	Genere_flag.c FUNCTION ANSI-C
*
* PURPOSE       Genère un vecteur flag en fonction d'un critère sur un vecteur.
*		Le flag peut prendre 3 valeurs signifiant vrai, faux ou indeterminé (à cause d'un NaN).
*       Ces 3 valeurs sont de type float et passées en arguments à l'opérateur.
*
* VERSION       $Revision:  $
*
* ARGUMENTS 	IN	float	X		vecteur sur lequel on applique le critère 
*		IN	float 	X_inf		valeur min pour laquelle la condition est vraie 
*		IN 	float 	X_sup		valeur max pour laquelle la condition est vraie
*		IN 	float 	X_mnq		valeur manquante de X
*		IN 	float 	vrai_val	valeur correspondant à vrai
*		IN 	float 	faux_val	valeur correspondant à faux
*		IN 	float 	ind_val	    valeur correspondant à indéterminé
*
*		OUT float 	Flag		vecteur flag en sortie 
*
* ENTRY		NONE
*
* SUBPROGRAMS 	NONE
* 
* REFERENCES	
*
* COPYRIGHT 	Meteo-France
*		Centre National de Recherches Meteorologiques
*		GMEI/TRAMM
*		42, av. G. Coriolis
* 		31057 	TOULOUSE cedex
*
* 		J.Couzinier 09/09/2015
*
************************************************************/

#define _POSIX_SOURCE 1
#define _XOPEN_SOURCE 600
/* Le #define _HPUX_SOURCE n'est la que pour "voir" strdup */
#define _HPUX_SOURCE 1

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>

#include "struct_oper.h"

unsigned long
Genere_flag (unsigned long Nloop,
		  const float *X,
		  const float X_inf,
		  const float X_sup,
          const float X_mnq,
		  const float vrai_val,
		  const float faux_val,
          const float ind_val,
		  float *Flag)
{

  unsigned long i;


  /***********************************************************
   La valeur de Flag est vraie si :
   	 X_inf <= X <= X_sup
   La valeur de Flag est indeterminée si :
     X = X_mnq
     X = NaN
   La valeur de X est fausse dans les autres cas.
  ************************************************************/

  for (i = 0; i < Nloop; i++)
    {
      if ( isfinite (X[i]) && (X[i] != X_mnq) )
	    {
	      if ( (X[i] > X_inf) && (X[i] < X_sup) )
	        {
	          Flag[i] = vrai_val;
	        }
	      else
	        {
	          Flag[i] = faux_val;
	        }
	    }
      else
	    {
	      Flag[i] = ind_val;
	    }
    }

  return OP_OK;
}

/* fonction d'enrobage */

int
OP_Genere_flag (unsigned long Nbval, void *ArgList[], char *DiagExec)
{
  unsigned long CodRet;
  int NCar;

  NCar = sprintf (DiagExec, "Genere_flag (%lu ech), %g<X<%g manquant=%g", Nbval,
		  *((float *) ArgList[1]), *((float *) ArgList[2]), *((float *) ArgList[3]) );
  DiagExec += (NCar < 0 ? 0 : NCar);

  CodRet = Genere_flag (Nbval,
			     (float *) ArgList[0],
			     *((float *) ArgList[1]),
			     *((float *) ArgList[2]),
			     *((float *) ArgList[3]),
			     *((float *) ArgList[4]),
			     *((float *) ArgList[5]),
			     *((float *) ArgList[6]),
			     (float *) ArgList[7]);

  return CodRet;
}

void
ID_Genere_flag (oper * optr)
{
  strcpy (optr->Nom, "Genere_flag");
  optr->Version = "$Revision:$";
  optr->Date = "$Date:$";
  optr->fctptr = OP_Genere_flag;
  optr->NbArg = 8;

  /* X */
  optr->Arg_Car[0].direction = DIR_IN;
  optr->Arg_Car[0].categorie = VECTOR;
  optr->Arg_Car[0].typ = ATYC_IF32;
  optr->Arg_Car[0].array_dim = "1";
  optr->Arg_Car[0].type_sample = "any";
  optr->Arg_Car[0].sample = "any";
  optr->Arg_Car[0].unite = "any";


  /* X_inf */
  optr->Arg_Car[1].direction = DIR_IN;
  optr->Arg_Car[1].categorie = COEFFICIENT;
  optr->Arg_Car[1].typ = ATYC_IF32;
  optr->Arg_Car[1].array_dim = "1";

  /* X_sup */
  optr->Arg_Car[2].direction = DIR_IN;
  optr->Arg_Car[2].categorie = COEFFICIENT;
  optr->Arg_Car[2].typ = ATYC_IF32;
  optr->Arg_Car[2].array_dim = "1";

  /* X_mnq */
  optr->Arg_Car[3].direction = DIR_IN;
  optr->Arg_Car[3].categorie = COEFFICIENT;
  optr->Arg_Car[3].typ = ATYC_IF32;
  optr->Arg_Car[3].array_dim = "1";

  /* vrai_val */
  optr->Arg_Car[4].direction = DIR_IN;
  optr->Arg_Car[4].categorie = COEFFICIENT;
  optr->Arg_Car[4].typ = ATYC_IF32;
  optr->Arg_Car[4].array_dim = "1";

  /* faux_val */
  optr->Arg_Car[5].direction = DIR_IN;
  optr->Arg_Car[5].categorie = COEFFICIENT;
  optr->Arg_Car[5].typ = ATYC_IF32;
  optr->Arg_Car[5].array_dim = "1";

  /* ind_val */
  optr->Arg_Car[6].direction = DIR_IN;
  optr->Arg_Car[6].categorie = COEFFICIENT;
  optr->Arg_Car[6].typ = ATYC_IF32;
  optr->Arg_Car[6].array_dim = "1";

  /* X_valid */
  optr->Arg_Car[7].direction = DIR_OUT;
  optr->Arg_Car[7].categorie = VECTOR;
  optr->Arg_Car[7].typ = ATYC_IF32;
  optr->Arg_Car[7].array_dim = "1";
  optr->Arg_Car[7].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[7].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[7].sample = "$Arg1.sample";
  optr->Arg_Car[7].ref_time = " $Arg1.ref_time";
  optr->Arg_Car[7].unite = "without";
  optr->Arg_Car[7].famille = "\"ctl\"";
  optr->Arg_Car[7].name =
    "\"vrai lorsque \" + $Arg1.name + \" est entre \" + $Arg2 +  \" et \" + $Arg3";
  optr->Arg_Car[7].en_name =
    "\"true when \" + $Arg1.english_name + \" is between \" + $Arg2 +  \" and \" + $Arg3";
}
