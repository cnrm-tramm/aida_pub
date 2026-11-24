/*******************************************************************
* OPERATOR      fssp_ncor_activ.c FUNCTION ANSI-C
*
* PURPOSE       Calcul du nombre total de gouttelettes ayant traversees
*               la DOF corrige des coincidences. 
*
* DESCRIPTION   La methode de correction est celle de NCAR/RAF
*               qui utilise l'activite calculee et un coef correctif.
*
* VERSION       $Revision$
*
* ARGUMENTS	IN 	float 	jcltot		nombre total de comptages (cnt)
*		IN	float 	activity	activite calcule (s)
*		IN	float 	beamfrac 	fraction des particules ayant traversees la 
*                                               DOF qui ont ete dimensionnees
*		IN	float 	coef		coefficient de correction de l'activite
*		IN 	float   fr 		frequency (Hz) 
*
*               OUT     float   ntot_ac  	nombre de particules total corrige 
*						a partir de l'activite (cnt)
*
* REFERENCES	An analysis and comparison of five water droplet measuring instruments.
*		D. Baumgardner 
*		Journal of Climate and Applied Meteorology, Vol 22, 891-910, May 1983
*             
* COPYRIGHT     Meteo-France
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
#include "fssp_eqn.h"

int
fssp_ncor_activ (unsigned long ndata,
		   float *jcltot,
		   float *activity,
		   float *beamfrac,
		   float coef,
		   float fr,
		   float *ntot_ac)
{
  unsigned long i;
  float actfac;

  for (i = 0; i < ndata; i++)
    {
      if ( jcltot[i] < 1 )
         ntot_ac[i] = 0.;
      else
         {
           actfac = 1 - coef * activity[i] * fr;
           ntot_ac[i] = jcltot[i] / ( beamfrac[i] * actfac );
         }
    }

  return 0;
}

/* fonction d'enrobage */

int
OP_fssp_ncor_activ (unsigned long NbVal, void *ArgList[], char *DiagExec)
{
  int CodRet;
  int NCar;

  NCar = sprintf (DiagExec, "fssp_ncor_activ : (%ld echant.) ", NbVal) ;
  if (NCar < 0)
    NCar = 0;
  DiagExec += NCar;

  CodRet = fssp_ncor_activ (NbVal,
		  (float *) ArgList[0],
		  (float *) ArgList[1],
		  (float *) ArgList[2],
		  *((float *) ArgList[3]),
		  *((float *) ArgList[4]),
		  (float *) ArgList[5]);
  switch (CodRet)
    {
    case 0:
      sprintf (DiagExec, "OK.");
      return OP_OK;
    default:
      sprintf (DiagExec, "ERR: Erreur %d", CodRet);
      return OP_FAIL;
    }

}

void
ID_fssp_ncor_activ (oper * optr)
{
  strcpy (optr->Nom, "fssp_ncor_activ");
  optr->Version = "$Revision$";
  optr->Date = "$Date$";
  optr->fctptr = OP_fssp_ncor_activ;
  optr->NbArg = 6;

  optr->Arg_Car[0].direction = DIR_IN;                 /* total count */
  optr->Arg_Car[0].categorie = VECTOR;
  optr->Arg_Car[0].typ = ATYC_IF32;
  optr->Arg_Car[0].array_dim = "1";
  optr->Arg_Car[0].type_sample = "any";
  optr->Arg_Car[0].sample = "any";
  optr->Arg_Car[0].unite = "any";

  optr->Arg_Car[1].direction = DIR_IN;                 /* activity */
  optr->Arg_Car[1].categorie = VECTOR;
  optr->Arg_Car[1].typ = ATYC_IF32;
  optr->Arg_Car[1].array_dim = "1";
  optr->Arg_Car[1].type_sample = "any";
  optr->Arg_Car[1].sample = "any";
  optr->Arg_Car[1].unite = "second";

  optr->Arg_Car[2].direction = DIR_IN;                 /* beam fraction */
  optr->Arg_Car[2].categorie = VECTOR;
  optr->Arg_Car[2].typ = ATYC_IF32;
  optr->Arg_Car[2].array_dim = "1";
  optr->Arg_Car[2].type_sample = "any";
  optr->Arg_Car[2].sample = "any";
  optr->Arg_Car[2].unite = "none";

  optr->Arg_Car[3].direction = DIR_IN;                 /* coef activity */
  optr->Arg_Car[3].categorie = COEFFICIENT;
  optr->Arg_Car[3].typ = ATYC_IF32;
  optr->Arg_Car[3].array_dim = "1";
  optr->Arg_Car[3].type_sample = NULL;
  optr->Arg_Car[3].sample = NULL;
  optr->Arg_Car[3].unite = "none";

  optr->Arg_Car[4].direction = DIR_IN;                 /* freq */
  optr->Arg_Car[4].categorie = COEFFICIENT;
  optr->Arg_Car[4].typ = ATYC_IF32;
  optr->Arg_Car[4].array_dim = "1";
  optr->Arg_Car[4].type_sample = NULL;
  optr->Arg_Car[4].sample = NULL;
  optr->Arg_Car[4].unite = "Hz";

  optr->Arg_Car[5].direction = DIR_OUT;              /* total count corr */
  optr->Arg_Car[5].categorie = VECTOR;
  optr->Arg_Car[5].typ = ATYC_IF32;
  optr->Arg_Car[5].array_dim = "1";
  optr->Arg_Car[5].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[5].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[5].sample = "$Arg1.sample";
  optr->Arg_Car[5].ref_time = "$Arg1.ref_time";
  optr->Arg_Car[5].unite = "$Arg1.unit";

}
