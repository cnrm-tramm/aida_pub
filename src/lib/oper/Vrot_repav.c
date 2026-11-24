/*************************************************************************
*
* OPERATOR         Vrot_repav.c  FUNCTION ANSI-C
*
* PURPOSE          Computation of angular speed of the aircraft 
                   in the aircraft frame 
*
* DESCRIPTION 
*		   Ce programme calcule les vitesses de rotation de l'avion
*		   autour de ses axes a partir des derivees des angles d'attitudes
*		   et des angles d'attitudes.
*
*      Elles sont calculées de la facon suivante :
*
*      |VRX     |dPhi          |0                  |0
*      |VRY  =  | 0   + M_phi .|dTheta + M_geo2av .|0 
*      |VRZ     | 0            |0                  |dPsi
*
*  avec dPhi : derivee du roulis
*	dTheta : derivee du tangage 
*	dCap : derivee du cap
*
*	M_phi : matrice de rotation de l'angle de roulis
*
*	             | 1     0         0     | 
*	     M_phi = | 0  cos(Phi)  sin(Phi) |
*                    | 0 -sin(Phi)  cos(Phi) | 
*
*	M_geo2av : matrice de passage du repere geographique au repere avion 
*		   (voir operateur Geo2mobile_3D.c)
*	
*
* VERSION    $Revision$
*
* ARGUMENTS  
*            IN   float   Roul	rad     Roll angle  
*            IN   float   Tang	rad     Pitch angle	
*            IN   float   dRoul rad/s  	Derivate of Roll 
*            IN   float   dTang rad/s   Derivate of Pitch 
*            IN   float   dCap	rad/s	Derivate of heading  
*            OUT  float*  Vrx	m/s	Angular speed around longitudinal aircraft axe  
*            OUT  float*  Vry	m/s 	Angular speed around transversal aircraft axe
*            OUT  float*  Vrz	m/s	Angular speed around vertical aircarft axe	
*
* ENTRY        NONE
*        
* SUBPROGRAMS  NONE
*
* FILES        NONE
*        
* REFERENCES   Measurements techniques: air motion sensing
*	       D. H. Lenschow and P. Spyers-Duran
*	       NCAR/RAF  bulletin no. 23, 1987 
*	
*	       Norme AFNOR NF X 02-115 Decembre 1974
*
* CHANGES       
*	 
*
* COPYRIGHT    Meteo-France
*	       Centre National de Recherches Meteorologiques 
*	       GMEI/ MMA
*	       42, av G. Coriolis
*	       31057 TOULOUSE cedex  
*
*
*############################################################################*/

#define _POSIX_SOURCE 1
#define _XOPEN_SOURCE 600
#define _XOPEN_SOURCE_EXTENDED 1

#include <math.h>
#include <stdio.h>
#include <string.h>
#include "struct_oper.h"


void
Vrot_repav (unsigned long NLoop,
	    const float *Roul,
	    const float *Tang,
	    const float *dRoul,
	    const float *dTang,
	    const float *dCap,
	    float *Vrx,
	    float *Vry, 
	    float *Vrz)
{
  unsigned long i;

  double siro, coro, cota, sita;

  for (i = 0; i < NLoop; i++)
    {
      siro = sin (*Roul);
      coro = cos (*Roul);
      cota = cos (*Tang);
      sita = sin (*Tang);

      *Vrx = *dRoul - sita * (*dCap);
      *Vry = coro * (*dTang) + siro * cota * (*dCap);
      *Vrz = -siro * (*dTang) + coro * cota * (*dCap);

      Roul++;
      Tang++;
      dRoul++;
      dTang++;
      dCap++;
      Vrx++;
      Vry++;
      Vrz++;
    }
  return;
}


/* la fonction d'enrobage classique */

int
OP_Vrot_repav (unsigned long NbVal, void *ArgList[], char *DiagExec)
{
  DiagExec[0] = 0;

  Vrot_repav (NbVal,
	      (float *) ArgList[0],
	      (float *) ArgList[1],
	      (float *) ArgList[2],
	      (float *) ArgList[3],
	      (float *) ArgList[4],
	      (float *) ArgList[5],
	      (float *) ArgList[6],
	      (float *) ArgList[7]);
  return OP_OK;
}

