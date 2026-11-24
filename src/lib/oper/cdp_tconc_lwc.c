/*************************************************
* OPERATOR 	cdp_tconc_lwc.c 	FUNCTION ANSI-C
*
* PURPOSE	calcul de la concentration totale et du contenu
*		en eau liquide a partir des 15 valeurs de 
*		concentratio  d'un CDP15 
*
* ARGUMENTS 	IN 	float	conc1 	concentration classe 1 (cm-3)
* 		IN 	float	conc2 	concentration classe 2
*  		IN 	float	conc3 	concentration classe 3
*  		IN 	float	conc4 	concentration classe 4
*  		IN 	float	conc5 	concentration classe 5
*  		IN 	float	conc6 	concentration classe 6
*  		IN 	float	conc7 	concentration classe 7
*  		IN 	float	conc8 	concentration classe 8
*  		IN 	float	conc9 	concentration classe 9
*  		IN 	float	conc10 	concentration classe 10
*  		IN 	float	conc11 	concentration classe 11
*  		IN 	float	conc12 	concentration classe 12
*  		IN 	float	conc13 	concentration classe 13
*  		IN 	float	conc14 	concentration classe 14
*  		IN 	float	conc15 	concentration classe 15
*		IN 	float 	res	resolution de l'appareil
*
*		OUT	float 	tcon 	concentration totale (cm-3)
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
cdp_tconc_lwc (unsigned long ndata,
	       float *conc1,
	       float *conc2,
	       float *conc3,
	       float *conc4,
	       float *conc5,
	       float *conc6,
	       float *conc7,
	       float *conc8,
	       float *conc9,
	       float *conc10,
	       float *conc11,
	       float *conc12,
	       float *conc13,
	       float *conc14,
	       float *conc15,
	       float res,
	       float *tconc,
	       float *lwc)

{

#define NB_CLASSE 15

  int j;

  long i;

  float pi = 3.141592;
  float dens = 1.0;		/* densite de l'eau */
  float conc[NB_CLASSE], dia[NB_CLASSE];

/*** calcul du diameter representatif de chaque classe ***/

  for (j = 0; j < NB_CLASSE; j++)
    {
      dia[j] = res * ((float) (j + 1));		/* microns */
    }

  for (i = 0; i < ndata; i++)
    {
      conc[0] = conc1[i];
      conc[1] = conc2[i];
      conc[2] = conc3[i];
      conc[3] = conc4[i];
      conc[4] = conc5[i];
      conc[5] = conc6[i];
      conc[6] = conc7[i];
      conc[7] = conc8[i];
      conc[8] = conc9[i];
      conc[9] = conc10[i];
      conc[10] = conc11[i];
      conc[11] = conc12[i];
      conc[12] = conc13[i];
      conc[13] = conc14[i];
      conc[14] = conc15[i];

      tconc[i] = 0.0;
      for (j = 0; j < NB_CLASSE; j++)
	{
	  tconc[i] = tconc[i] + conc[j];
	  lwc[i] = lwc[i] + dia[j] * dia[j] * dia[j] * conc[j];
	}

      lwc[i] = dens * (pi / 6.) * lwc[i] * 1.e-6;	/* g/m3 */
    }

  return 0;
}

/* fonction d'enrobage */

int
OP_cdp_tconc_lwc (unsigned long Nbval, void *ArgList[], char *DiagExec)
{
  int CodRet = cdp_tconc_lwc (Nbval,
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
			      *((float *) ArgList[15]),
			      (float *) ArgList[16],
			      (float *) ArgList[17]);


  return OP_OK;
}

