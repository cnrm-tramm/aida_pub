/*******************************************************************
* OPERATOR      fssp_tconc_cor.c FUNCTION ANSI-C
*
* PURPOSE       Calcul de la concentration totale de gouttelettes,
*		corrigee. 
*
* DESCRIPTION   La concentration corrigee est calculee a partir
*		du nombre de particule total corrige qui est
*		donne en entree.  
*
* VERSION       1.0
*
*		IN 	float 	strobe		nombre de particules dans la DOF
*		IN	float 	reset		nombre de particules total dans et hors de la DOF  
*               IN      float   ntot_cor        nombre de particules total corrige (reset corrige) 
*               IN      float   vp        	vitesse propre (m/s) 
*		IN 	float   fr 		frequency (Hz) 
*		IN 	float   dof_area	surface correspondant a la DOF (mm2) 
*
*               OUT     float   conc_cor        concentration corrigee (cm-3)	
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

int
fssp_tconc_cor (unsigned long ndata,
		float *strobe,
		float *reset,
		float *ntot_cor,
		float *vp,
		float fr,
		float dof_area,
		float *conc_cor)
{
  unsigned long i;

  float SV, DOF;


  for (i = 0; i < ndata; i++)
    {
      if ((reset[i] == 0.) || (vp[i] < 50.))
	{
	  conc_cor[i] = 0.;
	  continue;
	}
      DOF = strobe[i] / reset[i];

      SV = (dof_area * vp[i]);
      conc_cor[i] = (ntot_cor[i] * fr * DOF) / SV;
    }

  return 0;
}

/* fonction d'enrobage */

int
OP_fssp_tconc_cor (unsigned long Nbval, void *ArgList[], char *DiagExec)
{
  int CodRet = fssp_tconc_cor (Nbval,
			       (float *) ArgList[0],
			       (float *) ArgList[1],
			       (float *) ArgList[2],
			       (float *) ArgList[3],
			       *((float *) ArgList[4]),
			       *((float *) ArgList[5]),
			       (float *) ArgList[6]);

  return OP_OK;
}

void
ID_fssp_tconc_cor (oper * optr)
{
  strcpy (optr->Nom, "fssp_tconc_cor");
  optr->Version = "$Revision$";
  optr->Date = "$Date$";
  optr->fctptr = OP_fssp_tconc_cor;
  optr->NbArg = 7;

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

  /* ntot_cor */
  optr->Arg_Car[2].direction = DIR_IN;
  optr->Arg_Car[2].categorie = VECTOR;
  optr->Arg_Car[2].typ = ATYC_IF32;
  optr->Arg_Car[2].array_dim = "1";
  optr->Arg_Car[2].type_sample = "any";
  optr->Arg_Car[2].sample = "any";
  optr->Arg_Car[2].unite = "";

  optr->Arg_Car[3].direction = DIR_IN;
  optr->Arg_Car[3].categorie = VECTOR;
  optr->Arg_Car[3].typ = ATYC_IF32;
  optr->Arg_Car[3].array_dim = "1";
  optr->Arg_Car[3].type_sample = NULL;
  optr->Arg_Car[3].sample = NULL;
  optr->Arg_Car[3].unite = "meter/second";

  optr->Arg_Car[4].direction = DIR_IN;
  optr->Arg_Car[4].categorie = COEFFICIENT;
  optr->Arg_Car[4].typ = ATYC_IF32;
  optr->Arg_Car[4].array_dim = "1";
  optr->Arg_Car[4].type_sample = NULL;
  optr->Arg_Car[4].sample = NULL;
  optr->Arg_Car[4].unite = "Hz";

  optr->Arg_Car[5].direction = DIR_IN;
  optr->Arg_Car[5].categorie = COEFFICIENT;
  optr->Arg_Car[5].typ = ATYC_IF32;
  optr->Arg_Car[5].array_dim = "1";
  optr->Arg_Car[5].type_sample = NULL;
  optr->Arg_Car[5].sample = NULL;
  optr->Arg_Car[5].unite = "mm2";

  optr->Arg_Car[6].direction = DIR_OUT;
  optr->Arg_Car[6].categorie = VECTOR;
  optr->Arg_Car[6].typ = ATYC_IF32;
  optr->Arg_Car[6].array_dim = "1";
  optr->Arg_Car[6].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[6].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[6].sample = "$Arg1.sample";
  optr->Arg_Car[6].ref_time = "$Arg1.ref_time";
  optr->Arg_Car[6].unite = "cm-3";
}
