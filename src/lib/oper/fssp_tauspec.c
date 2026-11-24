/*******************************************************************
* OPERATOR      fssp_tauspec.c FUNCTION ANSI-C
*
* PURPOSE       Estimation du temps de transit d'un particule
*
* DESCRIPTION   Le calcul du temps de transit d'un particule 
*		est fait a partir du spectre mesure et des 
*		temps de reponse de l'electronique
*
* VERSION       1.0
*
*               IN      float   jcl1	   	nb de particules dans la classe 1	
*               IN      float   jcl2	   	nb de particules dans la classe 2	
*                .          .      .            .
*                .          .      .            .
*                .          .      .            .
*               IN  	float	jcl15		nb de particules dans la classe 15 
*               IN      float   vp		vitesse propre (m/s)
*		IN 	float   beam_diam 	diameter du faisceau (m) 
*		IN 	float   resp_time 	temps de reponse des ampli. (s) 
*		IN	float	volt0		seuil de tension de detection (mV)
*		IN 	float   volt_jcl[15] 	seuils de tension des classes (mV)
*
*               OUT     float   tauspec	        temps de transit d'une particule (s)	
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
fssp_tauspec (unsigned long ndata,
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
	      float *vp,
	      float beam_diam,
	      float resp_time,
	      float volt0,
	      float volt_jcl[],
	      float *tauspec)
{
#define NB_CLASSE 15
  unsigned long i;

  int j;

  float pi = 3.141592;
  float jcl_tot;
  float jcl[NB_CLASSE];

  double dtau, dx;
  double coef_dtau[NB_CLASSE];

/*** calcul du temps de transit dans chaque classe ****/

  for (j = 0; j < NB_CLASSE; j++)
    {
      dx = (double)(volt_jcl[j] / volt0);
      coef_dtau[j] = ((double)resp_time) * log (dx - 1.);
    }

/*** calcul du temps de transit ***/

  for (i = 0; i < ndata; i++)
    {
      if (vp[i] < 50.)
	{
	  tauspec[i] = 0.;
	  continue;
	}
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

      dtau = 0.;
      jcl_tot = 0.;
      for (j = 0; j < NB_CLASSE; j++)
	{
	  dtau = dtau + ((double)jcl[j]) * coef_dtau[j];
	  jcl_tot = jcl_tot + jcl[j];
	}

      if (jcl_tot == 0.)
	{
	  tauspec[i] = (pi * beam_diam) / (4. * vp[i]);
	  continue;
	}

      tauspec[i] = ((pi * beam_diam) / (4. * vp[i])) + (dtau / jcl_tot);

    }

  return 0;
}

/* fonction d'enrobage */

int
OP_fssp_tauspec (unsigned long Nbval, void *ArgList[], char *DiagExec)
{
/** la filiere ne prend pas des tableaux de constantes pour
l'instant donc on triche et on le code en dur **/

  int CodRet;

  float volt_jcl[15]; 

/* Pour range 0  (config FSSP CNRM) */

  volt_jcl[0] = 152.; 
  volt_jcl[1] = 343.;
  volt_jcl[2] = 558.;
  volt_jcl[3] = 817.;
  volt_jcl[4] = 1127.;
  volt_jcl[5] = 1497.;
  volt_jcl[6] = 1954.;
  volt_jcl[7] = 2533.;
  volt_jcl[8] = 3275.;
  volt_jcl[9] = 4152.;
  volt_jcl[10] = 5086.;
  volt_jcl[11] = 6068.;
  volt_jcl[12] = 7110.;
  volt_jcl[13] = 8214.;
  volt_jcl[14] = 9391.;
 
  CodRet = fssp_tauspec (Nbval,
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
			     *((float *) ArgList[18]),
			     volt_jcl,
			     (float *) ArgList[19] ) ;


  return OP_OK;
}

void
ID_fssp_tauspec (oper * optr)
{
  int j;

  strcpy (optr->Nom, "fssp_tauspec");
  optr->Version = "1.0";
  optr->Date = "10/24/96";
  optr->fctptr = OP_fssp_tauspec;
  optr->NbArg = 20;

  for (j = 0; j < 15; j++)
    {
      optr->Arg_Car[j].direction = DIR_IN;
      optr->Arg_Car[j].categorie = VECTOR;
      optr->Arg_Car[j].typ = ATYC_IF32;
      optr->Arg_Car[j].array_dim = "1";
      optr->Arg_Car[j].type_sample = "any";
      optr->Arg_Car[j].sample = "any";
      optr->Arg_Car[0].unite = "";
    }
  optr->Arg_Car[15].direction = DIR_IN;
  optr->Arg_Car[15].categorie = VECTOR;
  optr->Arg_Car[15].typ = ATYC_IF32;
  optr->Arg_Car[15].array_dim = "1";
  optr->Arg_Car[15].type_sample = "any";
  optr->Arg_Car[15].sample = "any";
  optr->Arg_Car[15].unite = "meter/second";

  optr->Arg_Car[16].direction = DIR_IN;
  optr->Arg_Car[16].categorie = COEFFICIENT;
  optr->Arg_Car[16].typ = ATYC_IF32;
  optr->Arg_Car[16].array_dim = "1";
  optr->Arg_Car[16].type_sample = NULL;
  optr->Arg_Car[16].sample = NULL;
  optr->Arg_Car[16].unite = "meter";

  optr->Arg_Car[17].direction = DIR_IN;
  optr->Arg_Car[17].categorie = COEFFICIENT;
  optr->Arg_Car[17].typ = ATYC_IF32;
  optr->Arg_Car[17].array_dim = "1";
  optr->Arg_Car[17].type_sample = NULL;
  optr->Arg_Car[17].sample = NULL;
  optr->Arg_Car[17].unite = "second";

  optr->Arg_Car[18].direction = DIR_IN;
  optr->Arg_Car[18].categorie = COEFFICIENT;
  optr->Arg_Car[18].typ = ATYC_IF32;
  optr->Arg_Car[18].array_dim = "1";
  optr->Arg_Car[18].type_sample = NULL;
  optr->Arg_Car[18].sample = NULL;
  optr->Arg_Car[18].unite = "mvolt";

  optr->Arg_Car[19].direction = DIR_OUT;
  optr->Arg_Car[19].categorie = VECTOR;
  optr->Arg_Car[19].typ = ATYC_IF32;
  optr->Arg_Car[19].array_dim = "1";
  optr->Arg_Car[19].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[19].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[19].ref_time = "$Arg1.ref_time";
  optr->Arg_Car[19].sample = "$Arg1.sample";
  optr->Arg_Car[19].unite = "second";
}
