/*******************************************************************
* OPERATOR      fssp_ncor_specrs.c FUNCTION ANSI-C
*
* PURPOSE       Calcul du nombre total de gouttelettes
*		corrige des coincidences.
*
* DESCRIPTION   La methode de correction utilise le temps
*		de transit "tauspec" estime a partir du
*		spectre de gouttes mesure et le taux de comptage.
*               dans le cas ou aucune des voies sup n'est disponibles.
*
* VERSION       1.0
*
* ARGUMENTS     IN      float   strobe		nb de particules dans la DOF
*               IN      float   reset  		nb de particules total
*                                               (dans et hors de la DOF)
*               IN      float   tauspec		temps de transit estime a
*						partir du spectre de gouttes(s)
*		IN 	float   fr 		frequency (Hz)
*		IN 	float   tau1		delai court de l'electronique(s)
*		IN 	float   tau2		delai long de l'electronique (s)
*		IN 	float   taur		reset (s)
*		IN	float 	crt0		seuil de taux de comptage pour
*						la correction de coincidence
*
*		OUT	float 	ntot_rs		nombre de particules total
*						corrige via le taux de comptage
*
* ENTRY         NONE
*
* SUBPROGRAMS   NONE
*
* REFERENCES
*		Coincidence and Dead-Time Corrections for Particle Counters.
*		Part I : A general Mathematical Formalism.
*			 J-L Brenguier and L. Amodei
*               Part II : High concentration Measurements with an FSSP.
*			  J-L Brenguier
*		Journal of Atmos. and Ocean. Tech., Vol 6, No 4, August 1989
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

#include <stdio.h>
#include <string.h>
#include <math.h>
#include "struct_oper.h"
#include "fssp_eqn.h"

unsigned long
fssp_ncor_specrs (unsigned long ndata,
		  const float *strobe,
		  const float *reset,
		  const float *tauspec,
		  float fr,
		  float tau1,
		  float tau2,
		  float taur,
		  float crt0,
		  float *ntot_rs)
{
  unsigned long i;
  unsigned long nb_stop_iter = 0;

  int iacrt;

  float expm = 0.367879;
  float tau, DOF;
  float dcrt, crt, crt1, crt2, crtx;
  float Al1, Al2;
  float acrt, dacrt, iter_acrt, acrtx;
  float Tbar1, Tbar2;
  float XX;

  FILE *fp;

  fp = fopen ("/tmp/aida_log/trt_fssp_specrs", "w");

  for (i = 0; i < ndata; i++)
    {
      /*** calcul de la DOF ***/
      if (reset[i] * fr < crt0)
        {
          ntot_rs[i] = 0.;
          continue;
        }
      DOF = strobe[i] / reset[i];

/************************************************/
/*** correction utilisant le taux de comptage ***/
/*** 2 solutions sont possibles : la solution choisie est
     celle qui est la plus faible ***/

      tau = tauspec[i];

/*** calcul du taux de comptage maximum ***/

      acrtx = 1. / tau;
      XX = expm * acrtx;
      crt2 = XX;
      if (tau2 > tau)
	crt2 = XX / (1. + XX * (tau2 - tau));
      crt1 = XX;
      if (tau1 > tau)
	crt1 = XX / (1. + XX * (tau1 - tau));

      crtx = 1. / (((1. - DOF) / crt1) + (DOF / crt2));

      if ((reset[i] * fr) > crtx)
	{
	  /* pas de solution */
	  fprintf (fp, "data: %ld  \n", i );
	  fprintf (fp, "**** No solution for the counted rate approach \n");
	  fprintf (fp, "Counted rate measured is too high\n");
	  ntot_rs[i] = acrtx / fr;
	  continue;
	}

      /*** iteration du tau de comptage reel (acrt) jusqu'a que ce que le
      taux de comptage mesure (reset[i]) et calcule (crt)
      soient suffisament proches ***/

      iacrt = 0;
      dacrt = 0.2 * acrtx;
      iter_acrt = 1.;
      acrt = reset[i] * fr;	/* taux de comptage mesure >= taux reel */
      dcrt = 1.01;		/* N'importe quelle valeur > 0.01       */
      while (fabs (dcrt) > 0.01)
	{
	  acrt = acrt + iter_acrt * dacrt;
          /*** on prend le min des 2 solutions ***/
	  if ((acrtx - acrt) < 0.)
	    acrt = acrtx;
	  if (acrt <= 1.)
	    acrt = 1.;
	  iacrt = iacrt + 1;

          /*** calcul du taux de comptage ***/
	  equ2 (acrt, tau, tau1, tau2, taur, &Tbar2, &crt2, &Al2);
	  equ1 (acrt, tau, tau1, taur, &Tbar1, &crt1, &Al1);

	  crt = 1. / (((1. - DOF) / crt1) + (DOF / crt2));

	  dcrt = 1. - ((reset[i] * fr) / crt);
          /*** stop iteration si ca ne converge pas assez vite ***/
	  if (fabs (dacrt) < 0.001 * acrt)
	    {
	      fprintf (fp, "***Stop after %d iterations\n", iacrt);
              nb_stop_iter++;
	      /* fprintf (fp, "Relative error on counted rate : %g\n", dacrt); */
	      break;
	    }

          /*** fixe le signe et la valeur de l'increment suivant ***/
	  if (dcrt * iter_acrt > 0.)
	    {
	      dacrt = 0.5 * dacrt;
	      iter_acrt = -1. * iter_acrt;
	    }
	}
      ntot_rs[i] = acrt / fr;
    }

  fclose (fp);

  return nb_stop_iter;
}

