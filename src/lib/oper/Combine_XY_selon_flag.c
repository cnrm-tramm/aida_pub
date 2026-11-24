/*************************************************************************
*
* OPERATOR         Combine_XY_selon_flag.c  FUNCTION ANSI-C
*
* PURPOSE          Combine 2 vecteurs selon la valeur d'un autre vecteur flag 
*
* DESCRIPTION     
* 		   Creation d'un vecteur contenant 
* 		     - les valeurs de X si Crit_min <= flag <= Crit_max
* 		     - les valeurs de Y si flag > Crit_max ou flag < Crit_min
*
*		   
* VERSION          1.0 
*
* ARGUMENTS  
*            IN   float   X         	Vecteur
*            IN   float   Y	       	Vecteur 
*            IN	  float   flag		Vecteur flag sur laquel on fait le test 
*            IN	  float   Crit_min 	Valeur minimale du critere de test 
*            IN	  float   Crit_max 	Valeur maximale du critere de test 
*            OUT  float   Z     	Vecteur resultat
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

#include <math.h>
#include "struct_oper.h"

unsigned long
Combine_XY_selon_flag (unsigned long ndata,
		   const float *X,
		   const float *Y,
		   const int *flag, 
		   const float Crit_min,
		   const float Crit_max,
		   float *Z)
{
  unsigned long i;
  unsigned long nb_crit = 0;

  for (i = 0; i < ndata; i++)
    {

      if (( (float)flag[i] >= Crit_min) && ( (float)flag[i] <= Crit_max ) )
	 {
 	  Z[i] = X[i];
	  nb_crit = nb_crit +1;
         }
      else 
	 {
	  Z[i] = Y[i];
 	 }

    }

  return nb_crit;
}


/* la fonction d'enrobage classique */
#include <string.h>
#include <stdio.h>

int
OP_Combine_XY_selon_flag (unsigned long NbVal, void *ArgList[], char *DiagExec)
{
  unsigned long CodRet;
  sprintf (DiagExec, "Combine_XY_selon_flag, %lu ech", NbVal);
  CodRet = Combine_XY_selon_flag (NbVal,
			      (float *) ArgList[0],
			      (float *) ArgList[1],
			      (int *) ArgList[2],
			      *(float *) ArgList[3],
			      *(float *) ArgList[4],
			      (float *) ArgList[5]);

  sprintf (DiagExec + strlen (DiagExec), ", %lu valeurs prises dans X ", CodRet);
  return OP_OK;
}

void
ID_Combine_XY_selon_flag (oper * optr)
{
  strcpy (optr->Nom, "Combine_XY_selon_flag");
  optr->Version = "$Revision:$";
  optr->Date = "$Date:";
  optr->fctptr = OP_Combine_XY_selon_flag;
  optr->NbArg = 6;

  /* X */
  optr->Arg_Car[0].direction = DIR_IN;
  optr->Arg_Car[0].categorie = VECTOR;
  optr->Arg_Car[0].typ = ATYC_IF32;
  optr->Arg_Car[0].array_dim = "1";
  optr->Arg_Car[0].type_sample = "any";
  optr->Arg_Car[0].sample = "any";
  optr->Arg_Car[0].unite = "any";

  /* Y */
  optr->Arg_Car[1].direction = DIR_IN;
  optr->Arg_Car[1].categorie = VECTOR;
  optr->Arg_Car[1].typ = ATYC_IF32;
  optr->Arg_Car[1].array_dim = "1";
  optr->Arg_Car[1].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[1].type_sample = "any";
  optr->Arg_Car[1].sample = "any";
  optr->Arg_Car[1].unite = "any";

  /* flag */
  optr->Arg_Car[2].direction = DIR_IN;
  optr->Arg_Car[2].categorie = VECTOR;
  optr->Arg_Car[2].typ = ATYC_I32;
  optr->Arg_Car[2].array_dim = "1";
  optr->Arg_Car[2].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[2].type_sample = "any";
  optr->Arg_Car[2].sample = "any";
  optr->Arg_Car[2].unite = "any";

  /* Crit_min */
  optr->Arg_Car[3].direction = DIR_IN;
  optr->Arg_Car[3].categorie = COEFFICIENT;
  optr->Arg_Car[3].typ = ATYC_IF32;
  optr->Arg_Car[3].array_dim = "1";
  optr->Arg_Car[3].type_sample = NULL;
  optr->Arg_Car[3].sample = NULL;
  optr->Arg_Car[3].unite = "";

  /* Crit_max */
  optr->Arg_Car[4].direction = DIR_IN;
  optr->Arg_Car[4].categorie = COEFFICIENT;
  optr->Arg_Car[4].typ = ATYC_IF32;
  optr->Arg_Car[4].array_dim = "1";
  optr->Arg_Car[4].type_sample = NULL;
  optr->Arg_Car[4].sample = NULL;
  optr->Arg_Car[4].unite = "";

  /* Z  */
  optr->Arg_Car[5].direction = DIR_OUT;
  optr->Arg_Car[5].categorie = VECTOR;
  optr->Arg_Car[5].typ = ATYC_IF32;
  optr->Arg_Car[5].array_dim = "1";
  optr->Arg_Car[5].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[5].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[5].sample = "$Arg1.sample";
  optr->Arg_Car[5].ref_time = "$Arg1.ref_time";
  optr->Arg_Car[5].unite = "$Arg1.unit";
  optr->Arg_Car[5].misval = "$Arg1.misval";
  optr->Arg_Car[5].famille = "$Arg1.famille";

}
