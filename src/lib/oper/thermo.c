/****************************************************
* $Id$
*
* LIBRARY      thermo.c   FUNCTIONS   ANSI-C
*
* PURPOSE      Thermodynamics functions 
*
* DESCRIPTION  Fonctions Thermodynamiques courantes
*
*	       Librement inspiré des bibliotheques thermo 
*	       du CAM, de 4M et des algorithmes recommandés 
*              par P. Durand (note pour PYREX). On essaie de citer 
*              les références originales a chaque fois. 
*
* VERSION      $Revision$
*
* ARGUMENTS   
*
* ENTRY        void (*ew)(const float , float *);
*              void ew_PYREX (const float tempe, float *ewt);
*              void ew_AFNOR (const float tempe, float *ewt)
*              void ew_Bolton (const float tempe, float *ewt)
*              void inv_ew_Bolton (const float ewt_Bolton, float *T_Bolton)
*              void ew_abadie (const float tempe, float *ewt)
*              void ewi_PYREX (const float tempe, float *eit);
*              void ewi_abadie (const float tempe, float *eit)
*              void ewi_AFNOR (const float tempe, float *eit)
*              void clw (const float tempe, float *lw)
*              void rmel_Td (const float Td, const float Ps, float *rapm)
*              void rmel_Td_hybride (const float Td, const float Ps, float *rapm)
*              void rmel_Hu (float Hum, float T, float Ps, float *rapm);
*              void Hu_rmel (const float Rap_M, const float T, const float Ps, float *Hum)
*              void Hu_rmel_hybride (const float Rap_M, const float T, const float Ps, float *Hum)
*              void tpot (float tempe, float ps, const float r_sur_cp, float *tp);
*              void tpot_Bolton (float Ps, float tempe, float Pcalc, float *TpBolton);
*              void tpoteq (float tempe, float tp, float rapm, const float cp, float *tpe);
*              void tpoteq_Bolton (float Ps, float tempe, float Pcalc, float *TpeqBolton);
*              void tvir (float tempe, float rapm, float *Tvir);
*              void cp_hum (const float cpa, float rapm, float *cp_h);
*              void rsurcp_hum (float rasurcpa, float rapm, float *rsurcp_h);
*              void tcond (float tempe, float Hum, float *Tcond);
*              void pcond (float Ps, float tempe, float Hum, float *Pcond);
*              void twcurv (float Ps, float tempe, float Pcalc, float *Twcurv);
*     
* SUBPROGRAMS   
*
* FILES        
*
* REFERENCES   Indiquée 
*
* CHANGES      1.2 minor cosmetics in the code and comments.
*	       1.3 correction d'une erreur dans le calcul de
*	           ew et ewi : T0 vaut 273.16 et non pas 273.6.
*		   (06/11/1997)
*
* COPYRIGHT    Meteo-France/CNRM.
*
* AGREEMENT    + Utilisation libre à condition de ne pas ôter les
*              références originales et de ne pas raccourcir l'historique.
*              + En cas d'ajout et/ou de correction, en transmettre une
*              copie à CNRM/GMEI/TRAMM
*              + Citer l'origine en cas d'utilisation explicite.
*#########################################################################*/
/*########################################################################*/
#include <math.h>
#include <stdio.h>
#include <string.h>
#include <ctype.h>
#include <strings.h>

#include <gene.h>

#ifndef K_T0
#define K_T0 (273.15)
#endif

#define TWCURV_ECHEC (-999.)
#define TPOTEQ_BOLTON_ECHEC (-999.)


/** Calcul de la tension de vapeur saturante / eau liquide
 *
 * @param tempe : température pour laquelle faire le calcul (Kelvin)
 * @param ewt : pointeur vers le résultat (en hPa)
 *
 * Références : algos. de P. Durand, pour PYREX.
 * 
 * Pas de référence plus précise. On a vérifié (06/11/1997)
 * que ce ne sont pas les "smithonians tables".
 * C'est très proche de Goff-Gratch(1946), tel qu'on peut aussi 
 * le trouver dans les manuels OMM de 1966.
 *****************************************************************
 */
