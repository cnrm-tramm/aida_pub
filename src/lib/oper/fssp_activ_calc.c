/*******************************************************************
* OPERATOR      fssp_activ_calc.c FUNCTION ANSI-C
*
* PURPOSE       Calcul de l'activite a partir des voies sup
*
* DESCRIPTION   Le temps de transit d'un particule 
*		est calcule a partir de la duree   
*	        d'impulsion moyenne.	
*
* VERSION       1.0
*
*		IN 	float 	strobe		nombre de particules dans la DOF (comptes par période d'échantillonnage)
*		IN	float 	fastreset	nombre de particules hors de la DOF (comptes par période d'échantillonnage)
*		IN	float 	TAS		vitesse propre (m/s)
*		IN 	float   tau1		delai long (seconde) 
*		IN	float   tau2	     	delai court (seconde)
*
*               OUT     float   activity        activite de la sonde (fraction de temps)
*
* ENTRY         NONE
*
* SUBPROGRAMS   NONE
*
* REFERENCES    Bulletin NCAR/RAF n°24
*               Airborne Measurements for Cloud Microphysics
*               by Darrel Baumgardner.
*             
* COPYRIGHT     Meteo-France
*              
*******************************************************************/

#define _POSIX_SOURCE 1
#define _XOPEN_SOURCE 600
#define _HPUX_SOURCE 1
#define _XOPEN_SOURCE_EXTENDED 1

#include <stdio.h>
#include <string.h>
#include <math.h>
#include "struct_oper.h"

int
fssp_activ_calc (unsigned long ndata,
		 float *strobe,
		 float *fastreset,
		 float *TAS,
                 float tau1,
                 float tau2,
                 float BeamDiam,
                 float *activity)
{
  unsigned long i;
  float transitTime;

  /* on verifie qd meme que les delais sont dans le bon ordre */
  if (tau1 < tau2)
    {
      return -1;
    }

  for (i = 0; i < ndata; i++)
    {
      /* les delais doivent tenir compte du temps de transit moyen */
      if (TAS[i] <= 0.)
	{
	  activity[i] = 0;
	  continue;
	}

      transitTime = BeamDiam / TAS[i];

      activity[i] = strobe[i] * (tau1 + transitTime)
	+ fastreset[i] * (tau2 + transitTime);

    }

  return 0;
}

/* fonction d'enrobage */

int
OP_fssp_activ_calc (unsigned long Nbval, void *ArgList[], char *DiagExec)
{
  int CodRet;
  int NCar;
  const float BeamDiam = 0.148e-3;

  NCar = sprintf (DiagExec,
		  "fssp_activ_calc (%ld, tau_1=%g, tau_2=%g, BeamDiam=%g)",
		  Nbval, *((float *) ArgList[3]), *((float *) ArgList[4]),
                  BeamDiam);
  if (NCar < 0)
    NCar = 0;
  DiagExec += NCar;

  CodRet = fssp_activ_calc (Nbval,
			    (float *) ArgList[0],
			    (float *) ArgList[1],
			    (float *) ArgList[2],
			    *((float *) ArgList[3]),
			    *((float *) ArgList[4]),
			    BeamDiam,
                            (float *) ArgList[5]);

  switch (CodRet)
    {
    case 0:
      sprintf (DiagExec, "OK.");
      return OP_OK;
    case -1:
      sprintf (DiagExec, "ERR: tau1 < tau2 !!!");
      return OP_FAIL;
    default:
      sprintf (DiagExec, "ERR: Erreur %d", CodRet);
      return OP_FAIL;
    }
}

void
ID_fssp_activ_calc (oper * optr)
{
  strcpy (optr->Nom, "fssp_activ_calc");
  optr->Version = "Revision:1.0";
  optr->Date = "$Date: 2010-12-02 10:25:30 $";
  optr->fctptr = OP_fssp_activ_calc;
  optr->NbArg = 6;

  /* strobe */
  optr->Arg_Car[0].direction = DIR_IN;
  optr->Arg_Car[0].categorie = VECTOR;
  optr->Arg_Car[0].typ = ATYC_IF32;
  optr->Arg_Car[0].array_dim = "1";
  optr->Arg_Car[0].type_sample = "any";
  optr->Arg_Car[0].sample = "any";
  optr->Arg_Car[0].unite = "any";

  /* fastreset */
  optr->Arg_Car[1].direction = DIR_IN;
  optr->Arg_Car[1].categorie = VECTOR;
  optr->Arg_Car[1].typ = ATYC_IF32;
  optr->Arg_Car[1].array_dim = "1";
  optr->Arg_Car[1].type_sample = "any";
  optr->Arg_Car[1].sample = "any";
  optr->Arg_Car[1].unite = "any";

  /* TAS */
  optr->Arg_Car[2].direction = DIR_IN;
  optr->Arg_Car[2].categorie = VECTOR;
  optr->Arg_Car[2].typ = ATYC_IF32;
  optr->Arg_Car[2].array_dim = "1";
  optr->Arg_Car[2].type_sample = "any";
  optr->Arg_Car[2].sample = "any";
  optr->Arg_Car[2].unite = "m/s";

  /* tau1 */
  optr->Arg_Car[3].direction = DIR_IN;
  optr->Arg_Car[3].categorie = COEFFICIENT;
  optr->Arg_Car[3].typ = ATYC_IF32;
  optr->Arg_Car[3].array_dim = "1";
  optr->Arg_Car[3].unite = "second";

  /* tau2 */
  optr->Arg_Car[4].direction = DIR_IN;
  optr->Arg_Car[4].categorie = COEFFICIENT;
  optr->Arg_Car[4].typ = ATYC_IF32;
  optr->Arg_Car[4].array_dim = "1";
  optr->Arg_Car[4].unite = "second";

  /* activity */
  optr->Arg_Car[5].direction = DIR_OUT;
  optr->Arg_Car[5].categorie = VECTOR;
  optr->Arg_Car[5].typ = ATYC_IF32;
  optr->Arg_Car[5].array_dim = "1";
  optr->Arg_Car[5].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[5].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[5].sample = "$Arg1.sample";
  optr->Arg_Car[5].ref_time = "$Arg1.ref_time";
  optr->Arg_Car[5].unite = "second/second";
  optr->Arg_Car[5].famille = "\"microphysique\" ";
  optr->Arg_Car[5].name = "Activité calculee";
  optr->Arg_Car[5].en_name = "Calculated Activity Fraction";
}
