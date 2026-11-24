/*************************************************************************
*
* OPERATOR         pos_sol_fixe_loa.c  FUNCTION ANSI-C
*
* PURPOSE          Calcul de la position du soleil dans le repère
*                géographique local d'un endroit fixe.
*
* DESCRIPTION      Appel d'une fonction du LOA
*
* VERSION          1.0
*
* ARGUMENTS
*            IN   int     dv             	? JDA ?
*            IN   double  t       sec	        Temps UTC après Oh de JDA
*            IN   float   lon     degree	longitude
*            IN   float   lat     degree        latitude
*
*            OUT  float   Theta0  degree        Angle solaire zénithal
*            OUT  float   Phi0    degree        Angle solaire azimutal
*            OUT  float   AMu0    radian        Position du soleil
*
*
* ENTRY        NONE
*
* SUBPROGRAMS  Appel de la routine FORTRAN du LOA.
*
* REFERENCES
*
* COPYRIGHT    Meteo-France
*	       Centre National de Recherches Meteorologiques
*	       GMEI/ TRAMM
*	       42, av G. Coriolis
*	       31057 TOULOUSE cedex 1
*
*
*############################################################################*/

#define _POSIX_SOURCE 1
#define _XOPEN_SOURCE 600

#include <math.h>
#include <stdio.h>
#include <string.h>
#include <math.h>

#include "struct_oper.h"
#include "oper_util.h"

/* déclaration de la routine en FORTRAN */
#include "possol.h"

void
pos_sol_fixe_loa (unsigned long ndata,
		  const int *dv,
		  const double *t,
		  double lon, double lat, float *theta, float *phi, float *mu)
{
  unsigned long i;
  double loc_theta, loc_phi, loc_mu;
  double t_heu;

  for (i = 0; i < ndata; i++)
    {
      /* Conversion de type de paramètres d'entrée */
      t_heu = t[i] / 3600.0;	/* en heure décimale */

      /* Appel de la fonction écrite en Fortran.  */
      possol (dv, &t_heu, &lon, &lat, &loc_theta, &loc_phi, &loc_mu);

      /* Conversion de type de paramètres de sortie */
      theta[i] = loc_theta;
      phi[i] = loc_phi;
      mu[i] = loc_mu;
    }
  return;
}


/* la fonction d'enrobage classique */
int
OP_pos_sol_fixe_loa (unsigned long NbVal, void *ArgList[], char *DiagExec)
{
  int NCar;

  NCar = sprintf (DiagExec, "pos_sol_fixe_loa (%ld ech, jour deb= %d, pos=(%gE, %gN))",
		  NbVal, *((int *) ArgList[0]), *((double *) ArgList[2]),
		  *((double *) ArgList[3]));
  DiagExec += NCar;
  DiagExec = ecrit_bornes_temps (DiagExec, "temps", (double *) ArgList[1],
				 NbVal);

  pos_sol_fixe_loa (NbVal, (int *) ArgList[0],
                    (double *) ArgList[1],
		    *((double *) ArgList[2]), *((double *) ArgList[3]),
		    (float *) ArgList[4],
                    (float *) ArgList[5],
		    (float *) ArgList[6]);

  return OP_OK;
}