void
ew_PYREX (const float tempe,	/*-- TEMPE en Kelvins  --*/
	  float *ewt)		/*-- en hPa   -----------*/
{
  double r1 = 23.832256;
  double r2 = -2949.076;
  double r3 = -5.02808;
  double r4 = -0.00015148;
  double r5 = 0.00042861;
  double r6 = 8.3040;
  double r7 = -4.76967;
  double T0 = 273.16;

  double t, ten1;

  t = (double) tempe;
  ten1 = r1 + r2 / t + r3 * log10 (t) + r4 * pow (10.0, r6 * (1. - t / T0))
    + r5 * pow (10.0, r7 * (T0 / t - 1.));

  *ewt = (float) pow (10., ten1);
}


/** Calcul de la tension de vapeur saturante par rapport à l'eau liquide
 *
 * N'est plus utilisée couramment, mais présente ici pour des raisons
 * historiques.
 *
 * tempe en Kelvins, résultat en hPa.
 */
void
ew_abadie (const float tempe, float *ewt)
{
  double a0 = 19.1566;
  double a1 = -4061.30;
  double a2 = -184965;

  *ewt = (float) exp (a0 + (a1 + a2 / tempe) / tempe);
}

/** Calcul de la tension de vapeur saturante par rapport à l'eau liquide
 *
 * Nous ne l'utilisons pas couramment; mais elle peut servir.
 * Reference : norme AFNOR NFX15-110, page 12
 * ATTENTION : tempe en Kelvins, résultat en hPa.
 */
void
ew_AFNOR (float tempe, float *ewt)
{
  double a1 = 21.2409642;
  double a0 = -6096.9385;
  double a2 = -2.711193e-2;
  double a3 = 1.673952e-5;
  double a4 = 2.433502;

  double T, tmp;

  T = tempe;
  tmp = a0 / T + a1 + (a2 + a3 * T) * T + (a4 * log (T));

  *ewt = (float) exp (tmp) / 100;
}

/**  Calcul de la tension de vapeur saturante par rapport à l'eau liquide, en fct de 
 * la température.
 *
 *  La réference exacte est : Bolton, 1980, M.W.R. vol. 108  p. 1047, eq. 10
 *
 *  C'est une formule du style de celle de Tetens, qui a l'avantage
 * d'etre simple à calculer, et qui a été re-calculée pour s'adapter
 * aux travaux de Wexler(1976) et atteindre ainsi une précision de 0.3%
 * entre -35 degC et +35 degC. On notera que -35 < 0, et que cette
 * formule cherche donc à couvrir aussi les valeurs négatives.
 *
 * *ATTENTION* aux unités :
 *    1) les coeffs ont été transformés pour que la tempé soit
 * exprimée en Kelvin, comme dans tous les autres programmes ew() de
 * cette bibliotheque.
 *    2) Pour les pressions partielles, Bolton travaille en mb (hPa)
 * la formule n'a pas été modifiée : si le programme appelant travaille
 * en unités SI et a besoin de Pascal, ne pas oublier de multiplier par 100.
 * 
 * @param tempe : T, en Kelvins
 * @param ewt : ew(T), en hPa
*/
void
ew_Bolton (float tempe, float *ewt)
{
  double a0 = 4826.56;		/* 273.15 * 17.67 */
  double a1 = 17.67;		/* le coeff originel */
  double b = 29.65;		/* 273.15 - 243.5 */

  *ewt = (float) 6.112 *exp ((a1 * tempe - a0) / (tempe - b));
}

