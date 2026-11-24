/*************************************************************************
*
* OPERATOR         CalcVentNA.c  FUNCTION ANSI-C
*
* PURPOSE          computation of wind 
*
* DESCRIPTION 
*
* Ce programme calcule le vent dans le repère géographique terrestre.
*
* Ce programme est issu de CalcVent mais traite le cas d'une INS Non Alignée (CalcVentNA)
*
* Les composantes de la vitesse de l'avion par rapport au sol
* doivent être données dans le repère lié à l'avion tel que:
*	- "x" suivant l'axe longitudinal de l'avion vers l'avant
*	- "y" suivant l'axe tranversal vers coté tribord 
*	- "z" suivant la verticale de l'avion vers le bas 
*
* Le vent est calculé d'abord dans le repère de l'avion puis on le
* passe dans le repère géographique.
* 
* 
* This procedure compute the wind with respect to the earth frame.
* 
* The velocity of the aircraft must be given with respect to the
* aircraft frame such as:
*	- "x" following the aircraft lengthwise axe towards front
*	- "y" following the aircraft tranverse axe towards right side
*	- "z" following the aircraft vertical axe downward 
*
* The wind is computed with respect the aircraft frame, and
* then it is transformed to the earth frame.
*
* VERSION          1.0 
*
* ARGUMENTS  IN   float   Lx     m      distance between the INS and the 
*					measure of "Alpha" and "Beta", with
*					respect to the axe "x" 
*	     IN   float   Ly     m      distance between the INS wrt "y" axis      ***New
*	     IN   float   Lz     m      distance between the INS wrt "z" axis      ***New
*            IN   float   Vp     m/s    True Air Speed     
*            IN   float   Alpha  rad   	Angle of Attack
*            IN   float   Beta   rad   	Angle of Sideslip 
*            IN   float   Vx     m/s   	Aircraft velocity with respect to 
*					the aircraft lengthwise axe 
*            IN   float   Vy     m/s    Aircraft velocity with respect to
*					the aircraft transverse axe
*            IN   float   Vz     m/s    Aircraft velocity with respect to
*					the aircraft vertical axe 
*            IN   float   Vrx	 radian/s	Roll rate                                  ***New
*            IN   float   Vry	 radian/s	Pitch rate 
*            IN   float   Vrz  	 radian/s	Yaw rate 
*            IN   float   Theta	 rad	Pitch Attitude 
*            IN   float   Phi    rad	Roll Attitude
*            IN   float   Psi	 rad	Head
*            OUT  float*  U	 m/s	East component, from West 
*            OUT  float*  V      m/s	North component, from South
*            OUT  float*  W      m/s	Vertical component, + up
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

#include <math.h>
#include <stdio.h>
#include <string.h>
#include "struct_oper.h"


int
CalcVentNA (unsigned long NLoop,
	    float Lx,
	    float Ly,
	    float Lz,
	    const float *Vp,
	    const float *Alpha,
	    const float *Beta,
	    const float *Vx,
	    const float *Vy,
	    const float *Vz,
	    const float *Vrx,
	    const float *Vry,
	    const float *Vrz,
	    const float *Theta,
	    const float *Phi, const float *Psi, float *U, float *V, float *W)
{
  unsigned long i;
  float stheta, sphi, spsi, ctheta, cphi, cpsi, talpha, tbeta, D_1;
  float ua, va, wa;

  for (i = 0; i < NLoop; i++)
    {
      stheta = sin (*Theta);
      sphi = sin (*Phi);
      spsi = sin (*Psi);
      ctheta = cos (*Theta);
      cphi = cos (*Phi);
      cpsi = cos (*Psi);
      talpha = tan (*Alpha);
      tbeta = tan (*Beta);

      D_1 = 1. / (sqrt (1. + talpha * talpha + tbeta * tbeta));

      ua = *Vx - *Vp * D_1 * 1 + Lz * *Vry - Ly * *Vrz;
      va = *Vy - *Vp * D_1 * tbeta + Lx * *Vrz - Lz * *Vrx;
      wa = *Vz - *Vp * D_1 * talpha + Ly * *Vrx - Lx * *Vry;

      *U = ua * spsi * ctheta + va * (cpsi * cphi + spsi * stheta * sphi)
	+ wa * (spsi * stheta * cphi - cpsi * sphi);

      *V = ua * cpsi * ctheta - va * (spsi * cphi - cpsi * stheta * sphi)
	+ wa * (cpsi * stheta * cphi + spsi * sphi);

      *W = ua * stheta - va * ctheta * sphi - wa * ctheta * cphi;

      Vp++;
      Alpha++;
      Beta++;
      Vx++;
      Vy++;
      Vz++;
      Vrx++;
      Vry++;
      Vrz++;
      Theta++;
      Phi++;
      Psi++;
      U++;
      V++;
      W++;
    }
  return 0;
}


/* la fonction d'enrobage classique */

