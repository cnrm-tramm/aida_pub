/*************************************************************************
*
* OPERATOR         Stationnarite_flag FUNCTION ANSI-C
*
* PURPOSE          Calcule le flag qualite a partir de l'indice de stationnarité calculé
* 		   par l'opérateur Stationnarite_Covar_XY 
*
* DESCRIPTION      
* 	           Attribue une valeur de flag entre 0 et 9 en fonction de la valeur de I_stationnarite
* 	           en utilisant l'echelle definie par T. Foken.
*
* VERSION          1.0 
*
* ARGUMENTS  
*            IN   float      I_stationnarite         Indice de stationnarite entre 0 et 1  
*
*            OUT  float      flag_stationnarite   
*
* ENTRY        NONE
*        
* SUBPROGRAMS  NONE
*        
* REFERENCES    
*
*   T. Foken, Micrometeorology, 2008 
*   Ed Springer, ISBN : 978-3-540-74665-2 
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
Stationnarite_flag ( unsigned long ndata,
			float *I_stationnarite, 
			float *flag_stationnarite )

{
 long i; 	
 int dev;


 for (i = 0; i < ndata; i++)
    {
      if (!isfinite(I_stationnarite[i]) ) 
	{
          flag_stationnarite[i] = 0./0.;
	}
      else 
        {
         dev = (int)( 100.*I_stationnarite[i] );
         if ( (dev >= 0) && (dev <= 15) )
	    flag_stationnarite[i] = 1;
         else if ( (15 < dev ) && (dev <= 30) )
            flag_stationnarite[i] = 2;
         else if ( (30 < dev ) && (dev <= 50) )
            flag_stationnarite[i] = 3;
         else if ( (50 < dev ) && (dev <= 75) )
            flag_stationnarite[i] = 4;
         else if ( (75 < dev ) && (dev <= 100) )
            flag_stationnarite[i] = 5;
         else if ( (100 < dev ) && (dev <= 250) )
            flag_stationnarite[i] = 6;
         else if ( (250 < dev ) && (dev <= 500) )
            flag_stationnarite[i] = 7;
         else if ( (500 < dev ) && (dev <= 1000) )
            flag_stationnarite[i] = 8;
         else if ( 1000 < dev  )
            flag_stationnarite[i] = 9;
	}
/*
      fprintf(stderr, "dev = %d flag_stationnarite = %g \n", dev, flag_stationnarite[i] ); 
*/
    }

  return OP_OK;
}

int 
OP_Stationnarite_flag ( unsigned long NbVal, void *ArgList[], char *DiagExec)
{
  unsigned long Codret;
		
  Codret = Stationnarite_flag ( NbVal,
		      (float *) ArgList[0],
		      (float *) ArgList[1] );
  return OP_OK;
  
}



void
ID_Stationnarite_flag (oper *optr)
{
  int idx;
  strcpy (optr->Nom, "Stationnarite_flag");
  optr->Version = "Revision:$";
  optr->Date = "$Date:$";
  optr->fctptr = OP_Stationnarite_flag;
  optr->NbArg = 2;		/* doit rester inf. a FIL_MAX_ARG */


  idx = 0;
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
  optr->Arg_Car[idx].famille = "\"controle\"";
  optr->Arg_Car[idx].name = "\"Flag qualite basee sur la stationnarite de la turbulente de\" + $Arg1.name ";
  optr->Arg_Car[idx].en_name = "\"Quality flag based on turbulence stationnarity of\" +$Arg1.english_name ";
  idx++;

}




