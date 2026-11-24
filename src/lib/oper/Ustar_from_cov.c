/****************************************************
*
* OPERATOR      Ustar_from_cov.c   FUNCTION  ANSI-C
*
* PURPOSE      	Calcul de Ustar à partir des
* 		des covariances W'U' et W'V'	
*
* DESCRIPTION    
*
*
* VERSION       $Revision: 6417 $
*
* ARGUMENTS   	
*             IN   float  cov_wu    	m2.s-2   	Covariance W'U'	
*             IN   float  cov_wv    	m2.s-2   	Covariance W'V'	
*
*             OUT  float  Ustar		m/s		Vitesse de frottement 
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
Ustar_from_cov (unsigned long NLoop,
	 	float *cov_wu,
	 	float *cov_wv,
		float *Ustar )
{
  unsigned long  k; 


   for (k = 0; k < NLoop; k++)

   {
      Ustar[k] = sqrt( sqrt( cov_wu[k]*cov_wu[k] + cov_wv[k]*cov_wv[k])) ;
    }
  return OP_OK;

}

/* la fonction d'enrobage classique */

int
OP_Ustar_from_cov (unsigned long NbVal, void *ArgList[], char *DiagExec)
{
  long CodRet;
  int NCar;

  NCar = sprintf (DiagExec, "Ustar_from_cov : (%ld echant.) ", NbVal) ;
  if (NCar < 0)
    NCar = 0;
  DiagExec += NCar;

  CodRet = Ustar_from_cov (NbVal,
		       (float *) ArgList[0],
		       (float *) ArgList[1],
			(float *)  ArgList[2]   );

  return CodRet;
}

void
ID_Ustar_from_cov (oper * optr)
{
  strcpy (optr->Nom, "Ustar_from_cov");
  optr->Version = "$Revision: 6417 $";
  optr->Date = "$Date: 2016-06-21 15:32:35 +0200 (mar. 21 juin 2016) $";
  optr->fctptr = OP_Ustar_from_cov;
  optr->NbArg = 3;
  optr->misval_auto = 1;

  optr->Arg_Car[0].direction = DIR_IN;
  optr->Arg_Car[0].categorie = VECTOR;
  optr->Arg_Car[0].typ = ATYC_IF32;
  optr->Arg_Car[0].array_dim = "1";
  optr->Arg_Car[0].type_sample = "any";
  optr->Arg_Car[0].sample = "any";
  optr->Arg_Car[0].unite = "m2.s-2"; 
  optr->Arg_Car[0].famille = "flux"; 

  optr->Arg_Car[1].direction = DIR_IN;
  optr->Arg_Car[1].categorie = VECTOR;
  optr->Arg_Car[1].typ = ATYC_IF32;
  optr->Arg_Car[1].array_dim = "1";
  optr->Arg_Car[1].type_sample = "any";
  optr->Arg_Car[1].sample = "any";
  optr->Arg_Car[1].unite = "m2.s-2"; 
  optr->Arg_Car[1].famille = "flux"; 

  optr->Arg_Car[2].direction = DIR_OUT;
  optr->Arg_Car[2].categorie = VECTOR;
  optr->Arg_Car[2].typ = ATYC_IF32;
  optr->Arg_Car[2].array_dim = "1";
  optr->Arg_Car[2].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[2].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[2].sample = "$Arg1.sample";
  optr->Arg_Car[2].ref_time = "$Arg1.ref_time";
  optr->Arg_Car[2].unite = "m/s";
  optr->Arg_Car[2].famille = "\"flux\"";
  optr->Arg_Car[2].name = "\"Vitesse de frottement\"";
  optr->Arg_Car[2].name = "\"Friction velocity\"";
}
