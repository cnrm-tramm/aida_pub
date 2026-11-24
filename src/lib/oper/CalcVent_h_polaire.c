/*****************************************************
*
* OPERATOR         CalcVent_h_polaire.c   FUNCTION  ANSI-C
*
* PURPOSE          Convert ship-wind to meteo-wind.
*
* DESCRIPTION      Computes true horizontal wind from relative wind
*                  and ground speed measured in polar coordinates
*                  (DD/FF and track_angle/speed).
*                  Angles counting from North.
*                  This operator is equivalent to CalcVent_h_simple_auto_unit, but
*                  applies to polar input (mobile speed expressed as route and speed).
*
* VERSION          $Revision$
*
* ARGUMENTS  IN   float    DDA  degree       Wind ship Direction FROM where the vector
*                                            starts (0=front of ship)
*            IN   float    FFA  m/s          Module of the vector Wind Speed on the ship
*            IN   float    DDR  degree       Route : direction where the ship is going (gravity center displacement)
*            IN   float    VVR  m/s          Speed of the ship on the Route
*            IN   float    CAP  degree       Cap : direction where the front of the ship is pointing
*
*            OUT  float    DDV  degree       Meteo Direction FROM where the vector starts (0=North)
*            OUT  float    FFV  m/s          Module of the meteo vector Wind Speed
*                                                
* ENTRY            NONE
*               
* SUBPROGRAMS      NONE
*
* FILES            NONE
*
* REFERENCES       
*
*
* CHANGES          1.3  adapted to follow categorie's definition change
*                  1.2  added args' sampling description
*
*
* COPYRIGHT        Meteo-France/CNRM
*
* AGREEMENT        
*########################################################################*/

#define _POSIX_SOURCE 1
#define _XOPEN_SOURCE 600
/* Le #define _HPUX_SOURCE est la pour utiliser la fonction isfinite */
#define _HPUX_SOURCE 1

#include <math.h>
#include <stdio.h>
#include <string.h>
#include "struct_oper.h"


