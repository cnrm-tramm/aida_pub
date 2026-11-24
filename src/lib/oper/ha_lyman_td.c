/*********************************************************
* OPERATOR 	ha_lyman_td.c FUNCTION ANSI-C
*
* PURPOSE 	computation of absolute humidity (g/m3)
*		with lyman-aplha calibrated by dew-point
*
* Cette fonction calcule l'humidité absolue mesurée avec
* un lyman-alpha calibré par un capteur point de rosée.
* Les mesures de Td et lyman-alpha doivent être synchrones et à la
* meme fréquence d'echantillonnage.
*
* VERSION       $Revision$
*
* ARGUMENTS 	IN	float	td	dew-point temperature 
*		IN 	float	vpel	dew-point Peltier voltage
*		IN 	float 	lyman 	lyman-alpha output voltage
*		IN 	float 	ts 	static temperature
*		IN 	float 	ps 	static pressure (hPa)
*		IN	float	vp 	true air speed (m/s)
*		IN 	float 	fr 	sample frequency
*		IN	float 	vpel_inf Peltier voltage minimum value   
*		IN 	float 	vpel_sup Peltier voltage maximum value
*
*		OUT 	float 	lyman_cal  absolute humidity (g/m3)
*
* ENTRY		NONE
*
* SUBPROGRAMS 	NONE
* 
* REFERENCES	
*
* CHANGES       1.2   added arg's sampling description
*		1.4   Ajout d'un test pour ne pas traiter
*		      lorsque la vitesse propre est
*		      insuffisante ( < 50 m/s) -> ajout vitesse 
*		      propre comme argument supplementaire. 
*		      Les valeurs du debut du vol (egales a
*		      zero dans la version 1.2) sont 
*		      remplacees par des valeurs calibrees. 
*		
*
* COPYRIGHT 	Meteo-France
*		Centre National de Recherches Meteorologiques
*		GMEI/MMA
*		42, av. G. Coriolis
* 		31057 	TOULOUSE cedex
*
************************************************************/

#define _POSIX_SOURCE 1
#define _XOPEN_SOURCE 600
/* Le #define _HPUX_SOURCE n'est la que pour "voir" strdup */
#define _HPUX_SOURCE 1
#define _XOPEN_SOURCE_EXTENDED 1

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>

#include "struct_oper.h"

