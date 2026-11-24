/*******************************************************************
* OPERATOR      rayon_IR.c FUNCTION ANSI-C
*
* PURPOSE       Calcul du flux de rayonnement Infra-Rouge  
*
* DESCRIPTION   Somme de deux termes : 
*		   L'un est la mesure de la thermopile (tension fois coef. sensibilité)
*		   L'autre prend en compte le rayonnement thermique proche (boîtier, coupelle)
*
* VERSION       1.0
*
*               IN      float   Vth		tension thermopile (K)
*               IN      float   Tb		temperature boitier (K)
*               IN      float   Tc 		temperature coupole (K)
*		IN 	float	ath		coefficient de sensibilite de la 
*						thermopile
*		IN	float	K 		correction caracteristique de 
*						la liaison thermique boitier coupole
*
*               OUT     float   IR		Flux Infra-rouge (W/m2)
*
* ENTRY         NONE
*
* SUBPROGRAMS   NONE
*
* REFERENCES   	G. Brogniez, LOA,  Lille  
*
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

#include <stdio.h>
#include <string.h>
#include <math.h>
#include "struct_oper.h"

unsigned long
rayon_IR (unsigned long ndata,
	  const float *Vth,
          const float *Tb,
          const float *Tc,
          float ath,
          float K,
          float *IR)
{
  unsigned long i;
  unsigned long nb_t_inval;

  /*** constante de Stefan-Boltzman ***/
  float sigma = 5.6698e-8;

  const float seuil_mini_t = 150.0;	/* K, soit -123.15 °C */
  float Tc4, Tb4;

  nb_t_inval = 0;
  for (i = 0; i < ndata; i++)
    {
      if ((Tc[i] < seuil_mini_t) || (Tb[i] < seuil_mini_t))
	{
	  nb_t_inval++;
	  IR[i] = 0. / 0.;
	  continue;
	}
      Tb4 = pow (Tb[i], 4);
      Tc4 = pow (Tc[i], 4);
      Tb4 = pow (Tb[i], 4);
      IR[i] = ath * Vth[i] + sigma * (Tb4 + K * (Tb4 - Tc4));
    }

  return nb_t_inval;
}

/* fonction d'enrobage */

int
OP_rayon_IR (unsigned long NbVal, void *ArgList[], char *DiagExec)
{
  unsigned long CodRet;
  int NCar;

  NCar = sprintf (DiagExec,
        	  "rayon_IR, %lu ech, sensibilité=%f, coeff boitier-coupelle=%f",
        	  NbVal, *(float *) ArgList[3],
        	  *(float *) ArgList[4]);
  if (NCar < 0)
    NCar = 0;
  DiagExec += NCar;

  CodRet = rayon_IR (NbVal,
		     (float *) ArgList[0],
		     (float *) ArgList[1],
		     (float *) ArgList[2],
		     *((float *) ArgList[3]),
		     *((float *) ArgList[4]),
		     (float *) ArgList[5]);

  sprintf (DiagExec, ", %lu T invalides", CodRet);

  return OP_OK;
}

void
ID_rayon_IR (oper * optr)
{
  strcpy (optr->Nom, "rayon_IR");
  optr->Version = "$Revision$";
  optr->Date = "$Date$";
  optr->fctptr = OP_rayon_IR;
  optr->NbArg = 6;

  /* Vth */
  optr->Arg_Car[0].direction = DIR_IN;
  optr->Arg_Car[0].categorie = VECTOR;
  optr->Arg_Car[0].typ = ATYC_IF32;
  optr->Arg_Car[0].array_dim = "1";
  optr->Arg_Car[0].type_sample = "any";
  optr->Arg_Car[0].sample = "any";
  optr->Arg_Car[0].unite = "";

  /* Tb */
  optr->Arg_Car[1].direction = DIR_IN;
  optr->Arg_Car[1].categorie = VECTOR;
  optr->Arg_Car[1].typ = ATYC_IF32;
  optr->Arg_Car[1].array_dim = "1";
  optr->Arg_Car[1].type_sample = "any";
  optr->Arg_Car[1].sample = "any";
  optr->Arg_Car[1].unite = "Kelvin";

  /* Tc */
  optr->Arg_Car[2].direction = DIR_IN;
  optr->Arg_Car[2].categorie = VECTOR;
  optr->Arg_Car[2].typ = ATYC_IF32;
  optr->Arg_Car[2].array_dim = "1";
  optr->Arg_Car[2].type_sample = "any";
  optr->Arg_Car[2].sample = "any";
  optr->Arg_Car[2].unite = "Kelvin";

  /* ath */
  optr->Arg_Car[3].direction = DIR_IN;
  optr->Arg_Car[3].categorie = COEFFICIENT;
  optr->Arg_Car[3].typ = ATYC_IF32;
  optr->Arg_Car[3].array_dim = "1";
  optr->Arg_Car[3].unite = "";

  /* K */
  optr->Arg_Car[4].direction = DIR_IN;
  optr->Arg_Car[4].categorie = COEFFICIENT;
  optr->Arg_Car[4].typ = ATYC_IF32;
  optr->Arg_Car[4].array_dim = "1";
  optr->Arg_Car[4].unite = "";

  /* IR */
  optr->Arg_Car[5].direction = DIR_OUT;
  optr->Arg_Car[5].categorie = VECTOR;
  optr->Arg_Car[5].typ = ATYC_IF32;
  optr->Arg_Car[5].array_dim = "1";
  optr->Arg_Car[5].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[5].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[5].sample = "$Arg1.sample";
  optr->Arg_Car[5].ref_time = "$Arg1.ref_time";
  optr->Arg_Car[5].unite = "W/m2";
  optr->Arg_Car[5].famille = " \"rayonnement\" ";
  optr->Arg_Car[5].misval = "$Arg1.misval";
  optr->Arg_Car[5].name = "\"rayonnement IR \" + $Arg1.name";
}