/** Calcul de la temperature correspondant à une tension de vapeur saturante 
 *
 * Fonction réciproque de la précédente.
 *
 *   La formule employée ici a été recalculée par inversion de la 
 * fonction directe, et donne un résultat équivalent à l'équation 11,
 * p 1047 de l'article : Bolton, 1980, M.W.R. vol. 108.
 *
 * L'auteur indique une précision de 0.03°C sur la gamme -35 <= T <+35 °C
 *
 * *ATTENTION* aux unités :
 *    1) les coeffs ont été transformés pour que la tempé soit
 * exprimée en Kelvin, comme dans tous les autres programmes ew() de
 * cette bibliotheque.
 *    2) Bolton travaille avec des les pressions partielles, exprimées
 * en mb (hPa). Cette fonction attend une tension de vapeur exprimée en
 * unité SI (Pa), et utilise donc ew / 100.
 *
 * @param ewt_Bolton : e, en Pa
 * @param T_Bolton : T tel que ew(T) = e, en Kelvin
 *
 */
void
inv_ew_Bolton (float ewt_Bolton, float *T_Bolton)
{
  double a0 = 4826.56;		/* 273.15 * 17.67 */
  double a1 = 17.67;		/* le coeff originel */
  double b = 29.65;		/* 273.15 - 243.5 */

  *T_Bolton =
    (float) ((b * log (ewt_Bolton / (100 * 6.112)) -
	      a0) / (log (ewt_Bolton / (100 * 6.112)) - a1));

}


/** Calcul de la tension de vapeur saturante par rapport à la glace
 *
 * Références : algos. de P. Durand, pour PYREX.
 * 
 ** Pas de référence plus précise. On a vérifié (06/11/1997)
 ** que ce ne sont pas les "smithonians tables".
 *****************************************************************
 */
void
ewi_PYREX (const float tempe,	/*--- TEMPE en Kelvin ---*/
	   float *eit)	/*--- en hPa          ---*/
{
  double r9 = -9.09718;
  double r10 = -3.56654;
  double r11 = 0.876793;
  double r12 = 6.10714;
  double T0 = 273.16;

  double t, ten2;

  t = (double) tempe;
  ten2 =
    r9 * (T0 / t - 1.) + r10 * log10 (T0 / t) + r11 * (1. - t / T0) +
    log10 (r12);

  *eit = (float) pow (10., ten2);
}


/** Calcul de la tension de vapeur saturante par rapport à la glace
 *
 ** N'est plus utilisée couramment, mais présente ici pour des raisons
 ** historiques.
 */
void
ewi_abadie (const float tempe, float *eit)
{
  double a0 = 24.3252;
  double a1 = -6150.205;

  *eit = (float) exp (a0 + a1 / tempe);
}


/**
 *
 * Nous ne l'utilisons pas couramment; mais elle peut servir.
 * Reference : norme AFNOR NFX15-110, page 12
 *      tempe en Kelvins, résultat en hPa.
 */
void
ewi_AFNOR (const float tempe, float *eit)
{
  const double a1 = 29.32707;
  const double a0 = -6024.52852;
  const double a2 = 1.0613868e-2;
  const double a3 = -1.3198825e-5;
  const double a4 = -0.49382577;

  double T, tmp;

  T = tempe;
  tmp = a0 / T + a1 + (a2 + a3 * T) * T + (a4 * log (T));

  *eit = (float) exp (tmp) / 100;
}

/** Calcul de la tension de vapeur saturante par rapport à la glace
 *
 * @param tempe : température pour laquelle faire le calcul (Kelvin)
 * @param ewt : pointeur vers le résultat (hPa)
 *
 *   Référence : OMM, Guide des instruments et méthodes 
 * d'observation météorologique (OMM-8), sixième édition, 
 * 1996, annexe 4.B. (dont la formule est en °C et hPa).
 *
 */
void
ewi_OMM (float tempe, float *eit)
{
  const double a0 = 6.112;
  const double a1 = 22.46;
  const double a2 = 272.62;
  double t_C;

  t_C = tempe - 273.15;
  *eit = a0 * exp (a1 * t_C / (a2 + t_C));
}