int
ha_lyman_td (unsigned long Nloop,
	     const float *td,
	     const float *vpel,
	     const float *lyman,
	     const float *ts,
	     const float *ps,
	     const float *vp,
	     const float fr,
	     const float vpel_inf, 
             const float vpel_sup, 
             float *lyman_cal)
{
  int nds2;
  int flg_prem_reg, ind_prem_reg;
  int nbpt, n0, nd;

  long i, k, n, ndeb;

  float ectyp_max = 0.3;
  float eps_td = 0.3;

  float fnd, ectyp_td, som_td, som_td2;

  float ts0, td0, fx;
  float e, ro, rapmel, huma, degK_ts, degK_td;

  float a_prem, b_prem;
  float ai, bi, an, bn, a0, b0, a, b, r2;
  float *ha, *lym;

  double dn;
  double dlym_deb, dlym_fin, dha_deb, dha_fin;
  double som_ha, som_ha2, som_lym, som_lym2, som_lym_ha;
  double ectyp_ha, nvar_lym;


/*** conversion Celsius -> kelvin ***/

  degK_td = 0.;
  degK_ts = 0.;
  if (td[0] < 100.)
    degK_td = 273.15;
  if (ts[0] < 100.)
    degK_ts = 273.15;

/*** allocation de lym et ha ****/

  ha = malloc (Nloop * sizeof (float));
  lym = malloc (Nloop * sizeof (float));

/**** Initialisations ****/

/* nbpt = nb de points de la fenetre de regression */
/* n0 = longueur de lissage des coefs de regression */
/* nd = nombre de points pour le calcul de l'ecart-type de td */

  nbpt = (int) (fr * 40);
  if (nbpt > Nloop)
    nbpt = Nloop;

  n0 = (int) (fr * 6);
  if (n0 > Nloop)
    n0 = Nloop;

  nd = (int) fr;
  if (nd > Nloop)
    nd = Nloop;

  nds2 = (int) (nd / 2);

  fnd = (float) nd;

  som_td = 0.;
  som_td2 = 0.;

  som_ha = 0.;
  som_ha2 = 0.;
  som_lym = 0.;
  som_lym2 = 0.;
  som_lym_ha = 0.;

  a0 = 0.;
  ai = 0.;
  an = 0.;
  b0 = 0.;
  bi = 0.;
  bn = 0.;

  huma = 0.;
  r2 = 0.;
  ectyp_ha = 0.;

  n = 0;
  k = 0;

  ind_prem_reg = 0;
  flg_prem_reg = 0;

/*************************************/

  fprintf (stderr, "Nloop= %d, nbpt=%d, fr=%f\n", (int) Nloop, nbpt, fr);

  for (i = 0; i < nd; i++)
    {
      som_td = som_td + td[i];
      som_td2 = som_td2 + (td[i] * td[i]);
    }

  for (i = 0; i < Nloop; i++)
    {
      if ((i > nds2 - 1) && (i < Nloop - nds2))
	{
	  som_td = som_td + td[i + nds2] - td[i - nds2];
	  som_td2 = som_td2 + (td[i + nds2] * td[i + nds2])
	    - (td[i - nds2] * td[i - nds2]);
	}

      ectyp_td = (som_td2 / fnd) - ((som_td * som_td) / (fnd * fnd));
      if (ectyp_td >= 0.)
	ectyp_td = sqrt (ectyp_td);
      else
	ectyp_td = 0.;

/***********************************************************
   Td est considere bon si ces criteres sont verifies :
   	1) vpel_inf < Tension Peltier < vpel_sup
   	2) Ecart-type de Td inferieur a ectyp_max
   	3) Td+eps_td > Ts
   	4) Vitesse propre > 50 m/s (pas assez ventile)
************************************************************/

      if ((vpel[i] > vpel_sup) || (vpel[i] < vpel_inf)
/*        || (ectyp_td > ectyp_max) */
	  || ((td[i] + degK_td + eps_td) > (ts[i] + degK_ts))
	  || (vp[i] < 50.))
	{
	  lyman_cal[i] = an * lyman[i] + bn;
	  continue;
	}

/**** calcul de l'humidite absolue ****/

      ts0 = ts[i] + degK_ts;
      td0 = td[i] + degK_td;

      e = 610.8 * exp (17.588 * ((td0 - 273.15) / (td0 - 31.25)));
      rapmel = (0.622 * e) / ((100. * ps[i]) - e);
      ro = ps[i] / (2.8705 * ts0);
      huma = 1000. * rapmel * ro;
/*
      fprintf (stderr, "e = %f, rapmel = %f, ro = %f, huma = %f \n",
      e, rapmel, ro, huma );
*/
/*** calcul des parameters statistiques ***/

      n = n + 1;

      if (n > nbpt)
	{
	  ndeb = n - nbpt - 1;

	  dha_deb = (double) (ha[ndeb]);
	  dha_fin = (double) huma;

	  dlym_deb = (double) (lym[ndeb]);
	  dlym_fin = (double) (lyman[i]);

	  som_ha = som_ha + dha_fin - dha_deb;
	  som_ha2 = som_ha2 + (dha_fin * dha_fin) - (dha_deb * dha_deb);

	  som_lym = som_lym + dlym_fin - dlym_deb;
	  som_lym2 = som_lym2 + (dlym_fin * dlym_fin) - (dlym_deb * dlym_deb);

	  som_lym_ha =
	    som_lym_ha + (dlym_fin * dha_fin) - (dlym_deb * dha_deb);

	  dn = (double) nbpt;
	}
      else
	{
	  dha_fin = (double) huma;
	  dlym_fin = (double) lyman[i];

	  som_ha = som_ha + dha_fin;
	  som_ha2 = som_ha2 + (dha_fin * dha_fin);

	  som_lym = som_lym + dlym_fin;
	  som_lym2 = som_lym2 + (dlym_fin * dlym_fin);

	  som_lym_ha = som_lym_ha + (dlym_fin * dha_fin);

	  dn = (double) n;
	}

      ha[n - 1] = huma;
      lym[n - 1] = lyman[i];

/*** ecart-type de Ha ****/

      ectyp_ha = (som_ha2 / dn) - ((som_ha * som_ha) / (dn * dn));
      if (ectyp_ha >= 0.)
	ectyp_ha = sqrt (ectyp_ha);
      else
	ectyp_ha = 0.;

/***********************************/
/*** test sur l'ecart-type de ha ***/

      if (ectyp_ha > 0.6)
	{
/*** calcul de la regression ****/

	  nvar_lym = (som_lym2 * dn) - (som_lym * som_lym);

	  if (nvar_lym > 0.)
	    {
	      a = (float) (((dn * som_lym_ha) - (som_lym * som_ha)) /
			   nvar_lym);
	      b = ((float) (som_ha / dn)) - a * ((float) (som_lym / dn));

	      r2 =
		a * a * (float) (nvar_lym / (dn * dn * ectyp_ha * ectyp_ha));
	    }
	  else
	    {
	      a = 0.;
	      b = 0.;
	      r2 = 0.;
	    }

/**********************************************/
/*** test sur le coefficient de correlation ***/

	  if (r2 > 0.80)
	    {
	      if (flg_prem_reg == 0)
		{
		  fprintf (stderr, "1ere Reg a %ld : %g, %g \n", i, a, b);
		  a_prem = a;
		  b_prem = b;
		  flg_prem_reg = 1;
		  ind_prem_reg = i;

		  ai = a;
		  bi = b;
		  a0 = ai;
		  b0 = bi;

		}
	      else
		{
		  k = 0;

		  ai = an;
		  bi = bn;

		  a0 = a;
		  b0 = b;
/*
   		  fprintf (stderr, "Reg a %ld : %g, a =%g, b=%g, ect_ha=%g, r2=%g \n",
			   i, a, b, ectyp_ha, nvar_lym, r2); 
			   */
		}
	    }

	}


/************************************************/#
/*** calcul de la valeur lyman-alpha calibree ***/

      k = k + 1;

      fx = exp (-1. * (((float) k) / ((float) n0)));

      an = a0 + (ai - a0) * fx;
      bn = b0 + (bi - b0) * fx;

      lyman_cal[i] = an * lyman[i] + bn;
    }

/*** boucle jusqu'a l'indice de premiere premiere regression
     (ind_prem_reg) pour que le vecteur commence par des
     valeurs non nulles  et "vraisemblables" ***/

  for (i = 0; i < ind_prem_reg; i++)
    {
      lyman_cal[i] = a_prem * lyman[i] + b_prem;
    }

/*** liberation de lym et ha ****/

  free (ha);
  free (lym);

  /*fclose (fp_out); */

  return 0;
}

