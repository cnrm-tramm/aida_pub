/*********************************************************
* OPERATOR 	Qualite_vent_relatif.c FUNCTION ANSI-C
*
* PURPOSE       Set of tests to determine the wind measurement quality
*		on plane.
*
*	        Ensemble de tests destines a determiner la qualite
*               de la mesure du vent sur avion.
*		
*		Valeurs des tests et des flags:
*               Si dp_pit > 8
*                       Test 1
*                               si |dp_pit - dp_rad| / dp_pit > 0.03
*				   => flag_1 = 0001 (alerte)
*                               si |dp_pit - dp_rad| / dp_pit > 0.07
*				   => flag_1 = 0002 (detection)
*                       Test 2
*				si |incid_rdm - incid_gir| >3
*				   => flag_2 = 0010
*                       Test 3
*				si dpi / dp_pit < -0.51 || dpi / dp_pit > 0.48
*                                  => flag_3 = 0100
*                       Test 4
*				si dpj / dp_pit > 0.4
*				   => flag_4 = 1000
*
*		flag_final = flag_1 + flag_2 + flag_3 + flag_4
*
* VERSION       $Revision$
*
* ARGUMENTS 	IN	float	dp_pit
*		IN 	float	dp_rad
*		IN 	float 	incid_rdm
*		IN	float 	incid_gir
*		IN 	float 	dpi
*		IN 	float 	dpj	
*
*		OUT 	int 	qualit_vent
*
* ENTRY		NONE
*
* SUBPROGRAMS 	NONE
* 
* REFERENCES	
*
* COPYRIGHT 	Meteo-France
*		Centre National de Recherches Meteorologiques
*		GMEI/TRAMM
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

long
Qualite_vent_relatif (unsigned long Nloop,
		      const float *dp_pit,
		      const float *dp_rad,
		      const float *incid_rdm,
		      const float *incid_gir,
		      const float *dpi,
		      const float *dpj,
                      int *qualit_vent,
                      long *Tab_diagno)
{
  unsigned long i;
  float ecart_rel_dp;
  long Nb_dp_rad, Nb_dpi, Nb_dpj, Nb_incid;
  int crit_dp_rad, crit_incid, crit_dpi, crit_dpj;
  const float seuil_dp = 8.0;

  Nb_dp_rad = 0;
  Nb_dpi = 0;
  Nb_dpj = 0;
  Nb_incid = 0;
  for (i = 0; i < Nloop; i++)
    {
      crit_dp_rad = 0;
      crit_incid = 0;
      crit_dpi = 0;
      crit_dpj = 0;
      if (dp_pit[i] > seuil_dp)
	{
	  ecart_rel_dp = fabs (dp_pit[i] - dp_rad[i]) / dp_pit[i];
	    if (ecart_rel_dp > 0.07)
	    {
	      crit_dp_rad = 2;
	      Nb_dp_rad++;
	    }
	  else if (ecart_rel_dp > 0.03)
	    {
	      crit_dp_rad = 1;
	      Nb_dp_rad++;
	    }
	  if (fabs (incid_rdm[i] - incid_gir[i]) > 3)
	    {
	      crit_incid = 1;
	      Nb_incid++;
	    }
	  if ((dpi[i] / dp_pit[i] < -0.51) || (dpi[i] / dp_pit[i] > 0.48))
	    {
	      crit_dpi = 1;
	      Nb_dpi++;
	    }
	  if (fabs (dpj[i]) / dp_pit[i] > 0.4)
	    {
	      crit_dpj = 1;
	      Nb_dpj++;
	    }
	}
      qualit_vent[i] =
	crit_dp_rad + 10 * crit_incid + 100 * crit_dpi + 1000 * crit_dpj;
    }

  Tab_diagno[0] = Nb_dp_rad;
  Tab_diagno[1] = Nb_incid;
  Tab_diagno[2] = Nb_dpi;
  Tab_diagno[3] = Nb_dpj;

  return i;
}

/* fonction d'enrobage */

