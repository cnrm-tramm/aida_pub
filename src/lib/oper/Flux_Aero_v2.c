/*************************************************************************
*
* OPERATOR         Flux_Aero_v2.c  FUNCTION ANSI-C
*
* PURPOSE          Calcul des flux de chaleur sensible par méthode 
*                  aérodynamique, avec gestion des cas particuliers
*                  par valeurs manquantes.
*
* DESCRIPTION      On utilise la methode aerodynamique, en utilisant 2 niveaux
*                  (dz=1.5 m) de mesure de la vitesse du vent et de la
*                  temperature, puis on déduit LE en supposant le
*                  bilan énergétique fermé.
*                  Cette version amelioree de Flux_Aero teste la valeur de
*                  HS notamment par rapport au RN (HS < RN). 
*                  Cette version traite aussi mieux les cas particuliers
*                  de dv et deltaT tres faibles .
*                  Elle integre aussi un test sur hbas : si negatif (maintenance
*                  en cours, tests de mesures au meme niveau par ex.) --> pas de calculs.
*                  Remarque : Plusieurs tests ne sont actives (HS, deltaT, dv)
*                  que pour les valeurs "de jour" (RN > 20 W/m2)
*                  Cet operateur renvoie aussi un flag en sortie...
*
* VERSION          1.1 : les tstar et ustar sont mis a mnq en sortie
*                        lorsque hs , le sont manquants... 
*
* ARGUMENTS  
*            IN   float   dv      m/s		ffhaut-ffbas
*            IN   float   ffhau   m/s           vitesse du vent superieur
*            IN   float   dt_air  °C   		thau-tbas
*            IN   float   t       °C		temperature sous abri
*            IN   float   rn      W/m2		rayonnement net
*            IN   float   phi0    W/m2		flux dans le sol
*            IN   float   hveg    m		hauteur de vegetation
*            IN   float   hbas    m		hauteur niveau inf. des mesures
*            IN   float   p       hPa		pression
*            IN   float   humid   %		humidite
*
*            OUT  float   hs   W/m2	flux de chaleur sensible
*            OUT  float   le   W/m2	flux de chaleur latente
*            OUT  float   z0   m	rugosite
*            OUT  float   vlmon sans	longueur de Monin Obukhov
*            OUT  float   ustar m/s	vitesse de frottement
*            OUT  float   tstar ??
*            OUT  float   flag          flag de validite des flux (0 si OK)
*            
*            
* ENTRY        NONE
*        
* SUBPROGRAMS  Appel de la routine traditionnelle codée en FORTRAN.
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
  /*calf_dp (float *dv, float *ffhau, float *dt_air, float *t, int *rn, int *phi0,
	   float *hveg, float *hbas, float *p, int *humid,
     int *hs, int *le, float *z0, float *vlmon, float *ustar, float *tstar);*/
  calf_dp (float *dv, float *ffhau, float *dt_air, float *t, int *rn, int *phi0,
	   float *hveg, float *hbas, float *p, int *humid,
     int *hs, int *le, float *z0, float *vlmon, float *ustar, float *tstar);

int
Flux_Aero_v2 (unsigned long ndata,
	  float *dv,
	  float *ffhau,
	  float *dt_air,
	  float *t,
	  float *rn,
	  float *phi0,
	  float *hveg,
	  float *hbas,
	  float *p,
	  float *humid,
	  float *hs,
	  float *le,
	  float *z0,
	  float *vlmon,
	  float *ustar,
	  float *tstar,
	  float *flag,
	  unsigned long *Tab_diagno
)