/* fonction d'enrobage */

int
OP_ha_lyman_td (unsigned long NbVal, void *ArgList[], char *DiagExec)
{
  int CodRet;
  int NCar;

  NCar = sprintf (DiagExec, "ha_lyman_td : (%ld echant.) ", NbVal) ;
  if (NCar < 0)
    NCar = 0;
  DiagExec += NCar;

  CodRet = ha_lyman_td (NbVal,
			(float *) ArgList[0],
			(float *) ArgList[1],
			(float *) ArgList[2],
			(float *) ArgList[3],
			(float *) ArgList[4],
			(float *) ArgList[5],
			*((float *) ArgList[6]),
			*((float *) ArgList[7]),
			*((float *) ArgList[8]), 
                        (float *) ArgList[9]);


  return OP_OK;
}

void
ID_ha_lyman_td (oper * optr)
{
  strcpy (optr->Nom, "ha_lyman_td");
  optr->Version = "$Revision$";
  optr->Date = "$Date$";
  optr->fctptr = OP_ha_lyman_td;
  optr->NbArg = 10;

  optr->Arg_Car[0].direction = DIR_IN;
  optr->Arg_Car[0].categorie = VECTOR;
  optr->Arg_Car[0].typ = ATYC_IF32;
  optr->Arg_Car[0].array_dim = "1";
  optr->Arg_Car[0].type_sample = "any";
  optr->Arg_Car[0].sample = "any";
  optr->Arg_Car[0].unite = "kelvin";

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
  optr->Arg_Car[2].unite = "volt";

  optr->Arg_Car[3].direction = DIR_IN;
  optr->Arg_Car[3].categorie = VECTOR;
  optr->Arg_Car[3].typ = ATYC_IF32;
  optr->Arg_Car[3].array_dim = "1";
  optr->Arg_Car[3].type_sample = "any";
  optr->Arg_Car[3].sample = "any";
  optr->Arg_Car[3].unite = "kelvin";

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

  optr->Arg_Car[6].direction = DIR_IN;
  optr->Arg_Car[6].categorie = COEFFICIENT;
  optr->Arg_Car[6].typ = ATYC_IF32;
  optr->Arg_Car[6].array_dim = "1";
  optr->Arg_Car[6].type_sample = NULL;
  optr->Arg_Car[6].sample = NULL;
  optr->Arg_Car[6].unite = "Hz";

  optr->Arg_Car[7].direction = DIR_IN;
  optr->Arg_Car[7].categorie = COEFFICIENT;
  optr->Arg_Car[7].typ = ATYC_IF32;
  optr->Arg_Car[7].array_dim = "1";
  optr->Arg_Car[7].type_sample = NULL;
  optr->Arg_Car[7].sample = NULL;
  optr->Arg_Car[7].unite = "Volt";

  optr->Arg_Car[8].direction = DIR_IN;
  optr->Arg_Car[8].categorie = COEFFICIENT;
  optr->Arg_Car[8].typ = ATYC_IF32;
  optr->Arg_Car[8].array_dim = "1";
  optr->Arg_Car[8].type_sample = NULL;
  optr->Arg_Car[8].sample = NULL;
  optr->Arg_Car[8].unite = "Volt";

  optr->Arg_Car[9].direction = DIR_OUT;
  optr->Arg_Car[9].categorie = VECTOR;
  optr->Arg_Car[9].typ = ATYC_IF32;
  optr->Arg_Car[9].array_dim = "1";
  optr->Arg_Car[9].NbVal = "$Arg3.NbVal";
  optr->Arg_Car[9].type_sample = "$Arg3.type_sample";
  optr->Arg_Car[9].sample = "$Arg3.sample";
  optr->Arg_Car[9].ref_time = " $Arg3.ref_time";
  optr->Arg_Car[9].unite = "gram/m3";

}
