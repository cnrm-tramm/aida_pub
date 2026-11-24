/*******************************************************************
* OPERATOR      fssp_activ.c FUNCTION ANSI-C
*
* PURPOSE       Calcul de l'activite du FSSP en second  
*
* DESCRIPTION   On multiplie l'activite brute par un  
*		coefficient de calibration et par la
*		frequence d'acquisition des donnees.
*
* VERSION       $Revision$
*
*               IN      float   act_brt 	activite brute 
*               IN      float   coef_act	coef. d'activite
*               IN      float   fr 		frequence d'acquisition
*
*               OUT     float   act_s		activite (seconds)
*
* ENTRY         NONE
*
* SUBPROGRAMS   NONE
*
* REFERENCES   	Traitement Jean-Louis Brenguier  
*
*             
* COPYRIGHT     Meteo-France
*               Centre National de Recherches Meteorologiques
*               GMEI/MMA
*               42, av. G. Coriolis
*               31057   TOULOUSE cedex
*              
*******************************************************************/

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
fssp_activ (unsigned long ndata, float *act_brt,	/* Mesure enregistree */
	    float coef_act, float fr, float *act_s)
{
  unsigned long i;

/************************************************
* L'activitee est obtenue en comptant des pulsations 
* d'horloge. 
* Dans la sonde le nombre de pulsations est divise
* par 2^x, donc le coefficient est egal a 
* 2^x/ (frequence de l'horloge).
*************************************************/
  if (coef_act <= 0)
    return -1;

  if (fr <= 0)
    return -2;

  for (i = 0; i < ndata; i++)
    {
      act_s[i] = coef_act * fr * act_brt[i];
    }

  return 0;
}

/* fonction d'enrobage */

int
OP_fssp_activ (unsigned long Nbval, void *ArgList[], char *DiagExec)
{
  int CodRet = fssp_activ (Nbval,
			   (float *) ArgList[0],
			   *((float *) ArgList[1]),
			   *((float *) ArgList[2]),
			   (float *) ArgList[3]);

  switch (CodRet)
    {
    case 0:
      return OP_OK;
      break;
    case -1:
      sprintf (DiagExec, "ERR: coef d'activite <= 0 !");
      break;
    case -2:
      sprintf (DiagExec, "ERR: Freq Ech <= 0 !");
      break;
    default:
      sprintf (DiagExec, "ERR: Erreur %d.", CodRet);
    }
  return OP_FAIL;

}

void
ID_fssp_activ (oper * optr)
{
  strcpy (optr->Nom, "fssp_activ");
  optr->Version = "$Revision$";
  optr->Date = "$Date$";
  optr->fctptr = OP_fssp_activ;
  optr->NbArg = 4;

  /* act_brt */
  optr->Arg_Car[0].direction = DIR_IN;
  optr->Arg_Car[0].categorie = VECTOR;
  optr->Arg_Car[0].typ = ATYC_IF32;
  optr->Arg_Car[0].array_dim = "1";
  optr->Arg_Car[0].type_sample = "any";
  optr->Arg_Car[0].sample = "any";
  optr->Arg_Car[0].unite = "";

  optr->Arg_Car[1].direction = DIR_IN;
  optr->Arg_Car[1].categorie = COEFFICIENT;
  optr->Arg_Car[1].typ = ATYC_IF32;
  optr->Arg_Car[1].array_dim = "1";
  optr->Arg_Car[1].type_sample = "any";
  optr->Arg_Car[1].sample = "any";
  optr->Arg_Car[1].unite = "";

  /* fr */
  optr->Arg_Car[2].direction = DIR_IN;
  optr->Arg_Car[2].categorie = COEFFICIENT;
  optr->Arg_Car[2].typ = ATYC_IF32;
  optr->Arg_Car[2].array_dim = "1";
  optr->Arg_Car[2].type_sample = NULL;
  optr->Arg_Car[2].sample = NULL;
  optr->Arg_Car[2].unite = "Hz";

  /* act_s */
  optr->Arg_Car[3].direction = DIR_OUT;
  optr->Arg_Car[3].categorie = VECTOR;
  optr->Arg_Car[3].typ = ATYC_IF32;
  optr->Arg_Car[3].array_dim = "1";
  optr->Arg_Car[3].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[3].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[3].sample = "$Arg1.sample";
  optr->Arg_Car[3].ref_time = "$Arg1.ref_time";
  optr->Arg_Car[3].unite = "second";
  optr->Arg_Car[3].name = "\"Activite\"";
  optr->Arg_Car[3].en_name = "\"Activity\"";
}
