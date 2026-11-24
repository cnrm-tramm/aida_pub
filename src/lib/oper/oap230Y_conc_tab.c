/*************************************************
* OPERATOR 	oap230Y_conc_tab.c 	FUNCTION ANSI-C
*
* PURPOSE	Calcul de la concentration à partir des
*		tableaux de comptage d'un OAP230Y et de Vp.
*
* ARGUMENTS 	IN 	float	cnt 		tableau des comptages.
*		IN	float 	vp 		vitesse propre (m/s)
*		IN	float 	fr		frequence d'echantillonnage (Hz)
*		IN	float	ndiode		nombre de diodes total
*		IN	float 	res		resolution (microns)
*		IN	float 	coef_dof        coef pour calcul de la DOF	
*		IN	float	fact_dia	facteur multiplicatif diametre moyen de la classe
*		IN 	float 	arm_d		distance entre les bras de mesure (mm)
*
*		OUT 	float 	conc		Tableau des concentrations (cm-3)
*		
* ENTRY		NONE
*
* SUBPROGRAMS 	NONE
*
* REFERENCE	Optical Array Probe PMS model OAP-230Y
*		Operating and Servicing Manual 
*		Serial No : 4557-1283-01
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
#define _XOPEN_SOURCE_EXTENDED 1
#define _HPUX_SOURCE 1

#define NB_CLASSE 30

#include <stdio.h>
#include <string.h>
#include <math.h>
#include "struct_oper.h"

float *
oap230Y_conc_tab (unsigned long ndata,
		  const float *cnt,
		  const float *vp,
		  float fr,
		  float ndiode,
		  float res,
		  float coef_dof,
		  float arm_d,
		  const float fact_dia[],
		  float *conc)
{
  unsigned long i;
  long j, k;

  int icl;

  float sv, dia;
  float nd;
  float esw[NB_CLASSE], dof[NB_CLASSE];
  static float SA[NB_CLASSE];	/* Sample Area */


  for (j = 0; j < NB_CLASSE; j++)
    {
      icl = (int) fact_dia[j];
      /** calcul du diameter moyen de la classe (mm) **/
      dia = (res * fact_dia[j]) / 1000.;

      /** calcul de esw (effective sample width)(mm) ***/

      nd = (float) icl;		/* nombre de diodes occultees = partie entiere du coef
				   multiplicatif du diametre (n°classe +1) */

      /* Dans le manuel de l'OAP230Y, l'équation suivante (section
       * 5, page 5-1) est écrite SANS référence à la resolution.
       * Il nous semble plus logique de multiplier ce terme par 
       * res/M (resolution/magnification), pour avoir une grandeur
       * physique (ici, des mm). Pour l'OPA230Y, M=1.   */
      /* Cela est confirmé par :
       * - Knollenberg, JAM 1970, eq (3), p 95
       * - Korolev et al, JAOT 1991, eq (11) p 519
       * - NCAR bulletin No 24 (rev 1/89) , eq (A.7)
       * - NASA Technical Paper 2888, April 1989, Appendix C
       */
      esw[j] = (ndiode - nd - 1) * (res/1.0e3);

      /** calcul de la DOF (qui est une distance).
       * Précision nécessaire : la formule est donnée classiquement
       * pour un rayon, et toutes les longeurs, exprimés en micron.
       */
      dia *= 1.0e3;		/* Passage en micron.   */
      dof[j] = (coef_dof * dia * dia) / 4.;
      /* dof est en micron, passons la en mm */
      dof[j] /= 1.0e3;

      /* Limitation de la DOF  à la largeur des bras. */
      if (dof[j] >= arm_d)
	dof[j] = arm_d;

      /* Classiquement, une aire (la Sample Area, en mm2) est le
       * produit de 2 longueurs : la dof et l'effective_sample_width */
      SA[j] = dof[j] * esw[j];
    }


  for (i = 0; i < ndata; i++)
    {
      k = i * NB_CLASSE;

      for (j = 0; j < NB_CLASSE; j++)
	{
	  /*** volume d'echantillonnage (cm3 = mm2*m) ***/
	  sv = SA[j] * (vp[i] / fr);

	  if ((vp[i] < 50.) || (cnt[k] == 0.) || (sv == 0.))
	    conc[k] = 0.;
	  else
	    conc[k] = cnt[k] / sv;

	  k = k + 1;
	}
    }

  return SA;
}

/* fonction d'enrobage */
int
OP_oap230Y_conc_tab (unsigned long Nbval, void *ArgList[], char *DiagExec)
{

  int i, len;
  float *CodRet;

  float fact_dia[NB_CLASSE];

  for (i = 0; i < NB_CLASSE; i++)
    {
      fact_dia[i] = *((float *) ArgList[7 + i]);
    }

  CodRet = oap230Y_conc_tab (Nbval,
			     (float *) ArgList[0],
			     (float *) ArgList[1],
			     *((float *) ArgList[2]),
			     *((float *) ArgList[3]),
			     *((float *) ArgList[4]),
			     *((float *) ArgList[5]),
			     *((float *) ArgList[6]),
			     fact_dia, (float *) ArgList[37]);

  len = sprintf (DiagExec, "Sample Area : [%f", CodRet[0]);
  for (i = 1; i < NB_CLASSE; i++)
    {
      len += sprintf (DiagExec + len, ", %f", CodRet[i]);
    }
  len += sprintf (DiagExec + len, "]");

  return OP_OK;
}

