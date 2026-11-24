/*************************************************************************
*
* OPERATOR         Calc_flag_filfin FUNCTION ANSI-C
*
* PURPOSE          Calcule un flag qualite de la température mesurée dans les 
* 		   boitiers filfin utilisés pendant la campagne Passy-2015 à partir de 
* 		   force et de la direction du vent 
*
* DESCRIPTION      
* 		   La campagne EFFIGI-2015 a mis en évidence des biais et des erreurs significatives 
* 		   sur la mesure de température dans les mini abris ventilés utilisés pendant la campagne Passy-2015.
* 		   L'erreur dépend de la force du vent et de la direction (vent face à l'ouverture, ou vent
* 		   arrière)
*
* 		   flag | Conditions
* 		   -------------------------------                  
* 		   1    | vent de face > seuil_FF_face
* 		   2    | vent de face < seuil_FF_face
* 		   3    | vent AR  
*
* VERSION          1.0 
*
* ARGUMENTS  
*            IN   float      FF    force du vent 
*            IN   float      DD    direction du vent  
*            IN   float      seuil_FF_ar     seuil de force du vent losrqu'il de l'arrière   
*            IN   float      DD_mini_face    direction min (inv sens trigo) déterminant le vent de face
*            IN   float      DD_max_face     direction max (inv sens trigo) déterminant le vent de face
*
*            OUT  float      flag_T_filfin   flag qualite de la mesure de température 
*
* ENTRY        NONE
*        
* SUBPROGRAMS  NONE
*        
* REFERENCES   
*
* Rapport qualification et calibration des mini-abri ventilés fil fins (Sandrine Girres)
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
Calc_flag_filfin ( unsigned long ndata,
			float *FF,
			float *DD,
			float seuil_FF_face,
			float DD_min_face,
			float DD_max_face,
			float *flag_T_filfin )

{
 long i; 	

 int dd_min_sup_max;

 if ( DD_min_face >  DD_max_face )  
    dd_min_sup_max = 1;
 else
    dd_min_sup_max = 0; 


 for (i = 0; i < ndata; i++)
    {
      if ( !isfinite(FF[i]) || !isfinite(DD[i])  ) 
	 {
          flag_T_filfin[i] = 0./0.; 
	 }
      else 
	 { 
	  if (( dd_min_sup_max && (( DD[i] > DD_min_face ) || (DD [i] < DD_max_face ) ) ) ||
	     (( DD[i] > DD_min_face ) && (DD [i] < DD_max_face ) ) )
		{
		  /* cas du vent de face */ 
	          if ( FF[i] >= seuil_FF_face) 
	             flag_T_filfin[i] = 1 ;
	          else
	             flag_T_filfin[i] = 2 ;
	         }
	       else 
		 {
		  /* cas du vent AR  */
	          flag_T_filfin[i] = 3 ;
	         }
         }
   }



  return OP_OK;
}

int 
OP_Calc_flag_filfin( unsigned long NbVal, void *ArgList[], char *DiagExec)
{
  unsigned long Codret;
		
  Codret = Calc_flag_filfin ( NbVal,
		      (float *) ArgList[0],
		      (float *) ArgList[1],
		      *((float *) ArgList[2]),
		      *((float *) ArgList[3]),
		      *((float *) ArgList[4]),
		      (float *) ArgList[5] );
  return OP_OK;
}



void
ID_Calc_flag_filfin (oper *optr)
{
  int idx;
  strcpy (optr->Nom, "Calc_flag_filfin");
  optr->Version = "Revision:$";
  optr->Date = "$Date:$";
  optr->fctptr = OP_Calc_flag_filfin;
  optr->NbArg = 6;		/* doit rester inf. a FIL_MAX_ARG */


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
 
  for ( idx = 2; idx < 5; idx++ )
     {
      optr->Arg_Car[idx].direction = DIR_IN;
      optr->Arg_Car[idx].categorie = COEFFICIENT; 
      optr->Arg_Car[idx].typ = ATYC_IF32;
      optr->Arg_Car[idx].array_dim = "1";
      optr->Arg_Car[idx].type_sample = NULL;
      optr->Arg_Car[idx].sample = NULL;
     }

  optr->Arg_Car[idx].direction = DIR_OUT;
  optr->Arg_Car[idx].categorie = VECTOR;
  optr->Arg_Car[idx].array_dim = "1";
  optr->Arg_Car[idx].sample = "$Arg1.sample";
  optr->Arg_Car[idx].typ = ATYC_IF32;
  optr->Arg_Car[idx].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[idx].ref_time = "$Arg1.ref_time";
  optr->Arg_Car[idx].unite = "without";
  optr->Arg_Car[idx].famille = "\"controle\"";
  optr->Arg_Car[idx].name = "\"Flag qualite de la temperature dans abri filfin";
  optr->Arg_Car[idx].en_name = "\"Quality flag of temperature measured in thin wire shield";
  idx++;

}




