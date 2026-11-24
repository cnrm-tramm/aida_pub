/*********************************************************
* OPERATOR 	ha_lyman_td_reg.c FUNCTION ANSI-C
*
* PURPOSE 	computation of absolute humidity (g/m3)
*		with lyman-aplha calibrated by dew-point
*
* Cette fonction calcule l'humidité absolue mesuree avec
* un lyman-alpha calibre par un capteur point de rosee.
* Les mesures de Td et lyman-alpha doivent etre synchrones et a la
* meme frequence d'echantillonnage.
*
* VERSION       $Revision$
*
* ARGUMENTS 	IN	float	td	dew-point temperature 
*		IN 	float	vpel	dew-point Peltier voltage
*		IN 	float 	lyman 	lyman-alpha output voltage
*		IN 	float 	ts 	static temperature
*		IN 	float 	ps 	static pressure (hPa)
*		IN	float	dp 	dynamic pressure (hPa)
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

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>

#include "struct_oper.h"

#include "unit.h"
#include "thermo.h"

int
ha_lyman_td_reg (unsigned long Nloop,
		 const float *td,
		 const float *vpel,
		 const float *lyman,
		 const float *ts,
		 const float *ps,
		 const float *dp,
		 const float fr,
		 const float vpel_inf,
		 const float vpel_sup,
		 float *lyman_cal,
		 double Diag_tab[])
{
  int nds2, nd;

  long i, n, ndeb;
  long n_test_1, n_test_2, n_test_3, n_test_4, n_test_5;
  int cnvt_inf_ts, cnvt_inf_td;

  float ectyp_max = 0.3;
  float eps_td = 0.3;

  double fnd, ectyp_td, som_td, som_td2;

  float ts0, td0;
  float e, ro, rapmel, huma, degK_ts, degK_td;

  float a, b, r2;
  float *ha, *lym;

  double dn;
  double dlym, dha;
  double som_ha, som_ha2, som_lym, som_lym2, som_lym_ha;
  double ectyp_ha, nvar_lym;

  /*** Eventuelle conversion Celsius -> kelvin ***
   * Utilisation de la bibliothèque unit.c */
  cnvt_inf_ts = auto_tempe_unit (Nloop, ts, &degK_ts);
  cnvt_inf_td = auto_tempe_unit (Nloop, td, &degK_td);

  /*** allocation de lym et ha ****/
  ha = malloc (Nloop * sizeof (*ha));
  if (ha == NULL)
    return 101;
  lym = malloc (Nloop * sizeof (*ha));
  if (lym == NULL)
    return 101;

  /**** Initialisations ****
   * nbpt = nb de points de la fenetre de regression
   * n0 = longueur de lissage des coefs de regression
   * nd = nombre de points pour le calcul de l'ecart-type de td
   **/

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

  huma = 0.;
  r2 = 0.;
  ectyp_ha = 0.;

  n = 0;
  n_test_1 = 0;
  n_test_2 = 0;
  n_test_3 = 0;
  n_test_4 = 0;
  n_test_5 = 0;

  /*************************************/

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
       * Td est considere bon si ces criteres sont verifies :
       *    1) vpel_inf < Tension Peltier < vpel_sup
       *    2) Ecart-type de Td inferieur a ectyp_max
       *    3) Td+eps_td > Ts
       *    4) dp > 12 hPa (soit vp > 50 m/s, ventilation suffisante)
       *    5) ts, td, ps ne sont pas des NaN
       ************************************************************/

      if ((vpel[i] > vpel_sup) || (vpel[i] < vpel_inf))
	{
	  /* Td n'est pas valide */
	  n_test_1++;
	  continue;
	}

/*       if  (ectyp_td > ectyp_max)  
   {
          n_test_2++;
   continue;
   } */

      if ((td[i] + degK_td + eps_td) > (ts[i] + degK_ts))
	{
	  /* Td n'est pas valide */
	  n_test_3++;
	  continue;
	}

      if (dp[i] < 12.)
	{
	  /* dp (donc Vp) trop faible : appareil non ventilé */
	  n_test_4++;
	  continue;
	}
      if ((!isfinite(td[i])) || (!isfinite(ts[i])) || (!isfinite(ps[i])))
	{
	  /* Une des valeurs nécessaires au calcul est manquante */
	  n_test_5++;
	  continue;
	}

      /* les mesures sont valides */

      /**** calcul de l'humidite absolue ****/

      ts0 = ts[i] + degK_ts;
      td0 = td[i] + degK_td;

      /* fonction de thermo.c, e en hPa */
      ew (td0, &e);

      rapmel = (0.622 * e) / ((ps[i]) - e);
      ro = ps[i] / (2.8705 * ts0);
      huma = 1000. * rapmel * ro;