void
ID_Vrot_repav (oper * optr)
{
  int idx = 0;
  strcpy (optr->Nom, "Vrot_repav");
  optr->Version = "$Revision$";
  optr->Date = "$Date$";
  optr->fctptr = OP_Vrot_repav;
  optr->NbArg = 8;		/* doit rester inf. a FIL_MAX_ARG */

  /* Roul */
  optr->Arg_Car[idx].direction = DIR_IN;
  optr->Arg_Car[idx].categorie = VECTOR;
  optr->Arg_Car[idx].typ = ATYC_IF32;
  optr->Arg_Car[idx].array_dim = "1";
  optr->Arg_Car[idx].type_sample = "any";
  optr->Arg_Car[idx].sample = "any";
  optr->Arg_Car[idx].unite = "radians";
  idx++;

  /* Tang */
  optr->Arg_Car[idx].direction = DIR_IN;
  optr->Arg_Car[idx].categorie = VECTOR;
  optr->Arg_Car[idx].typ = ATYC_IF32;
  optr->Arg_Car[idx].array_dim = "1";
  optr->Arg_Car[idx].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[idx].type_sample = "any";
  optr->Arg_Car[idx].sample = "any";
  optr->Arg_Car[idx].unite = "radians";
  idx++;

  /* dRoul */
  optr->Arg_Car[idx].direction = DIR_IN;
  optr->Arg_Car[idx].categorie = VECTOR;
  optr->Arg_Car[idx].typ = ATYC_IF32;
  optr->Arg_Car[idx].array_dim = "1";
  optr->Arg_Car[idx].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[idx].type_sample = "any";
  optr->Arg_Car[idx].sample = "any";
  optr->Arg_Car[idx].unite = "any";
  idx++;

  /* dTang */
  optr->Arg_Car[idx].direction = DIR_IN;
  optr->Arg_Car[idx].categorie = VECTOR;
  optr->Arg_Car[idx].typ = ATYC_IF32;
  optr->Arg_Car[idx].array_dim = "1";
  optr->Arg_Car[idx].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[idx].type_sample = "any";
  optr->Arg_Car[idx].sample = "any";
  optr->Arg_Car[idx].unite = "$Arg3.unit";
  idx++;

  /* dCap */
  optr->Arg_Car[idx].direction = DIR_IN;
  optr->Arg_Car[idx].categorie = VECTOR;
  optr->Arg_Car[idx].typ = ATYC_IF32;
  optr->Arg_Car[idx].array_dim = "1";
  optr->Arg_Car[idx].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[idx].type_sample = "any";
  optr->Arg_Car[idx].sample = "any";
  optr->Arg_Car[idx].unite = "$Arg3.unit";
  idx++;

  /* Vrx  */
  optr->Arg_Car[idx].direction = DIR_OUT;
  optr->Arg_Car[idx].categorie = VECTOR;
  optr->Arg_Car[idx].typ = ATYC_IF32;
  optr->Arg_Car[idx].array_dim = "1";
  optr->Arg_Car[idx].NbVal = "$Arg3.NbVal";
  optr->Arg_Car[idx].type_sample = "$Arg3.type_sample";
  optr->Arg_Car[idx].sample = "$Arg3.sample";
  optr->Arg_Car[idx].ref_time = "$Arg3.ref_time";
  optr->Arg_Car[idx].unite = "$Arg3.unit";
  optr->Arg_Car[idx].famille = " \"vitesse\" ";
  optr->Arg_Car[idx].name = " \"Vitesse de rotation axe X\" ";
  optr->Arg_Car[idx].en_name = " \"Rotation speed around X axis\" ";
  idx++;

  /* Vry  */
  optr->Arg_Car[idx].direction = DIR_OUT;
  optr->Arg_Car[idx].categorie = VECTOR;
  optr->Arg_Car[idx].typ = ATYC_IF32;
  optr->Arg_Car[idx].array_dim = "1";
  optr->Arg_Car[idx].NbVal = "$Arg3.NbVal";
  optr->Arg_Car[idx].type_sample = "$Arg3.type_sample";
  optr->Arg_Car[idx].sample = "$Arg3.sample";
  optr->Arg_Car[idx].ref_time = "$Arg3.ref_time";
  optr->Arg_Car[idx].unite = "$Arg3.unit";
  optr->Arg_Car[idx].famille = " \"vitesse\" ";
  optr->Arg_Car[idx].name = " \"Vitesse de rotation axe Y\" ";
  optr->Arg_Car[idx].en_name = " \"Rotation speed around Y axis\" ";
  idx++;

  /* Vrz  */
  optr->Arg_Car[idx].direction = DIR_OUT;
  optr->Arg_Car[idx].categorie = VECTOR;
  optr->Arg_Car[idx].typ = ATYC_IF32;
  optr->Arg_Car[idx].array_dim = "1";
  optr->Arg_Car[idx].NbVal = "$Arg3.NbVal";
  optr->Arg_Car[idx].type_sample = "$Arg3.type_sample";
  optr->Arg_Car[idx].sample = "$Arg3.sample";
  optr->Arg_Car[idx].ref_time = "$Arg3.ref_time";
  optr->Arg_Car[idx].unite = "$Arg3.unit";
  optr->Arg_Car[idx].famille = " \"vitesse\" ";
  optr->Arg_Car[idx].name = " \"Vitesse de rotation axe Z\" ";
  optr->Arg_Car[idx].en_name = " \"Rotation speed around Z axis\" ";
  idx++;
}