{
  unsigned long i;
  signed long nb_bug_rn, nb_bug_dv, nb_bug_dt;
  int loc_rn, loc_phi0, loc_humid;
  int loc_hs, loc_le;
  float loc_dv, loc_ffhau, loc_dt_air, loc_t, loc_hveg, loc_hbas, loc_p;
  const float misval_out = K_NaN;

  /* compteurs d'anomalies (hs>rn et dv<0) */
  nb_bug_rn = 0;
  nb_bug_dv = 0;
  nb_bug_dt = 0;

  for (i = 0; i < ndata; i++)
    {
/* Conversion de type de paramètres d'entrée */
/* ajout C.Berne 07/06/2001 : variable locale pour tester les misval... */
/*                          le ssprog calf_dp attend des -999 en misval */
      loc_rn = rn[i];
      if (!isfinite (rn[i])) loc_rn = -999;
      loc_phi0 = phi0[i];
      if (!isfinite (phi0[i])) loc_phi0 = -999;
      loc_humid = humid[i];
      if (!isfinite (humid[i])) loc_humid = -999;

      loc_dv = dv[i];
      if (!isfinite (loc_dv)) loc_dv = -999;
      loc_ffhau = ffhau[i];
      if (!isfinite (loc_ffhau)) loc_ffhau = -999;
      loc_dt_air = dt_air[i];
      if (!isfinite (loc_dt_air)) loc_dt_air = -999;
      loc_t = t[i];
      if (!isfinite (loc_t)) loc_t = -999;
      loc_hveg = hveg[i];
      if (!isfinite (loc_hveg)) loc_hveg = -999;
      loc_hbas = hbas[i];
      if (!isfinite (loc_hbas)) loc_hbas = -999;
      loc_p = p[i];
      if (!isfinite (loc_p)) loc_p = -999;

      /* appel de la fonction écrite en Fortran.  */

      calf_dp (&loc_dv, &loc_ffhau, &loc_dt_air, &loc_t, &loc_rn, &loc_phi0,
	       &loc_hveg, &loc_hbas, &loc_p, &loc_humid,
	 &loc_hs, &loc_le, &(z0[i]), &(vlmon[i]), &(ustar[i]), &(tstar[i]));

      /* Conversion de type de paramètres de sortie */
      if (loc_hs == -999)
      {
	    hs[i] = misval_out;
	    loc_le = -999;
            flag[i] = 0;
      }
      else if ( (loc_dv < 0.01) && (loc_rn > 20) )
      {
	      /* Cas ou DeltaFF trop faible (valeurs de jour seulement) */
	    hs[i] = misval_out;
	    loc_le = -999;
            flag[i] = -1;
	    z0[i] = misval_out;
	    vlmon[i] = misval_out;
	    ustar[i] = misval_out;
	    tstar[i] = misval_out;
            nb_bug_dv = nb_bug_dv + 1;
      }
      else if ( (fabs(loc_dt_air) < 0.01) && (loc_rn > 20) )
	      /* Cas ou DT_AIR trop faible en valeur absolue (valeurs de jour seulement) */
      {
	printf(" loc_dt_air = %f - val.abs. = %f\n",loc_dt_air,fabs(loc_dt_air));
	    hs[i] = misval_out;
	    loc_le = -999;
            flag[i] = -1;
	    z0[i] = misval_out;
	    vlmon[i] = misval_out;
	    ustar[i] = misval_out;
	    tstar[i] = misval_out;
            nb_bug_dt = nb_bug_dt + 1;
      }
      else if ( (loc_dt_air < -2.) || (loc_dt_air > 3) )
	      /* Cas ou DT_AIR hors gamme [-2, +3] */
      {
	    hs[i] = misval_out;
	    loc_le = -999;
            flag[i] = -1;
	    z0[i] = misval_out;
	    vlmon[i] = misval_out;
	    ustar[i] = misval_out;
	    tstar[i] = misval_out;
            nb_bug_dt = nb_bug_dt + 1;
      }
      else if ( (loc_hs > loc_rn) && (loc_rn > 20) )
	      /* Cas ou HS > RN ET RN > 0 (valeurs de jour seulement) */
      {
	    hs[i] = misval_out;
	    loc_le = -999;
            flag[i] = -2;
	    z0[i] = misval_out;
	    vlmon[i] = misval_out;
	    ustar[i] = misval_out;
	    tstar[i] = misval_out;
            nb_bug_rn = nb_bug_rn + 1;
      }
      else
      {
            hs[i] = loc_hs;
            flag[i] = 0;
      }

      if (loc_le == -999)
	    le[i] = misval_out;
      else
            le[i] = loc_le;

      /* Rajout d'un test sur hbas : si hbas<0. --> pas de calcul */
      /*  par ex. dans le cas ou les mesures DeltaT, DeltaFF sont effectuees au meme niveau */
      if (loc_hbas < 0.)
      {
	    hs[i] = misval_out;
	    le[i] = misval_out;
	    flag[i] = -3;
	    z0[i] = misval_out;
	    vlmon[i] = misval_out;
	    ustar[i] = misval_out;
	    tstar[i] = misval_out;
      }

    }

  Tab_diagno[0] = nb_bug_rn;
  Tab_diagno[1] = nb_bug_dv;
  Tab_diagno[2] = nb_bug_dt;

  return nb_bug_rn + nb_bug_dv + nb_bug_dt;
}


/* la fonction d'enrobage classique */

