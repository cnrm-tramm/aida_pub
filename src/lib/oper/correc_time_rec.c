/*******************************************************************
* OPERATOR      correc_time_rec.c FUNCTION ANSI-C
*
* PURPOSE       Correction des sauts du temps
*
* DESCRIPTION   Cet operateur corrige les sauts 
*		rencontres dans le temps, en
*		general. 
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
correc_time_rec (unsigned long ndata,
		 double *time,
		 float fr,
		 double *time_cor)

{
  int j, n, nmax, correc;

  long i;

  double dfr, dt, eps, dtn;
  double ecartm;

  dfr = (double) fr;
  dtn = 1. / dfr;

/** difference du temps par rapport a 1/fr **/
  eps = 6.e-4;

/** nombre max de valeurs sur lesquelles on peut avoir des sauts **/
  nmax = 20;

/*** on teste si time[0] est juste ***/

  time_cor[0] = time[0];

  if ((time[0] < 0)
      || (time[0] > 86400))
    {
      /* Cas où le 1er elem. du temps est faux : on ne sait pas corriger ! */
      for (i = 1; i < ndata; i++)
	{
	  time_cor[i] = 0;
	}
      return (-1);
    }

  i = 1;

  while (i < ndata)
    {

      dt = time[i] - time[i - 1];
      if ((dt >= dtn - eps) &&
	  (dt <= dtn + eps))
	{
/*** time[i] est juste ***/
	  time_cor[i] = time[i];
	  i = i + 1;
	}
      else
	{
	/*** time[i] est faux 
        on cherche time[i+n] juste ***/
	  correc = 1;
	  n = 0;
	  do
	    {
	      n = n + 1;
	      ecartm = (time[i + n] - time[i - 1]) / ((double) (n + 1));
	      /*
	         fprintf(stderr, "i : %d ecartm : %g \n", i, ecartm);
	       */
	      if (n >= nmax)
		{
	      /** sauts sur plus de "nmax" valeurs 
              on ne corrige pas **/
		  correc = 0;
		  break;
		}
	    }
	  while (((ecartm > dtn + eps) ||
		  (ecartm < dtn - eps)) &&
		 (i + n < ndata) &&
		 (n <= nmax));

	  if (correc == 1)
	    {
	      for (j = 0; j < n; j++)
		{
		  time_cor[i + j] = ecartm * ((double) (j + 1)) + time[i - 1];
		}
	    }
	  else
	    {
	      for (j = 0; j < n; j++)
		{
		  time_cor[i + j] = time[i + j];
		}
	    }

	  time_cor[i + n] = time[i + n];
	  i = i + n + 1;
	}
    }


  return (0);
}

/* fonction d'enrobage */

int
OP_correc_time_rec (unsigned long Nbval, void *ArgList[], char *DiagExec)
{
  int CodRet = correc_time_rec (Nbval,
				(double *) ArgList[0],
				*((float *) ArgList[1]),
				(double *) ArgList[2]);
  if (CodRet == 0)
    return OP_OK;
  else if (CodRet == -1)
    {
      fprintf (stderr, "*** ERREUR : 1er elem. du temps est faux \n");
      fprintf (stderr, "*** ERREUR : on ne sait pas corriger ! stop ! ");
      return OP_FAIL;
    }
  else
    return OP_FAIL;
}

void
ID_correc_time_rec (oper * optr)
{
  strcpy (optr->Nom, "correc_time_rec");
  optr->Version = "1.0";
  optr->Date = "06/09/97";
  optr->fctptr = OP_correc_time_rec;
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
