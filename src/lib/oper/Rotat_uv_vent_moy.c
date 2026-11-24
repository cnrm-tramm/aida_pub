/*****************************************************
*
* OPERATOR         Rotat_uv_vent_moy.c   FUNCTION  ANSI-C
*
* PURPOSE          Rotation des composantes U et V dans le repère du U moyen 
*
* DESCRIPTION     
*
* VERSION          1.0
*
* ARGUMENTS  IN   float   U        m/s      1ere composante du vent 
*            IN   float   V        m/s      2eme composante du vent 
*            IN   float   Fe	   Hz	    Frequence d'échantillonnage
*            IN   float   Tint 	   s	    Temps d'intégration pour le calcul de la moyenne 
*
* ARGUMENTS  OUT  float   U_rot       m/s      Composante du vent dans l'axe de U moyen  
*            OUT  float   V_rot       m/s      Composante du vent dans l'axe transverse à U moyen 
*
* ENTRY            NONE
*               
* SUBPROGRAMS      NONE
*
* FILES            NONE
*
* REFERENCES       
*
*
* CHANGES          1.1  Initial version
*
* COPYRIGHT        Meteo-France/CNRM
*
* AGREEMENT        
*########################################################################*/

#define _POSIX_SOURCE 1
#define _XOPEN_SOURCE 600

#include <math.h>
#include <stdio.h>
#include <string.h>
#include "struct_oper.h"

int
Rotat_uv_vent_moy (unsigned long Ndata,
	  const float *U,
	  const float *V, 
	  const float Fe,
	  const float Tint,
	  float *U_rot, 
	  float *V_rot)
{
  unsigned long i, j, k, ntour, nbpt;
  register double cos_a, sin_a;
  register double Um, Vm, FFm;

  /* Calcul du nombre de points sur lequels on va calculer */

  /*nb de points sur la periode demandee */
  nbpt = floor ((Tint * Fe) + 0.5);
  /*fprintf (stderr, " nbpt= %ld \n", nbpt); */

  if (nbpt <= 0)
    return -1;

  /*******Calcul du nombre de tours***/
  ntour = Ndata / nbpt;
  /*reste = Ndata % nbpt;*/

  for (k = 0; k < ntour; k++)
    {
     Um = 0.;
     Vm = 0.;
     for( j =0; j < nbpt; j++ )
        {
	 i = j + k*nbpt;
	 Um = Um + U[i];
	 Vm = Vm + V[i];
	}
      Um = Um/(float)nbpt;
      Vm = Vm/(float)nbpt;

      FFm = sqrt( Um*Um + Vm*Vm);

      cos_a = Um/FFm;
      sin_a = Vm/FFm;
      for( j =0; j < nbpt; j++ )
        {
	 i = j + k*nbpt;
	 U_rot[i] =     cos_a*U[i] + sin_a*V[i];
	 V_rot[i] = -1.*sin_a*U[i] + cos_a*V[i];
	}

    }


  return 0;
}


/* la fonction d'enrobage classique */

int
OP_Rotat_uv_vent_moy (unsigned long NbVal, void *ArgList[], char *DiagExec)
{
  int CodRet;

  (void) sprintf (DiagExec, "Rotat_uv_vent_moy, NbVal=%lu, Angle=%g, flag=%g)",
		  NbVal, *(float *) ArgList[2], *(float *) ArgList[3]);

  CodRet = Rotat_uv_vent_moy (NbVal,
		     (float *) ArgList[0],
		     (float *) ArgList[1],
		     *(float *) ArgList[2],
		     *(float *) ArgList[3],
		     (float *) ArgList[4], 
		     (float *) ArgList[5]);
  if (CodRet == -1)
    {
      strcat (DiagExec, "Nombre de points (Fe*Tint) est negatif ou nul");
      return OP_FAIL;
    }
  return OP_OK;
}

void
ID_Rotat_uv_vent_moy (oper * optr)
{
  strcpy (optr->Nom, "Rotat_uv_vent_moy");
  optr->Version = "$Revision: 6274 $";
  optr->Date = "$Date: 2016-02-24 11:36:23 +0100 (mer. 24 févr. 2016) $";
  optr->fctptr = OP_Rotat_uv_vent_moy;
  optr->NbArg = 6;

  /* U */
  optr->Arg_Car[0].direction = DIR_IN;
  optr->Arg_Car[0].categorie = VECTOR;
  optr->Arg_Car[0].typ = ATYC_IF32;
  optr->Arg_Car[0].array_dim = "1";
  optr->Arg_Car[0].type_sample = "any";
  optr->Arg_Car[0].sample = "any";
  optr->Arg_Car[0].unite = "any";
  optr->Arg_Car[0].famille = "any";

  /* V */
  optr->Arg_Car[1].direction = DIR_IN;
  optr->Arg_Car[1].categorie = VECTOR;
  optr->Arg_Car[1].typ = ATYC_IF32;
  optr->Arg_Car[1].array_dim = "1";
  optr->Arg_Car[1].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[1].type_sample = "any";
  optr->Arg_Car[1].sample = "any";
  optr->Arg_Car[1].unite = "$Arg1.unit";
  optr->Arg_Car[1].famille = "any";

  /* Fe */
  optr->Arg_Car[2].direction = DIR_IN;
  optr->Arg_Car[2].categorie = COEFFICIENT;
  optr->Arg_Car[2].typ = ATYC_IF32;
  optr->Arg_Car[2].array_dim = "1";
  optr->Arg_Car[2].type_sample = NULL;
  optr->Arg_Car[2].sample = NULL;
  optr->Arg_Car[2].unite = "";

  /* Tint */
  optr->Arg_Car[3].direction = DIR_IN;
  optr->Arg_Car[3].categorie = COEFFICIENT;
  optr->Arg_Car[3].typ = ATYC_IF32;
  optr->Arg_Car[3].array_dim = "1";
  optr->Arg_Car[3].type_sample = NULL;
  optr->Arg_Car[3].sample = NULL;
  optr->Arg_Car[3].unite = "";

  /* U_rot */
  optr->Arg_Car[4].direction = DIR_OUT;
  optr->Arg_Car[4].categorie = VECTOR;
  optr->Arg_Car[4].typ = ATYC_IF32;
  optr->Arg_Car[4].array_dim = "1";
  optr->Arg_Car[4].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[4].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[4].sample = "$Arg1.sample";
  optr->Arg_Car[4].ref_time = "$Arg1.ref_time";
  optr->Arg_Car[4].unite = "$Arg1.unit";
  optr->Arg_Car[4].famille = "$Arg1.famille";
  optr->Arg_Car[4].misval = "$Arg1.misval";

  /* V_rot */
  optr->Arg_Car[5].direction = DIR_OUT;
  optr->Arg_Car[5].categorie = VECTOR;
  optr->Arg_Car[5].typ = ATYC_IF32;
  optr->Arg_Car[5].array_dim = "1";
  optr->Arg_Car[5].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[5].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[5].sample = "$Arg1.sample";
  optr->Arg_Car[5].ref_time = "$Arg1.ref_time";
  optr->Arg_Car[5].unite = "$Arg1.unit";
  optr->Arg_Car[5].famille = "$Arg1.famille";
  optr->Arg_Car[5].misval = "$Arg1.misval";
}