int
OP_Flux_Aero_v2 (unsigned long NbVal, void *ArgList[], char *DiagExec)
{

  long CodRet;
  unsigned long toto[3];
  sprintf (DiagExec, "Flux_Aero_v2 (%ld)", NbVal);
  CodRet = Flux_Aero_v2 (NbVal,
	     (float *) ArgList[0],
	     (float *) ArgList[1],
	     (float *) ArgList[2],
	     (float *) ArgList[3],
	     (float *) ArgList[4],
	     (float *) ArgList[5],
	     (float *) ArgList[6],
	     (float *) ArgList[7],
	     (float *) ArgList[8],
	     (float *) ArgList[9],
	     (float *) ArgList[10],
	     (float *) ArgList[11],
	     (float *) ArgList[12],
	     (float *) ArgList[13],
	     (float *) ArgList[14],
	     (float *) ArgList[15],
	     (float *) ArgList[16], toto);

  if (CodRet > 0) 
  {
      (void) sprintf (DiagExec, "; NB Anomalies HS>RN = %d- NB deltaFF < 0.01  = %d- NB PB deltaT douteux = %d \n",toto[0],toto[1],toto[2]);
    }
  else 
  {
      (void) sprintf (DiagExec, "; Pas d anomalies detectees\n");
  }

  return OP_OK;

}

