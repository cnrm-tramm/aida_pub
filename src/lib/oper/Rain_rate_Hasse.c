/****************************************************
*
* OPERATOR      Rain_rate_Hasse.c   FUNCTION  ANSI-C
*
* PURPOSE      	Calculation of total rain rate under influence of wind speed
*               with a Hasse ship rain gauge
*               
* DESCRIPTION  	Cet opérateur calcule une intensite de precipitation a partir du nombre de gouttes
*               recoltees sur un collecteur superieur et lateral, en fonction de la force du vent mesuree
*               pres du pluviometre.
*
*		Les parametres d'entrée sont les valeurs de 3 compteurs (superieur, lateral et anemo)
*		à la meme fréquence que le vecteur de sortie.
*
* VERSION       $Revision$
*
* ARGUMENTS   	
*             IN   float 	 U    	m/s	Vitesse du vent mesure par l'anemo associe
*	      IN   float 	 Cs             Resultat du comptage superieur
*             IN   float 	 Cl   	  	Resultat du comptage lateral
*             IN   string	 unit_out     	Unite pour le parametre de sortie	
*
*             OUT  float 	 rr     	Intensite de precipitation
*
* REFERENCES
*
*
* COPYRIGHT     Meteo-France
*
*#########################################################################*/

#define _POSIX_SOURCE 1
#define _XOPEN_SOURCE 600

#include <stdio.h>
#include <math.h>
#include <string.h>
#include <limits.h>
#include <stdlib.h>

#include "thermo.h"

#include "struct_oper.h"

/* La vraie fonction... */

long int
/*int*/
Rain_rate_Hasse (unsigned long Ndata,
		 const float *U, const float *Cs, const float *Cl, float *rr)
{
  unsigned long i;
  float krr_sup, rr_sup, lwc_1, klwc, lwc, rr_lat;

  double a1 = 2.9562289E-02;
  double a2 = 9.8437145E-03;
  double a3 = -3.9051531E-03;
  double a4 = -4.8168935E-03;


  for (i = 0; i < Ndata; i++)
    {
      /*Calculation of end rain rate for top collection surface */
      if (Cs[i] == 0.)
	{
	  rr_sup = 0.;
	}
      else
	{
	  krr_sup =
	    (float) exp (a1 + a2 * U[i] + a3 * log ((double) Cs[i]) +
			 a4 * log ((double) Cs[i]) * U[i]);
	  rr_sup = krr_sup * Cs[i];
/*		fprintf (stderr, "krr_sup=%f , rr_sup= %f\n ", krr_sup, rr_sup);*/
	}

      /*Calculation of end rain rate for side collection surface */
      if (Cl[i] == 0.)
	{
	  rr_lat = 0.;
	}
      else
	{
	  if (U[i] > 0.)
	    {
	      lwc_1 = Cl[i] / U[i];
	      klwc = 1 + 0.0015 * U[i] * U[i];
	      lwc = lwc_1 * klwc;
	      rr_lat = 20.9032 * pow (lwc, 1.1264);
/*			fprintf (stderr, "rr_lat= %f\n ", rr_lat);*/
	    }
	  else
	    /* si le vent est nul, on prend de toute facon rr_sup */
	    {
	      rr_lat = 0.;
	    }
	}

      /*Calculation of total rain rate under influence of wind speed U */
      if (U[i] <= 11. && U[i] >= 9.)
	{
/*		fprintf (stderr, "U[%lu]=%f\n ", i, U[i]);*/
	  rr[i] =
	    (1 - (U[i] - 9.) / (11. - 9.)) * rr_sup +
	    ((U[i] - 9.) / (11. - 9.)) * rr_lat;
/*		fprintf (stderr, "119rr[%lu]=%f\n ", i, rr[i]);*/
	}
      else if (U[i] > 11.0)
	{
	  rr[i] = rr_lat;
/*		fprintf (stderr, "U[%lu]=%f\n ", i, U[i]);
		fprintf (stderr, "11rr[%lu]=%f\n ", i, rr[i]);*/
	}
      else			/* U < 9 m/s */
	{
	  rr[i] = rr_sup;
/*		fprintf (stderr, "U[%lu]=%f\n ", i, U[i]);
		fprintf (stderr, "rr9[%lu]=%f\n ", i, rr[i]);*/
	}
    }
/*  return 0;*/
  return i;
}

