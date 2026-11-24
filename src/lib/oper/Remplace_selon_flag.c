/****************************************************************
* OPERATOR 	Remplace_selon_flag  FUNCTION  ANSI-C
* 
* PURPOSE	Remplace les valeurs de X selon la valeur d'un flag 
*
* DESCRIPTION   Cette fonction remplace les valeurs X en fonction
* 		de la valeur d'un flag
*
* VERSION         1.0
*
* ARGUMENTS 	IN 	float 	X   	    parametre brut	
* 		IN 	int	flag	    flag 
*		IN 	float 	inf_flag    valeur min de flag pour remplacement de X par X_rempla
*		IN 	float 	sup_flag    valeur max de flag pour remplacement de X par X_rempla
*		IN 	float   X_rempla    Paramètre de remplacement
* 		OUT 	float 	Xcor 	    parametre corrige
*
* ENTRY		NONE
*
* SUBPROGRAMS 	NONE
* 
* REFERENCES	NONE
*
* CHANGES       1.0   
* 
* COPYRIGHT 	Meteo-France
*		Centre de Recherches Meteorologiques
*		GMEI/TRAMM
*		42, av. G. Coriolis
*		31057	TOULOUSE cedex
*
******************************************************************/

#define _POSIX_SOURCE 1
#define _XOPEN_SOURCE 600

/* Pour la fonction isfinite */
#define _HPUX_SOURCE 1


#include <stdio.h>
#include <string.h>
#include <limits.h>
#include <math.h>
#include "struct_oper.h"

unsigned long
Remplace_selon_flag (unsigned long Nloop,
		    const float *X,
		    const int *flag,
		    const float inf_flag,
		    const float sup_flag,
		    const float X_rempla,
		    float *Xcor )
{
  unsigned long i;

  long n_rempla;
  float f_flag;

  if ( inf_flag >= sup_flag ) 
    return ULONG_MAX;

  n_rempla = 0;
  for (i = 0; i < Nloop; i++)
    {
      /* Valeur correctement représentée par un float ?   */

      f_flag = (float)flag[i];
      if (( f_flag > inf_flag ) && ( f_flag < sup_flag ) ) 
	 {
	  Xcor[i] = X_rempla;
	  n_rempla = n_rempla +1;
 	 }
      else 
	 {
          Xcor[i] = X[i];
 	 }
         
    }

  return n_rempla;

}

/* fonction d'enrobage */

int
OP_Remplace_selon_flag (unsigned long Nbval, void *ArgList[], char *DiagExec)
{
  unsigned long CodRet;

  /* sprintf (DiagExec,""); */

  CodRet = Remplace_selon_flag (Nbval,
			       (float *) ArgList[0],
			       (int *) ArgList[1],
			       *((float *) ArgList[2]),
			       *((float *) ArgList[3]),
			       *((float *) ArgList[4]),
			       (float *) ArgList[5] );

  if (CodRet == ULONG_MAX)
    {
      sprintf (DiagExec, "Error : borne_min flag >= borne_max flag ");
      return OP_FAIL;
    }
  else
    {
      sprintf (DiagExec, "%lu valeur(s) (sur %lu) remplacée(s)",
	       CodRet, Nbval );
      return OP_OK;
    }

}

void
ID_Remplace_selon_flag (oper * optr)
{
  strcpy (optr->Nom, "Remplace_selon_flag");
  optr->Version = "1.0";
  optr->Date = "30/11/17";
  optr->fctptr = OP_Remplace_selon_flag;
  optr->misval_auto = 1;
  optr->NbArg = 6;
  optr->Arg_Car[0].direction = DIR_IN;
  optr->Arg_Car[0].categorie = VECTOR;
  optr->Arg_Car[0].typ = ATYC_IF32;
  optr->Arg_Car[0].array_dim = "1";
  optr->Arg_Car[0].unite = "";
  optr->Arg_Car[0].type_sample = "any";
  optr->Arg_Car[0].sample = "any";

  optr->Arg_Car[1].direction = DIR_IN;
  optr->Arg_Car[1].categorie = VECTOR;
  optr->Arg_Car[1].typ = ATYC_I32;
  optr->Arg_Car[1].array_dim = "1";
  optr->Arg_Car[1].unite = "";
  optr->Arg_Car[1].type_sample = "without";
  optr->Arg_Car[1].sample = "without";

  optr->Arg_Car[2].direction = DIR_IN;
  optr->Arg_Car[2].categorie = COEFFICIENT;
  optr->Arg_Car[2].typ = ATYC_IF32;
  optr->Arg_Car[2].array_dim = "1";
  optr->Arg_Car[2].unite = "";
  optr->Arg_Car[2].type_sample = NULL;
  optr->Arg_Car[2].sample = NULL;

  optr->Arg_Car[3].direction = DIR_IN;
  optr->Arg_Car[3].categorie = COEFFICIENT;
  optr->Arg_Car[3].typ = ATYC_IF32;
  optr->Arg_Car[3].array_dim = "1";
  optr->Arg_Car[3].unite = "";
  optr->Arg_Car[3].type_sample = NULL;
  optr->Arg_Car[3].sample = NULL;

  optr->Arg_Car[4].direction = DIR_IN;
  optr->Arg_Car[4].categorie = COEFFICIENT;
  optr->Arg_Car[4].typ = ATYC_IF32;
  optr->Arg_Car[4].array_dim = "1";
  optr->Arg_Car[4].unite = "";
  optr->Arg_Car[4].type_sample = NULL;
  optr->Arg_Car[4].sample = NULL;

  optr->Arg_Car[5].direction = DIR_OUT;
  optr->Arg_Car[5].categorie = VECTOR;
  optr->Arg_Car[5].typ = ATYC_IF32;
  optr->Arg_Car[5].array_dim = "1";
  optr->Arg_Car[5].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[5].sample = "$Arg1.sample";
  optr->Arg_Car[5].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[5].ref_time = "$Arg1.ref_time";
  optr->Arg_Car[5].name = "$Arg1.name" ;
  optr->Arg_Car[5].en_name = "$Arg1.english_name" ;
  optr->Arg_Car[5].unite = "$Arg1.unit";
  optr->Arg_Car[5].famille = "$Arg1.famille";
  optr->Arg_Car[5].misval = "$Arg1.misval";
}
