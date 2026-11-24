/*************************************************************************
*
* OPERATOR         Combine_flag_EC_Foken FUNCTION ANSI-C
*
* PURPOSE          Calcule un flag qualite general de la covariance XY à partir des
*                  flag qualite sur l'intensite turbulente et sur
*                  la stationnarite. 
*
* DESCRIPTION      
* 	          Utilise la classification de flag qualite proposee
* 	          par Thomas Foken
*
* VERSION          1.0 
*
* ARGUMENTS  
*            IN   float      stat_flag_XY  flag qualite de la stationnarite de la covariance XY 
*            IN   float      ITC_flag_X    flag qualite de l'intensite turbulente basee sur le parametre X 
*            IN   float      ITC_flag_Y    flag qualite de l'intensite turbulente basee sur la parametre Y 
*
*            OUT  float      flag_EC_Foken flag qualite de la covariance XY 
*
* ENTRY        NONE
*        
* SUBPROGRAMS  NONE
*        
* REFERENCES   
*
*  T. Foken, Micrometeorology, 2008 
*  Ed Spinger, ISBN : 978-3-540-74665-2
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
Combine_flag_EC_Foken ( unsigned long ndata,
			float *stat_flag_XY,
			float *ITC_flag_X,
			float *ITC_flag_Y,
			float *flag_EC_Foken )

{
 long i; 	

 int stat, itc; 

 for (i = 0; i < ndata; i++)
    {
      if ( !isfinite(stat_flag_XY[i]) || !isfinite(ITC_flag_X[i]) || !isfinite(ITC_flag_Y[i]) ) 
	 {
          flag_EC_Foken[i] = 0./0.; 
	 }
      else 
	 { 
           stat = (int)stat_flag_XY[i];
	   /* on prend le max de ITC_flag_X et de ITC_flag_Y */
	   if ( ITC_flag_X[i] > ITC_flag_Y[i] )
	       itc = (int)ITC_flag_X[i];
	   else 
	       itc = (int)ITC_flag_Y[i];

           if ( ( stat == 9) || (itc == 9 ) )   
               flag_EC_Foken[i] = 9.0;
	   if ( ((1 <= stat) && (stat <= 8)) && 
	        ((1 <= itc) && (itc <= 8)) ) 
	       flag_EC_Foken[i] = 8.0;
	   if ( ((1 <= stat) && (stat <= 6)) && 
	        ((1 <= itc) && (itc <= 6)) ) 
	       flag_EC_Foken[i] = 7.0;
	   if ( (stat == 5 ) && 
	        ((1 <= itc) && (itc <= 6)) ) 
	       flag_EC_Foken[i] = 6.0;
	   if ( ((1 <= stat) && (stat <= 4)) && 
	        ((3 <= itc) && (itc <= 5)) ) 
	       flag_EC_Foken[i] = 5.0;
	   if ( ((stat == 3 ) || (stat == 4)) && 
	        ((itc == 1 ) || (itc == 2)) ) 
	       flag_EC_Foken[i] = 4.0;
	   if ( ((stat == 1 ) || (stat == 2)) && 
	        ((itc == 3 ) || (itc == 4)) ) 
	       flag_EC_Foken[i] = 3.0;
	   if ( (stat == 2 ) && 
	        ((itc == 1 ) || (itc == 2)) ) 
	       flag_EC_Foken[i] = 2.0;
	   if ( (stat == 1 ) && 
	        ((itc == 1 ) || (itc == 2)) ) 
	       flag_EC_Foken[i] = 1.0;


	 }

      /*
	  fprintf (stderr, "stat = %g, itc_X = %g, itc_Y = %g, itc = %d, flag = %g \n", 
			    stat_flag_XY[i], ITC_flag_X[i], ITC_flag_Y[i], itc, flag_EC_Foken[i] );
      */


    }

  return OP_OK;
}

int 
OP_Combine_flag_EC_Foken( unsigned long NbVal, void *ArgList[], char *DiagExec)
{
  unsigned long Codret;
		
  Codret = Combine_flag_EC_Foken ( NbVal,
		      (float *) ArgList[0],
		      (float *) ArgList[1],
		      (float *) ArgList[2],
		      (float *) ArgList[3] );
  return OP_OK;
}



void
ID_Combine_flag_EC_Foken (oper *optr)
{
  int idx;
  strcpy (optr->Nom, "Combine_flag_EC_Foken");
  optr->Version = "Revision:$";
  optr->Date = "$Date:$";
  optr->fctptr = OP_Combine_flag_EC_Foken;
  optr->NbArg = 4;		/* doit rester inf. a FIL_MAX_ARG */


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
  optr->Arg_Car[idx].name = "\"Flag qualite Foken de  la covariance \" + $Arg1.name + \" et \" + $Arg2.name";
  optr->Arg_Car[idx].en_name = "\"Quality flag Foken of the covariance \" +$Arg1.english_name + \" and \" + $Arg2.english_name";
  idx++;

}




