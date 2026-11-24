/*******************************************************************
* OPERATOR      GPS_to_UTC_irreg.c FUNCTION ANSI-C
*
* PURPOSE       Transformation du temps GPS en temps UTC
*
* DESCRIPTION	Le temps GPS est compté en secondes depuis le début de
*               la semaine, dans le système GPS (décalé d'avec le TAI et l'UTC).
*               Le temps UTC est compté en secondes depuis 0h00 le jour
*               du démarrage de l'acquisition.
*
* VERSION       $Revision$
*
* ARGUMENTS     IN  float  Temps_GPS	secondes	Temps GPS
*               IN  float  Decal        secondes	Décalage GPS/UTC fourni par le récepteur
*               IN  u_long N_Decal	compte  	Nombre d'éléments du vecteur Decal
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
#include <math.h>
#include "struct_oper.h"

#include "struct_GPS_to_UTC_irreg.h"


int
GPS_to_UTC_irreg (unsigned long NLoop, const float *GPS_time,	/* secondes */
		  const float *Decal, unsigned long N_Decal, double *UTC_time,
		  CR_conv_GPS_time_t * comptes)
{
  /* marge = le nombre d'heure sans datation toléré avant/aprés le changement
   * de semaine GPS. */
  const int marge = 3;
  const int min_decal_OK = 1;	/* A verifier : correspond sans doute aux années 1980 */
  const int max_decal_OK = 100;	/* Arrivera vers la fin du 21eme siecle. Encore des GPS à cette époque ? */
  unsigned long i;
  const double M = 86400.0;
  double offset;

  comptes->nb_decal_OK = 0;
  comptes->nb_GPS_time_mnq = 0;
  /* Recherche du décalage */
  comptes->decal = 0;
  for (i = 0; i < N_Decal; i++)
    {
      if (isfinite (Decal[i]) && (Decal[i] >= min_decal_OK)
	  && (Decal[i] <= max_decal_OK))
	{
	  comptes->nb_decal_OK++;
	  if (comptes->decal == 0)
	    {
	      comptes->decal = Decal[i];
	    }
	  else
	    {
	      if (comptes->decal != Decal[i])
		{
		  return GPS_UTC_MULTI;
		}
	    }
	}
    }
  if (comptes->decal == 0)
    {
      return GPS_UTC_NOTFOUND;
    }
  /* Calcul d'un offset sur le premier non-nul */
  i = 0;
  while ((GPS_time[i] == 0) && (i < NLoop))
    i++;
  if (GPS_time[i] < comptes->decal)
    {
      /* Cas particulier où on a déja changé de jour GPS, mais pas encore de
       *  jour UTC */
      offset = -86400.0;
    }
  else
    offset = (double) (M * ((int) ((GPS_time[i] - comptes->decal) / M)));

  /* Boucle de calcul des temps UTC à partir des temps GPS */
  for (i = 0; i < NLoop; i++)
    {
      if (*GPS_time == 0.0)
	comptes->nb_GPS_time_mnq++;
      /* Si on change de semaine GPS, le nombre de secondes
       * depuis le début de la semaine devient tout petit.
       * La détection est empirique, puisqu'on n'a pas accès au
       * numéro de semaine GPS. */
      if (i > 1)
	{
	  if (*GPS_time < *(GPS_time - 1))
	    {
	      if ((*GPS_time < marge * 3600)
		  && (*(GPS_time - 1) > (7 * 24 - marge) * 3600))
		{
		  offset = offset - 7 * 24 * 3600;
		}
	    }
	}
      *UTC_time = (*GPS_time) - offset - comptes->decal;

      UTC_time++;
      GPS_time++;
    }

  return GPS_UTC_OK;
}

/* fonction d'enrobage */

int
OP_GPS_to_UTC_irreg (unsigned long Nbval, void *ArgList[], char *DiagExec)
{
  int CodRet;
  int nc;
  CR_conv_GPS_time_t comptes;

  nc =
    sprintf (DiagExec, "GPS_to_UTC_irreg (%lu ech, %lu decalages)", Nbval,
	     *((unsigned long *) ArgList[2]));

  if (nc > 0)
    DiagExec += nc;

  CodRet = GPS_to_UTC_irreg (Nbval,
			     (float *) ArgList[0],
			     (float *) ArgList[1],
			     *((unsigned long *) ArgList[2]),
			     (double *) ArgList[3], &comptes);

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
ID_GPS_to_UTC_irreg (oper * optr)
{
  strcpy (optr->Nom, "GPS_to_UTC_irreg");
  optr->Version = "$Revision$";
  optr->Date = "$Date$";
  optr->fctptr = OP_GPS_to_UTC_irreg;
  optr->NbArg = 4;

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
  optr->Arg_Car[1].NbVal = "any";	/* "$Arg3", mais référence avant impossible */
  optr->Arg_Car[1].type_sample = "any";
  optr->Arg_Car[1].sample = "any";
  optr->Arg_Car[1].unite = "second";
  optr->Arg_Car[1].famille = "any";

  /* N_Decal */
  optr->Arg_Car[2].direction = DIR_IN;
  optr->Arg_Car[2].categorie = COEFFICIENT;
  optr->Arg_Car[2].typ = ATYC_LOCAL_ULONG;

  /* UTC_time */
  optr->Arg_Car[3].direction = DIR_OUT;
  optr->Arg_Car[3].categorie = VECTOR;
  optr->Arg_Car[3].typ = ATYC_IF64;
  optr->Arg_Car[3].array_dim = "1";
  optr->Arg_Car[3].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[3].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[3].sample = "$Arg1.sample";
  optr->Arg_Car[3].unite = "second";
  optr->Arg_Car[3].famille = "$Arg1.famille";
  optr->Arg_Car[3].name = "$Arg1.name exprime en UTC";
  optr->Arg_Car[3].en_name = "$Arg1.english_name expressed in UTC";
}
