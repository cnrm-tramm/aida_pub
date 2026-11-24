/*******************************************************************
* OPERATOR      correc_time_cal.c FUNCTION ANSI-C
*
* PURPOSE       Correction des sauts du temps
*
* DESCRIPTION   Cet operateur corrige les sauts 
*		rencontres dans le temps pendant 
*		la campagne ECRIN96 (vols me9639, me9640,
*		me9641). 
*		Ces sauts sont toujours positifs et 
*		se produisent sur une seule valeur.
*
* VERSION       1.0
*
*               IN      double  time		temps brut
*               IN      float   fr              frequence d'acquisition
*
*		OUT	double  time_cor 	temps corrige des sauts
*
* ENTRY         NONE
*
* SUBPROGRAMS   NONE
*
* REFERENCES     
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
#include "struct_oper.h"

int
correc_time_cal (unsigned long ndata,
		 double *time,
		 float fr,
		 double *time_cor)

{
  unsigned long i, nbsaut;

  double dfr, eps, dtn;
  double time0, ecartm;
  /* double tdeb, tfin; */

  dfr = (double) fr;
  dtn = 1. / dfr;

  eps = 6.e-4;

  /*fprintf (stdout, "dtn : %10.9f\n", dtn);
  */

  nbsaut = 0;
  time_cor[0] = time[0];
  time_cor[ndata - 1] = time[ndata - 1];

  for (i = 1; i < ndata - 1; i++)
    {
      time0 = (time[i + 1] + time[i - 1]) / 2.;
      ecartm = (time[i + 1] - time[i - 1]) / 2.;

      time_cor[i] = time[i];

      if (( i > 8745) && (i < 8770))
        {
         fprintf(stderr, " %ld , time0 : %g, ecartm : %g, time[i] : %g \n",
         i, time0, ecartm, time[i] );
        }
           

      if ((ecartm <= (dtn + eps)) &&
	  (ecartm >= (dtn - eps))) 
	{
/** time[i+1] et time[i-1] ont l'air justes **/
	  if ((time[i] > (time0 + 2. * eps)) ||
	      (time[i] < (time0 - 2. * eps)))
	    {
/** time[i] est une valeur fausse **/

	      time_cor[i] = time0;
	      nbsaut = nbsaut + 1;
	    }
	}
    }

  fprintf(stderr, "Nombre de sauts trouves et corriges : %lu\n", nbsaut);

  return (0);
}

/* fonction d'enrobage */

int
OP_correc_time_cal (unsigned long Nbval, void *ArgList[], char *DiagExec)
{
  int CodRet = correc_time_cal (Nbval,
				(double *) ArgList[0],
				*((float *) ArgList[1]),
				(double *) ArgList[2]);
  return OP_OK;
}

void
ID_correc_time_cal (oper * optr)
{
  strcpy (optr->Nom, "correc_time_cal");
  optr->Version = "1.0";
  optr->Date = "01/13/96";
  optr->fctptr = OP_correc_time_cal;
  optr->NbArg = 3;

  optr->Arg_Car[0].direction = DIR_IN;
  optr->Arg_Car[0].categorie = VECTOR;
  optr->Arg_Car[0].typ = ATYC_IF64;
  optr->Arg_Car[0].array_dim = "1";
  optr->Arg_Car[0].type_sample = "any";
  optr->Arg_Car[0].sample = "any";
  optr->Arg_Car[0].unite = "second";

  optr->Arg_Car[1].direction = DIR_IN;
  optr->Arg_Car[1].categorie = COEFFICIENT;
  optr->Arg_Car[1].typ = ATYC_IF32;
  optr->Arg_Car[1].array_dim = "1";
  optr->Arg_Car[1].type_sample = "any";
  optr->Arg_Car[1].sample = "any";
  optr->Arg_Car[1].unite = "";

  optr->Arg_Car[2].direction = DIR_OUT;
  optr->Arg_Car[2].categorie = VECTOR;
  optr->Arg_Car[2].typ = ATYC_IF64;
  optr->Arg_Car[2].array_dim = "1";
  optr->Arg_Car[2].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[2].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[2].sample = "$Arg1.sample";
  optr->Arg_Car[2].ref_time = "$Arg1.ref_time";
  optr->Arg_Car[2].unite = "second";
}
