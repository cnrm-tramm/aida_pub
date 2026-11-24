/****************************************************
*
* OPERATOR     Rotat_XY.c   FUNCTION  ANSI-C
*
* PURPOSE      	Double rotation des composantes U, V, W autour des axes X et Y  
*
* DESCRIPTION  	
* 		
*
*
* VERSION       $Revision: 5097 $
*
* ARGUMENTS   IN   float  U    		m/s    	        composante U du vent	
*             IN   float  V    		m/s    		composante V du vent 
*             IN   float  W    		m/s    		composante W du vent
*             IN   float  alpha         degrés		angle de rotation autour de l'axe Y ( composante V)	
*             IN   float  beta          degrés		angle de rotation autour de l'axe X ( composante U)	
*             IN   float  offset_W      m/s		offset sur la vitesse verticale	
*
*             OUT  float  U_p      	m/s	        composante U vent après rotation 
*             OUT  float  V_p      	m/s	        composante V vent après rotation 
*             OUT  float  W_p      	m/s	        composante W vent après rotation  
*
* REFERENCES
* 	J.M. Wilczak et al. Sonic Anemometer tilt correction algorihms
*       Boundary Layer Meteorology 99: 127-150, 2001
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

#include "thermo.h"

#include "struct_oper.h"

/* La vraie fonction... */

long
Rotat_XY (unsigned long Ndata,
	  const float *U,
	  const float *V, 
	  const float *W, 
	  const float alpha, 
	  const float beta, 
	  const float w_offset, 
	  float *U_p,
	  float *V_p,
	  float *W_p )
{
  long i; 
  double sin_alpha, cos_alpha, sin_beta, cos_beta, Wc; 

  sin_alpha = sin( alpha*M_PI/180.);
  cos_alpha = cos( alpha*M_PI/180.);
  sin_beta = sin( beta*M_PI/180.);
  cos_beta = cos( beta*M_PI/180.);

  for ( i=0; i< Ndata; i++)
    {
     Wc = W[i] - w_offset;
     U_p[i] = cos_alpha*U[i] - sin_alpha*sin_beta*V[i] + sin_alpha*cos_beta*Wc ; 
     V_p[i] = 0.0            + cos_beta*V[i]           + sin_beta*Wc;
     W_p[i] = sin_alpha*U[i] - cos_alpha*sin_beta*V[i] + cos_alpha*cos_beta*Wc; 
    }

  return 0;
}

/* la fonction d'enrobage classique */

int
OP_Rotat_XY (unsigned long NbVal, void *ArgList[], char *DiagExec)
{
  long CodRet;

  CodRet = Rotat_XY (NbVal,
		     (float *) ArgList[0],
		     (float *) ArgList[1],
		     (float *) ArgList[2],
		     *((float *) ArgList[3]),
		     *((float *) ArgList[4]),
		     *((float *) ArgList[5]),
		     (float *) ArgList[6],
		     (float *) ArgList[7],
		     (float *) ArgList[8] );

  if (CodRet >= 0)
    {
      sprintf (DiagExec, "OK: %ld val. calculées.", CodRet);
      return OP_OK;
    }

}

void
ID_Rotat_XY (oper * optr)
{
  int i;

  strcpy (optr->Nom, "Rotat_XY");
  optr->Version = "$Revision: 5097 $";
  optr->Date = "$Date: 2013-03-25 13:23:40 +0100 (lun. 25 mars 2013) $";
  optr->fctptr = OP_Rotat_XY;
  optr->NbArg = 9;
  optr->misval_auto = 1;

  optr->Arg_Car[0].direction = DIR_IN;
  optr->Arg_Car[0].categorie = VECTOR;
  optr->Arg_Car[0].typ = ATYC_IF32;
  optr->Arg_Car[0].array_dim = "1";
  optr->Arg_Car[0].type_sample = "any";
  optr->Arg_Car[0].sample = "any";
  optr->Arg_Car[0].unite = "m/s";

  optr->Arg_Car[1].direction = DIR_IN;
  optr->Arg_Car[1].categorie = VECTOR;
  optr->Arg_Car[1].typ = ATYC_IF32;
  optr->Arg_Car[1].array_dim = "1";
  optr->Arg_Car[1].type_sample = "any";
  optr->Arg_Car[1].sample = "any";
  optr->Arg_Car[1].unite = "m/s";

  optr->Arg_Car[2].direction = DIR_IN;
  optr->Arg_Car[2].categorie = VECTOR;
  optr->Arg_Car[2].array_dim = "1";
  optr->Arg_Car[2].typ = ATYC_IF32;
  optr->Arg_Car[2].unite = "m/s";
  optr->Arg_Car[2].type_sample = NULL;
  optr->Arg_Car[2].sample = NULL;

  for (i = 3; i <= 5; i++)
    {
      optr->Arg_Car[i].direction = DIR_IN;
      optr->Arg_Car[i].categorie = COEFFICIENT;
      optr->Arg_Car[i].array_dim = "1";
      optr->Arg_Car[i].typ = ATYC_IF32;
      optr->Arg_Car[i].unite = "any";
      optr->Arg_Car[i].type_sample = NULL;
      optr->Arg_Car[i].sample = NULL;
    }
  
  optr->Arg_Car[6].direction = DIR_OUT;
  optr->Arg_Car[6].categorie = VECTOR;
  optr->Arg_Car[6].typ = ATYC_IF32;
  optr->Arg_Car[6].array_dim = "1";
  optr->Arg_Car[6].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[6].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[6].sample = "$Arg1.sample";
  optr->Arg_Car[6].ref_time = "$Arg1.ref_time";
  optr->Arg_Car[6].unite = "$Arg1.unit";
  optr->Arg_Car[6].misval = "$Arg1.misval";
  optr->Arg_Car[6].famille = "$Arg1.famille";
  optr->Arg_Car[6].name = "\"Composante U du vent issue d'une rotation planar-fit\"";
  optr->Arg_Car[6].en_name = "\"U wind component after planar-fit rotation\"";

  optr->Arg_Car[7].direction = DIR_OUT;
  optr->Arg_Car[7].categorie = VECTOR;
  optr->Arg_Car[7].typ = ATYC_IF32;
  optr->Arg_Car[7].array_dim = "1";
  optr->Arg_Car[7].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[7].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[7].sample = "$Arg1.sample";
  optr->Arg_Car[7].ref_time = "$Arg1.ref_time";
  optr->Arg_Car[7].unite = "$Arg1.unit";
  optr->Arg_Car[7].misval = "$Arg1.misval";
  optr->Arg_Car[7].famille = "$Arg1.famille";
  optr->Arg_Car[7].name = "\"Composante V du vent issue d'une rotation planar-fit\"";
  optr->Arg_Car[7].en_name = "\"V wind component after planar-fit rotation\"";

  optr->Arg_Car[8].direction = DIR_OUT;
  optr->Arg_Car[8].categorie = VECTOR;
  optr->Arg_Car[8].typ = ATYC_IF32;
  optr->Arg_Car[8].array_dim = "1";
  optr->Arg_Car[8].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[8].sample = "$Arg1.sample";
  optr->Arg_Car[8].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[8].ref_time = "$Arg1.ref_time";
  optr->Arg_Car[8].unite = "$Arg1.unit";
  optr->Arg_Car[8].misval = "$Arg1.misval";
  optr->Arg_Car[8].famille = "$Arg1.famille";
  optr->Arg_Car[8].name = "\"Composante W du vent issue d'une rotation planar-fit\"";
  optr->Arg_Car[8].en_name = "\"W wind component after planar-fit rotation\"";
}
