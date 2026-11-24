/*************************************************
* OPERATOR 	oap230Y_conc.c 	FUNCTION ANSI-C
*
* PURPOSE	calcul de la concentration pour une classe
*		de mesure d'un OAP230Y 
*
* ARGUMENTS 	IN 	float	jcl 		classe 
*		IN	float 	vp 		vitesse propre (m/s)
*		IN	float 	fr		frequence d'echantillonnage (Hz)
*		IN	float	ndiode		nombre de diodes total
*		IN	float 	res		resolution (microns)
*		IN	float 	coef_dof        coef pour calcul de la DOF	
*		IN	float	fact_dia	facteur multiplicatif diameter moyen de la classe
*		IN 	float 	arm_d		distance entre les bras de mesure (mm)
*
*		OUT 	float 	conc		concentration dans la classe "jcl" (cm-3)
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

#include <stdio.h>
#include <string.h>
#include <math.h>
#include "struct_oper.h"

int
oap230Y_conc (unsigned long ndata,
	      float *jcl,
	      float *vp,
	      float fr,
	      float ndiode,
	      float res,
	      float coef_dof, 
	      float fact_dia, 
	      float arm_d, 
	      float *conc)
{
  long i;

  int icl;

  float sv, esw, dof, dia;
  float nd;

  /** calcul du diametre moyen de la classe (mm) **/

  icl = (int) fact_dia;
  dia = (res * fact_dia) / 1000.;

  /** calcul de esw (effective sample width)(mm) ***/

  nd = (float) icl;		/* nombre de diodes occultees = partie entiere
				   du coef multiplicatif du diametre (n°classe +1) */

  esw = (ndiode - nd - 1);

  /** calcul de la DOF **
   * Précision nécessaire : la formule est donnée classiquement
   * pour un rayon, et toutes les longeurs, exprimés en micron.
   * Ici, avec dia en mm, le résultat (dof) est 10^6 inférieur,
   * donc en mètres...  */

  dof = coef_dof * (dia * dia / 4. );
  /* Dans les versions précédentes, il n'y a avait pas de conversion
   * d'unité d'arm, donc on n'appliquait jamais la limitation de 
   * DOF à arm_d */
  arm_d /= 1.0e6;		/* passage de mm à m */
  if (dof >= arm_d)
    dof = arm_d;

  for (i = 0; i < ndata; i++)
    {
      /*** volume d'echantillonnage : litre = m * mm *m  ***/
      sv = dof * esw * (vp[i] / fr);

      if ((vp[i] < 50.) || (jcl[i] == 0.) || (sv == 0.))
	conc[i] = 0.;
      else
	/*** concentration (l^-1) ***/
	conc[i] = jcl[i] / sv;
    }

  return 0;
}

/* fonction d'enrobage */
int
OP_oap230Y_conc (unsigned long Nbval, void *ArgList[], char *DiagExec)
{
  int CodRet = oap230Y_conc (Nbval,
			     (float *) ArgList[0],
			     (float *) ArgList[1],
			     *((float *) ArgList[2]),
			     *((float *) ArgList[3]),
			     *((float *) ArgList[4]),
			     *((float *) ArgList[5]),
			     *((float *) ArgList[6]),
			     *((float *) ArgList[7]),
			     (float *) ArgList[8]);

  return OP_OK;
}

void
ID_oap230Y_conc (oper * optr)
{
  strcpy (optr->Nom, "oap230Y_conc");
  optr->Version = "$Revision$";
  optr->Date = "$Date$";
  optr->fctptr = OP_oap230Y_conc;
  optr->NbArg = 9;

  /* jcl */
  optr->Arg_Car[0].direction = DIR_IN;
  optr->Arg_Car[0].categorie = VECTOR;
  optr->Arg_Car[0].typ = ATYC_IF32;
  optr->Arg_Car[0].array_dim = "1";
  optr->Arg_Car[0].type_sample = "any";
  optr->Arg_Car[0].sample = "any";
  optr->Arg_Car[0].unite = "";

  /* vp  */
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

  optr->Arg_Car[8].direction = DIR_OUT;
  optr->Arg_Car[8].categorie = VECTOR;
  optr->Arg_Car[8].typ = ATYC_IF32;
  optr->Arg_Car[8].array_dim = "1";
  optr->Arg_Car[8].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[8].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[8].ref_time = "$Arg1.ref_time";
  optr->Arg_Car[8].sample = "$Arg1.sample";
  optr->Arg_Car[8].unite = "l-1";
  optr->Arg_Car[8].famille = "\"microphysique\"";
  optr->Arg_Car[8].name = "Drop concentration";

}
