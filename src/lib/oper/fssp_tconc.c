/*******************************************************************
* OPERATOR      fssp_tconc.c FUNCTION ANSI-C
*
* PURPOSE       Calcul de la concentration a partir des
*		donnees d'un FSSP mesurant le "STROBE"  
*
* DESCRIPTION	La concentration est obtenu en divisant le
*		STROBE par le volume d'echantillonnage ( dof*Vp/fr)     
*
* VERSION       1.0
*
*               IN      float   strobe	 	nb total de gouttes acceptees
*               IN      float   vp		vitesse propre
*               IN      float   fr 		frequence d'acquisition
*		IN 	float 	dof_area	section de DOF de la sonde (mm2)
*
*               OUT     float   conc		concentration (cm-3)
*
* ENTRY         NONE
*
* SUBPROGRAMS   NONE
*
* REFERENCES   	Traitement Jean-Louis Brenguier  
*		Bulletin NCAR/RAF n³28 
*		Airborne Measurements for Cloud Microphysics
*		by Darrel Baumgardner. 
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

long
fssp_tconc (unsigned long ndata,
	    float *strobe, float *vp, float fr, float dof_area,
	    float seuil_vp, float *conc)
{
  unsigned long i;
  long nb_valid = 0;

  for (i = 0; i < ndata; i++)
    {
      if (vp[i] > seuil_vp)
	{
	  conc[i] = (strobe[i] * fr) / (dof_area * vp[i]);
	  nb_valid++;
	}
      else
	conc[i] = 0.;		/* K_NaN, plutôt ? */
    }

  return nb_valid;
}

/* fonction d'enrobage */
int
OP_fssp_tconc (unsigned long Nbval, void *ArgList[], char *DiagExec)
{
  const float seuil_vp = 50.;
  long CodRet = fssp_tconc (Nbval,
			    (float *) ArgList[0],
			    (float *) ArgList[1],
			    *((float *) ArgList[2]),
			    *((float *) ArgList[3]),
			    seuil_vp,
			    (float *) ArgList[4]);

  sprintf (DiagExec, "%ld ech., %ld valides (Vp>%gm/s)", Nbval, CodRet,
	   seuil_vp);

  return OP_OK;
}

void
ID_fssp_tconc (oper * optr)
{
  strcpy (optr->Nom, "fssp_tconc");
  optr->Version = "$Revision$";
  optr->Date = "$Date$";
  optr->fctptr = OP_fssp_tconc;
  optr->NbArg = 5;

  /* strobe */
  optr->Arg_Car[0].direction = DIR_IN;
  optr->Arg_Car[0].categorie = VECTOR;
  optr->Arg_Car[0].typ = ATYC_IF32;
  optr->Arg_Car[0].array_dim = "1";
  optr->Arg_Car[0].type_sample = "any";
  optr->Arg_Car[0].sample = "any";
  optr->Arg_Car[0].unite = "count";

  /* vp */
  optr->Arg_Car[1].direction = DIR_IN;
  optr->Arg_Car[1].categorie = VECTOR;
  optr->Arg_Car[1].typ = ATYC_IF32;
  optr->Arg_Car[1].array_dim = "1";
  optr->Arg_Car[1].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[1].type_sample = "any";
  optr->Arg_Car[1].sample = "any";
  optr->Arg_Car[1].unite = "meter/second";

  /* fr */
  optr->Arg_Car[2].direction = DIR_IN;
  optr->Arg_Car[2].categorie = COEFFICIENT;
  optr->Arg_Car[2].typ = ATYC_IF32;
  optr->Arg_Car[2].array_dim = "1";
  optr->Arg_Car[2].type_sample = NULL;
  optr->Arg_Car[2].sample = NULL;
  optr->Arg_Car[2].unite = "";

  /* dof_area */
  optr->Arg_Car[3].direction = DIR_IN;
  optr->Arg_Car[3].categorie = COEFFICIENT;
  optr->Arg_Car[3].typ = ATYC_IF32;
  optr->Arg_Car[3].array_dim = "1";
  optr->Arg_Car[3].type_sample = NULL;
  optr->Arg_Car[3].sample = NULL;
  optr->Arg_Car[3].unite = "";

  /* conc */
  optr->Arg_Car[4].direction = DIR_OUT;
  optr->Arg_Car[4].categorie = VECTOR;
  optr->Arg_Car[4].typ = ATYC_IF32;
  optr->Arg_Car[4].array_dim = "1";
  optr->Arg_Car[4].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[4].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[4].sample = "$Arg1.sample";
  optr->Arg_Car[4].ref_time = "$Arg1.ref_time";
  optr->Arg_Car[4].unite = "count / cm3";
  optr->Arg_Car[4].famille = " \"microphysique\" ";
  optr->Arg_Car[4].name = "\"Concentration totale en goutelettes\" ";
  optr->Arg_Car[4].en_name = " \"Droplet totlal concentration\" ";
}