/** Calcul de la température correspondant à une tension de vapeur
 * saturante au-dessus de la glace.
 *
 * Fonction réciproque de la précédente.
 *
 * @param ei : Tension de vapeur/glace (hPa)
 * @param tempe : température pour laquelle ei(T) = ei, en Kelvin
 *
 *   Référence : OMM, Guide des instruments et méthodes 
 * d'observation météorologique (OMM-8), sixième édition, 
 * 1996, annexe 4.B. (dont la formule est en °C et hPa).
 *
 */
void
inv_ewi_OMM (float ei, float *tempe)
{
  const double a0 = 6.112;
  const double a1 = 22.46;
  const double a2 = 272.62;
  double log_tmp;

  log_tmp = log (ei / a0);

  *tempe = (a2 * log_tmp / (a1 - log_tmp)) + 273.15;
}

/**************************************
 *  Déclaration de "ew_ptr" comme un pointeur sur le type de fonction
 * utilisé pour tous les "ew_xxx"
 * Cela permet de changer de fonction en une seule instruction :
 * ew_ptr = ew_xxx;
 */
void (*ew_ptr) (const float, float *) = ew_PYREX;
void (*ewi_ptr) (const float, float *) = ewi_PYREX;

/** Fonction d'indirection.
 *  Utilise le pointeur ew_ptr défini ci-dessus.
 */
void
ew (const float tempe, float *ewt)
{
  ew_ptr (tempe, ewt);
}

/** Fonction d'indirection.
 */
void
ewi (const float tempe, float *ewit)
{
  ewi_ptr (tempe, ewit);
}


/**  Une fonction qui retourne un pointeur vers la
 * fonction de la série ew_* () qui correspond au nom
 * passé en argument (ou NULL si aucune ne correspond)
 *
 * Techniquement, c'est une fonction qui prend un argument de type 
 * "const char *" et qui retourne un pointeur vers une 
 * fonction (const float, pointer to float) returning void
 */
void (*ew_function (const char *formule_name)) (const float, float *)
{
  if (formule_name == NULL)
    {				/* Fonction par défaut */
      return ew_PYREX;
    }

  /* Les "blancs" en début de chaîne sont ignorés */
  while ((*formule_name == ' ') || (*formule_name == '\t'))
    {
      formule_name++;
    }

  /* Si chaîne vide, fonction en usage actuellement */
  if (*formule_name == 0)
    {
      return ew_ptr;
    }

  if (!strncasecmp_blankend (formule_name, "pyrex", strlen ("pyrex")))
    {
      return ew_PYREX;
    }
  else if (!strncasecmp_blankend (formule_name, "afnor", strlen ("afnor")))
    {
      return ew_AFNOR;
    }
  else if (!strncasecmp_blankend (formule_name, "abadie", strlen ("abadie")))
    {
      return ew_abadie;
    }
  else if (!strncasecmp_blankend (formule_name, "bolton", strlen ("bolton")))
    {
      return ew_Bolton;
    }
  else
    {
      return NULL;
    }
}

/** Une fonction qui retourne un pointeur vers la
 * fonction de la série ewi_* () qui correspond au nom
 * passé en argument (ou NULL si aucune ne correspond)
 *
 * Techniquement, c'est une fonction qui prend un argument de type 
 * "const char *" et qui retourne un pointeur vers une 
 * fonction (const float, pointer to float) returning void
 */
void (*ewi_function (const char *formule_name)) (const float, float *)
{
  if (formule_name == NULL)
    {				/* Fonction par défaut */
      return ewi_PYREX;
    }

  /* Les "blancs" en début de chaîne sont ignorés */
  while ((*formule_name == ' ') || (*formule_name == '\t'))
    {
      formule_name++;
    }

  /* Si chaîne vide, fonction en usage actuellement */
  if (*formule_name == 0)
    {
      return ewi_ptr;
    }
  if (!strncasecmp_blankend (formule_name, "pyrex", strlen ("pyrex")))
    {
      return ewi_PYREX;
    }
  else if (!strncasecmp_blankend (formule_name, "afnor", strlen ("afnor")))
    {
      return ewi_AFNOR;
    }
  else if (!strncasecmp_blankend (formule_name, "abadie", strlen ("abadie")))
    {
      return ewi_abadie;
    }
  else
    {
      return NULL;
    }
}