void
ID_Flux_Aero_v2 (oper * optr)
{
  strcpy (optr->Nom, "Flux_Aero_v2");
  optr->Version = "1.0";
  optr->Date = "15/11/05";
  optr->fctptr = OP_Flux_Aero_v2;
  optr->NbArg = 17;		/* doit rester inf. a FIL_MAX_ARG */

  /* dv */
  optr->Arg_Car[0].direction = DIR_IN;
  optr->Arg_Car[0].categorie = VECTOR;
  optr->Arg_Car[0].typ = ATYC_IF32;
  optr->Arg_Car[0].array_dim = "1";
  optr->Arg_Car[0].type_sample = "any";
  optr->Arg_Car[0].sample = "any";
  optr->Arg_Car[0].unite = "m/s";

  /* ffhau */
  optr->Arg_Car[1].direction = DIR_IN;
  optr->Arg_Car[1].categorie = VECTOR;
  optr->Arg_Car[1].typ = ATYC_IF32;
  optr->Arg_Car[1].array_dim = "1";
  optr->Arg_Car[1].type_sample = "any";
  optr->Arg_Car[1].sample = "any";
  optr->Arg_Car[1].unite = "m/s";

  /* dt_air */
  optr->Arg_Car[2].direction = DIR_IN;
  optr->Arg_Car[2].categorie = VECTOR;
  optr->Arg_Car[2].typ = ATYC_IF32;
  optr->Arg_Car[2].array_dim = "1";
  optr->Arg_Car[2].type_sample = "any";
  optr->Arg_Car[2].sample = "any";
  optr->Arg_Car[2].unite = "celsius";

  /* t */
  optr->Arg_Car[3].direction = DIR_IN;
  optr->Arg_Car[3].categorie = VECTOR;
  optr->Arg_Car[3].typ = ATYC_IF32;
  optr->Arg_Car[3].array_dim = "1";
  optr->Arg_Car[3].type_sample = "any";
  optr->Arg_Car[3].sample = "any";
  optr->Arg_Car[3].unite = "celsius";

  /* rn */
  optr->Arg_Car[4].direction = DIR_IN;
  optr->Arg_Car[4].categorie = VECTOR;
  optr->Arg_Car[4].typ = ATYC_IF32;
  optr->Arg_Car[4].array_dim = "1";
  optr->Arg_Car[4].type_sample = "any";
  optr->Arg_Car[4].sample = "any";
  optr->Arg_Car[4].unite = "W/m2";

  /* phi0 */
  optr->Arg_Car[5].direction = DIR_IN;
  optr->Arg_Car[5].categorie = VECTOR;
  optr->Arg_Car[5].typ = ATYC_IF32;
  optr->Arg_Car[5].array_dim = "1";
  optr->Arg_Car[5].type_sample = "any";
  optr->Arg_Car[5].sample = "any";
  optr->Arg_Car[5].unite = "W/m2";

  /* hveg */
  optr->Arg_Car[6].direction = DIR_IN;
  optr->Arg_Car[6].categorie = VECTOR;
  optr->Arg_Car[6].typ = ATYC_IF32;
  optr->Arg_Car[6].array_dim = "1";
  optr->Arg_Car[6].type_sample = "any";
  optr->Arg_Car[6].sample = "any";
  optr->Arg_Car[6].unite = "m";

  /* hbas */
  optr->Arg_Car[7].direction = DIR_IN;
  optr->Arg_Car[7].categorie = VECTOR;
  optr->Arg_Car[7].typ = ATYC_IF32;
  optr->Arg_Car[7].array_dim = "1";
  optr->Arg_Car[7].type_sample = "any";
  optr->Arg_Car[7].sample = "any";
  optr->Arg_Car[7].unite = "m";

  /* p */
  optr->Arg_Car[8].direction = DIR_IN;
  optr->Arg_Car[8].categorie = VECTOR;
  optr->Arg_Car[8].typ = ATYC_IF32;
  optr->Arg_Car[8].array_dim = "1";
  optr->Arg_Car[8].type_sample = "any";
  optr->Arg_Car[8].sample = "any";
  optr->Arg_Car[8].unite = "hPa";

  /* humid */
  optr->Arg_Car[9].direction = DIR_IN;
  optr->Arg_Car[9].categorie = VECTOR;
  optr->Arg_Car[9].typ = ATYC_IF32;
  optr->Arg_Car[9].array_dim = "1";
  optr->Arg_Car[9].type_sample = "any";
  optr->Arg_Car[9].sample = "any";
  optr->Arg_Car[9].unite = "%";

  /* premier param. de sortie : Hs */
  optr->Arg_Car[10].direction = DIR_OUT;
  optr->Arg_Car[10].categorie = VECTOR;
  optr->Arg_Car[10].typ = ATYC_IF32;
  optr->Arg_Car[10].array_dim = "1";
  optr->Arg_Car[10].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[10].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[10].sample = "$Arg1.sample";
  optr->Arg_Car[10].ref_time = "$Arg1.ref_time";
  optr->Arg_Car[10].unite = "W/m2";
  optr->Arg_Car[10].misval = "-999";
  optr->Arg_Car[10].famille = " \"flux\" ";

  /*  le */
  optr->Arg_Car[11].direction = DIR_OUT;
  optr->Arg_Car[11].categorie = VECTOR;
  optr->Arg_Car[11].typ = ATYC_IF32;
  optr->Arg_Car[11].array_dim = "1";
  optr->Arg_Car[11].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[11].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[11].sample = "$Arg1.sample";
  optr->Arg_Car[11].ref_time = "$Arg1.ref_time";
  optr->Arg_Car[11].unite = "W/m2";
  optr->Arg_Car[11].misval = "-999";
  optr->Arg_Car[11].famille = " \"flux\" ";

  /*  z0 */
  optr->Arg_Car[12].direction = DIR_OUT;
  optr->Arg_Car[12].categorie = VECTOR;
  optr->Arg_Car[12].typ = ATYC_IF32;
  optr->Arg_Car[12].array_dim = "1";
  optr->Arg_Car[12].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[12].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[12].sample = "$Arg1.sample";
  optr->Arg_Car[12].ref_time = "$Arg1.ref_time";
  optr->Arg_Car[12].unite = "m";
  optr->Arg_Car[12].misval = "-999";
  optr->Arg_Car[12].famille = " \"turbulence\" ";

  /*  vlmon : longueur de Monin Obukhov  */
  optr->Arg_Car[13].direction = DIR_OUT;
  optr->Arg_Car[13].categorie = VECTOR;
  optr->Arg_Car[13].typ = ATYC_IF32;
  optr->Arg_Car[13].array_dim = "1";
  optr->Arg_Car[13].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[13].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[13].sample = "$Arg1.sample";
  optr->Arg_Car[13].ref_time = "$Arg1.ref_time";
  optr->Arg_Car[13].unite = "m";
  optr->Arg_Car[13].misval = "-999";
  optr->Arg_Car[13].famille = " \"turbulence\" ";

  /*  u* */
  optr->Arg_Car[14].direction = DIR_OUT;
  optr->Arg_Car[14].categorie = VECTOR;
  optr->Arg_Car[14].typ = ATYC_IF32;
  optr->Arg_Car[14].array_dim = "1";
  optr->Arg_Car[14].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[14].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[14].sample = "$Arg1.sample";
  optr->Arg_Car[14].ref_time = "$Arg1.ref_time";
  optr->Arg_Car[14].unite = "m";
  optr->Arg_Car[14].misval = "-999";
  optr->Arg_Car[14].famille = " \"flux\" ";

  /*  t* */
  optr->Arg_Car[15].direction = DIR_OUT;
  optr->Arg_Car[15].categorie = VECTOR;
  optr->Arg_Car[15].typ = ATYC_IF32;
  optr->Arg_Car[15].array_dim = "1";
  optr->Arg_Car[15].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[15].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[15].sample = "$Arg1.sample";
  optr->Arg_Car[15].ref_time = "$Arg1.ref_time";
  optr->Arg_Car[15].unite = "Celsius";
  optr->Arg_Car[15].misval = "-999";
  optr->Arg_Car[15].famille = " \"flux\" ";

  /*  flag */
  optr->Arg_Car[16].direction = DIR_OUT;
  optr->Arg_Car[16].categorie = VECTOR;
  optr->Arg_Car[16].typ = ATYC_IF32;
  optr->Arg_Car[16].array_dim = "1";
  optr->Arg_Car[16].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[16].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[16].sample = "$Arg1.sample";
  optr->Arg_Car[16].ref_time = "$Arg1.ref_time";
  optr->Arg_Car[16].unite = "";
  optr->Arg_Car[16].misval = "-999";
  optr->Arg_Car[16].famille = "\"controle\"";
}
