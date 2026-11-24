/*************************************************
* OPERATOR 	cdp_conc_cor.c 	FUNCTION ANSI-C
*
* PURPOSE	calcul de la concentration pour une classe
*		de mesure d'un CDP (OAP-200X) 
*		Un algorithme de correction de la DOF est
*		utilise
*
* ARGUMENTS 	IN 	float	jcl 	classe 
*		IN	float 	vp 	vitesse propre (m/s)
*		IN	int 	fr	frequence d'echantillonnage (Hz)
*		IN 	int	icl	numero de la classe (de 1 à 15)
*		IN	int	ndiode	nombre de diodes
*		IN 	float   diod_dia diameter d'une diode  (mm)
*		IN	float 	res	resolution (microns)
*		IN	float 	mag 	facteur amplification de la sonde
*		IN 	float 	arm_d	distance entre les bras de mesure (mm)
*		IN	float	resp_t 	temps de reponse (microsecond)
*
*		OUT 	float 	conc	concentration dans la classe "icl" (cm-3)
*		
* ENTRY		NONE
*
* SUBPROGRAMS 	NONE
*
* REFERENCE     L'algorithme de correction de la DOF vient 
*               de Darrel Baumgardner. (NCAR/RAF)
*		Les formules ont ete tirees du Bulletin NCAR/RAF n°24
*		"Aiborne Measurements For Cloud Microphysics"
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
cdp_conc_cor (unsigned long ndata,
	      float *jcl,
	      float *vp,
	      float fr,
	      float icl,
	      float ndiode,
	      float diod_dia,
	      float res, float mag, float arm_d, float resp_t, float *conc)
{
  long i;

  float sv, esw, dof, rad;
  float szz, timex, frac, f, z;

/** calcul du rayon (mm) **/

  rad = icl * res / 2000.;

/** calcul de esw (effective sample width)(mm) ***/
/** icl varie de 1 à 15 --> calcul avec icl-1  (BP 20030718) ***/

  esw = (diod_dia * (ndiode - (icl - 1) - 1)) / mag;

/** taille selon le nombre d'element du tableau de diodes **/

  szz = 2. * rad;		/* en mm */

  /* Diminish this radius by an amount that accounts for
     * the fact that the particle is not on the diode array
     * 100% of the time 50% shadowed. This amount is approximately
     * one half diode array width wide.
   */
  szz += 0.008;


  for (i = 0; i < ndata; i++)
    {

      if (vp[i] < 50.)
	{
	  conc[i] = 0.;
	  continue;
	}

      /* Calculate amount of time particle will be on the array
       */
      if (vp[i] > 0)
	timex = (szz * 1.e-3) / (vp[i] * 1.e-6);	/* en microseconds */
      else
	timex = 0.;

      /* This is the fraction of total amplitude caused by response
         time */
      frac = (double) 1.0 - exp ((double) ((-1. * timex) / resp_t));

      /* Have to meet 70% occultation for the 1D.
       */
      if (frac < 0.7)
	{
	  dof = 0.;
	  conc[i] = 0.;
	}
      else
	/* Cautionary note to users of this routine, the relationship
	 * between dof and Z was derived from laboratory studies which
	 * are somewhat prelimnary in nature and need additional
	 * verification, A new algorithm should be available by 9/1/92
	 */
	{
	  f = (0.7 / frac) * 100.0;
	  z = 30.46 - (0.628 * f) + (0.003246 * f * f);
	  dof = 1580.0 * z * rad * rad;

	  if (dof >= arm_d)
	    dof = arm_d;

	  sv = dof * esw * (vp[i] / fr);	/* mm2*m = cm3 */

	  if (sv > 0)
	    conc[i] = jcl[i] / sv;
	  else
	    conc[i] = 0.;
	}
/*
   fprintf(stderr, "jcl : %f vp : %f timex : %f sv : %f dof : %f esw : %f conc : %f \n",
   jcl[i], vp[i], timex, sv, dof, esw, conc[i] );
 */
    }
  return 0;
}

/* fonction d'enrobage */
int
OP_cdp_conc_cor (unsigned long Nbval, void *ArgList[], char *DiagExec)
{
  int CodRet = cdp_conc_cor (Nbval,
			     (float *) ArgList[0],
			     (float *) ArgList[1],
			     *((float *) ArgList[2]),
			     *((float *) ArgList[3]),
			     *((float *) ArgList[4]),
			     *((float *) ArgList[5]),
			     *((float *) ArgList[6]),
			     *((float *) ArgList[7]),
			     *((float *) ArgList[8]),
			     *((float *) ArgList[9]),
			     (float *) ArgList[10]);


  return OP_OK;
}