/** Change les fonctions ew(T) et ewi(T) en usage.
 */
int
set_ew_formula (const char *formule_name)
{
  void (*ew_tmp) (const float, float *);

  ew_tmp = ew_function (formule_name);
  if (ew_tmp == NULL)
    return 1;
  ew_ptr = ew_tmp;

  ew_tmp = ewi_function (formule_name);
  if (ew_tmp == NULL)
    return 2;
  ewi_ptr = ew_tmp;
  return 0;
}

/** Calcul de la chaleur latente de vaporisation d'une particule
 * definie par sa temperature en Kelvin.
 *
 * Reference : Bolton - 1980 - mwr vol.108 p.1047
 *  Id. a la fct clw.f libmto Puech d. (sauf unites)
 */
void
clw (const float tempe,	/*-- Temperature de l'air en Kelvin --*/
     float *lw)		/*-- Chaleur latente en J/kg --*/
{

  float tc;
  tc = tempe - 273.15;
  *lw = (2.501 - (.00237 * tc)) * 1.e+06;

}

/** Calcul d'un rapport de mélange en vapeur d'eau 
 * à partir d'une température de point de rosée.
 * 
 * Le calcul de la tension de vapeur ( e = ew(Td) )
 * se fait TOUJOURS par rapport à de l'eau liquide.
 * Pour un choix eau/glace selon valeur de Td, utiliser
 * la fonction rmel_Td_hybride().
 */
void
rmel_Td (const float Td,	/*-- Td en Kelvin  --*/
	 const float Ps,	/*-- Ps en hPa     --*/
	 float *rapm)		/*-- en g/Kg       --*/
{
  float ewtd;

  ew (Td, &ewtd);

  *rapm = 622. * ewtd / (Ps - ewtd);	/*  rapport de melange en g/kg */
}

/**Calcul d'un rapport de mélange en vapeur d'eau 
 * à partir d'une température de point de rosée.
 * 
 * Le calcul de la tension de vapeur ( e = ew(Td) )
 * se fait par rapport à de l'eau liquide ou de la glace,
 * selon valeur de Td.
 * 
 */
void
rmel_Td_hybride (const float Td,	/*-- Td en Kelvin  --*/
		 const float Ps,/*-- Ps en hPa     --*/
		 float *rapm)	/*-- en g/Kg       --*/
{
  float ewtd;

  if (Td < 273.15)
    ewi (Td, &ewtd);
  else
    ew (Td, &ewtd);

  *rapm = 622. * ewtd / (Ps - ewtd);	/*  rapport de melange en g/kg */
}


/**Calcul d'un rapport de mélange en vapeur d'eau 
 * à partir d'une humidité relative.
 * 
 * Le calcul de la tension de vapeur saturante ( ew(T) )
 * se fait TOUJOURS par rapport à de l'eau liquide.
 * 
 */
void
rmel_Hu (const float Hum,	/*-- Hum en pour_cent -*/
	 const float T,		/*-- T en Kelvin !!  --*/
	 const float Ps,	/*-- Ps en hPa       --*/
	 float *rapm)		/*-- en g/Kg         --*/
{
  float ewt, e;

  ew (T, &ewt);

  e = ewt * Hum / 100.0;
  *rapm = 622. * e / (Ps - e);	/*  rapport de melange en g/kg */
}


/**Calcul d'une humidité relative à partir d'un rapport
 *  de mélange en vapeur d'eau.
 * 
 * Le calcul de la tension de vapeur saturante ( ew(T) )
 * se fait TOUJOURS par rapport à de l'eau liquide.
 */
