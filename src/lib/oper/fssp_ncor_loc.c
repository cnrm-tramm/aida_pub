/*******************************************************************
* OPERATOR      fssp_ncor_loc.c FUNCTION ANSI-C
*
* PURPOSE       Calcul du nombre total de gouttelettes 
*		corrige des coincidences. 
*
* DESCRIPTION   La methode de correction utilise le temps
*		de transit "tauspec" estime a partir du
*		spectre de gouttes mesure, et le  
*		rapport  taux de comptage, sur l'activite.  
*
* VERSION       1.0
*
*		IN 	float 	strobe		nombre de particules dans la DOF
*		IN	float 	reset		nombre de particules total dans et hors de la DOF  
*		IN	float 	activity	activite (s)
*		IN 	float 	tbar		temps de transit moyen d'un particule (s)
*               IN      float   tauspec		temps de transit estime a 
*						partir du spectre de gouttes(s)
*		IN 	float   fr 		frequency (Hz) 
*		IN 	float   tau1		delai court de l'electronique (s) 
*		IN 	float   tau2		delai long de l'electronique (s) 
*		IN 	float   taur		reset (s) 
*		IN	float 	crt0		seuil de taux de comptage pour la correction
*						de coincidence
*
*               OUT     float   ntot_loc  	nombre de particules total corrige 
*		OUT	float 	homc		homogeneite calculee	
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
#include "fssp_eqn.h"

int
fssp_ncor_loc (unsigned long ndata,
	       float *strobe,
	       float *reset,
	       float *activity,
	       float *tbar,
	       float *tauspec,
	       float fr,
	       float tau1,
	       float tau2,
	       float taur,
	       float crt0,
	       float *ntot_loc,
	       float *homc)
{
  unsigned long i;

  int it, flg_err;

  float tau, DOF;
  float crt, crt1, crt2;
  float dtbar, Ac, Al1, Al2;
  float tbarn, tbarc;
  float acrt, dacrt, iter_acrt;
  float Tbar1, Tbar2;

  FILE *fp;

  fp = fopen ("$AIDA_HOME/log/trt_fssp_loc", "w");

  for (i = 0; i < ndata; i++)
    {

/*** calcul de la DOF ***/

      if ((reset[i] * fr < crt0) ||
	  (tbar[i] < 0.8 * tauspec[i]))
	{
	  ntot_loc[i] = 0.;
	  homc[i] = 0.;
	  continue;
	}
      DOF = ((double) strobe[i]) / ((double) reset[i]);


/*** initialisation avant l'iteration  ***/
      tau = (double) tauspec[i];
      it = 0;
      acrt = (double) (reset[i] * fr);
      dacrt = 0.2 * acrt;
      iter_acrt = 1.;
      dtbar = 1.;
      tbarn = 2. * tau;

      flg_err = 0;


     /**********************************************
     iteration sur le taux de comptage 
     tant que le temps de transit moyen calcule
     est different de celui mesure ***/

      while (fabs (dtbar) > 0.01)
	{
	  acrt = acrt + iter_acrt * dacrt;
	  if (acrt < 1.)
	    acrt = 1.;
	  it = it + 1;

/*** calcul de l'activite, tau de comptage et temps de transit moyen ***/

	  equ2 (acrt, tau, tau1, tau2, taur, &Tbar2, &crt2, &Al2);
	  equ1 (acrt, tau, tau1, taur, &Tbar1, &crt1, &Al1);

	  crt = 1. / (((1. - DOF) / crt1) + (DOF / crt2));
	  Ac = crt * ((1. - DOF) * (Tbar1 + tau1 - Al1)
		      + DOF * (Tbar2 + tau2 - Al2));

	  tbarc = (1. - DOF) * Tbar1 + DOF * Tbar2;

/*
   fprintf (stderr, "acrt = %g, crt = %g, Ac = %g, Tbarc = %g\n",
   acrt, crt, Ac, tbarc);
 */
	  if (tbarn > tbarc)
	    tbarn = tbarc;

	  dtbar = 1. - (tbar[i] / tbarc);

	  if ((acrt == 1) &&
	      (tbar[i] < tbarn))
	    {
	      fprintf (fp, "Mean transit time %g smaller than minimun %g\n",
		       tbar[i], tbarn);
	      flg_err = 1;
	      break;
	    }
/*** stop iteration si ca ne converge pas assez vite ***/

	  if (fabs (dacrt) < 0.001 * acrt)
	    {
	      fprintf (fp, "***Stop after %d iterations\n", it);
	      fprintf (fp, "Relative error on counted rate : %g\n", dtbar);
	      break;
	    }

	  if (dtbar * iter_acrt >= 0.)
	    {
	      dacrt = dacrt * 0.5;
	      iter_acrt = -1. * iter_acrt;
	    }
	}
      if (flg_err == 1)
	{
	  ntot_loc[i] = 0.;
	  homc[i] = 0.;
	}
      else
	{
	  ntot_loc[i] = (acrt) / fr;
	  homc[i] = activity[i] / (Ac);
/*        
   if ( homc[i] > 2.)
   {
   fprintf(stderr,"******* homc = %g \n", homc[i]);
   fprintf(stderr," strobe = %g , reset = %g, DOF = %g, acti = %g \n", 
   strobe[i], reset[i], DOF, activity[i]); 
   fprintf(stderr," tauspec = %g , Tbar = %g, tbarc = %g \n", 
   tauspec[i], tbar[i], tbarc); 
   fprintf(stderr,"Tbar1 + tau1 - Al1  = %g , Tbar2 + tau2 - Al2 = %g \n", 
   Tbar1 + tau1 - Al1, Tbar2 + tau2 - Al2 ); 
   fprintf(stderr,"crt1  = %g , crt2 = %g \n", 
   crt1, crt2 ); 
   fprintf(stderr," Ac = %g , crt = %g acrt = %g\n", 
   Ac, crt, acrt); 
   }
 */
	}
    }

  fclose (fp);

  return (0);
}