int
OP_CalcVentNA (unsigned long NbVal, void *ArgList[], char *DiagExec)
{
  int CodRet;

  CodRet = CalcVentNA (NbVal,
		       *((float *) ArgList[0]),
		       *((float *) ArgList[1]),
		       *((float *) ArgList[2]),
		       (float *) ArgList[3],
		       (float *) ArgList[4],
		       (float *) ArgList[5],
		       (float *) ArgList[6],
		       (float *) ArgList[7],
		       (float *) ArgList[8],
		       (float *) ArgList[9],
		       (float *) ArgList[10],
		       (float *) ArgList[11],
		       (float *) ArgList[12],
		       (float *) ArgList[13],
		       (float *) ArgList[14],
		       (float *) ArgList[15],
		       (float *) ArgList[16],
		       (float *) ArgList[17]);
  return OP_OK;
}

void
ID_CalcVentNA (oper * optr)
{
  strcpy (optr->Nom, "CalcVentNA");
  optr->Version = "$Revision$";
  optr->Date = "$Date$";
  optr->fctptr = OP_CalcVentNA;
  optr->NbArg = 18;		/* doit rester inf. a FIL_MAX_ARG */

  /* Lx */
  optr->Arg_Car[0].direction = DIR_IN;
  optr->Arg_Car[0].categorie = COEFFICIENT;
  optr->Arg_Car[0].typ = ATYC_IF32;
  optr->Arg_Car[0].array_dim = "1";
  optr->Arg_Car[0].type_sample = NULL;	/* sans objet pour COEFFICIENT */
  optr->Arg_Car[0].sample = NULL;	/* sans objet pour COEFFICIENT */
  optr->Arg_Car[0].unite = "m";

  /* Ly */
  optr->Arg_Car[1].direction = DIR_IN;
  optr->Arg_Car[1].categorie = COEFFICIENT;
  optr->Arg_Car[1].typ = ATYC_IF32;
  optr->Arg_Car[1].array_dim = "1";
  optr->Arg_Car[1].type_sample = NULL;	/* sans objet pour COEFFICIENT */
  optr->Arg_Car[1].sample = NULL;	/* sans objet pour COEFFICIENT */
  optr->Arg_Car[1].unite = "m";

  /* Lz */
  optr->Arg_Car[2].direction = DIR_IN;
  optr->Arg_Car[2].categorie = COEFFICIENT;
  optr->Arg_Car[2].typ = ATYC_IF32;
  optr->Arg_Car[2].array_dim = "1";
  optr->Arg_Car[2].type_sample = NULL;	/* sans objet pour COEFFICIENT */
  optr->Arg_Car[2].sample = NULL;	/* sans objet pour COEFFICIENT */
  optr->Arg_Car[2].unite = "m";

  /* Vp */
  optr->Arg_Car[3].direction = DIR_IN;
  optr->Arg_Car[3].categorie = VECTOR;
  optr->Arg_Car[3].typ = ATYC_IF32;
  optr->Arg_Car[3].array_dim = "1";
  optr->Arg_Car[3].type_sample = "any";
  optr->Arg_Car[3].sample = "any";
  optr->Arg_Car[3].unite = "m/s";

  /* Alpha */
  optr->Arg_Car[4].direction = DIR_IN;
  optr->Arg_Car[4].categorie = VECTOR;
  optr->Arg_Car[4].typ = ATYC_IF32;
  optr->Arg_Car[4].array_dim = "1";
  optr->Arg_Car[4].NbVal = "$Arg4.NbVal";
  optr->Arg_Car[4].type_sample = "any";
  optr->Arg_Car[4].sample = "any";
  optr->Arg_Car[4].unite = "radian";

  /* Beta */
  optr->Arg_Car[5].direction = DIR_IN;
  optr->Arg_Car[5].categorie = VECTOR;
  optr->Arg_Car[5].typ = ATYC_IF32;
  optr->Arg_Car[5].array_dim = "1";
  optr->Arg_Car[5].NbVal = "$Arg4.NbVal";
  optr->Arg_Car[5].type_sample = "any";
  optr->Arg_Car[5].sample = "any";
  optr->Arg_Car[5].unite = "radian";

  /* Vx */
  optr->Arg_Car[6].direction = DIR_IN;
  optr->Arg_Car[6].categorie = VECTOR;
  optr->Arg_Car[6].typ = ATYC_IF32;
  optr->Arg_Car[6].array_dim = "1";
  optr->Arg_Car[6].NbVal = "$Arg4.NbVal";
  optr->Arg_Car[6].type_sample = "any";
  optr->Arg_Car[6].sample = "any";
  optr->Arg_Car[6].unite = "m/s";

  /* Vy */
  optr->Arg_Car[7].direction = DIR_IN;
  optr->Arg_Car[7].categorie = VECTOR;
  optr->Arg_Car[7].typ = ATYC_IF32;
  optr->Arg_Car[7].array_dim = "1";
  optr->Arg_Car[7].NbVal = "$Arg4.NbVal";
  optr->Arg_Car[7].type_sample = "any";
  optr->Arg_Car[7].sample = "any";
  optr->Arg_Car[7].unite = "m/s";

  /* Vz */
  optr->Arg_Car[8].direction = DIR_IN;
  optr->Arg_Car[8].categorie = VECTOR;
  optr->Arg_Car[8].typ = ATYC_IF32;
  optr->Arg_Car[8].array_dim = "1";
  optr->Arg_Car[8].NbVal = "$Arg4.NbVal";
  optr->Arg_Car[8].type_sample = "any";
  optr->Arg_Car[8].sample = "any";
  optr->Arg_Car[8].unite = "m/s";

  /* Vrx */
  optr->Arg_Car[9].direction = DIR_IN;
  optr->Arg_Car[9].categorie = VECTOR;
  optr->Arg_Car[9].typ = ATYC_IF32;
  optr->Arg_Car[9].array_dim = "1";
  optr->Arg_Car[9].NbVal = "$Arg4.NbVal";
  optr->Arg_Car[9].type_sample = "any";
  optr->Arg_Car[9].sample = "any";
  optr->Arg_Car[9].unite = "radian/s";

  /* Vry */
  optr->Arg_Car[10].direction = DIR_IN;
  optr->Arg_Car[10].categorie = VECTOR;
  optr->Arg_Car[10].typ = ATYC_IF32;
  optr->Arg_Car[10].array_dim = "1";
  optr->Arg_Car[10].NbVal = "$Arg4.NbVal";
  optr->Arg_Car[10].type_sample = "any";
  optr->Arg_Car[10].sample = "any";
  optr->Arg_Car[10].unite = "radian/s";

  /* Vrz */
  optr->Arg_Car[11].direction = DIR_IN;
  optr->Arg_Car[11].categorie = VECTOR;
  optr->Arg_Car[11].typ = ATYC_IF32;
  optr->Arg_Car[11].array_dim = "1";
  optr->Arg_Car[11].NbVal = "$Arg4.NbVal";
  optr->Arg_Car[11].type_sample = "any";
  optr->Arg_Car[11].sample = "any";
  optr->Arg_Car[11].unite = "radian/s";

  /* Theta */
  optr->Arg_Car[12].direction = DIR_IN;
  optr->Arg_Car[12].categorie = VECTOR;
  optr->Arg_Car[12].typ = ATYC_IF32;
  optr->Arg_Car[12].array_dim = "1";
  optr->Arg_Car[12].NbVal = "$Arg4.NbVal";
  optr->Arg_Car[12].type_sample = "any";
  optr->Arg_Car[12].sample = "any";
  optr->Arg_Car[12].unite = "radian";

  /* Phi */
  optr->Arg_Car[13].direction = DIR_IN;
  optr->Arg_Car[13].categorie = VECTOR;
  optr->Arg_Car[13].typ = ATYC_IF32;
  optr->Arg_Car[13].array_dim = "1";
  optr->Arg_Car[13].NbVal = "$Arg4.NbVal";
  optr->Arg_Car[13].type_sample = "any";
  optr->Arg_Car[13].sample = "any";
  optr->Arg_Car[13].unite = "radian";

  /* Psi */
  optr->Arg_Car[14].direction = DIR_IN;
  optr->Arg_Car[14].categorie = VECTOR;
  optr->Arg_Car[14].typ = ATYC_IF32;
  optr->Arg_Car[14].array_dim = "1";
  optr->Arg_Car[14].NbVal = "$Arg4.NbVal";
  optr->Arg_Car[14].type_sample = "any";
  optr->Arg_Car[14].sample = "any";
  optr->Arg_Car[14].unite = "radian";

  /* U */
  optr->Arg_Car[15].direction = DIR_OUT;
  optr->Arg_Car[15].categorie = VECTOR;
  optr->Arg_Car[15].typ = ATYC_IF32;
  optr->Arg_Car[15].array_dim = "1";
  optr->Arg_Car[15].NbVal = "$Arg4.NbVal";
  optr->Arg_Car[15].type_sample = "$Arg4.type_sample";
  optr->Arg_Car[15].sample = "$Arg4.sample";
  optr->Arg_Car[15].ref_time = "$Arg4.ref_time";
  optr->Arg_Car[15].unite = "$Arg4.unit";
  optr->Arg_Car[15].famille = " \"vent\" ";
  optr->Arg_Car[15].name = " \"Composante Ouest-Est du vent\" ";
  optr->Arg_Car[15].en_name = " \"West-East wind component\" ";

  /* V */
  optr->Arg_Car[16].direction = DIR_OUT;
  optr->Arg_Car[16].categorie = VECTOR;
  optr->Arg_Car[16].typ = ATYC_IF32;
  optr->Arg_Car[16].array_dim = "1";
  optr->Arg_Car[16].NbVal = "$Arg4.NbVal";
  optr->Arg_Car[16].type_sample = "$Arg4.type_sample";
  optr->Arg_Car[16].sample = "$Arg4.sample";
  optr->Arg_Car[16].ref_time = "$Arg4.ref_time";
  optr->Arg_Car[16].unite = "$Arg4.unit";
  optr->Arg_Car[16].famille = " \"vent\" ";
  optr->Arg_Car[16].name = " \"Composante Sud-Nord du vent\" ";
  optr->Arg_Car[16].en_name = " \"South-North  wind component\" ";

  /* W */
  optr->Arg_Car[17].direction = DIR_OUT;
  optr->Arg_Car[17].categorie = VECTOR;
  optr->Arg_Car[17].typ = ATYC_IF32;
  optr->Arg_Car[17].array_dim = "1";
  optr->Arg_Car[17].NbVal = "$Arg4.NbVal";
  optr->Arg_Car[17].type_sample = "$Arg4.type_sample";
  optr->Arg_Car[17].sample = "$Arg4.sample";
  optr->Arg_Car[17].ref_time = "$Arg4.ref_time";
  optr->Arg_Car[17].unite = "$Arg4.unit";
  optr->Arg_Car[17].famille = " \"vent\" ";
  optr->Arg_Car[17].name = " \"Composante verticale du vent\" ";
  optr->Arg_Car[17].en_name = " \"Vertical wind component\" ";

}