void
CalcVent_h_polaire (unsigned long NLoop,
		    const float *dda, const float *ffa, const float *ddr,
		    const float *vvr, const float *cap, float *ddv,
		    float *ffv)
{
  unsigned long i;
  double Deg2Rad, Rad2Deg;
  register double beta, gamma, dda_r, cap_r, ddr_r, rapv, ddv_r;
  const float seuil_vent_nul = 0.05;	/* Les vitesses en-dessous de ce seuil sont assimilées à 0. */

  /* entree de l'angle en degres, donc conversion en radians */
  Deg2Rad = M_PI / 180.0;
  Rad2Deg = 180.0 / M_PI;

  for (i = 0; i < NLoop; i++)
    {
      /* TODO : Il faudrait etudier la vitesse angulaire ; */
      /* Dans tous les cas, il faudrait corriger la vvr par la vitesse de rotation
       * la longueur l entre le centre de gravite et le mat devrait etre entree en
       * argument */
      /* Il faut calculer l*dcap/dt, dt etant le pas de temps de l'acquisition
       * Si dcap/dt n'est pas negligeable, alors on calcule avec la methode du 
       * triangle en posant :
       * ddr = cap +/- 90° selon que le bateau tourne dans le sens des aiguilles
       * d'une montre ou non */
      /* vvr = dcap/dt */
      /* si dcap/dt est presque nul, on considere que le bateau est immobile : */
      /* ddv = dda + cap et ffv = ffa */


      if (vvr[i] == 0.)
	{
	  /* Et pas de rotation ou rotation tres lente */
	  ddv[i] = dda[i] + cap[i];
	  /* ddv_r = dda_r + cap_r; */
	  ffv[i] = ffa[i];
	  /* Convention MTO : direction nulle si vitesse nulle */
	  if (ffv[i] < seuil_vent_nul)
	    {
	      ddv[i] = 0.0;
	      ffv[i] = 0.0;
	    }
	}
      else
	/* cas vvr (vitesse bateau) non nulle */
	{
	  /* on passe en radian */
	  dda_r = dda[i] * Deg2Rad;
	  cap_r = cap[i] * Deg2Rad;
	  ddr_r = ddr[i] * Deg2Rad;

	  /* Il y a une route definie donc non nulle et a priori, une route 
	   * nord est a 360° */
	  /* au cas ou .. */
	  if (ddr_r == 0.)
	    ddr_r = 2. * M_PI;

	  /* un cap au nord est a 360° */
	  if (cap_r == 0.)
	    cap_r = 2. * M_PI;

	  /* on compte tout dans le sens normal (aiguille d'une montre)
	   * on calcule l'angle beta entre la route et la direction (sens mathematique)
	   * du vent apparent */
	  /* Attention : les cap et route sont a 360 degres pour le nord et pas O
	   * (sinon, on les y a mis juste avant)! */

	  /* si direction nulle du vent apparent on devrait forcer la vitesse a 0 */
	  /* if (dda_r == 0.)
	     ffa[i] = 0.; */

	  beta = dda_r + cap_r - ddr_r;

	  /* on calcule le module du vecteur vent vrai d'apres la formule du triangle */
	  ffv[i] =
	    sqrt (ffa[i] * ffa[i] + vvr[i] * vvr[i] -
		  (2. * ffa[i] * vvr[i] * cos (beta)));
	  /* Note : si ffa=ffv et beta=0, ffv peut etre numeriquement non nul ... d'ou le forcage a 0 plus loin */

	  /*cas ou le vent vrai est non nul */
	  if (ffv[i] >= seuil_vent_nul)
	    /* if (ffv[i] != 0.)  */
	    {
	      rapv = vvr[i] / ffv[i];

	      /* on en deduit l'angle gamma entre le vent apparent et le vent vrai */
	      /* formule du triangle : egalite des rapports sin(angle)/cote oppose */


	      gamma = asin (sin (beta) * rapv);
	      /*Attention : asin2 n'existant pas, asin renvoie entre -pi/2 et pi/2 */
	      /*Il faut donc tester la forme du triangle, angle aigu ou obtu ou nul */
	      /* si dda=0 (vent apparent nul), beta est aussi nul, et gamma */

	      /* Rappels de trigo elementaire et de la methode dite du jardinier :
	       * Un cordon attache aux extremites du diametre d'un cercle (egale a
	       * la vitesse du navire), de longueur suffisante pour qu'un piquet
	       * situe sur le cercle le tende exactement, permet de tracer un angle
	       * droit quelque soit la place du piquet sur le cercle.
	       * Donc, pour un cordon plus court, le piquet etant en dedans
	       *  le cercle, l'angle sera necessairement obtu
	       **/

	      /* if ((cos (beta) < 0) || (dda_r == 0.)) : ce test n'est pas suffisant */
	      if ((ffv[i] * ffv[i] + ffa[i] * ffa[i] < vvr[i] * vvr[i])
		  || (dda_r == 0.))
		gamma = M_PI - gamma;

	      ddv_r = cap_r + dda_r + gamma;
	      /* ddv_r = fmod (cap_r + dda_r + gamma,2 * M_PI) ; */

	      /* On repasse en degres */
	      ddv[i] = ddv_r * Rad2Deg;

	      if (ddv[i] == 0.)
		{
		  /* on est tjs ds le cas ffv non nul donc vent de nord */
		  ddv[i] = 360.;
		}

	    }
	  else
	    {
	      /* *ffv = 0.; */
	      /* convention meteo et OMM avec notre seuil  */
	      ddv[i] = 0.;
	      /* On force le vent à 0 */
	      ffv[i] = 0.;
	    }
	}
      /* pas utile si modulo avant.. */
      if (ddv[i] > 360.)
	ddv[i] -= 360.;
    }
  return;
}


/* la fonction d'enrobage classique */

int
OP_CalcVent_h_polaire (unsigned long NbVal, void *ArgList[], char *DiagExec)
{

  (void) sprintf (DiagExec, "CalcVent_h_polaire, NbVal=%lu", NbVal);

  CalcVent_h_polaire (NbVal,
		      (float *) ArgList[0],
		      (float *) ArgList[1],
		      (float *) ArgList[2], (float *) ArgList[3],
		      (float *) ArgList[4],
		      (float *) ArgList[5], (float *) ArgList[6]);
  return OP_OK;
}