void
Hu_rmel (const float Rap_M,	/*-- en g/kg    --*/
	 const float T,		/*-- T en Kelvin !! --*/
	 const float Ps,	/*-- Ps en hPa     --*/
	 float *Hum)		/*-- en %          --*/
{
  float ewt, e;

  ew (T, &ewt);

  /* Réciproque de : rapm = 622. * e / (Ps - e)  */
  e = Ps * Rap_M / (Rap_M + 622.);

  *Hum = 100 * e / ewt;
}

/** Calcul d'une humidité relative à partir d'un rapport
 *  de mélange en vapeur d'eau.
 * 
 * Le calcul de la tension de vapeur saturante ( ew(T) )
 * se fait par rapport à de l'eau liquide ou la glace,
 * selon que Ts > Seuil ou Ts<= Seuil
 *
 * Cela est contraire aux usages de mesures météorologiques
 * opérationnelles (par exemple les radiosondages), pour
 * lesquels l'humidité relative est toujours définie par
 * rapport à l'eau liquide, même à des températures
 * inférieures à 0°C (cf. le Guide des instruments et des méthodes
 * d'observation météorologique).
 * 
 */
void
Hu_rmel_hybride (const float Rap_M,	/*-- en g/kg    --*/
		 const float T,	/*-- T en Kelvin !! --*/
		 const float Ps,/*-- Ps en hPa     --*/
		 float *Hum)	/*-- en %          --*/
{
  float ewt, e;

  /* Pb. de détermination du seuil... */

  if (T < 273.15)
    ewi (T, &ewt);
  else
    ew (T, &ewt);

  /* Réciproque de : rapm = 622. * e / (Ps - e)  */
  e = Ps * Rap_M / (Rap_M + 622.);

  *Hum = 100 * e / ewt;
}

/************* Calcul de la temperature potentielle ************
 *       tp=t*(1000/ps) **(r/Cp) 
 * 
 * Référence : Triplet-Roche (page 46 de l'édition de 1997).
 ***************************************************************
 */
void
tpot (const float tempe,	/*-- tempe et tp en Kelvin  --*/
      const float ps,		/*-- ps en hPa              --*/
      const float r_sur_cp, float *tp)
{
  double t, x, y;

  t = (double) tempe;
  y = (double) 1000. / ps;
  x = (double) r_sur_cp;

  *tp = (float) t *pow (y, x);
}

/************* Calcul de la temperature potentielle equivalente ***
 *          tpe = tp*(1+rapm*L/(Cp*T)) en kelvin 
 * avec : tp = tempe potentielle
 *        rapm = rapport de melange en  g/Kg
 *        L = 2497-2.34*T (pour T en Celsius)
 *        T d'etat en Kelvin
 *
 *  Directement copiée de la routine du CAM, qui est identique à 
 * l'algo de P. Durand (PYREX). 
 * Utiliser de préférence la formule de Bolton (MWR, 1980), mais
 * qui utilise une humidité relative....
 ******************************************************************
 */
void
tpoteq (const float tempe,	/*-- tempe en Kelvins             ---*/
	const float tp,		/*-- tempe potentielle en Kelvins ---*/
	const float rapm,	/*-- en g/Kg  ---*/
	const float cp,		/*-- les constantes "variables"   ---*/
	float *tpe)		/*-- resultat en kelvins          ---*/
{
  double t, l;

  t = tempe * cp;
/* La formule initiale etait :
   l = 2497. - 2.34 * (tempe - K_T0);
   On a enleve le terme "T0"  */
  l = 3136.17 - 2.34 * tempe;
  *tpe = tp * (1.0 + rapm * l / t);
}

/************* Calcul de la temperature virtuelle ***************
 *              tvir = t*(1+1.608rapm)/(1+rapm) 
 *
 * Référence : Triplet-Roche (page 56 de l'édition de 1997).
 ****************************************************************
 */
