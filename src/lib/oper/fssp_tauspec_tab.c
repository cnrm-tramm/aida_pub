/*******************************************************************
* OPERATOR      fssp_tauspec_tab.c FUNCTION ANSI-C
*
* PURPOSE       Estimation du temps de transit d'un particule
*
* DESCRIPTION   Le calcul du temps de transit d'un particule 
*		est fait a partir du spectre mesure et des 
*		temps de reponse de l'electronique
*
* VERSION       1.0
*
*               IN      float   cnt[15] 	Tableau des comptes de particules dans les classes
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

#define NB_CLASSE 15

#include <stdio.h>
#include <string.h>
#include <math.h>
#include "struct_oper.h"

int
fssp_tauspec_tab (unsigned long ndata,
		  float *Cnt,
		  float *vp,
		  float beam_diam,
		  float resp_time,
		  float volt0, float volt_jcl[], float *tauspec)
{
  unsigned long i, k;

  int j;

  double CntTot;

  double tau0, dtau, dx;
  double coef_dtau[NB_CLASSE];

  /*** calcul du temps de transit dans chaque classe ****/

  for (j = 0; j < NB_CLASSE; j++)
    {
      dx = (double) (volt_jcl[j] / volt0);
      coef_dtau[j] = ((double) resp_time) * log (dx - 1.);
    }

  /*** calcul du temps de transit ***/

  for (i = 0; i < ndata; i++)
    {
      k = i * NB_CLASSE;
      if (vp[i] < 50.)
	{
	  tauspec[i] = 0.;
	  continue;
	}

      dtau = 0.0;
      CntTot = 0.0;
      tau0 = (M_PI_4 * (double) beam_diam) / ((double) vp[i]);

      for (j = 0; j < NB_CLASSE; j++)
	{
	  dtau = dtau + ((double) Cnt[k]) * coef_dtau[j];
	  CntTot = CntTot + (double) Cnt[k];
	  k = k + 1;
	}
      if (CntTot == 0.)
	{
	  tauspec[i] = (float) tau0;
	}
      else
	{
	  tauspec[i] = (float) (tau0 + (dtau / CntTot));
	}
    }

  return 0;
}

/* fonction d'enrobage */

int
OP_fssp_tauspec_tab (unsigned long Nbval, void *ArgList[], char *DiagExec)
{
  int i, CodRet;

  float volt_jcl[NB_CLASSE];


  /** la filiere ne prend pas des tableaux de constantes pour
   * l'instant donc on le construit à partir de 15 arguments */
  for (i = 0; i < NB_CLASSE; i++)
    {
      volt_jcl[i] = *((float *) ArgList[5 + i]);
    }

/* Historique : valeurs pour FSSP du CAM
   Pour range 0  (config FSSP CNRM) 
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
   volt_jcl[14] = 9391.; */


  CodRet = fssp_tauspec_tab (Nbval,
			     (float *) ArgList[0],
			     (float *) ArgList[1],
			     *((float *) ArgList[2]),
			     *((float *) ArgList[3]),
			     *((float *) ArgList[4]),
			     volt_jcl, (float *) ArgList[20]);

  DiagExec[0] = 0;		/* Rien à dire. */
  return OP_OK;
}

void
ID_fssp_tauspec_tab (oper * optr)
{
  int j;

  strcpy (optr->Nom, "fssp_tauspec_tab");
  optr->Version = "1.0";
  optr->Date = "08/23/2000";
  optr->fctptr = OP_fssp_tauspec_tab;
  optr->NbArg = 21;

  optr->Arg_Car[0].direction = DIR_IN;
  optr->Arg_Car[0].categorie = VECTOR;
  optr->Arg_Car[0].typ = ATYC_IF32;
  optr->Arg_Car[0].array_dim = "15";
  optr->Arg_Car[0].type_sample = "any";
  optr->Arg_Car[0].sample = "any";
  optr->Arg_Car[0].unite = "";

  optr->Arg_Car[1].direction = DIR_IN;
  optr->Arg_Car[1].categorie = VECTOR;
  optr->Arg_Car[1].typ = ATYC_IF32;
  optr->Arg_Car[1].array_dim = "1";
  optr->Arg_Car[1].type_sample = "any";
  optr->Arg_Car[1].sample = "any";
  optr->Arg_Car[1].unite = "meter/second";

  optr->Arg_Car[2].direction = DIR_IN;
  optr->Arg_Car[2].categorie = COEFFICIENT;
  optr->Arg_Car[2].typ = ATYC_IF32;
  optr->Arg_Car[2].array_dim = "1";
  optr->Arg_Car[2].type_sample = NULL;
  optr->Arg_Car[2].sample = NULL;
  optr->Arg_Car[2].unite = "meter";

  optr->Arg_Car[3].direction = DIR_IN;
  optr->Arg_Car[3].categorie = COEFFICIENT;
  optr->Arg_Car[3].typ = ATYC_IF32;
  optr->Arg_Car[3].array_dim = "1";
  optr->Arg_Car[3].type_sample = NULL;
  optr->Arg_Car[3].sample = NULL;
  optr->Arg_Car[3].unite = "second";

  optr->Arg_Car[4].direction = DIR_IN;
  optr->Arg_Car[4].categorie = COEFFICIENT;
  optr->Arg_Car[4].typ = ATYC_IF32;
  optr->Arg_Car[4].array_dim = "1";
  optr->Arg_Car[4].type_sample = NULL;
  optr->Arg_Car[4].sample = NULL;
  optr->Arg_Car[4].unite = "mVolt";

  for (j = 0; j < NB_CLASSE; j++)
    {
      optr->Arg_Car[5 + j].direction = DIR_IN;
      optr->Arg_Car[5 + j].categorie = COEFFICIENT;
      optr->Arg_Car[5 + j].typ = ATYC_IF32;
      optr->Arg_Car[5 + j].array_dim = "1";
      optr->Arg_Car[5 + j].type_sample = NULL;
      optr->Arg_Car[5 + j].sample = NULL;
      optr->Arg_Car[5 + j].unite = "mVolt";
    }
  optr->Arg_Car[20].direction = DIR_OUT;
  optr->Arg_Car[20].categorie = VECTOR;
  optr->Arg_Car[20].typ = ATYC_IF32;
  optr->Arg_Car[20].array_dim = "1";
  optr->Arg_Car[20].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[20].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[20].ref_time = "$Arg1.ref_time";
  optr->Arg_Car[20].sample = "$Arg1.sample";
  optr->Arg_Car[20].unite = "second";
  optr->Arg_Car[20].misval = "$Arg1.misval";
  optr->Arg_Car[20].famille = "\"microphysique\"";
  optr->Arg_Car[20].name = "Temps de transit déduit du spectre";
  optr->Arg_Car[20].en_name = "Transit time computed from spectrum";
}