int
OP_Qualite_vent_relatif (unsigned long Nbval, void *ArgList[], char *DiagExec)
{
  long CodRet;
  long toto[4];

  CodRet = Qualite_vent_relatif (Nbval,
				 (float *) ArgList[0],
				 (float *) ArgList[1],
				 (float *) ArgList[2],
				 (float *) ArgList[3],
				 (float *) ArgList[4],
				 (float *) ArgList[5],
				 (int *) ArgList[6],
                                 toto);
  sprintf (DiagExec,
	   "Nb tests positifs : dprad = %ld, incid = %ld, dpi = %ld, dpj = %ld\n",
	   toto[0], toto[1], toto[2], toto[3]);

  return OP_OK;
}

void
ID_Qualite_vent_relatif (oper * optr)
{
  strcpy (optr->Nom, "Qualite_vent_relatif");
  optr->Version = "$Revision$";
  optr->Date = "$Date$";
  optr->fctptr = OP_Qualite_vent_relatif;
  optr->NbArg = 7;

  /* dp_pit */
  optr->Arg_Car[0].direction = DIR_IN;
  optr->Arg_Car[0].categorie = VECTOR;
  optr->Arg_Car[0].typ = ATYC_IF32;
  optr->Arg_Car[0].array_dim = "1";
  optr->Arg_Car[0].type_sample = "any";
  optr->Arg_Car[0].sample = "any";
  optr->Arg_Car[0].unite = "unknown";

  /*  dp_rad */
  optr->Arg_Car[1].direction = DIR_IN;
  optr->Arg_Car[1].categorie = VECTOR;
  optr->Arg_Car[1].typ = ATYC_IF32;
  optr->Arg_Car[1].array_dim = "1";
  optr->Arg_Car[1].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[1].type_sample = "any";
  optr->Arg_Car[1].sample = "any";
  optr->Arg_Car[1].unite = "unknown";

  /* incid_rdm */
  optr->Arg_Car[2].direction = DIR_IN;
  optr->Arg_Car[2].categorie = VECTOR;
  optr->Arg_Car[2].typ = ATYC_IF32;
  optr->Arg_Car[2].array_dim = "1";
  optr->Arg_Car[2].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[2].type_sample = "any";
  optr->Arg_Car[2].sample = "any";
  optr->Arg_Car[2].unite = "unknown";

  /* incid_gir */
  optr->Arg_Car[3].direction = DIR_IN;
  optr->Arg_Car[3].categorie = VECTOR;
  optr->Arg_Car[3].typ = ATYC_IF32;
  optr->Arg_Car[3].array_dim = "1";
  optr->Arg_Car[3].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[3].type_sample = "any";
  optr->Arg_Car[3].sample = "any";
  optr->Arg_Car[3].unite = "unknown";

  /* dpi */
  optr->Arg_Car[4].direction = DIR_IN;
  optr->Arg_Car[4].categorie = VECTOR;
  optr->Arg_Car[4].typ = ATYC_IF32;
  optr->Arg_Car[4].array_dim = "1";
  optr->Arg_Car[4].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[4].type_sample = "any";
  optr->Arg_Car[4].sample = "any";
  optr->Arg_Car[4].unite = "unknown";

  /* dpj */
  optr->Arg_Car[5].direction = DIR_IN;
  optr->Arg_Car[5].categorie = VECTOR;
  optr->Arg_Car[5].typ = ATYC_IF32;
  optr->Arg_Car[5].array_dim = "1";
  optr->Arg_Car[5].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[5].type_sample = "any";
  optr->Arg_Car[5].sample = "any";
  optr->Arg_Car[5].unite = "unknown";

  optr->Arg_Car[6].direction = DIR_OUT;
  optr->Arg_Car[6].categorie = VECTOR;
  optr->Arg_Car[6].typ = ATYC_I32;
  optr->Arg_Car[6].array_dim = "1";
  optr->Arg_Car[6].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[6].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[6].sample = "$Arg1.sample";
  optr->Arg_Car[6].ref_time = " $Arg1.ref_time";
  optr->Arg_Car[6].unite = "bits";
  optr->Arg_Car[6].famille = " \"controle\" ";
  optr->Arg_Car[6].misval = "-9";

}