/* fonction d'enrobage */

int
OP_fssp_ncor_loc (unsigned long Nbval, void *ArgList[], char *DiagExec)
{
  int CodRet = fssp_ncor_loc (Nbval,
			      (float *) ArgList[0],
			      (float *) ArgList[1],
			      (float *) ArgList[2],
			      (float *) ArgList[3],
			      (float *) ArgList[4],
			      *((float *) ArgList[5]),
			      *((float *) ArgList[6]),
			      *((float *) ArgList[7]),
			      *((float *) ArgList[8]),
			      *((float *) ArgList[9]),
			      (float *) ArgList[10],
			      (float *) ArgList[11]);
  return OP_OK;
}

void
ID_fssp_ncor_loc (oper * optr)
{
  strcpy (optr->Nom, "fssp_ncor_loc");
  optr->Version = "1.0";
  optr->Date = "05/28/97";
  optr->fctptr = OP_fssp_ncor_loc;
  optr->NbArg = 12;

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
  optr->Arg_Car[3].type_sample = NULL;
  optr->Arg_Car[3].sample = NULL;
  optr->Arg_Car[3].unite = "second";

  optr->Arg_Car[4].direction = DIR_IN;
  optr->Arg_Car[4].categorie = VECTOR;
  optr->Arg_Car[4].typ = ATYC_IF32;
  optr->Arg_Car[4].array_dim = "1";
  optr->Arg_Car[4].type_sample = NULL;
  optr->Arg_Car[4].sample = NULL;
  optr->Arg_Car[4].unite = "second";

  optr->Arg_Car[5].direction = DIR_IN;
  optr->Arg_Car[5].categorie = COEFFICIENT;
  optr->Arg_Car[5].typ = ATYC_IF32;
  optr->Arg_Car[5].array_dim = "1";
  optr->Arg_Car[5].type_sample = NULL;
  optr->Arg_Car[5].sample = NULL;
  optr->Arg_Car[5].unite = "Hz";

  optr->Arg_Car[6].direction = DIR_IN;
  optr->Arg_Car[6].categorie = COEFFICIENT;
  optr->Arg_Car[6].typ = ATYC_IF32;
  optr->Arg_Car[6].array_dim = "1";
  optr->Arg_Car[6].type_sample = NULL;
  optr->Arg_Car[6].sample = NULL;
  optr->Arg_Car[6].unite = "second";

  optr->Arg_Car[7].direction = DIR_IN;
  optr->Arg_Car[7].categorie = COEFFICIENT;
  optr->Arg_Car[7].typ = ATYC_IF32;
  optr->Arg_Car[7].array_dim = "1";
  optr->Arg_Car[7].type_sample = NULL;
  optr->Arg_Car[7].sample = NULL;
  optr->Arg_Car[7].unite = "second";

  optr->Arg_Car[8].direction = DIR_IN;
  optr->Arg_Car[8].categorie = COEFFICIENT;
  optr->Arg_Car[8].typ = ATYC_IF32;
  optr->Arg_Car[8].array_dim = "1";
  optr->Arg_Car[8].type_sample = NULL;
  optr->Arg_Car[8].sample = NULL;
  optr->Arg_Car[8].unite = "second";

  optr->Arg_Car[9].direction = DIR_IN;
  optr->Arg_Car[9].categorie = COEFFICIENT;
  optr->Arg_Car[9].typ = ATYC_IF32;
  optr->Arg_Car[9].array_dim = "1";
  optr->Arg_Car[9].type_sample = NULL;
  optr->Arg_Car[9].sample = NULL;
  optr->Arg_Car[9].unite = "second-1";

  optr->Arg_Car[10].direction = DIR_OUT;
  optr->Arg_Car[10].categorie = VECTOR;
  optr->Arg_Car[10].typ = ATYC_IF32;
  optr->Arg_Car[10].array_dim = "1";
  optr->Arg_Car[10].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[10].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[10].sample = "$Arg1.sample";
  optr->Arg_Car[10].ref_time = "$Arg1.ref_time";
  optr->Arg_Car[10].unite = "";

  optr->Arg_Car[11].direction = DIR_OUT;
  optr->Arg_Car[11].categorie = VECTOR;
  optr->Arg_Car[11].typ = ATYC_IF32;
  optr->Arg_Car[11].array_dim = "1";
  optr->Arg_Car[11].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[11].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[11].sample = "$Arg1.sample";
  optr->Arg_Car[11].ref_time = "$Arg1.ref_time";
  optr->Arg_Car[11].unite = "";
}