void
tvir (const float tempe,	/*-- tempe et tvir en Kelvins        --*/
      const float rapm,		/*-- rapm: rapport de melange en Kg/Kg -*/
      float *Tvir)
{
  double x, y;

  y = 1 + 1.608 * rapm;
  x = 1 + rapm;
  *Tvir = tempe * y / x;
}

/********** Calcul de la Chal. mass. a P cste de l'air humide *****
 *
 * References : Triplet-Roche de 1971, p. 55-56
 ******************************************************************
 */
void
cp_hum (const float cpa,	/*-- Chal. massique a Press. cte de Air Sec */
	const float rapm,	/*-- rapm: rapport de melange en Kg/Kg -*/
	float *cp_h)
{
  *cp_h = cpa * (1 + 1.85 * rapm) / (1 + rapm);
}

/********** Calcul de la Chal. mass. a P cste de l'air humide *****
 ** 
 ** References : Triplet-Roche de 1971, p. 55-56
 ******************************************************************
 */
void
rsurcp_hum (const float rasurcpa,	/*-- r/cp, pour l'Air Sec */
	    const float rapm,		/*-- rapm: rap. de melange en Kg/Kg */
	    float *rsurcp_h)
{
  *rsurcp_h = rasurcpa * (1 + 1.608 * rapm) / (1 + 1.85 * rapm);
}

/********** Calcul de la temperature du point de condensation 
 * d'une particule definie par : tempe , humidite.
 * 
 * Tempé en Kelvin, Humidité en %
 * 
 * Reference : Bolton - 1980 - mwr vol.108 p.1046
 * Id. a la fct tcond.f libmto Puech d. (sauf unites)
 *****************************************************
 */
void
tcond (float tempe,	/*-- Temperature de l'air en Kelvin  --*/
       float Hum,	/*-- Humidite de l'air en %          --*/
       float *Tcond)
{
  double a, b;
  a = 1. / (tempe - 55.);
  b = log (Hum / 100.) / 2840.;
  *Tcond = (1. / (a - b)) + 55.;
}

/*********  Calcul de la temperature potentielle de l'air humide
 *  d'une particule definie par : pression, temperature et humidite 
 * 
 * Unités : *** temperatures en Kelvin******
 *
 * Appel : rmel_Hu (calcul du rapport de melange)
 *
 * Reference : Bolton - 1980 - mwr vol.108 p.1047 equation no 7
 ********************************
 */
void
tpot_Bolton (float Ps,		/*-- Pression de la particule d'air en hPa --*/
	     float tempe,	/*-- Temperature de l'air en Kelvin        --*/
	     float Hum,		/*-- Humidite de l'air en %                --*/
	     float *TpBolton)
{
  float rm;
  rmel_Hu (Hum, tempe, Ps, &rm);	/* en g/kg */
  *TpBolton = tempe * pow ((1000. / Ps), (0.2854 * (1 - 0.00028 * rm)));	/* Kelvin */
}


/**
 * --------------------------------------------------------------
 *    Calcul de la temperature potentielle equivalente
 * d'une particule definie par : pression, temperature et humidite.
 *
 *  Temperatures en Kelvin 
 *
 *  Appels : rmel_Hu (calcul du rapport de melange)
 *           tpot_Bolton (t. potentielle air humide)
 *           tcond (t. point de condensation)
 *
 * Reference : Bolton - 1980 - mwr vol.108 p.1052 equation no 43
 ************************************************
 */
