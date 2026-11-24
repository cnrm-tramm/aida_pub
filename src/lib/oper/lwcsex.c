/****************************************************
*
* OPERATOR       lwcsex.c   FUNCTION  ANSI-C
*
* PURPOSE        Computation of liquid water content 
*
* DESCRIPTION    Calcul du rapport de melange en eau liquide
*		 a partir des mesures du barreau Sextant.  
*
* VERSION        1.0
*
* ARGUMENTS  IN   float  pbsex	  Volt    	Mesure puissnce barreau
*            IN   float  rbsex    Volt 		Mesure tempe barreau 
*            IN   float  tt   	  Kelvin ou C  	Tempe d'impact
*	     IN   float  ts 	  Kelvin ou C  	Tempe de l'air
*            IN   float  ps       hPa     	Pression statique
*            IN   float  vp	  m/s		Vitesse propre
*            IN   double C_lwc[]           	Coeffs pour calcul lwc 
*            IN   double C_psec[]           	Coeffs pour calcul puissance air sec
*            IN   double C_pw[]           	Coeffs pour calcul puissance bareau  
*            IN   double C_tw[]           	Coeffs pour calcul tempe barreau 
*            OUT  float  lwc 	  g/m3		Rapport de melange en eau liquide	
*
* ENTRY            
*                 
* FILES   
*
* REFERENCES   
*
* CHANGES
*
* COPYRIGHT        Meteo-France
*
* AGREEMENT        The author wishes that .....
*#########################################################################*/

#define _POSIX_SOURCE 1
#define _XOPEN_SOURCE 600
/* Le #define _HPUX_SOURCE n'est la que pour "voir" strdup */
#define _HPUX_SOURCE 1


#include <stdio.h>
#include <string.h>
#include <math.h>
#include "struct_oper.h"

#ifndef K_T0
#define K_T0 (273.15)
#endif

int
lwcsex (unsigned long nbval,
	const float *pbsex,
	const float *rbsex,
	const float *tt,
	const float *ts,
	const float *ps,
	const float *vp,
	const double C_lwc[],
	const double C_psec[],
	const double C_pw[],
	const double C_tw[],
	float *lwc)
{
  unsigned long i;

  double x, tw, pw, psec;
  double CtoK_ts, CtoK_tt;

  double d_lwc, d_pbsex, d_rbsex, d_ts, d_tt, d_ps, d_vp;

/** preparation conversion Celsius -> Kelvin **/

  if (ts[nbval / 2] < 100.)
    CtoK_ts = (double) K_T0;
  else
    CtoK_ts = 0.;

  if (tt[nbval / 2] < 100.)
    CtoK_tt = (double) K_T0;
  else
    CtoK_tt = 0.;

  fprintf (stderr, "Coefficients de conversion Celsius -> Kelvin \n");
  fprintf (stderr, "CtoK_ts : %g, CtoK_tt : %g \n", CtoK_ts, CtoK_tt);

  for (i = 0; i < nbval; i++)
    {

      if (vp[i] < 50.)
	{
	  lwc[i] = 0.;
	  continue;
	}


/** conversion en double pour le calcul **/

      d_pbsex = (double) (pbsex[i]);
      d_rbsex = (double) (rbsex[i]);
      d_tt = (double) (tt[i]) + CtoK_tt;
      d_ts = (double) (ts[i]) + CtoK_ts;
      d_ps = (double) (ps[i]) * 100.;
      d_vp = (double) (vp[i]);

/** calcul tempe du barreau **/

      tw = (1. / C_tw[0]) * ((d_rbsex / C_tw[1]) - 1.);
      tw = tw + K_T0;

/** calcul de la puissance totale fournit au barreau **/

      pw = C_pw[0] * d_pbsex * C_pw[1] / d_rbsex;

/** calcul de la puissance en air sec **/

      x = (d_ps * d_vp * (d_ts + 120.)) /
	(pow (d_ts, 2.5));

      psec = C_psec[0] * (tw - d_tt) * (pow (x, C_psec[1]));

/** calcul rapport de melange en eau liquide **/


      d_lwc = ((pw - psec) * 1000.) /
	(C_lwc[0] * d_vp * (C_lwc[1] + C_lwc[2] * (tw - d_ts)));

      lwc[i] = (float) d_lwc;

    }
  return 0;
}


/* la fonction d'enrobage classique */

