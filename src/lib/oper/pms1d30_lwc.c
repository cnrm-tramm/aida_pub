/*****************************************************************
* OPERATOR 	pms1d30_lwc.c 	FUNCTION ANSI-C
*
* PURPOSE	Calcul du contenu en eau liquide (g/m3)
*		a partir des mesures d'une sonde PMS1D 30 classes
*
* ARGUMENTS 	IN 	float	conc1 	concentration dans la classe 1 
* 		IN 	float	conc2 	concentration dans la classe 2
*                .          .      .    .
*                .          .      .    .
*                .          .      .    .
* 		IN 	float	conc30 	concentration dans la classe 15
*		IN	float 	dia[] 	diameter moyen de chaque classe (microns)
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
pms1d30_lwc (unsigned long ndata,
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
	     float *conc16,
	     float *conc17,
	     float *conc18,
	     float *conc19,
	     float *conc20,
	     float *conc21,
	     float *conc22,
	     float *conc23,
	     float *conc24,
	     float *conc25,
	     float *conc26,
	     float *conc27,
	     float *conc28,
	     float *conc29, float *conc30, float dia[], float *lwc)
{
#define NB_CLASSE 30

  int j;
  unsigned long i;

  const float pi = 3.141592;
  float row = 1000.;		/* densite de l'eau (kg/m3) */
  float d3[NB_CLASSE];

  for (j = 0; j < NB_CLASSE; j++)
    {
      d3[j] = dia[j] * dia[j] * dia[j];
    }

  for (i = 0; i < ndata; i++)
    {
      lwc[i] = conc1[i] * d3[0] +
	conc2[i] * d3[1] +
	conc3[i] * d3[2] +
	conc4[i] * d3[3] +
	conc5[i] * d3[4] +
	conc6[i] * d3[5] +
	conc7[i] * d3[6] +
	conc8[i] * d3[7] +
	conc9[i] * d3[8] +
	conc10[i] * d3[9] +
	conc11[i] * d3[10] +
	conc12[i] * d3[11] +
	conc13[i] * d3[12] +
	conc14[i] * d3[13] +
	conc15[i] * d3[14] +
	conc16[i] * d3[15] +
	conc17[i] * d3[16] +
	conc18[i] * d3[17] +
	conc19[i] * d3[18] +
	conc20[i] * d3[19] +
	conc21[i] * d3[20] +
	conc22[i] * d3[21] +
	conc23[i] * d3[22] +
	conc24[i] * d3[23] +
	conc25[i] * d3[24] +
	conc26[i] * d3[25] +
	conc27[i] * d3[26] +
	conc28[i] * d3[27] + conc29[i] * d3[28] + conc30[i] * d3[29];

      lwc[i] = row * (pi / 6.) * 1.e-9 * lwc[i];	/* g/m3 */
    }

  return;
}

/* fonction d'enrobage */

int
OP_pms1d30_lwc (unsigned long Nbval, void *ArgList[], char *DiagExec)
{
  sprintf (DiagExec, "pms1d30_lwc (%lu ech)", Nbval);

  pms1d30_lwc (Nbval,
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
	       (float *) ArgList[16],
	       (float *) ArgList[17],
	       (float *) ArgList[18],
	       (float *) ArgList[19],
	       (float *) ArgList[20],
	       (float *) ArgList[21],
	       (float *) ArgList[22],
	       (float *) ArgList[23],
	       (float *) ArgList[24],
	       (float *) ArgList[25],
	       (float *) ArgList[26],
	       (float *) ArgList[27],
	       (float *) ArgList[28],
	       (float *) ArgList[29],
	       (float *) ArgList[30], (float *) ArgList[31]);

  return OP_OK;
}

void
ID_pms1d30_lwc (oper * optr)
{
  int i;

  strcpy (optr->Nom, "pms1d30_lwc");
  optr->Version = "1.0";
  optr->Date = "10/22/96";
  optr->fctptr = OP_pms1d30_lwc;
  optr->NbArg = 32;

  for (i = 0; i < 30; i++)
    {
      optr->Arg_Car[i].direction = DIR_IN;
      optr->Arg_Car[i].categorie = VECTOR;
      optr->Arg_Car[i].typ = ATYC_IF32;
      optr->Arg_Car[i].array_dim = "1";
      optr->Arg_Car[i].type_sample = "any";
      optr->Arg_Car[i].sample = "any";
      optr->Arg_Car[i].unite = "cm-3";
    }
  for (i = 1; i < 30; i++)
    {
      optr->Arg_Car[i].NbVal = "$Arg1.NbVal";
    }

  optr->Arg_Car[30].direction = DIR_IN;
  optr->Arg_Car[30].categorie = COEFFICIENT;
  optr->Arg_Car[30].typ = ATYC_IF32;
  optr->Arg_Car[30].array_dim = "15";
  optr->Arg_Car[30].type_sample = NULL;
  optr->Arg_Car[30].sample = NULL;
  optr->Arg_Car[30].unite = "microns";

  optr->Arg_Car[31].direction = DIR_OUT;
  optr->Arg_Car[31].categorie = VECTOR;
  optr->Arg_Car[31].typ = ATYC_IF32;
  optr->Arg_Car[31].array_dim = "1";
  optr->Arg_Car[31].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[31].sample = "$Arg1.sample";
  optr->Arg_Car[31].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[31].unite = "gram/m3";
}
