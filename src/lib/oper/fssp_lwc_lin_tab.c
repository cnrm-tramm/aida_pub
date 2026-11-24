/*****************************************************************
* OPERATOR 	fssp_lwc_lin_tab.c 	FUNCTION ANSI-C
*
* PURPOSE	calcul du contenu en eau liquide (g/m3)
*		a partir des mesures du FSSP standard 
*		Le diametre moyen dans chaque classe est
*		fixe par les coefs : aphi et bphi suivant
*		la formule suivante : 
*		    diam_moyen(i) = a_phi*i + bphi, i = 1,15 
*		    (en microns)
*
* ARGUMENTS 	IN 	float	jcl1 	tableau de comptage dans les 15 classes
*		IN 	float 	tconc   concentration totale
*		IN	float 	aphi  	coefficient	
*		IN	float	bphi 	coefficient
*
*		OUT	float 	lwc	rapport de melange en eau liquide (g/m3)
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

#include <stdio.h>
#include <string.h>
#include <math.h>
#include "struct_oper.h"


void
fssp_lwc_lin_tab (unsigned long ndata,
		  float *jcl,
		  float *tconc, float aphi, float bphi, float *lwc)
{
  int j;
  unsigned long i;

  float const pi = 3.14159265359;
  const float rhow = 1000.;	/* densite de l'eau (kg/m3) */
  float cnt_cl, phim[15];

  float dvol3, jcltot;

  for (j = 1; j <= 15; j++)
    {
      phim[j - 1] = aphi * ((float) j) + bphi;
    }

  for (i = 0; i < ndata; i++)
    {
      dvol3 = 0.;
      jcltot = 0.;
      for (j = 0; j < 15; j++)
	{
	  cnt_cl = jcl[15 * i + j];
	  dvol3 = dvol3 + phim[j] * phim[j] * phim[j] * cnt_cl;
	  jcltot = jcltot + cnt_cl;
	}
      if ((tconc[i] == 0.) || (jcltot == 0))
	{
	  lwc[i] = 0.;
	  continue;
	}
      dvol3 = dvol3 / jcltot;
      lwc[i] = rhow * (pi / 6.) * 1.e-9 * tconc[i] * dvol3;	/* g/m3 */
    }

  return;
}

/* fonction d'enrobage */

int
OP_fssp_lwc_lin_tab (unsigned long Nbval, void *ArgList[], char *DiagExec)
{

  sprintf (DiagExec,
	   "OP_fssp_lwc_lin_tab, NbVal=%lu, Args=(..., ..., %f, %f, ...);",
	   Nbval, *((float *) ArgList[2]), *((float *) ArgList[3]));

  fssp_lwc_lin_tab (Nbval,
		     (float *) ArgList[0],
		     (float *) ArgList[1],
		     *((float *) ArgList[2]),
		     *((float *) ArgList[3]), (float *) ArgList[4]);

  return OP_OK;
}

void
ID_fssp_lwc_lin_tab (oper * optr)
{
  int idx = 0;

  strcpy (optr->Nom, "fssp_lwc_lin_tab");
  optr->Version = "$Revision$";
  optr->Date = "$Date$";
  optr->fctptr = OP_fssp_lwc_lin_tab;
  optr->NbArg = 5;

  /* jcl */
  optr->Arg_Car[idx].direction = DIR_IN;
  optr->Arg_Car[idx].categorie = VECTOR;
  optr->Arg_Car[idx].typ = ATYC_IF32;
  optr->Arg_Car[idx].array_dim = "15";
  optr->Arg_Car[idx].type_sample = "any";
  optr->Arg_Car[idx].sample = "any";
  optr->Arg_Car[idx].unite = "";

  /* tconc */
  idx ++;
  optr->Arg_Car[idx].direction = DIR_IN;
  optr->Arg_Car[idx].categorie = VECTOR;
  optr->Arg_Car[idx].typ = ATYC_IF32;
  optr->Arg_Car[idx].array_dim = "1";
  optr->Arg_Car[idx].type_sample = "any";
  optr->Arg_Car[idx].sample = "any";
  optr->Arg_Car[idx].unite = "cm-3";

  /* aphi */
  idx ++;
  optr->Arg_Car[idx].direction = DIR_IN;
  optr->Arg_Car[idx].categorie = COEFFICIENT;
  optr->Arg_Car[idx].typ = ATYC_IF32;
  optr->Arg_Car[idx].array_dim = "1";
  optr->Arg_Car[idx].type_sample = NULL;
  optr->Arg_Car[idx].sample = NULL;
  optr->Arg_Car[idx].unite = "microns";

  /* bphi */
  idx ++;
  optr->Arg_Car[idx].direction = DIR_IN;
  optr->Arg_Car[idx].categorie = COEFFICIENT;
  optr->Arg_Car[idx].typ = ATYC_IF32;
  optr->Arg_Car[idx].array_dim = "1";
  optr->Arg_Car[idx].type_sample = NULL;
  optr->Arg_Car[idx].sample = NULL;
  optr->Arg_Car[idx].unite = "microns";

  /* lwc */
  idx ++;
  optr->Arg_Car[idx].direction = DIR_OUT;
  optr->Arg_Car[idx].categorie = VECTOR;
  optr->Arg_Car[idx].typ = ATYC_IF32;
  optr->Arg_Car[idx].array_dim = "1";
  optr->Arg_Car[idx].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[idx].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[idx].sample = "$Arg1.sample";
  optr->Arg_Car[idx].ref_time = "$Arg1.ref_time";
  optr->Arg_Car[idx].unite = "gram/m3";
  optr->Arg_Car[idx].famille = "\"eau_liquide\"";
  optr->Arg_Car[idx].misval = "$Arg2.misval";
  optr->Arg_Car[idx].name =
    "\"Rapport de mélange en eau liquide issu de \"+ $Arg1.name";
  optr->Arg_Car[idx].en_name = 
    "\"liquid water content from \"+ $Arg1.english_name";
}
