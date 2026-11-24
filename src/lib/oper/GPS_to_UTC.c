/*******************************************************************
* OPERATOR      GPS_to_UTC.c FUNCTION ANSI-C
*
* PURPOSE       Transformation du temps GPS en temps UTC
*		
* DESCRIPTION	Le temps GPS est compté en secondes depuis le début de 
*               la semaine, dans le système GPS (décalé d'avec le TAI et l'UTC).
*               Le temps UTC est compté en secondes depuis 0h00
*		
*		 
* VERSION       1.0
*
* ARGUMENTS     IN  float Temps_GPS	secondes	Temps GPS
*               IN  int    Decal	secondes	Décalage GPS/UTC au moment du vol (positif)
*
*		OUT double Temps_UTC	secondes	le même temps, exprimé dans le système UTC
*
* ENTRY         NONE
*
* SUBPROGRAMS   NONE
*
* REFERENCES    "GPS, theory and practice" par B. Hofmann-Wellenhof,
*               H. Lichtenegger, et J. Collins, Springer-Verlag, Wien
*               1992.
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

#include <stdio.h>
#include <string.h>
#include <math.h>
#include "struct_oper.h"

void
GPS_to_UTC (unsigned long NLoop, const float *GPS_time,	/* secondes */
	    int Decal, double *UTC_time)
{
  unsigned long i;
  double M = 86400.0;
  double offset;

  /* Calcul d'un offset sur le premier non-nul */
  i = 0;
  while ((GPS_time[i] == 0) && (i < NLoop))
    i++;
  if (GPS_time[i] < Decal)
    {				/* Cas particulier ou a déja changé de jour GPS, mais pas encore de jour UTC */
      offset = -86400.0;
    }
  else
    offset = (double) (M * ((int) ((GPS_time[i] - Decal) / M)));

  for (i = 0; i < NLoop; i++)
    {
      *UTC_time = (*GPS_time) - offset - Decal;
      UTC_time++;
      GPS_time++;
    }


}

/* fonction d'enrobage */

int
OP_GPS_to_UTC (unsigned long Nbval, void *ArgList[], char *DiagExec)
{
  sprintf (DiagExec, "GPS_to_UTC (%lu ech),  Decal = %d s. (res = orig - Decal).", Nbval,
	   *((int *) ArgList[1]));

  GPS_to_UTC (Nbval,
	      (float *) ArgList[0],
	      *((int *) ArgList[1]), (double *) ArgList[2]);

  return OP_OK;
}

void
ID_GPS_to_UTC (oper * optr)
{
  strcpy (optr->Nom, "GPS_to_UTC");
  optr->Version = "$Revision$";
  optr->Date = "$Date$";
  optr->fctptr = OP_GPS_to_UTC;
  optr->NbArg = 3;

  /* GPS_time */
  optr->Arg_Car[0].direction = DIR_IN;
  optr->Arg_Car[0].categorie = VECTOR;
  optr->Arg_Car[0].typ = ATYC_IF32;
  optr->Arg_Car[0].array_dim = "1";
  optr->Arg_Car[0].type_sample = "any";
  optr->Arg_Car[0].sample = "any";
  optr->Arg_Car[0].unite = "second";
  optr->Arg_Car[0].famille = "any";

  /* Decal */
  optr->Arg_Car[1].direction = DIR_IN;
  optr->Arg_Car[1].categorie = COEFFICIENT;
  optr->Arg_Car[1].typ = ATYC_I32;
  optr->Arg_Car[1].array_dim = "1";
  optr->Arg_Car[1].type_sample = "any";
  optr->Arg_Car[1].sample = "any";
  optr->Arg_Car[1].unite = "second";
  optr->Arg_Car[1].famille = "any";

  /* UTC_time */
  optr->Arg_Car[2].direction = DIR_OUT;
  optr->Arg_Car[2].categorie = VECTOR;
  optr->Arg_Car[2].typ = ATYC_IF64;
  optr->Arg_Car[2].array_dim = "1";
  optr->Arg_Car[2].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[2].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[2].sample = "$Arg1.sample";
  optr->Arg_Car[2].unite = "second";
  optr->Arg_Car[2].famille = "$Arg1.famille";
}
