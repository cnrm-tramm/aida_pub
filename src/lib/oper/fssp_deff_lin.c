/*****************************************************************
* OPERATOR 	fssp_deff_lin.c 	FUNCTION ANSI-C
*
* PURPOSE	Calcul du diameter effectif. 
*
* DESCRIPTION   Calcul par :
*		
*		moyenne arithmetique du diameter au cube /
*		moyenne arithmetique du diameter au carre
*		
*		Cette formule n'est valable que si la largeur
*		de classe est constante.		
*
* ARGUMENTS 	IN 	float	jcl1 	comptage dans la classe 1 
* 		IN 	float	jcl2 	comptage dans la classe 2
*                .          .      .    .
*                .          .      .    .
*                .          .      .    .
* 		IN 	float	jcl15 	comptage dans la classe 15
*		IN	float 	aphi  	coefficient	
*		IN	float	bphi 	coefficient
*
*		OUT	float 	deff	diameter moyen (microns)
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
fssp_deff_lin (unsigned long ndata,
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
	      float aphi,
	      float bphi,
	      float *deff)

{
  unsigned long i;
  int j;

  float jcl[15], phim[15];

  float jcltot;
  
  double dm2, dm3;

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

      jcltot = 0.;
      dm2 = 0.;
      dm3 = 0.;

      for (j = 0; j < 15; j++)
	{
	  dm2 = dm2 + (double)(phim[j]*phim[j]* jcl[j]);
	  dm3 = dm3 + (double)(phim[j]*phim[j]*phim[j]*jcl[j]);
          jcltot = jcltot + jcl[j];
	}
      if (jcltot < 1)
        deff[i] = 0.;
      else
        deff[i] = (float)(dm3 / dm2);
    }

  return (0);
}

/* fonction d'enrobage */

int
OP_fssp_deff_lin (unsigned long Nbval, void *ArgList[], char *DiagExec)
{
  int CodRet = fssp_deff_lin (Nbval,
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
			     *((float *) ArgList[16]),
			     (float *) ArgList[17]);


  return OP_OK;
}

void
ID_fssp_deff_lin (oper * optr)
{
  int i;

  strcpy (optr->Nom, "fssp_deff_lin");
  optr->Version = "1.0";
  optr->Date = "02/18/97";
  optr->fctptr = OP_fssp_deff_lin;
  optr->NbArg = 18;

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
  optr->Arg_Car[15].categorie = COEFFICIENT;
  optr->Arg_Car[15].typ = ATYC_IF32;
  optr->Arg_Car[15].array_dim = "1";
  optr->Arg_Car[15].type_sample = NULL;
  optr->Arg_Car[15].sample = NULL;
  optr->Arg_Car[15].unite = "microns";

  optr->Arg_Car[16].direction = DIR_IN;
  optr->Arg_Car[16].categorie = COEFFICIENT;
  optr->Arg_Car[16].typ = ATYC_IF32;
  optr->Arg_Car[16].array_dim = "1";
  optr->Arg_Car[16].type_sample = NULL;
  optr->Arg_Car[16].sample = NULL;
  optr->Arg_Car[16].unite = "microns";

  optr->Arg_Car[17].direction = DIR_OUT;
  optr->Arg_Car[17].categorie = VECTOR;
  optr->Arg_Car[17].typ = ATYC_IF32;
  optr->Arg_Car[17].array_dim = "1";
  optr->Arg_Car[17].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[17].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[17].sample = "$Arg1.sample";
  optr->Arg_Car[17].ref_time = "$Arg1.ref_time";
  optr->Arg_Car[17].unite = "microns";
}