void
ID_oap230Y_conc_tab (oper * optr)
{
  int i;

  strcpy (optr->Nom, "oap230Y_conc_tab");
  optr->Version = "$Revision$";
  optr->Date = "$Date$";
  optr->fctptr = OP_oap230Y_conc_tab;
  optr->NbArg = 38;

  /* cnt */
  optr->Arg_Car[0].direction = DIR_IN;
  optr->Arg_Car[0].categorie = VECTOR;
  optr->Arg_Car[0].typ = ATYC_IF32;
  optr->Arg_Car[0].array_dim = "30";
  optr->Arg_Car[0].type_sample = "any";
  optr->Arg_Car[0].sample = "any";
  optr->Arg_Car[0].unite = "";

  /* vp */
  optr->Arg_Car[1].direction = DIR_IN;
  optr->Arg_Car[1].categorie = VECTOR;
  optr->Arg_Car[1].typ = ATYC_IF32;
  optr->Arg_Car[1].array_dim = "1";
  optr->Arg_Car[1].NbVal = "$Arg1.NbVal";       /*  Autant de Vp que de comptages   */
  optr->Arg_Car[1].type_sample = "any";
  optr->Arg_Car[1].sample = "any";
  optr->Arg_Car[1].unite = "m/s";

  /* fr */
  optr->Arg_Car[2].direction = DIR_IN;
  optr->Arg_Car[2].categorie = COEFFICIENT;
  optr->Arg_Car[2].typ = ATYC_IF32;
  optr->Arg_Car[2].array_dim = "1";
  optr->Arg_Car[2].unite = "Hz";

  /* ndiode */
  optr->Arg_Car[3].direction = DIR_IN;
  optr->Arg_Car[3].categorie = COEFFICIENT;
  optr->Arg_Car[3].typ = ATYC_IF32;
  optr->Arg_Car[3].array_dim = "1";
  optr->Arg_Car[3].type_sample = "any";
  optr->Arg_Car[3].sample = "any";
  optr->Arg_Car[3].unite = "";

  /* res */
  optr->Arg_Car[4].direction = DIR_IN;
  optr->Arg_Car[4].categorie = COEFFICIENT;
  optr->Arg_Car[4].typ = ATYC_IF32;
  optr->Arg_Car[4].array_dim = "1";
  optr->Arg_Car[4].type_sample = NULL;
  optr->Arg_Car[4].sample = NULL;
  optr->Arg_Car[4].unite = "";

  /* coef_dof */
  optr->Arg_Car[5].direction = DIR_IN;
  optr->Arg_Car[5].categorie = COEFFICIENT;
  optr->Arg_Car[5].typ = ATYC_IF32;
  optr->Arg_Car[5].array_dim = "1";
  optr->Arg_Car[5].type_sample = NULL;
  optr->Arg_Car[5].sample = NULL;
  optr->Arg_Car[5].unite = "";

  /* arm_d */
  optr->Arg_Car[6].direction = DIR_IN;
  optr->Arg_Car[6].categorie = COEFFICIENT;
  optr->Arg_Car[6].typ = ATYC_IF32;
  optr->Arg_Car[6].array_dim = "1";
  optr->Arg_Car[6].type_sample = NULL;
  optr->Arg_Car[6].sample = NULL;
  optr->Arg_Car[6].unite = "mm";

  for (i = 0; i < NB_CLASSE; i++)
    {
      optr->Arg_Car[7 + i].direction = DIR_IN;
      optr->Arg_Car[7 + i].categorie = COEFFICIENT;
      optr->Arg_Car[7 + i].typ = ATYC_IF32;
      optr->Arg_Car[7 + i].array_dim = "1";
      optr->Arg_Car[7 + i].type_sample = NULL;
      optr->Arg_Car[7 + i].sample = NULL;
      optr->Arg_Car[7 + i].unite = "";
    }

  optr->Arg_Car[37].direction = DIR_OUT;
  optr->Arg_Car[37].categorie = VECTOR;
  optr->Arg_Car[37].typ = ATYC_IF32;
  optr->Arg_Car[37].array_dim = "$Arg1.array_dim";
  optr->Arg_Car[37].bornes = "$Arg1.bornes";
  optr->Arg_Car[37].unit_bornes = "$Arg1.unit_bornes";
  optr->Arg_Car[37].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[37].ref_time = "$Arg1.ref_time";
  optr->Arg_Car[37].misval = "$Arg1.misval";
  optr->Arg_Car[37].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[37].sample = "$Arg1.sample";
  optr->Arg_Car[37].unite = "cm-3";

}
