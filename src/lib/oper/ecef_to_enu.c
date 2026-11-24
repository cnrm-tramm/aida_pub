/*******************************************************************
* OPERATOR      ecef_to_enu.c FUNCTION ANSI-C
*
* PURPOSE       Passage d'un vecteur donne dans le repere ECEF
*		(Earth Centered Earth Fixed) dans la repere 
*		ENU (Est Nord Up).  
*		
* DESCRIPTION	ECEF : 	le centre est situe au centre de la terre
*			X dans le plan equatorial du centre vers le meridien 0	
*			Y dans le plan equatorial du centre vers le meridien +90
*			Z dans le plan equatorial du centre vers le pole nord 
*
*		ENU :  	le centre est l'objet repere 
*			X d'ouest en est 
*			Y du sud au nord
*			Z vertical
*		 
* VERSION       1.0
*
* ARGUMENTS     IN  float  lat	degre  latitude 
*               IN  float  lon	degre  longitude
*               IN  float  vx          composante selon l'axe X du repere ECEF
*               IN  float  vy          composante selon l'axe Y du repere ECEF
*               IN  float  vz          composante selon l'axe Z du repere ECEF
*
*               OUT float  ve          composante Ouest-Est
*		OUT float  vn	       composante Sud-Nord 
*		OUT float  vv 	       composante verticale
*       vx, vy, vz must be in the same unit, and ve, vn, vv are in this unit
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
/* Le #define _HPUX_SOURCE n'est la que pour "voir" strdup */
#define _HPUX_SOURCE 1
#define _XOPEN_SOURCE_EXTENDED 1

#include <stdio.h>
#include <string.h>
#include <math.h>
#include "struct_oper.h"

unsigned long
ecef_to_enu (unsigned long ndata, const float *lat,	/* degres */
	     const float *lon,	/* degres */
	     const float *vx,
	     const float *vy,
	     const float *vz, float *ve, float *vn, float *vv)
{
  unsigned long i;
  unsigned nb_bad_lat = 0;

  float dgrd = 3.14159265 / 180.;
  float clat, tlat, slon, clon;

  for (i = 0; i < ndata; i++)
    {
      if (fabs (lat[i]) > 90.0)
	{
	  nb_bad_lat++;
	  vv[i] = 0.0 / 0.0;
	  ve[i] = 0.0 / 0.0;
	  vn[i] = 0.0 / 0.0;
	  continue;
	}
      clat = cos (dgrd * lat[i]);
      tlat = tan (dgrd * lat[i]);
      slon = sin (dgrd * lon[i]);
      clon = cos (dgrd * lon[i]);

      vv[i] = clat * (clon * vx[i] + slon * vy[i] + tlat * vz[i]);
      ve[i] = clon * vy[i] - slon * vx[i];
      vn[i] = (vz[i] / clat) - (tlat * vv[i]);
    }

  return nb_bad_lat;
}

/* fonction d'enrobage */

int
OP_ecef_to_enu (unsigned long Nbval, void *ArgList[], char *DiagExec)
{
  unsigned long CodRet;

  CodRet = ecef_to_enu (Nbval,
			(float *) ArgList[0],
			(float *) ArgList[1],
			(float *) ArgList[2],
			(float *) ArgList[3],
			(float *) ArgList[4],
			(float *) ArgList[5],
			(float *) ArgList[6], (float *) ArgList[7]);

  sprintf (DiagExec, "ecef_to_enu (%lu ech), %lu latitudes hors-gamme", Nbval,
	   CodRet);

  return OP_OK;
}

void
ID_ecef_to_enu (oper * optr)
{
  strcpy (optr->Nom, "ecef_to_enu");
  optr->Version = "1.0";
  optr->Date = "06/19/96";
  optr->fctptr = OP_ecef_to_enu;
  optr->NbArg = 8;

  /* lat */
  optr->Arg_Car[0].direction = DIR_IN;
  optr->Arg_Car[0].categorie = VECTOR;
  optr->Arg_Car[0].typ = ATYC_IF32;
  optr->Arg_Car[0].array_dim = "1";
  optr->Arg_Car[0].type_sample = "any";
  optr->Arg_Car[0].sample = "any";
  optr->Arg_Car[0].unite = "degree";

  /* lon */
  optr->Arg_Car[1].direction = DIR_IN;
  optr->Arg_Car[1].categorie = VECTOR;
  optr->Arg_Car[1].typ = ATYC_IF32;
  optr->Arg_Car[1].array_dim = "1";
  optr->Arg_Car[1].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[1].type_sample = "any";
  optr->Arg_Car[1].sample = "any";
  optr->Arg_Car[1].unite = "degree";

  optr->Arg_Car[2].direction = DIR_IN;
  optr->Arg_Car[2].categorie = VECTOR;
  optr->Arg_Car[2].typ = ATYC_IF32;
  optr->Arg_Car[2].array_dim = "1";
  optr->Arg_Car[2].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[2].type_sample = "any";
  optr->Arg_Car[2].sample = "any";
  optr->Arg_Car[2].unite = "";

  optr->Arg_Car[3].direction = DIR_IN;
  optr->Arg_Car[3].categorie = VECTOR;
  optr->Arg_Car[3].typ = ATYC_IF32;
  optr->Arg_Car[3].array_dim = "1";
  optr->Arg_Car[3].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[3].type_sample = "any";
  optr->Arg_Car[3].sample = "any";

  optr->Arg_Car[4].unite = "";
  optr->Arg_Car[4].direction = DIR_IN;
  optr->Arg_Car[4].categorie = VECTOR;
  optr->Arg_Car[4].typ = ATYC_IF32;
  optr->Arg_Car[4].array_dim = "1";
  optr->Arg_Car[4].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[4].type_sample = "any";
  optr->Arg_Car[4].sample = "any";
  optr->Arg_Car[4].unite = "";

  optr->Arg_Car[5].direction = DIR_OUT;
  optr->Arg_Car[5].categorie = VECTOR;
  optr->Arg_Car[5].typ = ATYC_IF32;
  optr->Arg_Car[5].array_dim = "1";
  optr->Arg_Car[5].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[5].sample = "$Arg1.sample";
  optr->Arg_Car[5].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[5].unite = "$Arg4.unit";

  optr->Arg_Car[6].direction = DIR_OUT;
  optr->Arg_Car[6].categorie = VECTOR;
  optr->Arg_Car[6].typ = ATYC_IF32;
  optr->Arg_Car[6].array_dim = "1";
  optr->Arg_Car[6].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[6].sample = "$Arg1.sample";
  optr->Arg_Car[6].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[6].unite = "$Arg4.unit";

  optr->Arg_Car[7].direction = DIR_OUT;
  optr->Arg_Car[7].categorie = VECTOR;
  optr->Arg_Car[7].typ = ATYC_IF32;
  optr->Arg_Car[7].array_dim = "1";
  optr->Arg_Car[7].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[7].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[7].sample = "$Arg1.sample";
  optr->Arg_Car[7].unite = "$Arg5.unit";
}