void
ID_cdp_conc_cor (oper * optr)
{
  strcpy (optr->Nom, "cdp_conc_cor");
  optr->Version = "1.0";
  optr->Date = "03/19/96";
  optr->fctptr = OP_cdp_conc_cor;
  optr->NbArg = 11;

  /* jcl */
  optr->Arg_Car[0].direction = DIR_IN;
  optr->Arg_Car[0].categorie = VECTOR;
  optr->Arg_Car[0].typ = ATYC_IF32;
  optr->Arg_Car[0].array_dim = "1";
  optr->Arg_Car[0].type_sample = "any";
  optr->Arg_Car[0].sample = "any";
  optr->Arg_Car[0].unite = "";

  /* vp */
  optr->Arg_Car[1].direction = DIR_IN;
  optr->Arg_Car[1].categorie = VECTOR;
  optr->Arg_Car[1].typ = ATYC_IF32;
  optr->Arg_Car[1].array_dim = "1";
  optr->Arg_Car[1].type_sample = "any";
  optr->Arg_Car[1].sample = "any";
  optr->Arg_Car[1].unite = "m/s";

  /* fr */
  optr->Arg_Car[2].direction = DIR_IN;
  optr->Arg_Car[2].categorie = COEFFICIENT;
  optr->Arg_Car[2].typ = /* TYP_INT */ ATYC_IF32;
  optr->Arg_Car[2].array_dim = "1";
  optr->Arg_Car[2].unite = "Hz";

  /* icl */
  optr->Arg_Car[3].direction = DIR_IN;
  optr->Arg_Car[3].categorie = COEFFICIENT;
  optr->Arg_Car[3].typ =
    /* TYP_INT */ ATYC_IF32;
  optr->Arg_Car[3].array_dim = "1";
  optr->Arg_Car[3].type_sample = "any";
  optr->Arg_Car[3].sample = "any";
  optr->Arg_Car[3].unite = "";

  /* ndiode */
  optr->Arg_Car[4].direction = DIR_IN;
  optr->Arg_Car[4].categorie = COEFFICIENT;
  optr->Arg_Car[4].typ =
    /* TYP_INT */ ATYC_IF32;
  optr->Arg_Car[4].array_dim = "1";
  optr->Arg_Car[4].type_sample = NULL;
  optr->Arg_Car[4].sample = NULL;
  optr->Arg_Car[4].unite = "";
  optr->Arg_Car[5].direction = DIR_IN;
  optr->Arg_Car[5].categorie = COEFFICIENT;
  optr->Arg_Car[5].typ = ATYC_IF32;
  optr->Arg_Car[5].array_dim = "1";
  optr->Arg_Car[5].type_sample = NULL;
  optr->Arg_Car[5].sample = NULL;
  optr->Arg_Car[5].unite = "";
  optr->Arg_Car[6].direction = DIR_IN;
  optr->Arg_Car[6].categorie = COEFFICIENT;
  optr->Arg_Car[6].typ = ATYC_IF32;
  optr->Arg_Car[6].array_dim = "1";
  optr->Arg_Car[6].type_sample = NULL;
  optr->Arg_Car[6].sample = NULL;
  optr->Arg_Car[6].unite = "";
  optr->Arg_Car[7].direction = DIR_IN;
  optr->Arg_Car[7].categorie = COEFFICIENT;
  optr->Arg_Car[7].typ = ATYC_IF32;
  optr->Arg_Car[7].array_dim = "1";
  optr->Arg_Car[7].type_sample = NULL;
  optr->Arg_Car[7].sample = NULL;
  optr->Arg_Car[7].unite = "";
  optr->Arg_Car[8].direction = DIR_IN;
  optr->Arg_Car[8].categorie = COEFFICIENT;
  optr->Arg_Car[8].typ = ATYC_IF32;
  optr->Arg_Car[8].array_dim = "1";
  optr->Arg_Car[8].type_sample = NULL;
  optr->Arg_Car[8].sample = NULL;
  optr->Arg_Car[8].unite = "";
  optr->Arg_Car[9].direction = DIR_IN;
  optr->Arg_Car[9].categorie = COEFFICIENT;
  optr->Arg_Car[9].typ = ATYC_IF32;
  optr->Arg_Car[9].array_dim = "1";
  optr->Arg_Car[9].type_sample = NULL;
  optr->Arg_Car[9].sample = NULL;
  optr->Arg_Car[9].unite = "";

  /* conc */
  optr->Arg_Car[10].direction = DIR_OUT;
  optr->Arg_Car[10].categorie = VECTOR;
  optr->Arg_Car[10].typ = ATYC_IF32;
  optr->Arg_Car[10].array_dim = "1";
  optr->Arg_Car[10].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[10].ref_time = "$Arg1.ref_time";
  optr->Arg_Car[10].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[10].sample = "$Arg1.sample";
  optr->Arg_Car[10].unite = "cm-3";
}
