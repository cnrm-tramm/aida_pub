/*************************************************************************
*
* OPERATOR         Flux_dq.c  FUNCTION ANSI-C
*
* PURPOSE          Calcul des profil d'humidite par méthode aérodynamique.
*
* DESCRIPTION      On utilise la methode aerodynamique, en utilisant 2 niveaux
*                  (dz=6,00-1.7 m) de mesure de la vitesse du vent et de la
*                  temperature, puis on déduit DeltaQ avec un LE 
*                  issu de la methode par correlation.
*
* VERSION          1.0 
*
* ARGUMENTS  
*            IN   float   dv      m/s		ffhaut-ffbas
*            IN   float   dt_air  °C   		thau-tbas
*            IN   float   t       °C		temperature sous abri
*            IN   float   p       hPa		pression sous abri
*            IN   float   tv      °C		temperature virtuelle
*            IN   float   hveg    m		hauteur de vegetation
*            IN   float   hbas    m		hauteur niveau inf. des mesures
*            IN   float   le      W/m2    	flux de chaleur latente
*
*            OUT  float   qstar                 ??
*            OUT  float   deltaq    m/s	        difference humabs  
*            
*            
* ENTRY        NONE
*        
* SUBPROGRAMS  Appel de la routine traditionelle codée en FORTRAN.
*
* REFERENCES   Programme Fortran 77 de Dominique Puech et note 6 de GMEI
*
* COPYRIGHT    Meteo-France
*	       Centre National de Recherches Meteorologiques 
*	       GMEI/ TRAMM
*	       42, av G. Coriolis
*	       31057 TOULOUSE cedex  
*
*
*############################################################################*/

#define _POSIX_SOURCE 1
#define _XOPEN_SOURCE 600
#define _HPUX_SOURCE 1

#include <math.h>
#include <stdio.h>
#include <string.h>
#include <math.h>
#include "struct_oper.h"

/* déclaration de la routine en FORTRAN */
extern void
  caldq_ot (float *dv, float *dt_air, float *t, float *p, float *tv,
	   float *hveg, float *hbas, float *le, float *qstar, float *deltaq);

int
Flux_dq (unsigned long ndata,
	  float *dv,
	  float *dt_air,
	  float *t,
	  float *p,
	  float *tv,
	  float *hveg,
	  float *hbas,
	  float *le,

	  float *qstar,
	  float *deltaq
)

{
  unsigned long i;
  float loc_dv, loc_dt_air, loc_t, loc_p, loc_tv, loc_hveg, loc_hbas, loc_le;
  /* const float misval_out = K_NaN; */

  for (i = 0; i < ndata; i++)
    {
/* Conversion de type de paramètres d'entrée */
/* test  misval... */
/* le ssprog caldq_ot attend des -999 en misval */

      loc_dv = dv[i];
      if (!isfinite (loc_dv)) loc_dv = -999;
      loc_dt_air = dt_air[i];
      if (!isfinite (loc_dt_air)) loc_dt_air = -999;
      loc_t = t[i];
      if (!isfinite (loc_t)) loc_t = -999;
      loc_p = p[i];
      if (!isfinite (loc_p)) loc_p = -999;
      loc_tv = tv[i];
      if (!isfinite (loc_tv)) loc_tv = -999;
      loc_hveg = hveg[i];
      if (!isfinite (loc_hveg)) loc_hveg = -999;
      loc_hbas = hbas[i];
      if (!isfinite (loc_hbas)) loc_hbas = -999;
      loc_le = le[i];
      if (!isfinite (loc_le)) loc_le = -999;

      /* appel de la fonction écrite en Fortran.  */

      fprintf (stderr, "in C, loc_le=%f, loc_t=%f\n", loc_le, loc_t);
      caldq_ot (&loc_dv, &loc_dt_air, &loc_t, &loc_p, &loc_tv,
	       &loc_hveg, &loc_hbas, &loc_le,
	 &(qstar[i]), &(deltaq[i]));

    }

  return 0;
}


/* la fonction d'enrobage classique */

int
OP_Flux_dq (unsigned long NbVal, void *ArgList[], char *DiagExec)
{

  sprintf (DiagExec, "OP_Flux_dq (%ld)", NbVal);
  Flux_dq (NbVal,
	     (float *) ArgList[0],
	     (float *) ArgList[1],
	     (float *) ArgList[2],
	     (float *) ArgList[3],
	     (float *) ArgList[4],
	     (float *) ArgList[5],
	     (float *) ArgList[6],
	     (float *) ArgList[7],
	     (float *) ArgList[8],
	     (float *) ArgList[9]);

  return OP_OK;

}