/* fonction d'enrobage */

int
OP_fssp_ncor_specrs (unsigned long Nbval, void *ArgList[], char *DiagExec)
{
  unsigned long CodRet;
  CodRet = fssp_ncor_specrs (Nbval,
			     (float *) ArgList[0],
			     (float *) ArgList[1],
			     (float *) ArgList[2],
			     *((float *) ArgList[3]),
			     *((float *) ArgList[4]),
			     *((float *) ArgList[5]),
			     *((float *) ArgList[6]),
			     *((float *) ArgList[7]),
			     (float *) ArgList[8]);
  if (CodRet != 0)
    {
      sprintf (DiagExec, "%lu (/%lu) iterations stoppees", CodRet, Nbval);
    }
  return OP_OK;
}

void
ID_fssp_ncor_specrs (oper * optr)
{
  strcpy (optr->Nom, "fssp_ncor_specrs");
  optr->Version = "1.0";
  optr->Date = "16/10/98";
  optr->fctptr = OP_fssp_ncor_specrs;
  optr->NbArg = 9;

  /* strobe */
  optr->Arg_Car[0].direction = DIR_IN;
  optr->Arg_Car[0].categorie = VECTOR;
  optr->Arg_Car[0].typ = ATYC_IF32;
  optr->Arg_Car[0].array_dim = "1";
  optr->Arg_Car[0].type_sample = "any";
  optr->Arg_Car[0].sample = "any";
  optr->Arg_Car[0].unite = "count";

  /* reset */
  optr->Arg_Car[1].direction = DIR_IN;
  optr->Arg_Car[1].categorie = VECTOR;
  optr->Arg_Car[1].typ = ATYC_IF32;
  optr->Arg_Car[1].array_dim = "1";
  optr->Arg_Car[1].type_sample = "any";
  optr->Arg_Car[1].sample = "any";
  optr->Arg_Car[1].unite = "count";

  /* tauspec */
  optr->Arg_Car[2].direction = DIR_IN;
  optr->Arg_Car[2].categorie = VECTOR;
  optr->Arg_Car[2].typ = ATYC_IF32;
  optr->Arg_Car[2].array_dim = "1";
  optr->Arg_Car[2].type_sample = "any";
  optr->Arg_Car[2].sample = "any";
  optr->Arg_Car[2].unite = "second";

  optr->Arg_Car[3].direction = DIR_IN;
  optr->Arg_Car[3].categorie = COEFFICIENT;
  optr->Arg_Car[3].typ = ATYC_IF32;
  optr->Arg_Car[3].array_dim = "1";
  optr->Arg_Car[3].type_sample = "any";
  optr->Arg_Car[3].sample = "any";
  optr->Arg_Car[3].unite = "Hz";

  optr->Arg_Car[4].direction = DIR_IN;
  optr->Arg_Car[4].categorie = COEFFICIENT;
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
  optr->Arg_Car[5].unite = "second";

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
  optr->Arg_Car[7].unite = "count second-1";

  optr->Arg_Car[8].direction = DIR_OUT;
  optr->Arg_Car[8].categorie = VECTOR;
  optr->Arg_Car[8].typ = ATYC_IF32;
  optr->Arg_Car[8].array_dim = "1";
  optr->Arg_Car[8].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[8].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[8].sample = "$Arg1.sample";
  optr->Arg_Car[8].ref_time = "$Arg1.ref_time";
  optr->Arg_Car[8].unite = "count";
  optr->Arg_Car[8].famille = " \"microphysique\" ";
}