/* la fonction d'enrobage classique */

int
OP_Rain_rate_Hasse (unsigned long NbVal, void *ArgList[], char *DiagExec)
{
  unsigned long CodRet;
  int NCar;

  NCar = sprintf (DiagExec, "Rain_rate_Hasse : (%ld echant.) ", NbVal) ;
  if (NCar < 0)
    NCar = 0;
  DiagExec += NCar;

  CodRet = Rain_rate_Hasse (NbVal,
			    (float *) ArgList[0],
			    (float *) ArgList[1],
			    (float *) ArgList[2], (float *) ArgList[4]);

  if (CodRet > 0)
    {
      sprintf (DiagExec, "OK: %ld val. calculées.", CodRet);
      return OP_OK;
    }
  switch (CodRet)
    {
    case -1:
      strcat (DiagExec, "; Nb resultats <= 0");
      return OP_FAIL;
    case -2:
      strcat (DiagExec, "; Trop de valeurs manquantes ");
      return OP_FAIL;
    default:
      strcat (DiagExec, "; Erreur inattendue");
      return OP_FAIL;
    }

}


void
ID_Rain_rate_Hasse (oper * optr)
{
  int i;

  strcpy (optr->Nom, "Rain_rate_Hasse");
  optr->Version = "$Revision$";
  optr->Date = "$Date$";
  optr->fctptr = OP_Rain_rate_Hasse;
  optr->NbArg = 5;
  optr->misval_auto = 1;

  optr->Arg_Car[0].direction = DIR_IN;
  optr->Arg_Car[0].categorie = VECTOR;
  optr->Arg_Car[0].typ = ATYC_IF32;
  optr->Arg_Car[0].array_dim = "1";
  optr->Arg_Car[0].type_sample = "any";
  optr->Arg_Car[0].sample = "any";
  optr->Arg_Car[0].unite = "any";
/*optr->Arg_Car[0].unite = "m/s";*/

  for (i = 1; i <= 2; i++)
    {
      optr->Arg_Car[i].direction = DIR_IN;
      optr->Arg_Car[i].categorie = VECTOR;
      optr->Arg_Car[i].typ = ATYC_IF32;
      optr->Arg_Car[i].array_dim = "1";
      optr->Arg_Car[i].type_sample = "any";
      optr->Arg_Car[i].sample = "any";
      optr->Arg_Car[i].unite = "any";
    }

  optr->Arg_Car[3].direction = DIR_IN;
  optr->Arg_Car[3].categorie = COEFFICIENT;
  optr->Arg_Car[3].array_dim = "1";
  optr->Arg_Car[3].typ = ATYC_STRING;
  optr->Arg_Car[3].unite = "any";
  optr->Arg_Car[3].type_sample = NULL;
  optr->Arg_Car[3].sample = NULL;

  optr->Arg_Car[4].direction = DIR_OUT;
  optr->Arg_Car[4].categorie = VECTOR;
  optr->Arg_Car[4].typ = ATYC_IF32;
  optr->Arg_Car[4].array_dim = "1";
  optr->Arg_Car[4].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[4].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[4].sample = "$Arg1.sample";
  optr->Arg_Car[4].ref_time = "$Arg1.ref_time";
  optr->Arg_Car[4].misval = "$Arg1.misval";
  optr->Arg_Car[4].unite = "$Arg4";
  optr->Arg_Car[4].famille = " \"precipitation\" ";
}
