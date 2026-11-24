/*************************************************
* OPERATOR 	conc_tab_sa_const.c 	FUNCTION ANSI-C
*
* PURPOSE	Calcul de la concentration à partir des comptages
*		pour un instrument sur lequel on peut appliquer la
*		formule : Volume_ech = SA * Vp /freq, avec SA ne
*		dépendant que de la classe (indépendant du temps, de Vp, ...).
*
* ARGUMENTS 	IN 	float	cnt 		tableau des comptages.
*		IN	int 	nb_classes 	nombre de classes du tableau.
*		IN	float 	vp 		vitesse propre (m/s)
*		IN	float 	fr		frequence d'echantillonnage (Hz)
*		IN	float	sa[nb_classes]	Tableau des "Sample Area" (mm2).
*
*		OUT 	float 	conc		tableau des concentration (cm-3)
*		
* ENTRY		NONE
*
* SUBPROGRAMS 	NONE
*
* REFERENCE	
*
* COPYRIGHT	Meteo-France
*		Centre National de Recherches Meteorologiques
*		GMEI/ TRAMM
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
conc_tab_sa_const (unsigned long ndata,
		   const float *cnt,
		   int nb_classes,
		   const float *vp, float fr, const float sa[], float *conc)
{
  unsigned long i;
  long j, k;

  float sv;

  for (i = 0; i < ndata; i++)
    {
      k = i * nb_classes;
      for (j = 0; j < nb_classes; j++)
	{
	  /*** volume d'echantillonnage (cm3 = mm2*m) ***/
	  sv = sa[j] * (vp[i] / fr);

	  if ((vp[i] < 50.) || (cnt[k] == 0.) || (sv == 0.))
	    {
	      conc[k] = 0.;
	    }
	  else
	    {
	      conc[k] = cnt[k] / sv;
	    }

	  k = k + 1;
	}
    }

  return 0;
}

/* fonction d'enrobage */
int
OP_conc_tab_sa_const (unsigned long Nbval, void *ArgList[], char *DiagExec)
{
  int CodRet;

  *DiagExec = 0;
  CodRet = conc_tab_sa_const (Nbval,
			      (float *) ArgList[0],
			      *((int *) ArgList[1]),
			      (float *) ArgList[2],
			      *((float *) ArgList[3]),
			      (float *) ArgList[4],
                              (float *) ArgList[5]);

  return OP_OK;
}

void
ID_conc_tab_sa_const (oper * optr)
{
  int i;

  strcpy (optr->Nom, "conc_tab_sa_const");
  optr->Version = "$Revision$";
  optr->Date = "$Date$";
  optr->fctptr = OP_conc_tab_sa_const;
  optr->NbArg = 6;

  i = 0;
  /* cnt */
  optr->Arg_Car[i].direction = DIR_IN;
  optr->Arg_Car[i].categorie = VECTOR;
  optr->Arg_Car[i].typ = ATYC_IF32;
  optr->Arg_Car[i].array_dim = "any";
  optr->Arg_Car[i].type_sample = "any";
  optr->Arg_Car[i].sample = "any";
  optr->Arg_Car[i].unite = "";
  i++;

  /* nb_classes */
  optr->Arg_Car[i].direction = DIR_IN;
  optr->Arg_Car[i].categorie = COEFFICIENT;
  optr->Arg_Car[i].typ = ATYC_I32;
  optr->Arg_Car[i].array_dim = "1";
  optr->Arg_Car[i].type_sample = "any";
  optr->Arg_Car[i].sample = "any";
  optr->Arg_Car[i].unite = "";
  i++;

  /* vp */
  optr->Arg_Car[i].direction = DIR_IN;
  optr->Arg_Car[i].categorie = VECTOR;
  optr->Arg_Car[i].typ = ATYC_IF32;
  optr->Arg_Car[i].array_dim = "1";
  optr->Arg_Car[i].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[i].type_sample = "any";
  optr->Arg_Car[i].sample = "any";
  optr->Arg_Car[i].unite = "m/s";
  i++;

  /* fr */
  optr->Arg_Car[i].direction = DIR_IN;
  optr->Arg_Car[i].categorie = COEFFICIENT;
  optr->Arg_Car[i].typ = ATYC_IF32;
  optr->Arg_Car[i].array_dim = "1";
  optr->Arg_Car[i].unite = "Hz";
  i++;

  /* SA[] */
  optr->Arg_Car[i].direction = DIR_IN;
  optr->Arg_Car[i].categorie = COEFFICIENT;
  optr->Arg_Car[i].typ = ATYC_IF32;
  optr->Arg_Car[i].array_dim = "any";
  optr->Arg_Car[i].type_sample = "any";
  optr->Arg_Car[i].sample = "any";
  optr->Arg_Car[i].unite = "mm2";
  i++;

  /* Conc_tab */
  optr->Arg_Car[i].direction = DIR_OUT;
  optr->Arg_Car[i].categorie = VECTOR;
  optr->Arg_Car[i].typ = ATYC_IF32;
  optr->Arg_Car[i].array_dim = "$Arg1.array_dim";
  optr->Arg_Car[i].bornes = "$Arg1.bornes";
  optr->Arg_Car[i].unit_bornes = "$Arg1.unit_bornes";
  optr->Arg_Car[i].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[i].ref_time = "$Arg1.ref_time";
  optr->Arg_Car[i].misval = "$Arg1.misval";
  optr->Arg_Car[i].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[i].sample = "$Arg1.sample";
  optr->Arg_Car[i].unite = "cm-3";
  optr->Arg_Car[i].famille = "\"microphysique\"";
  optr->Arg_Car[i].name = "Concentration";
  optr->Arg_Car[i].en_name = "Concentration";
  i++;

}