void
tpoteq_Bolton (float Ps,	/*-- Pression de la particule d'air en hPa --*/
	       float tempe,	/*-- Temperature de l'air en Kelvin        --*/
	       float Hum,	/*-- Humidite de l'air en %                --*/
	       float *TpeqBolton)
{
  float rm, tl, Tpbolton;
  float b, c;

  rmel_Hu (Hum, tempe, Ps, &rm);	/* en g/kg */
  tpot_Bolton (Ps, tempe, Hum, &Tpbolton);	/* en Kelvin */
  tcond (tempe, Hum, &tl);	/* en Kelvin */
  b = (3.376 / tl) - 0.00254;
  c = 1 + 0.00081 * rm;
  *TpeqBolton = Tpbolton * exp (b * rm * c);	/* en Kelvin */
}

/********** Calcul de la pression du niveau de condensation
 * d'une particule definie par : pression, tempe et humidite.
 *
 * Tous les calculs sont en Kelvin
 *
 * Le calcul fait en 2 temps :
 *      1) calcul de Tcond par routine tcond (ci-dessus)
 *      2) calcul de P_cond par égalité des rapports de
 *        mélange entre les 2 niveaux.
 *
 *  Fonction largement inspirée de la fct pcond.f de la 
 * libmto Puech d. 
 *************************
 */
void
pcond (float Ps,	/*-- Pression de la particule d'air en hPa --*/
       float tempe,	/*-- Temperature de l'air en Kelvin        --*/
       float Hum,	/*-- Humidite de l'air en % --*/
       float *Pcond)
{
  float t1, ewt, e, ewt1;

  tcond (tempe, Hum, &t1);
  ew_Bolton (tempe, &ewt);
  e = ewt * Hum / 100.;
  ew_Bolton (t1, &ewt1);
  *Pcond = Ps * ewt1 / e;
}

/***** Calcul de la temperature le long d'une pseudo-adiabatique
 * definie par : pression, temperature du point de condensation.
 *
 * Toutes les tempe sont en Kelvin
 *
 * Reference : bibmet-ct,d8
 * Identique a la fct twcurv.f libmto Puech d (sauf unites)
 ******************************
 */
void
twcurv (float Ps,	/*-- Pression de la particule d'air en hPa --*/
	float tempe,	/*-- Temperature de l'air en Kelvin --*/
	float Pcalc,	/*-- Pression du niveau de calcul en hPa --*/
	float *Twcurv)
{
  int i;
  float rap, xk, a, b, dydx, de;
  float tc, e, cl, rop, fact, x, y, z;
  float cp = 1005.;
  float eps = .62198;
  float t0 = 273.15;
  float alpha = .28562;
  float criter = .05;

  *Twcurv = TWCURV_ECHEC;

  tc = tempe - t0;
  ew_Bolton (tempe, &e);
  rap = pow ((Pcalc / (Ps - e)), alpha);
  fact = eps / (cp * Pcalc);
  clw (tempe, &cl);
  rop = eps * cl * e / cp / Ps / tempe;
  x = tc;

  for (i = 0; i <= 50; i++)
    {

      ew_Bolton ((x + t0), &e);
      clw ((x + t0), &cl);
      de =
	(4.438099984e-1 +
	 x * (2.857002636e-2 +
	      x * (7.938054040e-4 +
		   x * (1.215215065e-6 +
			x * (1.036561403e-7 +
			     x * (3.532421810e-10 - x * 7.090244484e-13))))));
      xk = x + t0;
      if (e > 200.)
	return;

      a = tempe * rap * pow ((1. - e / Pcalc), alpha);
      b = exp (rop - cl * fact * e / xk);
      y = a * b - t0;

      if (y < -100.)
	return;

      /* Calcul de z = valeur absolue de (y-x) */
      if (y > x)
	{
	  z = y - x;
	}
      else
	{
	  z = x - y;
	}

      /* Test de "convergence" des temperatures x et y */
      if (z < criter)
	{
	  *Twcurv = y + t0;
	  return;
	}

      dydx =
	a * b * (-alpha * de / (Pcalc - e) + fact * cl * (e / xk - de) / xk);
      x = (y - x * dydx) / (1. - dydx);

    }

  *Twcurv = TWCURV_ECHEC;
  return;
}
