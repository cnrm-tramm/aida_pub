/*******************************************************************
* OPERATOR      cont_time.c FUNCTION ANSI-C
*
* PURPOSE       Genere un temps continu a partir 
*		d'un temps qui passe a zero a 86400
*
* DESCRIPTION    
*
* VERSION       1.0
*
*               IN      double  time		temps brut
*               IN      float   fr              frequence d'acquisition
*
*		OUT	double  time_cont 	temps continu
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
cont_time (unsigned long ndata,
		 double *time,
		 float fr,
		 double *time_cont)

{
  unsigned long i;
  float te, dt, toff, t0;

  te = 1./fr;
  t0 = 86400.;
  toff = 0.;
  
  time_cont[0] = time[0]; 

  for (i = 0; i < ndata; i++)
   {
    dt = time[i] - time[i-1];
    if ( (dt >= te - t0) &&
	 (dt <= (3.*te/2.) - t0) )      
  	toff = 86400.;

    time_cont[i] = time[i] + toff;
   }

  return (0);
}

/* fonction d'enrobage */

int
OP_cont_time (unsigned long Nbval, void *ArgList[], char *DiagExec)
{
  int CodRet = cont_time (Nbval,
				(double *) ArgList[0],
				*((float *) ArgList[1]),
				(double *) ArgList[2]);
  return OP_OK;
}

void
ID_cont_time (oper * optr)
{
  strcpy (optr->Nom, "cont_time");
  optr->Version = "1.0";
  optr->Date = "02/12/98";
  optr->fctptr = OP_cont_time;
  optr->NbArg = 3;

  /* time */
  optr->Arg_Car[0].direction = DIR_IN;
  optr->Arg_Car[0].categorie = VECTOR;
  optr->Arg_Car[0].typ = ATYC_IF64;
  optr->Arg_Car[0].array_dim = "1";
  optr->Arg_Car[0].type_sample = "any";
  optr->Arg_Car[0].sample = "any";
  optr->Arg_Car[0].unite = "second";

  /* fr */
  optr->Arg_Car[1].direction = DIR_IN;
  optr->Arg_Car[1].categorie = COEFFICIENT;
  optr->Arg_Car[1].typ = ATYC_IF32;
  optr->Arg_Car[1].array_dim = "1";
  optr->Arg_Car[1].type_sample = "any";
  optr->Arg_Car[1].sample = "any";
  optr->Arg_Car[1].unite = "";

  /* time_cont */
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
