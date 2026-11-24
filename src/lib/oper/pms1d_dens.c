/*************************************************
* OPERATOR 	pms1d_dens.c 	FUNCTION ANSI-C
*
* PURPOSE	calcul de la densite a partir
*		d'une classe de comptage d'une sonde PMS.
*
* ARGUMENTS 	IN 	float	conc 	   concentration dans la classe (cm-3) 
*		IN	float   delta_phi  plage de diameter couvert
*					   par la classe (microns)   	 
*
*		OUT 	float 	dens       densite dans la classe (cm-3.microns-1) 
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

int
pms1d_dens (unsigned long ndata,
	    float *conc,
	    float delta_phi,
	    float *dens)

{
  unsigned long i;

  for (i = 0; i < ndata; i++)
    {
      dens[i] = conc[i] / delta_phi;
    }

  return 0;
}

/* fonction d'enrobage */

int
OP_pms1d_dens (unsigned long Nbval, void *ArgList[], char *DiagExec)
{
  int CodRet = pms1d_dens (Nbval,
			   (float *) ArgList[0],
			   *((float *) ArgList[1]),
			   (float *) ArgList[2]);


  return OP_OK;
}

void
ID_pms1d_dens (oper * optr)
{
  strcpy (optr->Nom, "pms1d_dens");
  optr->Version = "1.0";
  optr->Date = "10/07/96";
  optr->fctptr = OP_pms1d_dens;
  optr->NbArg = 3;

  /*  conc */
  optr->Arg_Car[0].direction = DIR_IN;
  optr->Arg_Car[0].categorie = VECTOR;
  optr->Arg_Car[0].typ = ATYC_IF32;
  optr->Arg_Car[0].array_dim = "1";
  optr->Arg_Car[0].type_sample = "any";
  optr->Arg_Car[0].sample = "any";
  optr->Arg_Car[0].unite = "cm-3";

  /* delta_phi */
  optr->Arg_Car[1].direction = DIR_IN;
  optr->Arg_Car[1].categorie = COEFFICIENT;
  optr->Arg_Car[1].typ = ATYC_IF32;
  optr->Arg_Car[1].array_dim = "1";
  optr->Arg_Car[1].type_sample = NULL;
  optr->Arg_Car[1].sample = NULL;
  optr->Arg_Car[1].unite = "microns";

  /* dens */
  optr->Arg_Car[2].direction = DIR_OUT;
  optr->Arg_Car[2].categorie = VECTOR;
  optr->Arg_Car[2].typ = ATYC_IF32;
  optr->Arg_Car[2].array_dim = "1";
  optr->Arg_Car[2].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[2].ref_time = "$Arg1.ref_time";
  optr->Arg_Car[2].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[2].sample = "$Arg1.sample";
  optr->Arg_Car[2].unite = "microns-1.cm-3";
}
