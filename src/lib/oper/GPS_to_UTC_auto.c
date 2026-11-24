/*******************************************************************
* OPERATOR      GPS_to_UTC_auto.c FUNCTION ANSI-C
*
* PURPOSE       Transformation du temps GPS en temps UTC
*		
* DESCRIPTION	Le temps GPS est compté en secondes depuis le début de
*               la semaine, dans le système GPS (décalé d'avec le TAI et l'UTC).
*               Le temps UTC est compté en secondes depuis 0h00
*
* VERSION       1.0
*
* ARGUMENTS     IN  float Temps_GPS	secondes	Temps GPS
*               IN  float Decal	        secondes	Décalage GPS/UTC fourni par le récepteur
*
*               OUT double Temps_UTC	secondes	le même temps, exprimé dans le système UTC
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
*               GMEI/TRAMM
*               42, av. G. Coriolis
*               31057   TOULOUSE cedex
*
*******************************************************************/

#define _POSIX_SOURCE 1
#define _XOPEN_SOURCE 600

#include <stdio.h>
#include <string.h>

#include "struct_oper.h"
#include "struct_GPS_to_UTC_irreg.h"
#include "GPS_to_UTC_irreg.h"


/*
 *    Le cas traité par GPS_to_UTC_auto est un cas particulier
 * de GPS_to_UTC_irreg, dans lequel le nombre d'éléments de
 * Decal (l'argument 2) est le même que le nombre d'éléments de
 * T_GPS (l'argument 1).
 *
 *    On se contente donc d'appeler GPS_to_UTC_irreg() avec les
 * arguments adaptés.
 */


int
OP_GPS_to_UTC_auto (unsigned long Nbval, void *ArgList[], char *DiagExec)
{
  int CodRet;
  int nc;
  CR_conv_GPS_time_t comptes;

  nc = sprintf (DiagExec, "GPS_to_UTC_auto (%lu ech)", Nbval);

  if (nc > 0)
    DiagExec += nc;

  CodRet = GPS_to_UTC_irreg (Nbval,
			    (float *) ArgList[0],
			    (float *) ArgList[1],
			    Nbval,
                            (double *) ArgList[2],
			    &comptes);

  if (CodRet == GPS_UTC_OK)
    {
      sprintf (DiagExec,
	       "; OK : %lu infos de decalage, Decalage=%gs, %lu temps absents",
	       comptes.nb_decal_OK, comptes.decal, comptes.nb_GPS_time_mnq);
      return OP_OK;
    }

  if (CodRet == GPS_UTC_MULTI)
    sprintf (DiagExec, "; Echec : Plusieurs valeurs de decalage dans Arg2");

  if (CodRet == GPS_UTC_NOTFOUND)
    sprintf (DiagExec,
	     "; Echec : Pas de valeurs de decalage valide dans Arg2");

  return OP_FAIL;
}

void
ID_GPS_to_UTC_auto (oper * optr)
{
  strcpy (optr->Nom, "GPS_to_UTC_auto");
  optr->Version = "$Revision$";
  optr->Date = "$Date$";
  optr->fctptr = OP_GPS_to_UTC_auto;
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
  optr->Arg_Car[1].categorie = VECTOR;
  optr->Arg_Car[1].typ = ATYC_IF32;
  optr->Arg_Car[1].array_dim = "1";
  optr->Arg_Car[1].NbVal = "$Arg1.NbVal";
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
  optr->Arg_Car[2].name = "$Arg1.name exprime en UTC";
  optr->Arg_Car[2].en_name = "$Arg1.english_name expressed in UTC";
}