int
OP_lwcsex (unsigned long NbVal, void *ArgList[], char *DiagExec)
{
  int CodRet;
  double C_lwc[3];
  double C_psec[2];
  double C_pw[2];
  double C_tw[2];


  /* Petite "tricherie" :  */
  /*   comme on ne sait pas encore recevoir des tableaux de     */
  /* constantes depuis le pgm principal, on ne recoit rien ...  */
  /* ... et on passe a la fonctions des valeurs codees "en dur" */
  C_lwc[0] = 3.408e-4;
  C_lwc[1] = 2360.e3;
  C_lwc[2] = 4188.;

  C_psec[0] = 0.018564101;
  C_psec[1] = 0.421;

  C_pw[0] = 11.016;
  C_pw[1] = 7.937;

  C_tw[0] = 5.788e-3;
  C_tw[1] = 5.425;

  CodRet = lwcsex (NbVal,
		   (float *) ArgList[0],
		   (float *) ArgList[1],
		   (float *) ArgList[2],
		   (float *) ArgList[3],
		   (float *) ArgList[4],
		   (float *) ArgList[5],
		   C_lwc,
		   C_psec,
		   C_pw,
		   C_tw,
		   (float *) ArgList[6]);
  return OP_OK;
}

void
ID_lwcsex (oper * optr)
{
  strcpy (optr->Nom, "lwcsex");
  optr->Version = "1.0";
  optr->Date = "04/25/97";
  optr->fctptr = OP_lwcsex;
  optr->NbArg = 7;

  optr->Arg_Car[0].direction = DIR_IN;
  optr->Arg_Car[0].categorie = VECTOR;
  optr->Arg_Car[0].typ = ATYC_IF32;
  optr->Arg_Car[0].array_dim = "1";
  optr->Arg_Car[0].type_sample = "any";
  optr->Arg_Car[0].sample = "any";
  optr->Arg_Car[0].unite = "volt";

  optr->Arg_Car[1].direction = DIR_IN;
  optr->Arg_Car[1].categorie = VECTOR;
  optr->Arg_Car[1].typ = ATYC_IF32;
  optr->Arg_Car[1].array_dim = "1";
  optr->Arg_Car[1].type_sample = "any";
  optr->Arg_Car[1].sample = "any";
  optr->Arg_Car[1].unite = "volt";

  optr->Arg_Car[2].direction = DIR_IN;
  optr->Arg_Car[2].categorie = VECTOR;
  optr->Arg_Car[2].typ = ATYC_IF32;
  optr->Arg_Car[2].array_dim = "1";
  optr->Arg_Car[2].type_sample = "any";
  optr->Arg_Car[2].sample = "any";
  optr->Arg_Car[2].unite = "any";

  optr->Arg_Car[3].direction = DIR_IN;
  optr->Arg_Car[3].categorie = VECTOR;
  optr->Arg_Car[3].typ = ATYC_IF32;
  optr->Arg_Car[3].array_dim = "1";
  optr->Arg_Car[3].type_sample = "any";
  optr->Arg_Car[3].sample = "any";
  optr->Arg_Car[3].unite = "any";

  optr->Arg_Car[4].direction = DIR_IN;
  optr->Arg_Car[4].categorie = VECTOR;
  optr->Arg_Car[4].typ = ATYC_IF32;
  optr->Arg_Car[4].array_dim = "1";
  optr->Arg_Car[4].type_sample = "any";
  optr->Arg_Car[4].sample = "any";
  optr->Arg_Car[4].unite = "hPa";

  optr->Arg_Car[5].direction = DIR_IN;
  optr->Arg_Car[5].categorie = VECTOR;
  optr->Arg_Car[5].typ = ATYC_IF32;
  optr->Arg_Car[5].array_dim = "1";
  optr->Arg_Car[5].type_sample = "any";
  optr->Arg_Car[5].sample = "any";
  optr->Arg_Car[5].unite = "m/s";

  optr->Arg_Car[6].direction = DIR_OUT;
  optr->Arg_Car[6].categorie = VECTOR;
  optr->Arg_Car[6].typ = ATYC_IF32;
  optr->Arg_Car[6].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[6].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[6].sample = "$Arg1.sample";
  optr->Arg_Car[6].ref_time = "$Arg1.ref_time";
  optr->Arg_Car[6].unite = "gram/m3";
  /*** SB correction famille ***/
  optr->Arg_Car[6].famille = "\"eau_liquide\"";

}