void
ID_cdp_tconc_lwc (oper * optr)
{
  strcpy (optr->Nom, "cdp_tconc_lwc");
  optr->Version = "1.0";
  optr->Date = "03/20/96";
  optr->fctptr = OP_cdp_tconc_lwc;
  optr->NbArg = 18;
  optr->Arg_Car[0].direction = DIR_IN;
  optr->Arg_Car[0].categorie = VECTOR;
  optr->Arg_Car[0].typ = ATYC_IF32;
  optr->Arg_Car[0].array_dim = "1";
  optr->Arg_Car[0].type_sample = "any";
  optr->Arg_Car[0].sample = "any";
  optr->Arg_Car[0].unite = "";
  optr->Arg_Car[1].direction = DIR_IN;
  optr->Arg_Car[1].categorie = VECTOR;
  optr->Arg_Car[1].typ = ATYC_IF32;
  optr->Arg_Car[1].array_dim = "1";
  optr->Arg_Car[1].type_sample = "any";
  optr->Arg_Car[1].sample = "any";
  optr->Arg_Car[1].unite = "";
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
  optr->Arg_Car[3].type_sample = "any";
  optr->Arg_Car[3].sample = "any";
  optr->Arg_Car[3].unite = "";
  optr->Arg_Car[4].direction = DIR_IN;
  optr->Arg_Car[4].categorie = VECTOR;
  optr->Arg_Car[4].typ = ATYC_IF32;
  optr->Arg_Car[4].array_dim = "1";
  optr->Arg_Car[4].type_sample = "any";
  optr->Arg_Car[4].sample = "any";
  optr->Arg_Car[4].unite = "";
  optr->Arg_Car[5].direction = DIR_IN;
  optr->Arg_Car[5].categorie = VECTOR;
  optr->Arg_Car[5].typ = ATYC_IF32;
  optr->Arg_Car[5].array_dim = "1";
  optr->Arg_Car[5].type_sample = "any";
  optr->Arg_Car[5].sample = "any";
  optr->Arg_Car[5].unite = "";
  optr->Arg_Car[6].direction = DIR_IN;
  optr->Arg_Car[6].categorie = VECTOR;
  optr->Arg_Car[6].typ = ATYC_IF32;
  optr->Arg_Car[6].array_dim = "1";
  optr->Arg_Car[6].type_sample = "any";
  optr->Arg_Car[6].sample = "any";
  optr->Arg_Car[6].unite = "";
  optr->Arg_Car[7].direction = DIR_IN;
  optr->Arg_Car[7].categorie = VECTOR;
  optr->Arg_Car[7].typ = ATYC_IF32;
  optr->Arg_Car[7].array_dim = "1";
  optr->Arg_Car[7].type_sample = "any";
  optr->Arg_Car[7].sample = "any";
  optr->Arg_Car[7].unite = "";
  optr->Arg_Car[8].direction = DIR_IN;
  optr->Arg_Car[8].categorie = VECTOR;
  optr->Arg_Car[8].typ = ATYC_IF32;
  optr->Arg_Car[8].array_dim = "1";
  optr->Arg_Car[8].type_sample = "any";
  optr->Arg_Car[8].sample = "any";
  optr->Arg_Car[8].unite = "";
  optr->Arg_Car[9].direction = DIR_IN;
  optr->Arg_Car[9].categorie = VECTOR;
  optr->Arg_Car[9].typ = ATYC_IF32;
  optr->Arg_Car[9].array_dim = "1";
  optr->Arg_Car[9].type_sample = "any";
  optr->Arg_Car[9].sample = "any";
  optr->Arg_Car[9].unite = "";
  optr->Arg_Car[10].direction = DIR_IN;
  optr->Arg_Car[10].categorie = VECTOR;
  optr->Arg_Car[10].typ = ATYC_IF32;
  optr->Arg_Car[10].array_dim = "1";
  optr->Arg_Car[10].type_sample = "any";
  optr->Arg_Car[10].sample = "any";
  optr->Arg_Car[10].unite = "";
  optr->Arg_Car[11].direction = DIR_IN;
  optr->Arg_Car[11].categorie = VECTOR;
  optr->Arg_Car[11].typ = ATYC_IF32;
  optr->Arg_Car[11].array_dim = "1";
  optr->Arg_Car[11].type_sample = "any";
  optr->Arg_Car[11].sample = "any";
  optr->Arg_Car[11].unite = "";
  optr->Arg_Car[12].direction = DIR_IN;
  optr->Arg_Car[12].categorie = VECTOR;
  optr->Arg_Car[12].typ = ATYC_IF32;
  optr->Arg_Car[12].array_dim = "1";
  optr->Arg_Car[12].type_sample = "any";
  optr->Arg_Car[12].sample = "any";
  optr->Arg_Car[11].unite = "";
  optr->Arg_Car[13].direction = DIR_IN;
  optr->Arg_Car[13].categorie = VECTOR;
  optr->Arg_Car[13].typ = ATYC_IF32;
  optr->Arg_Car[13].array_dim = "1";
  optr->Arg_Car[13].type_sample = "any";
  optr->Arg_Car[13].sample = "any";
  optr->Arg_Car[14].unite = "";
  optr->Arg_Car[14].direction = DIR_IN;
  optr->Arg_Car[14].categorie = VECTOR;
  optr->Arg_Car[14].typ = ATYC_IF32;
  optr->Arg_Car[14].array_dim = "1";
  optr->Arg_Car[14].type_sample = "any";
  optr->Arg_Car[14].sample = "any";
  optr->Arg_Car[14].unite = "";
  optr->Arg_Car[15].direction = DIR_IN;
  optr->Arg_Car[15].categorie = COEFFICIENT;
  optr->Arg_Car[15].typ = ATYC_IF32;
  optr->Arg_Car[15].array_dim = "1";
  optr->Arg_Car[15].type_sample = "any";
  optr->Arg_Car[15].sample = "any";
  optr->Arg_Car[15].unite = "";
  optr->Arg_Car[16].direction = DIR_OUT;
  optr->Arg_Car[16].categorie = VECTOR;
  optr->Arg_Car[16].typ = ATYC_IF32;
  optr->Arg_Car[16].array_dim = "1";
  optr->Arg_Car[16].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[16].sample = "$Arg1.sample";
  optr->Arg_Car[16].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[16].unite = "cm-3";

  optr->Arg_Car[17].direction = DIR_OUT;
  optr->Arg_Car[17].categorie = VECTOR;
  optr->Arg_Car[17].typ = ATYC_IF32;
  optr->Arg_Car[17].array_dim = "1";
  optr->Arg_Car[17].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[17].sample = "$Arg1.sample";
  optr->Arg_Car[17].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[17].unite = "gram/m3";

}