/*
   fprintf (stderr, "e = %f, rapmel = %f, ro = %f, huma = %f \n",
   e, rapmel, ro, huma );
 */
      /*** calcul des parameters statistiques ***/

      dha = (double) huma;
      dlym = (double) lyman[i];

      som_ha = som_ha + dha;
      som_ha2 = som_ha2 + (dha * dha);

      som_lym = som_lym + dlym;
      som_lym2 = som_lym2 + (dlym * dlym);

      som_lym_ha = som_lym_ha + (dlym * dha);

      dn = (double) n;

      ha[n] = huma;
      lym[n] = lyman[i];

      n = n + 1;
    }

  /*** ecart-type de Ha ****/
  ectyp_ha = (som_ha2 / dn) - ((som_ha * som_ha) / (dn * dn));
  if (ectyp_ha >= 0.)
    ectyp_ha = sqrt (ectyp_ha);
  else
    ectyp_ha = 0.;

  /*** calcul de la regression ****/

  nvar_lym = (som_lym2 * dn) - (som_lym * som_lym);

  if (nvar_lym > 0.)
    {
      a = (float) (((dn * som_lym_ha) - (som_lym * som_ha)) / nvar_lym);
      b = ((float) (som_ha / dn)) - a * ((float) (som_lym / dn));

      r2 = a * a * (float) (nvar_lym / (dn * dn * ectyp_ha * ectyp_ha));
    }
  else
    {
      a = 0.;
      b = 0.;
      r2 = 0.;
    }

  fprintf (stderr, " n = %ld | a = %f | b = %f | r2 = %f \n", n, a, b, r2);

  /** 2eme boucle pour l'application de la regression */
  for (i = 0; i < Nloop; i++)
    {
      lyman_cal[i] = a * lyman[i] + b;
      if (lyman_cal[i] < 0)
	lyman_cal[i] = 0.;
    }

  /*** liberation des tableaux temporaires. ****/
  free (ha);
  free (lym);

  Diag_tab[0] = n;
  Diag_tab[1] = a;
  Diag_tab[2] = b;
  Diag_tab[3] = r2;
  Diag_tab[4] = cnvt_inf_ts;
  Diag_tab[5] = cnvt_inf_td;
  Diag_tab[6] = n_test_1;
  Diag_tab[7] = n_test_2;
  Diag_tab[8] = n_test_3;
  Diag_tab[9] = n_test_4;
  Diag_tab[10] = n_test_5;

  return 0;
}

/* fonction d'enrobage */

int
OP_ha_lyman_td_reg (unsigned long NbVal, void *ArgList[], char *DiagExec)
{
  int CodRet;
  double Diag_tab[11];
  int NCar;

  NCar = sprintf (DiagExec, "ha_lyman_td_reg : (%ld echant.) ", NbVal) ;
  if (NCar < 0)
    NCar = 0;
  DiagExec += NCar;

  CodRet = ha_lyman_td_reg (NbVal,
			    (float *) ArgList[0],
			    (float *) ArgList[1],
			    (float *) ArgList[2],
			    (float *) ArgList[3],
			    (float *) ArgList[4],
			    (float *) ArgList[5],
			    *((float *) ArgList[6]),
			    *((float *) ArgList[7]),
			    *((float *) ArgList[8]),
			    (float *) ArgList[9], Diag_tab);

  switch (CodRet)
    {
    case 0:
      sprintf (DiagExec,
	       "%g valeurs (sur %lu) utilisees, regress: Ha = %g * V + %g , r2=%g, rejets : vpel:%g, ectyp:%g, td>ts:%g, dp:%g, NaN:%g",
	       Diag_tab[0], NbVal, Diag_tab[1], Diag_tab[2], Diag_tab[3],
	       Diag_tab[6], Diag_tab[7], Diag_tab[8], Diag_tab[9], Diag_tab[10]);
      return OP_OK;
    case 101:
      sprintf (DiagExec, "Error : couldn't allocate memory");
    default:
      sprintf (DiagExec, "Error ");
    }
  return OP_FAIL;
}

void
ID_ha_lyman_td_reg (oper * optr)
{
  strcpy (optr->Nom, "ha_lyman_td_reg");
  optr->Version = "$Revision$";
  optr->Date = "$Date$";
  optr->fctptr = OP_ha_lyman_td_reg;
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
  optr->Arg_Car[5].unite = "hPa";

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
  optr->Arg_Car[9].famille = " \"eau_vapeur\" ";
  optr->Arg_Car[9].name = " \"Humidite absolue calibree empiriquement\" ";

}
