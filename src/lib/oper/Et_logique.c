/****************************************************
*
* OPERATOR       Et_logique.c   FUNCTION  ANSI-C
*
* PURPOSE        Calcule Arg1 ET Arg 2
*
* DESCRIPTION    operation logique "ET"
*
* VERSION        1.0
*
* ARGUMENTS    IN   float   X    Vecteur
*              IN   float   Y    Vecteur
*		       IN 	float 	X_vrai	valeur de X correspondant à vrai
*		       IN 	float 	X_faux	valeur de X correspondant à faux
*		       IN 	float 	X_ind	valeur de X correspondant à indéterminé
*		       IN 	float 	Y_vrai	valeur de Y correspondant à vrai
*		       IN 	float 	Y_faux	valeur de Y correspondant à faux
*		       IN 	float 	Y_ind	valeur de Y correspondant à indéterminé
*		       IN 	float 	ET_vrai	valeur de ET correspondant à vrai
*		       IN 	float 	ET_faux	valeur de ET correspondant à faux
*		       IN 	float 	ET_ind	valeur de ET correspondant à indéterminé
*              OUT  float   ET Vecteur résultat
*
* ENTRY            
*                 
* SUBPROGRAMS    none
*
* FILES   
*
* REFERENCES   
*
* CHANGES               
*                
*
* COPYRIGHT      Meteo-France
*
* AGREEMENT      The author wishes that .....
*#########################################################################*/

#define _POSIX_SOURCE 1
#define _XOPEN_SOURCE 600
/* Le #define _HPUX_SOURCE n'est la que pour "voir" strdup */
#define _HPUX_SOURCE 1

#include <stdio.h>
#include <string.h>
#include "struct_oper.h"

unsigned long
Et_logique (unsigned long Nloop,
		  const float *X,
          const float *Y,
		  const float X_vrai,
		  const float X_faux,
          const float X_ind,
          const float Y_vrai,
		  const float Y_faux,
          const float Y_ind,
          const float ET_vrai,
		  const float ET_faux,
          const float ET_ind,
		  float *ET)
{

  unsigned long i;


  /***********************************************************
    Le calcule se fait selon la table de vérité suivante (V=vrai, F=faux , I=indeterminé) :
      ----------------
      |  V |  F |  I |
   ---|----|----|----|
    V |  V |  F |  I |
   ---|----|----|----|
    F |  F |  F |  I |
   ---|----|----|----|
    I |  I |  I |  I |
   -------------------       
  ************************************************************/

  for (i = 0; i < Nloop; i++)
    {
    /* au moins 1 ind => ind */
    if ( (X[i] == X_ind) || (Y[i] == Y_ind) )
      ET[i] = ET_ind;
    /* 2 vrais => vrai */
    else if ( (X[i] == X_vrai) && (Y[i] == Y_vrai) )
      ET[i] = ET_vrai;
    /* faux dans les autres cas */
    else
      ET[i] = ET_faux;      
    }
  return OP_OK;
}

/* la fonction d'enrobage classique */

int
OP_Et_logique (unsigned long NbVal, void *ArgList[], char *DiagExec)
{
  unsigned long CodRet;
  int NCar;

  NCar = sprintf (DiagExec, "Et_logique, %lu echant.",
		  NbVal);
  DiagExec += (NCar < 0 ? 0 : NCar);

  CodRet = Et_logique (NbVal,
			     (float *) ArgList[0],
                 (float *) ArgList[1],
			     *((float *) ArgList[2]),
			     *((float *) ArgList[3]),
			     *((float *) ArgList[4]),
			     *((float *) ArgList[5]),
			     *((float *) ArgList[6]),
			     *((float *) ArgList[7]),
                 *((float *) ArgList[8]),
			     *((float *) ArgList[9]),
			     *((float *) ArgList[10]),
			     (float *) ArgList[11]);

  return CodRet;
}

