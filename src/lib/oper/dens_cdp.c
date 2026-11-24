/*************************************************
* OPERATOR 	dens_cdp.c 	FUNCTION ANSI-C
*
* PURPOSE	calcul de la densite a partir
*		d'une classe de comptage d'une sonde PMS.
*
* ARGUMENTS 	IN 	float	jcl classe 
*		IN	float 	vp vitesse propre
*		IN 	float   fr frequence d'echantillonnage
*		IN 	float	sa aire d'echantillonnage (mm2)
*		IN	float	delta_phi difference de diameter (mm)
*
*		OUT 	float 	dens densite de la classe 
*		
* ENTRY		NONE
*
* SUBPROGRAMS 	NONE
*
* REFERENCE	NONE
*
* COPYRIGHT	Meteo-France
*		Centre National de Recherches Meteorologiques
*		GMEI/ MMA
*		42, av G. Coriolis 
*		31057	TOULOUSE cedex
*
*****************************************************************/

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
dens_cdp (unsigned long ndata,
	  float *jcl,
	  float *vp,
	  float fr,
	  float sample_area,
	  float delta_phi,
	  float *dens)

{
  unsigned long i;

  for (i = 0; i < ndata; i++)
    {
      dens[i] = jcl[i] / (sample_area * (vp[i] / fr) * delta_phi);
    }

  return;
}

/* fonction d'enrobage */

int
OP_dens_cdp (unsigned long Nbval, void *ArgList[], char *DiagExec)
{
  sprintf (DiagExec, "OP_dens_cdp (%lu, ...); ", Nbval);

  dens_cdp (Nbval,
	    (float *) ArgList[0],
	    (float *) ArgList[1],
	    *((float *) ArgList[2]),
	    *((float *) ArgList[3]),
	    *((float *) ArgList[4]),
	    (float *) ArgList[5]);


  return OP_OK;
}

void
ID_dens_cdp (oper * optr)
{
  strcpy (optr->Nom, "dens_cdp");
  optr->Version = "1.0";
  optr->Date = "03/18/96";
  optr->fctptr = OP_dens_cdp;
  optr->NbArg = 6;

  /* jcl */
  optr->Arg_Car[0].direction = DIR_IN;
  optr->Arg_Car[0].categorie = VECTOR;
  optr->Arg_Car[0].typ = ATYC_IF32;
  optr->Arg_Car[0].array_dim = "1";
  optr->Arg_Car[0].type_sample = "any";
  optr->Arg_Car[0].sample = "any";
  optr->Arg_Car[0].unite = "";

  /* vp */
  optr->Arg_Car[1].direction = DIR_IN;
  optr->Arg_Car[1].categorie = VECTOR;
  optr->Arg_Car[1].typ = ATYC_IF32;
  optr->Arg_Car[1].array_dim = "1";
  optr->Arg_Car[1].type_sample = "any";
  optr->Arg_Car[1].sample = "any";
  optr->Arg_Car[1].unite = "m/s";

  optr->Arg_Car[2].direction = DIR_IN;
  optr->Arg_Car[2].categorie = COEFFICIENT;
  optr->Arg_Car[2].typ = ATYC_IF32;
  optr->Arg_Car[2].array_dim = "1";
  optr->Arg_Car[2].type_sample = NULL;
  optr->Arg_Car[2].sample = NULL;
  optr->Arg_Car[2].unite = "Hz";
  optr->Arg_Car[3].direction = DIR_IN;

  optr->Arg_Car[3].direction = DIR_IN;
  optr->Arg_Car[3].categorie = COEFFICIENT;
  optr->Arg_Car[3].typ = ATYC_IF32;
  optr->Arg_Car[3].array_dim = "1";
  optr->Arg_Car[3].type_sample = NULL;
  optr->Arg_Car[3].sample = NULL;
  optr->Arg_Car[3].unite = "mm2";

  optr->Arg_Car[4].direction = DIR_IN;
  optr->Arg_Car[4].categorie = COEFFICIENT;
  optr->Arg_Car[4].typ = ATYC_IF32;
  optr->Arg_Car[4].array_dim = "1";
  optr->Arg_Car[4].type_sample = NULL;
  optr->Arg_Car[4].sample = NULL;
  optr->Arg_Car[4].unite = "micron";

  optr->Arg_Car[5].direction = DIR_OUT;
  optr->Arg_Car[5].categorie = VECTOR;
  optr->Arg_Car[5].typ = ATYC_IF32;
  optr->Arg_Car[5].array_dim = "1";
  optr->Arg_Car[5].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[5].sample = "$Arg1.sample";
  optr->Arg_Car[5].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[5].unite = "microns-1.cm-3";
}