void
ID_CalcVent_h_polaire (oper * optr)
{
  int idx = 0;
  strcpy (optr->Nom, "CalcVent_h_polaire");
  optr->Version = "$Revision$";
  optr->Date = "$Date$";
  optr->fctptr = OP_CalcVent_h_polaire;
  optr->misval_auto = 1;	/* gestion auto des misval */
  optr->NbArg = 7;

  /* dda */
  optr->Arg_Car[idx].direction = DIR_IN;
  optr->Arg_Car[idx].categorie = VECTOR;
  optr->Arg_Car[idx].typ = ATYC_IF32;
  optr->Arg_Car[idx].array_dim = "1";
  optr->Arg_Car[idx].type_sample = "any";
  optr->Arg_Car[idx].sample = "any";
  optr->Arg_Car[idx].unite = "degree";

  /* ffa */
  idx++;
  optr->Arg_Car[idx].direction = DIR_IN;
  optr->Arg_Car[idx].categorie = VECTOR;
  optr->Arg_Car[idx].typ = ATYC_IF32;
  optr->Arg_Car[idx].array_dim = "1";
  optr->Arg_Car[idx].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[idx].type_sample = "any";
  optr->Arg_Car[idx].sample = "any";
  optr->Arg_Car[idx].unite = "m/s";

  /* ddr */
  idx++;
  optr->Arg_Car[idx].direction = DIR_IN;
  optr->Arg_Car[idx].categorie = VECTOR;
  optr->Arg_Car[idx].typ = ATYC_IF32;
  optr->Arg_Car[idx].array_dim = "1";
  optr->Arg_Car[idx].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[idx].type_sample = "any";
  optr->Arg_Car[idx].sample = "any";
  optr->Arg_Car[idx].unite = "degree";

  /* vvr */
  idx++;
  optr->Arg_Car[idx].direction = DIR_IN;
  optr->Arg_Car[idx].categorie = VECTOR;
  optr->Arg_Car[idx].typ = ATYC_IF32;
  optr->Arg_Car[idx].array_dim = "1";
  optr->Arg_Car[idx].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[idx].type_sample = "any";
  optr->Arg_Car[idx].sample = "any";
  optr->Arg_Car[idx].unite = "m/s";

  /* cap */
  idx++;
  optr->Arg_Car[idx].direction = DIR_IN;
  optr->Arg_Car[idx].categorie = VECTOR;
  optr->Arg_Car[idx].typ = ATYC_IF32;
  optr->Arg_Car[idx].array_dim = "1";
  optr->Arg_Car[idx].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[idx].type_sample = "any";
  optr->Arg_Car[idx].sample = "any";
  optr->Arg_Car[idx].unite = "degree";

  /* ddv */
  idx++;
  optr->Arg_Car[idx].direction = DIR_OUT;
  optr->Arg_Car[idx].categorie = VECTOR;
  optr->Arg_Car[idx].typ = ATYC_IF32;
  optr->Arg_Car[idx].array_dim = "1";
  optr->Arg_Car[idx].NbVal = "$Arg1.NbVal";
  /* le sample (mais pas l'unite) se deduit de l'entree  */
  optr->Arg_Car[idx].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[idx].sample = "$Arg1.sample";
  optr->Arg_Car[idx].ref_time = "$Arg1.ref_time";
  optr->Arg_Car[idx].misval = "$Arg1.misval";
  optr->Arg_Car[idx].unite = "degree";
  optr->Arg_Car[idx].famille = "$Arg1.famille";
  optr->Arg_Car[idx].name = " \"Direction du vent reel\"";
  optr->Arg_Car[idx].en_name = " \"True wind direction\"";

  /* ffv */
  idx++;
  optr->Arg_Car[idx].direction = DIR_OUT;
  optr->Arg_Car[idx].categorie = VECTOR;
  optr->Arg_Car[idx].typ = ATYC_IF32;
  optr->Arg_Car[idx].array_dim = "1";
  optr->Arg_Car[idx].NbVal = "$Arg2.NbVal";
  /* l'unite et le sample se deduisent de l'entree  */
  optr->Arg_Car[idx].type_sample = "$Arg2.type_sample";
  optr->Arg_Car[idx].sample = "$Arg2.sample";
  optr->Arg_Car[idx].ref_time = "$Arg2.ref_time";
  optr->Arg_Car[idx].misval = "$Arg2.misval";
  optr->Arg_Car[idx].unite = "$Arg2.unit";
  optr->Arg_Car[idx].famille = "$Arg2.famille";
  optr->Arg_Car[idx].name = "\"Vitesse du vent reel\"";
  optr->Arg_Car[idx].en_name = " \"True wind speed\"";
}