void
ID_Flux_dq (oper * optr)
{
  strcpy (optr->Nom, "Flux_dq");
  optr->Version = "$Revision$";
  optr->Date = "$Date$";
  optr->fctptr = OP_Flux_dq;
  optr->NbArg = 10;		/* doit rester inf. a FIL_MAX_ARG */

  /* dv */
  optr->Arg_Car[0].direction = DIR_IN;
  optr->Arg_Car[0].categorie = VECTOR;
  optr->Arg_Car[0].typ = ATYC_IF32;
  optr->Arg_Car[0].array_dim = "1";
  optr->Arg_Car[0].type_sample = "any";
  optr->Arg_Car[0].sample = "any";
  optr->Arg_Car[0].unite = "m/s";

  /* dt_air */
  optr->Arg_Car[1].direction = DIR_IN;
  optr->Arg_Car[1].categorie = VECTOR;
  optr->Arg_Car[1].typ = ATYC_IF32;
  optr->Arg_Car[1].array_dim = "1";
  optr->Arg_Car[1].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[1].type_sample = "any";
  optr->Arg_Car[1].sample = "any";
  optr->Arg_Car[1].unite = "celsius";

  /* t */
  optr->Arg_Car[2].direction = DIR_IN;
  optr->Arg_Car[2].categorie = VECTOR;
  optr->Arg_Car[2].typ = ATYC_IF32;
  optr->Arg_Car[2].array_dim = "1";
  optr->Arg_Car[2].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[2].type_sample = "any";
  optr->Arg_Car[2].sample = "any";
  optr->Arg_Car[2].unite = "celsius";

  /* p */
  optr->Arg_Car[3].direction = DIR_IN;
  optr->Arg_Car[3].categorie = VECTOR;
  optr->Arg_Car[3].typ = ATYC_IF32;
  optr->Arg_Car[3].array_dim = "1";
  optr->Arg_Car[3].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[3].type_sample = "any";
  optr->Arg_Car[3].sample = "any";
  optr->Arg_Car[3].unite = "hPa";
  
  /* tv */
  optr->Arg_Car[4].direction = DIR_IN;
  optr->Arg_Car[4].categorie = VECTOR;
  optr->Arg_Car[4].typ = ATYC_IF32;
  optr->Arg_Car[4].array_dim = "1";
  optr->Arg_Car[4].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[4].type_sample = "any";
  optr->Arg_Car[4].sample = "any";
  optr->Arg_Car[4].unite = "celsius";

  /* hveg */
  optr->Arg_Car[5].direction = DIR_IN;
  optr->Arg_Car[5].categorie = VECTOR;
  optr->Arg_Car[5].typ = ATYC_IF32;
  optr->Arg_Car[5].array_dim = "1";
  optr->Arg_Car[5].type_sample = "any";
  optr->Arg_Car[5].sample = "any";
  optr->Arg_Car[5].unite = "m";

  /* hbas */
  optr->Arg_Car[6].direction = DIR_IN;
  optr->Arg_Car[6].categorie = VECTOR;
  optr->Arg_Car[6].typ = ATYC_IF32;
  optr->Arg_Car[6].array_dim = "1";
  optr->Arg_Car[6].type_sample = "any";
  optr->Arg_Car[6].sample = "any";
  optr->Arg_Car[6].unite = "m";
  
  /* le */
  optr->Arg_Car[7].direction = DIR_IN;
  optr->Arg_Car[7].categorie = VECTOR;
  optr->Arg_Car[7].typ = ATYC_IF32;
  optr->Arg_Car[7].array_dim = "1";
  optr->Arg_Car[7].type_sample = "any";
  optr->Arg_Car[7].sample = "any";
  optr->Arg_Car[7].unite = "W/m2";

  /*  qstar */
  optr->Arg_Car[8].direction = DIR_OUT;
  optr->Arg_Car[8].categorie = VECTOR;
  optr->Arg_Car[8].typ = ATYC_IF32;
  optr->Arg_Car[8].array_dim = "1";
  optr->Arg_Car[8].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[8].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[8].sample = "$Arg1.sample";
  optr->Arg_Car[8].ref_time = "$Arg1.ref_time";
  optr->Arg_Car[8].unite = "gram/m3";
  optr->Arg_Car[8].misval = "-999";
  optr->Arg_Car[8].famille = " \"flux\" ";

  /*  deltaq */
  optr->Arg_Car[9].direction = DIR_OUT;
  optr->Arg_Car[9].categorie = VECTOR;
  optr->Arg_Car[9].typ = ATYC_IF32;
  optr->Arg_Car[9].array_dim = "1";
  optr->Arg_Car[9].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[9].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[9].sample = "$Arg1.sample";
  optr->Arg_Car[9].ref_time = "$Arg1.ref_time";
  optr->Arg_Car[9].unite = "gram/m3";
  optr->Arg_Car[9].misval = "-999";
  optr->Arg_Car[9].famille = " \"flux\" ";
}
