/*******************************************************************
* OPERATOR      fssp_Tbar.c FUNCTION ANSI-C
*
* PURPOSE       Estimation du temps de transit d'une particule
*
* DESCRIPTION   Le temps de transit d'un particule 
*		est calcule a partir de la duree   
*	        d'impulsion moyenne.	
*
* VERSION       1.0
*
*		IN 	float 	strobe		nombre de particules dans la DOF
*		IN	float 	reset		nombre de particules total dans et hors de la DOF  
*               IN      float   activity        activite de la sonde (s)
*		IN 	float   fr 		frequency (Hz) 
*		IN 	float   tau1		delai electronique mesure en labo. (second) 
*		IN	float   tau2	     	delai electronique mesure en labo. (second)
*		IN	float	crt0		seuil de tau de comptage pour le calcul 
*						de Tbar
*
*               OUT     float   Tbar	        temps de transit d'une particule (second)	
*
* ENTRY         NONE
*
* SUBPROGRAMS   NONE
*
* REFERENCES   	  
*		Coincidence and Dead-Time Corrections for Particle Counters.
*		Part I : A general Mathematical Formalism. J-L Brenguier and L. Amodei 
*               Part II : High concentration Measurements with an FSSP. J-L Brenguier 
*		Journal of Atmos. and Ocean. Technolology, Vol 6, No 4, August 1989
*             
* COPYRIGHT     Meteo-France
*               Centre National de Recherches Meteorologiques
*               GMEI/MMA
*               42, av. G. Coriolis
*               31057   TOULOUSE cedex
*              
*******************************************************************/

#define _POSIX_SOURCE 1
#define _XOPEN_SOURCE 600
/* Le #define _HPUX_SOURCE n'est la que pour "voir" strdup */
#define _HPUX_SOURCE 1
#define _XOPEN_SOURCE_EXTENDED 1

#include <stdio.h>
#include <string.h>
#include <math.h>
#include "struct_oper.h"

void
fssp_Tbar (unsigned long ndata,
	   const float *strobe,
	   const float *reset,
	   const float *activity,
	   float fr,
           float tau1,
           float tau2,
           float crt0,
           float *Tbar)
{
/*** pour specifier si l'appareil possede
     un seul delai il suffit de mettre 
     tau1 a une valeur negative ****/

  unsigned long i;
  float DOF, taubar, t;

  /*** calcul du temps de transit ***/

  for (i = 0; i < ndata; i++)
    {
      if ((fr * reset[i]) < crt0)
	{
	  Tbar[i] = 0.;
	  continue;
	}

      DOF = strobe[i] / reset[i];

      if ((tau1 > 0.) && (DOF < 1.))
	{
	  /* 2 delais */
	  taubar = (1. - DOF) * tau1 + (DOF * tau2);
	}
      else
	{
	  /* 1 seul delai long */
	  taubar = tau2;
	}

      t = activity[i] / (fr * reset[i]);
/*
   if ( (reset[i] > 100. ) && (i <400000) ) 
   fprintf(stderr, "DOF = %f , taubar = %f  t = %f \n", DOF, taubar, t);
 */

      Tbar[i] = t - taubar;

      if (Tbar[i] < 0.)
	Tbar[i] = 0.;
    }

  return;
}

/* fonction d'enrobage */

int
OP_fssp_Tbar (unsigned long Nbval, void *ArgList[], char *DiagExec)
{
  sprintf (DiagExec, "fssp_Tbar, freq = %g, tau1 = %f, tau2 = %f, seuil = %g",
	   *((float *) ArgList[3]),
	   *((float *) ArgList[4]),
	   *((float *) ArgList[5]), *((float *) ArgList[6]));

  fssp_Tbar (Nbval,
	     (float *) ArgList[0],
	     (float *) ArgList[1],
	     (float *) ArgList[2],
	     *((float *) ArgList[3]),
	     *((float *) ArgList[4]),
	     *((float *) ArgList[5]),
	     *((float *) ArgList[6]),
             (float *) ArgList[7]);

  return OP_OK;
}

void
ID_fssp_Tbar (oper * optr)
{
  strcpy (optr->Nom, "fssp_Tbar");
  optr->Version = "1.0";
  optr->Date = "10/24/96";
  optr->fctptr = OP_fssp_Tbar;
  optr->NbArg = 8;

  /* strobe */
  optr->Arg_Car[0].direction = DIR_IN;
  optr->Arg_Car[0].categorie = VECTOR;
  optr->Arg_Car[0].typ = ATYC_IF32;
  optr->Arg_Car[0].array_dim = "1";
  optr->Arg_Car[0].type_sample = "any";
  optr->Arg_Car[0].sample = "any";
  optr->Arg_Car[0].unite = "";

  /* reset */
  optr->Arg_Car[1].direction = DIR_IN;
  optr->Arg_Car[1].categorie = VECTOR;
  optr->Arg_Car[1].typ = ATYC_IF32;
  optr->Arg_Car[1].array_dim = "1";
  optr->Arg_Car[1].type_sample = "any";
  optr->Arg_Car[1].sample = "any";
  optr->Arg_Car[1].unite = "";

  /* activity */
  optr->Arg_Car[2].direction = DIR_IN;
  optr->Arg_Car[2].categorie = VECTOR;
  optr->Arg_Car[2].typ = ATYC_IF32;
  optr->Arg_Car[2].array_dim = "1";
  optr->Arg_Car[2].type_sample = "any";
  optr->Arg_Car[2].sample = "any";
  optr->Arg_Car[2].unite = "second";

  optr->Arg_Car[3].direction = DIR_IN;
  optr->Arg_Car[3].categorie = COEFFICIENT;
  optr->Arg_Car[3].typ = ATYC_IF32;
  optr->Arg_Car[3].array_dim = "1";
  optr->Arg_Car[3].type_sample = NULL;
  optr->Arg_Car[3].sample = NULL;
  optr->Arg_Car[3].unite = "Hz";

  optr->Arg_Car[4].direction = DIR_IN;
  optr->Arg_Car[4].categorie = COEFFICIENT;
  optr->Arg_Car[4].typ = ATYC_IF32;
  optr->Arg_Car[4].array_dim = "1";
  optr->Arg_Car[4].type_sample = NULL;
  optr->Arg_Car[4].sample = NULL;
  optr->Arg_Car[4].unite = "second";

  optr->Arg_Car[5].direction = DIR_IN;
  optr->Arg_Car[5].categorie = COEFFICIENT;
  optr->Arg_Car[5].typ = ATYC_IF32;
  optr->Arg_Car[5].array_dim = "1";
  optr->Arg_Car[5].type_sample = NULL;
  optr->Arg_Car[5].sample = NULL;
  optr->Arg_Car[5].unite = "second";

  optr->Arg_Car[6].direction = DIR_IN;
  optr->Arg_Car[6].categorie = COEFFICIENT;
  optr->Arg_Car[6].typ = ATYC_IF32;
  optr->Arg_Car[6].array_dim = "1";
  optr->Arg_Car[6].type_sample = NULL;
  optr->Arg_Car[6].sample = NULL;
  optr->Arg_Car[6].unite = "without";

  optr->Arg_Car[7].direction = DIR_OUT;
  optr->Arg_Car[7].categorie = VECTOR;
  optr->Arg_Car[7].typ = ATYC_IF32;
  optr->Arg_Car[7].array_dim = "1";
  optr->Arg_Car[7].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[7].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[7].sample = "$Arg1.sample";
  optr->Arg_Car[7].ref_time = "$Arg1.ref_time";
  optr->Arg_Car[7].unite = "second";
}
