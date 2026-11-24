/*************************************************************************
*
* OPERATOR         ITC FUNCTION ANSI-C
*
* PURPOSE          Calcule la caracteristique integrale de la turbulence
*                  (Integral Turbulent Characteristis en anglais) lié au paramètre X
*
* DESCRIPTION      
* 	           ITC = sqrt(Var_X)/Xstar
*
* VERSION          1.0 
*
* ARGUMENTS  
*            IN   float      Var_X   Variance du parametre X 
*            IN	  float      Xstar   Echelle de X 
*
*            OUT  float      ITC_X      Intensité turbulente.
*
* ENTRY        NONE
*        
* SUBPROGRAMS  NONE
*        
* REFERENCES   
*
*     T. Foken, Micrometeorology, 2008 
*     Ed Spinger, ISBN : 978-3-540-74665-2 
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

#include <math.h>
#include <stdio.h>
#include <string.h>
#include <stdlib.h>

#include "struct_oper.h"

int
ITC ( unsigned long ndata,
			float *Var_X,
			float *Xstar,
			float *ITC_X )

{
 long i, nb_inval; 	

 nb_inval = 0;
 for (i = 0; i < ndata; i++)
    {
      if ( (Var_X[i] < 0.0) || (Xstar[i] < 0 ) ) 
	nb_inval++;

      /* on laisse la librairie math. mettre un NaN, si Var_X <0 ou Xstar=0 */
      ITC_X[i] = sqrt (Var_X[i]) /fabs(Xstar[i]);

    }

  return nb_inval;
}

int 
OP_ITC( unsigned long NbVal, void *ArgList[], char *DiagExec)
{
  unsigned long Codret;
		
  Codret = ITC ( NbVal,
		      (float *) ArgList[0],
		      (float *) ArgList[1],
		      (float *) ArgList[2] );
  if (Codret < 0 )
     return OP_FAIL;
  else 
    {
     sprintf (DiagExec,
	   "Nb val invalides :%lu",
	   Codret );
     return OP_OK;
    }
}



void
ID_ITC (oper *optr)
{
  int idx;
  strcpy (optr->Nom, "ITC");
  optr->Version = "Revision:$";
  optr->Date = "$Date:$";
  optr->fctptr = OP_ITC;
  optr->NbArg = 3;		/* doit rester inf. a FIL_MAX_ARG */


  idx = 0;
  optr->Arg_Car[idx].direction = DIR_IN;
  optr->Arg_Car[idx].categorie = VECTOR;
  optr->Arg_Car[idx].typ = ATYC_IF32;
  optr->Arg_Car[idx].array_dim = "1";
  optr->Arg_Car[idx].type_sample = "any";
  optr->Arg_Car[idx].sample = "any";
  optr->Arg_Car[idx].unite = "";
  idx++;

  optr->Arg_Car[idx].direction = DIR_IN;
  optr->Arg_Car[idx].categorie = VECTOR;
  optr->Arg_Car[idx].typ = ATYC_IF32;
  optr->Arg_Car[idx].array_dim = "1";
  optr->Arg_Car[idx].type_sample = "any";
  optr->Arg_Car[idx].sample = "any";
  optr->Arg_Car[idx].unite = "";
  idx++;

  optr->Arg_Car[idx].direction = DIR_OUT;
  optr->Arg_Car[idx].categorie = VECTOR;
  optr->Arg_Car[idx].array_dim = "1";
  optr->Arg_Car[idx].sample = "$Arg1.sample";
  optr->Arg_Car[idx].typ = ATYC_IF32;
  optr->Arg_Car[idx].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[idx].ref_time = "$Arg1.ref_time";
  optr->Arg_Car[idx].unite = "without";
  optr->Arg_Car[idx].famille = "\"turbulence\"";
  optr->Arg_Car[idx].name = "\"Caracteristique integrale turbulente de\" + $Arg1.name ";
  optr->Arg_Car[idx].en_name = "\"Integral turbulence characteristics of\" +$Arg1.english_name ";
  idx++;

}




