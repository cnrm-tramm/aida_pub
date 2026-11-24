/*************************************************************************
*
* OPERATOR         ITC_flag FUNCTION ANSI-C
*
* PURPOSE          Calcule le flag qualite a partir des caractéristiques intérgrale
*                  de la turbulence
*
* DESCRIPTION      
* 	           Calcule le rapport (ITC mesure - ITC modele ) / ITC modele 
* 	           Attribue une valeur de flag entre 0 et 9 en fonction de la valeur du rapport
* 	           en utilisant l'échelle définie par Foken.
*
* VERSION          1.0 
*
* ARGUMENTS  
*            IN   float      ITC         Caractéristiques integrale de la turbulence mesurée  
*            IN	  float      ITC_model   Caractéristiques integrale de la turbulence théorique
*
*            OUT  float      flag_ITC   
*
* ENTRY        NONE
*        
* SUBPROGRAMS  NONE
*        
* REFERENCES    
*
* 	     T. Foken, Micrometeorology, 2008 
* 	     Ed Spinger, ISBN : 978-3-540-74665-2 

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
ITC_flag ( unsigned long ndata,
			float *ITC,
			float *ITC_model,
			float *flag_ITC )

{
 long i, nb_inval; 	

 double dev;

 nb_inval = 0;
 for (i = 0; i < ndata; i++)
    {
      dev = 100.*fabs ( (ITC[i] - ITC_model[i]) / ITC_model[i] );

      if (!isfinite(dev) ) 
          flag_ITC[i] = 0./0.;
      else if ( (dev > 0) && (dev <= 15) )
	  flag_ITC[i] = 1;
      else if ( (15 < dev ) && (dev <= 30) )
          flag_ITC[i] = 2;
      else if ( (30 < dev ) && (dev <= 50) )
          flag_ITC[i] = 3;
      else if ( (50 < dev ) && (dev <= 75) )
          flag_ITC[i] = 4;
      else if ( (75 < dev ) && (dev <= 100) )
          flag_ITC[i] = 5;
      else if ( (100 < dev ) && (dev <= 250) )
          flag_ITC[i] = 6;
      else if ( (250 < dev ) && (dev <= 500) )
          flag_ITC[i] = 7;
      else if ( (500 < dev ) && (dev <= 1000) )
          flag_ITC[i] = 8;
      else if ( 1000 < dev  )
          flag_ITC[i] = 9;

      /*
      fprintf ( stderr, "ITC : %g , ITC_model : %g, dev : %g , flag : %g \n", ITC[i], ITC_model[i], dev, flag_ITC[i] ) ; 
      */

    }

  return OP_OK;
}

int 
OP_ITC_flag ( unsigned long NbVal, void *ArgList[], char *DiagExec)
{
  unsigned long Codret;
		
  Codret = ITC_flag ( NbVal,
		      (float *) ArgList[0],
		      (float *) ArgList[1],
		      (float *) ArgList[2] );
  return OP_OK;
  
}



void
ID_ITC_flag (oper *optr)
{
  int idx;
  strcpy (optr->Nom, "ITC_flag");
  optr->Version = "Revision:$";
  optr->Date = "$Date:$";
  optr->fctptr = OP_ITC_flag;
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
  optr->Arg_Car[idx].famille = "\"controle\"";
  optr->Arg_Car[idx].name = "\"Flag qualite basee sur la caracteristique integrale turbulente de\" + $Arg1.name ";
  optr->Arg_Car[idx].en_name = "\"Quality flag bases on integral turbulence characteristics of\" +$Arg1.english_name ";
  idx++;

}