void
ID_Et_logique (oper * optr)
{
  strcpy (optr->Nom, "Et_logique");
  optr->Version = "$Revision:$";
  optr->Date = "$Date:$";
  optr->fctptr = OP_Et_logique;
  optr->NbArg = 12;		/* doit rester inf. a FIL_MAX_ARG */

  /* X */
  optr->Arg_Car[0].direction = DIR_IN;
  optr->Arg_Car[0].categorie = VECTOR;
  optr->Arg_Car[0].typ = ATYC_IF32;
  optr->Arg_Car[0].array_dim = "1";
  optr->Arg_Car[0].type_sample = "any";
  optr->Arg_Car[0].sample = "any";
  optr->Arg_Car[0].unite = "any";
  optr->Arg_Car[0].famille = "any";

  /* Y */
  optr->Arg_Car[1].direction = DIR_IN;
  optr->Arg_Car[1].categorie = VECTOR;
  optr->Arg_Car[1].typ = ATYC_IF32;
  optr->Arg_Car[1].array_dim = "1";
  optr->Arg_Car[1].type_sample = "any";
  optr->Arg_Car[1].sample = "any";
  optr->Arg_Car[1].unite = "any";
  optr->Arg_Car[1].famille = "any";

  /* X_vrai */
  optr->Arg_Car[2].direction = DIR_IN;
  optr->Arg_Car[2].categorie = COEFFICIENT;
  optr->Arg_Car[2].typ = ATYC_IF32;
  optr->Arg_Car[2].array_dim = "1";

  /* X_faux */
  optr->Arg_Car[3].direction = DIR_IN;
  optr->Arg_Car[3].categorie = COEFFICIENT;
  optr->Arg_Car[3].typ = ATYC_IF32;
  optr->Arg_Car[3].array_dim = "1";

  /* X_ind */
  optr->Arg_Car[4].direction = DIR_IN;
  optr->Arg_Car[4].categorie = COEFFICIENT;
  optr->Arg_Car[4].typ = ATYC_IF32;
  optr->Arg_Car[4].array_dim = "1";

  /* Y_vrai */
  optr->Arg_Car[5].direction = DIR_IN;
  optr->Arg_Car[5].categorie = COEFFICIENT;
  optr->Arg_Car[5].typ = ATYC_IF32;
  optr->Arg_Car[5].array_dim = "1";

  /* Y_faux */
  optr->Arg_Car[6].direction = DIR_IN;
  optr->Arg_Car[6].categorie = COEFFICIENT;
  optr->Arg_Car[6].typ = ATYC_IF32;
  optr->Arg_Car[6].array_dim = "1";

  /* Y_ind */
  optr->Arg_Car[7].direction = DIR_IN;
  optr->Arg_Car[7].categorie = COEFFICIENT;
  optr->Arg_Car[7].typ = ATYC_IF32;
  optr->Arg_Car[7].array_dim = "1";

  /* ET_vrai */
  optr->Arg_Car[8].direction = DIR_IN;
  optr->Arg_Car[8].categorie = COEFFICIENT;
  optr->Arg_Car[8].typ = ATYC_IF32;
  optr->Arg_Car[8].array_dim = "1";

  /* ET_faux */
  optr->Arg_Car[9].direction = DIR_IN;
  optr->Arg_Car[9].categorie = COEFFICIENT;
  optr->Arg_Car[9].typ = ATYC_IF32;
  optr->Arg_Car[9].array_dim = "1";

  /* ET_ind */
  optr->Arg_Car[10].direction = DIR_IN;
  optr->Arg_Car[10].categorie = COEFFICIENT;
  optr->Arg_Car[10].typ = ATYC_IF32;
  optr->Arg_Car[10].array_dim = "1";

  /* ET */
  optr->Arg_Car[11].direction = DIR_OUT;
  optr->Arg_Car[11].categorie = VECTOR;
  optr->Arg_Car[11].typ = ATYC_IF32;
  optr->Arg_Car[11].array_dim = "1";
  optr->Arg_Car[11].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[11].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[11].sample = "$Arg1.sample";
  optr->Arg_Car[11].ref_time = " $Arg1.ref_time";
  optr->Arg_Car[11].unite = "without";
  optr->Arg_Car[11].famille = "\"ctl\"";
  optr->Arg_Car[11].name =
    "\"vecteur flag avec vrai=\" + $Arg9+ \" faux=\" + $Arg10 + \" ind=\" + $Arg11";
  optr->Arg_Car[9].en_name =
    "\"flag vector with true=\" + $Arg9+ \" false=\" + $Arg10 + \" undef=\" + $Arg11";

}
