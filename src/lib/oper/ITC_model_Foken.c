/*************************************************************************
*
* OPERATOR         ITC_model_Foken FUNCTION ANSI-C
*
* PURPOSE          Calcule la caracteristique integrale de la turbulence
*                  (Integral Turbulent Characteristis en anglais) a partir 
*                  des modèles fournis par Foken
*
* DESCRIPTION     Utilisation du modele fourni par Foken 
* 	            
*
* VERSION          1.0 
*
* ARGUMENTS  
*            IN   float      Ustar   Vitesse de frottement  
*            IN	  float      LMO     Longueur de Monin-Obukhov 
*            IN	  float      z       Hauteur de mesure (m) 
*            IN	  float      Hc      Hauteur de la canopée (m) 
*            IN	  float      Lat     Latitude (degres decimal) 
*
*            OUT  float      ITCm_U     Caracteristique integrale de la turbulence selon U 
*            OUT  float      ITCm_W     Caracteristique integrale de la turbulence selon W 
*            OUT  float      ITCm_T     Caracteristique integrale de la turbulence selon T 
*
* ENTRY        NONE
*        
* SUBPROGRAMS  NONE
*        
* REFERENCES 
*
*            T. Foken, Micrometeorology, 2008 
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
ITC_model_Foken ( unsigned long ndata,
			float *Ustar,
			float *LMO, 
			float z,
			float Hc, 
			float Lat,
			float *ITCm_U,
	       		float *ITCm_W,
	                float *ITCm_T)

{
 long i; 	
 double zL, f, c1, c2;

 /* calcul du paramètre de Coriolis f */

 f = fabs ( 2. * (2.*M_PI/(24.*60.*60.)) * sin(M_PI*Lat/180.) );	 

 for (i = 0; i < ndata; i++)
    {
      zL = z / LMO[i];

      /**** calcul de ITCm_U ****/
      if (fabs(zL) < 0.032)
	 {
	  c1 = 2.7;
          c2 = 0.0;
	 }
      else if (fabs(zL) >= 0.032 )
	 {
	  c1 = 4.15;
          c2 = 1./8.;
	 }
      ITCm_U[i] = c1*pow(fabs(zL), c2 );

      /* after Thomas und Foken 2002 under near neutral conditions */
      if ((-0.2 < zL) && (zL < 0.4))
	 {
          ITCm_U[i]  = 0.44 * log(1. * f / Ustar[i]) + 6.3;
	 }
     
      /**** calcul de ITCm_W ****/
      if (fabs(zL) < 0.032)
	 {
	  c1 = 1.3;
          c2 = 0.0;
	 }
      else if (fabs(zL) >= 0.032 )
	 {
	  c1 = 2.0;
	  c2 = 1./8.;
	 }

      ITCm_W[i] = c1*pow(fabs(zL), c2 );

      /* after Thomas und Foken 2002 under near neutral conditions */
      if ((-0.2 < zL) && (zL < 0.4))
	 {
          ITCm_W[i]  = 0.21 * log(1. * f / Ustar[i]) + 3.1; 
	 }

      /**** calcul de ITCm_T ****/

      if ((0.02 <= zL) && (zL < 1.)) /*stable*/
          {
	   c1 = 1.4;
	   c2 = -1./4.;
	  }
      else if ((0.02 > zL) && (zL >= -0.062)) /*near neutral*/ 
          {
           c1 = 0.5;
	   c2 = -1./2.;
	  }
      else if ((-0.062 > zL) && (zL >= -1.)) /*unstable*/
	  {
           c1 = 1.0;
           c2 = -1./4.;
	  }
      else if (-1. > zL) /*very unstable*/
	  {
           c1 = 1.0;
           c2 = -1./3.;
	  }
      else if (zL >= 1.) /*very stable*/
	  {
	   c1 = 1.4;
	   c2 = -1./3.;
	  }

      ITCm_T[i] = c1*pow(fabs(zL), c2 );
 
    }

  return 0;
}

int 
OP_ITC_model_Foken( unsigned long NbVal, void *ArgList[], char *DiagExec)
{
  unsigned long Codret;
		
  Codret = ITC_model_Foken ( NbVal,
		      (float *) ArgList[0],
		      (float *) ArgList[1],
		      *((float *) ArgList[2]),
		      *((float *) ArgList[3]),
		      *((float *) ArgList[4]),
		      (float *) ArgList[5],
		      (float *) ArgList[6],
		      (float *) ArgList[7]);
  if (Codret < 0 )
     return OP_FAIL;
  else 
     return OP_OK;
}



void
ID_ITC_model_Foken (oper *optr)
{
  int idx;
  strcpy (optr->Nom, "ITC_model_Foken");
  optr->Version = "Revision:$";
  optr->Date = "$Date:$";
  optr->fctptr = OP_ITC_model_Foken;
  optr->NbArg = 8;		/* doit rester inf. a FIL_MAX_ARG */

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
  optr->Arg_Car[idx].type_sample = NULL;
  optr->Arg_Car[idx].sample = NULL;
  optr->Arg_Car[idx].unite = "";
  idx++;

  optr->Arg_Car[idx].direction = DIR_IN;
  optr->Arg_Car[idx].categorie = COEFFICIENT;
  optr->Arg_Car[idx].typ = ATYC_IF32;
  optr->Arg_Car[idx].array_dim = "1";
  optr->Arg_Car[idx].type_sample = NULL;
  optr->Arg_Car[idx].sample = NULL;
  optr->Arg_Car[idx].unite = "";
  idx++;

  optr->Arg_Car[idx].direction = DIR_IN;
  optr->Arg_Car[idx].categorie = COEFFICIENT;
  optr->Arg_Car[idx].typ = ATYC_IF32;
  optr->Arg_Car[idx].array_dim = "1";
  optr->Arg_Car[idx].type_sample = NULL;
  optr->Arg_Car[idx].sample = NULL;
  optr->Arg_Car[idx].unite = "";
  idx++;
  
  optr->Arg_Car[idx].direction = DIR_IN;
  optr->Arg_Car[idx].categorie = COEFFICIENT;
  optr->Arg_Car[idx].typ = ATYC_IF32;
  optr->Arg_Car[idx].array_dim = "1";
  optr->Arg_Car[idx].type_sample = NULL;
  optr->Arg_Car[idx].sample = NULL;
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
  optr->Arg_Car[idx].name = "\"Caracteristique integrale turbulente de U calculee par le modele Foken";
  optr->Arg_Car[idx].en_name = "\"Integral turbulence characteristics of U calculated with Foken model";
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
  optr->Arg_Car[idx].name = "\"Caracteristique integrale turbulente de W calculee par le modele Foken";
  optr->Arg_Car[idx].en_name = "\"Integral turbulence characteristics of U calculated with Foken model";
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
  optr->Arg_Car[idx].name = "\"Caracteristique integrale turbulente de T calculee par le modele Foken";
  optr->Arg_Car[idx].en_name = "\"Integral turbulence characteristics of U calculated with Foken model";
  idx++;

}




