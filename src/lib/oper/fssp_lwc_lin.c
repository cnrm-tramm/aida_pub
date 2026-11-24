/*****************************************************************
* OPERATOR 	fssp_lwc_lin.c 	FUNCTION ANSI-C
*
* PURPOSE	Calcul du contenu en eau liquide (g/m3)
*		a partir des mesures du FSSP standard 
*		Le diametre moyen dans chaque classe est
*		fixe par les coefs : aphi et bphi suivant
*		la formule suivante : 
*		    diam_moyen(i) = a_phi*i + bphi, i = 1,15 
*		    (en microns)
*
* ARGUMENTS 	IN 	float	jcl1 	comptage dans la classe 1 
* 		IN 	float	jcl2 	comptage dans la classe 2
*                .          .      .    .
*                .          .      .    .
*                .          .      .    .
* 		IN 	float	jcl15 	comptage dans la classe 15
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


int
fssp_lwc_lin (unsigned long ndata,
	      float *jcl1,
	      float *jcl2,
	      float *jcl3,
	      float *jcl4,
	      float *jcl5,
	      float *jcl6,
	      float *jcl7,
	      float *jcl8,
	      float *jcl9,
	      float *jcl10,
	      float *jcl11,
	      float *jcl12,
	      float *jcl13,
	      float *jcl14,
	      float *jcl15,
	      float *tconc,
	      float aphi,
	      float bphi,
	      float *lwc)

{
  int j;
  long i;

  float pi = 3.141592;
  float row = 1000.;		/* densite de l'eau (kg/m3) */
  float jcl[15], phim[15];

  float dvol3, jcltot;

  for (j = 1; j <= 15; j++)
    {
      phim[j - 1] = aphi * ((float) j) + bphi;
    }

  for (i = 0; i < ndata; i++)
    {
      jcl[0] = jcl1[i];
      jcl[1] = jcl2[i];
      jcl[2] = jcl3[i];
      jcl[3] = jcl4[i];
      jcl[4] = jcl5[i];
      jcl[5] = jcl6[i];
      jcl[6] = jcl7[i];
      jcl[7] = jcl8[i];
      jcl[8] = jcl9[i];
      jcl[9] = jcl10[i];
      jcl[10] = jcl11[i];
      jcl[11] = jcl12[i];
      jcl[12] = jcl13[i];
      jcl[13] = jcl14[i];
      jcl[14] = jcl15[i];

      dvol3 = 0.;
      jcltot = 0.;
      for (j = 0; j < 15; j++)
	{
	  dvol3 = dvol3 + phim[j] * phim[j] * phim[j] * jcl[j];
	  jcltot = jcltot + jcl[j];
	}
      if ((tconc[i] == 0.) || (jcltot == 0))
	{
	  lwc[i] = 0.;
	  continue;
	}
      dvol3 = dvol3 / jcltot;
      lwc[i] = row * (pi / 6.) * 1.e-9 * tconc[i] * dvol3;	/* g/m3 */
    }

  return 0;
}

/* fonction d'enrobage */

int
OP_fssp_lwc_lin (unsigned long Nbval, void *ArgList[], char *DiagExec)
{
  int CodRet = fssp_lwc_lin (Nbval,
			     (float *) ArgList[0],
			     (float *) ArgList[1],
			     (float *) ArgList[2],
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
			     *((float *) ArgList[16]),
			     *((float *) ArgList[17]),
			     (float *) ArgList[18]);


  return OP_OK;
}

void
ID_fssp_lwc_lin (oper * optr)
{
  int i;

  strcpy (optr->Nom, "fssp_lwc_lin");
  optr->Version = "$Revision$";
  optr->Date = "$Date$";
  optr->fctptr = OP_fssp_lwc_lin;
  optr->NbArg = 19;

  for (i = 0; i < 15; i++)
    {
      optr->Arg_Car[i].direction = DIR_IN;
      optr->Arg_Car[i].categorie = VECTOR;
      optr->Arg_Car[i].typ = ATYC_IF32;
      optr->Arg_Car[i].array_dim = "1";
      optr->Arg_Car[i].type_sample = "any";
      optr->Arg_Car[i].sample = "any";
      optr->Arg_Car[i].unite = "";
    }
  optr->Arg_Car[15].direction = DIR_IN;
  optr->Arg_Car[15].categorie = VECTOR;
  optr->Arg_Car[15].typ = ATYC_IF32;
  optr->Arg_Car[15].array_dim = "1";
  optr->Arg_Car[15].type_sample = "any";
  optr->Arg_Car[15].sample = "any";
  optr->Arg_Car[15].unite = "cm-3";

  optr->Arg_Car[16].direction = DIR_IN;
  optr->Arg_Car[16].categorie = COEFFICIENT;
  optr->Arg_Car[16].typ = ATYC_IF32;
  optr->Arg_Car[16].array_dim = "1";
  optr->Arg_Car[16].type_sample = NULL;
  optr->Arg_Car[16].sample = NULL;
  optr->Arg_Car[16].unite = "microns";

  optr->Arg_Car[17].direction = DIR_IN;
  optr->Arg_Car[17].categorie = COEFFICIENT;
  optr->Arg_Car[17].typ = ATYC_IF32;
  optr->Arg_Car[17].array_dim = "1";
  optr->Arg_Car[17].type_sample = NULL;
  optr->Arg_Car[17].sample = NULL;
  optr->Arg_Car[17].unite = "microns";

  optr->Arg_Car[18].direction = DIR_OUT;
  optr->Arg_Car[18].categorie = VECTOR;
  optr->Arg_Car[18].typ = ATYC_IF32;
  optr->Arg_Car[18].array_dim = "1";
  optr->Arg_Car[18].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[18].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[18].sample = "$Arg1.sample";
  optr->Arg_Car[18].ref_time = "$Arg1.ref_time";
  optr->Arg_Car[18].unite = "gram/m3";
  optr->Arg_Car[18].famille = "\"eau_liquide\"";
}
