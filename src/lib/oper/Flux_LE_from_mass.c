/****************************************************
*
* OPERATOR      Flux_LE_from_mass.c   FUNCTION  ANSI-C
*
* PURPOSE      	Calcul du flux de chaleur latente à partir du flux
* 		de vapeur d'eau
*
* DESCRIPTION   Le flux de chaleur latente est le flux de vapeur d'eau *
* 		la chaleur latente de vaporisation 
*
*
* VERSION       $Revision: 6417 $
*
* ARGUMENTS   	
*             IN   float  flx_h2o    	g.m-2.s-1  Flux de vapeur d'eau	
*	      IN   float  Ta		C ou K	Temperature de l'air 
*             OUT  float  Flx_LE	W/m2	Flux de chaleur latente 
*
* REFERENCES
*
*
* COPYRIGHT     Meteo-France
*
*#########################################################################*/

#define _POSIX_SOURCE 1
#define _XOPEN_SOURCE 600

#include <stdio.h>
#include <math.h>
#include <string.h>
#include <limits.h>
#include <stdlib.h>

#include "struct_oper.h"
#include "thermo.h"
#include "unit_def.h"

/* La vraie fonction... */
long
Flux_LE_from_mass (unsigned long NLoop,
	 	float *flx_h2o,
		float *Ta,
		float *Flx_LE )
{
  int flag_info;
  unsigned long  k; 

  float Lv;

  float C_to_K_moy;


/* vérification de la température  et initialisation
du coef de conversion */ 
 
  flag_info = auto_tempe_unit (NLoop, Ta, &C_to_K_moy);

  if (flag_info == MANQUANTES)
    return flag_info;

   for (k = 0; k < NLoop; k++)

   {
      
/* calcul des flux */

/* appel des fonctions de la la lib thermo */

      clw( (float)(Ta[k] + C_to_K_moy), &Lv);  

      Flx_LE[k] = (float)(Lv*flx_h2o[k]*0.001);
 
    }
  return flag_info;
}

/* la fonction d'enrobage classique */

int
OP_Flux_LE_from_mass (unsigned long NbVal, void *ArgList[], char *DiagExec)
{
  long CodRet;
  int NCar;

  NCar = sprintf (DiagExec, "Flux_LE_from_mass : (%ld echant.) ", NbVal) ;
  if (NCar < 0)
    NCar = 0;
  DiagExec += NCar;

  CodRet = Flux_LE_from_mass (NbVal,
		       (float *) ArgList[0],
		       (float *) ArgList[1],
		       (float *) ArgList[2]);

 switch (CodRet)
    {
    case T_EN_K:
      strcat (DiagExec, " Tempe reconnue en Kelvins");
      break;;
    case T_EN_C:
      strcat (DiagExec, " Tempe reconnue en degres Celsius");
      break;;
    case MANQUANTES:
      strcat (DiagExec, "Unite tempe non reconnue");
      return OP_FAIL;
      break;
    }
  return OP_OK;

}

void
ID_Flux_LE_from_mass (oper * optr)
{
  strcpy (optr->Nom, "Flux_LE_from_mass");
  optr->Version = "$Revision: 6417 $";
  optr->Date = "$Date: 2016-06-21 15:32:35 +0200 (mar. 21 juin 2016) $";
  optr->fctptr = OP_Flux_LE_from_mass;
  optr->NbArg = 3;
  optr->misval_auto = 1;

  optr->Arg_Car[0].direction = DIR_IN;
  optr->Arg_Car[0].categorie = VECTOR;
  optr->Arg_Car[0].typ = ATYC_IF32;
  optr->Arg_Car[0].array_dim = "1";
  optr->Arg_Car[0].type_sample = "any";
  optr->Arg_Car[0].sample = "any";
  optr->Arg_Car[0].unite = "g.m-2.s-1"; 
  optr->Arg_Car[0].famille = "flux"; 

  optr->Arg_Car[1].direction = DIR_IN;
  optr->Arg_Car[1].categorie = VECTOR;
  optr->Arg_Car[1].typ = ATYC_IF32;
  optr->Arg_Car[1].array_dim = "1";
  optr->Arg_Car[1].type_sample = "any";
  optr->Arg_Car[1].sample = "any";
  optr->Arg_Car[1].unite = "any"; 
  optr->Arg_Car[1].famille = "temperature"; 

  optr->Arg_Car[2].direction = DIR_OUT;
  optr->Arg_Car[2].categorie = VECTOR;
  optr->Arg_Car[2].typ = ATYC_IF32;
  optr->Arg_Car[2].array_dim = "1";
  optr->Arg_Car[2].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[2].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[2].sample = "$Arg1.sample";
  optr->Arg_Car[2].ref_time = "$Arg1.ref_time";
  optr->Arg_Car[2].unite = "W/m2";
  optr->Arg_Car[2].famille = "\"flux\"";
  optr->Arg_Car[2].name = "\"Flux de chaleur latente\"";
  optr->Arg_Car[2].name = "\"Latent heat flux\"";
}