void
ID_pos_sol_fixe_loa (oper * optr)
{
  strcpy (optr->Nom, "pos_sol_fixe_loa");
  optr->Version = "$Revision$";
  optr->Date = "$Date$";
  optr->fctptr = OP_pos_sol_fixe_loa;
  optr->NbArg = 7;		/* doit rester inf. a FIL_MAX_ARG */

  /* dv */
  optr->Arg_Car[0].direction = DIR_IN;
  optr->Arg_Car[0].categorie = COEFFICIENT;
  optr->Arg_Car[0].typ = ATYC_I32;
  optr->Arg_Car[0].array_dim = "1";
  optr->Arg_Car[0].type_sample = "any";
  optr->Arg_Car[0].sample = "any";
  optr->Arg_Car[0].unite = "day";

  /* UTC */
  optr->Arg_Car[1].direction = DIR_IN;
  optr->Arg_Car[1].categorie = VECTOR;
  optr->Arg_Car[1].typ = ATYC_IF64;
  optr->Arg_Car[1].array_dim = "1";
  optr->Arg_Car[1].type_sample = "any";
  optr->Arg_Car[1].sample = "any";
  optr->Arg_Car[1].unite = "sec since $Arg1";

  /* lon */
  optr->Arg_Car[2].direction = DIR_IN;
  optr->Arg_Car[2].categorie = COEFFICIENT;
  optr->Arg_Car[2].typ = ATYC_IF64;
  optr->Arg_Car[2].array_dim = "1";
  optr->Arg_Car[2].unite = "degree";

  /* lat */
  optr->Arg_Car[3].direction = DIR_IN;
  optr->Arg_Car[3].categorie = COEFFICIENT;
  optr->Arg_Car[3].typ = ATYC_IF64;
  optr->Arg_Car[3].array_dim = "1";
  optr->Arg_Car[3].unite = "degree";

  /* theta :  */
  optr->Arg_Car[4].direction = DIR_OUT;
  optr->Arg_Car[4].categorie = VECTOR;
  optr->Arg_Car[4].typ = ATYC_IF32;
  optr->Arg_Car[4].array_dim = "1";
  optr->Arg_Car[4].NbVal = "$Arg2.NbVal";
  optr->Arg_Car[4].type_sample = "any";
  optr->Arg_Car[4].sample = "$Arg2.sample";
  optr->Arg_Car[4].ref_time = "$Arg2.nom";
  optr->Arg_Car[4].unite = "degree";
  optr->Arg_Car[4].famille = " \"position_horizontale\" ";
  optr->Arg_Car[4].name = "\"Angle solaire zenithal\"";
  optr->Arg_Car[4].en_name = "\"Solar Zenith Angle\"";

  /*  phi :  */
  optr->Arg_Car[5].direction = DIR_OUT;
  optr->Arg_Car[5].categorie = VECTOR;
  optr->Arg_Car[5].typ = ATYC_IF32;
  optr->Arg_Car[5].array_dim = "1";
  optr->Arg_Car[5].NbVal = "$Arg2.NbVal";
  optr->Arg_Car[5].type_sample = "$Arg2.type_sample";
  optr->Arg_Car[5].sample = "$Arg2.sample";
  optr->Arg_Car[5].ref_time = "$Arg2.nom";
  optr->Arg_Car[5].unite = "degree";
  optr->Arg_Car[5].misval = "-999";
  optr->Arg_Car[5].famille = " \"position_horizontale\" ";
  optr->Arg_Car[5].name = "\"Angle solaire azimutal\"";
  optr->Arg_Car[5].en_name = "\"Solar Azimuth\"";

  /*  mu :  */
  optr->Arg_Car[6].direction = DIR_OUT;
  optr->Arg_Car[6].categorie = VECTOR;
  optr->Arg_Car[6].typ = ATYC_IF32;
  optr->Arg_Car[6].array_dim = "1";
  optr->Arg_Car[6].NbVal = "$Arg2.NbVal";
  optr->Arg_Car[6].type_sample = "$Arg2.type_sample";
  optr->Arg_Car[6].sample = "$Arg2.sample";
  optr->Arg_Car[6].ref_time = "$Arg2.nom";
  optr->Arg_Car[6].unite = "1";
  optr->Arg_Car[6].misval = "-999";
  optr->Arg_Car[6].famille = "\"position_horizontale\" ";
  optr->Arg_Car[6].name = "\"Cosinus de l'angle solaire zénithal\"";
  optr->Arg_Car[6].en_name = "\"cosine of solar zenith angle\"";
}
