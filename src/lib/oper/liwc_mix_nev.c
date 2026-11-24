/*******************************************************************
* OPERATOR	liwc_mix_nev.c FUNCTION ANSI-C
* 
* PURPOSE 	liquid and iced water content from Nevzorov measurements.
*
* DESCRIPTION   Cette fonction calcule le contenu en eau liquide 
* 			et de glace à partir des données du Nevzorov
* 			Utilisation de la formule pour les nuages en
* 			phase mixte. 
* 
* VERSION       1.0
*
* ARGUMENTS 	
* 		IN 	float 	V_lc  lwc collector voltage	
* 		IN 	float 	I_lc  lwc collector intensity	
* 		IN 	float 	V_lr  lwc reference voltage	
* 		IN 	float 	I_lr  lwc reference intensity
* 		IN 	float 	V_tc  twc collector voltage	
* 		IN 	float 	I_tc  twc collector intensity	
* 		IN 	float 	V_tr  twc reference voltage	
* 		IN 	float 	I_tr  twc reference intensity
*		IN 	float 	Ta 	static air temperature (K or Celsius)
*		IN 	float 	Vp	true air speed (m/s)
*		IN 	float 	Sl	lwc collector surface (0.305 cm2 standard) 
*		IN 	float 	St	twc collector surface (0.503 cm2 standard) 
*		IN 	float 	Te 	Sensor temperature (K)
*		IN 	float 	kl	Dry air calibration coefficient 
*		IN 	float 	kt	Dry air calibration coefficient 
*		
*		OUT 	float 	LWC  	liquid water content (g/m3)	
*		OUT 	float 	IWC  	Ice content (g/m3)	
*
* ENTRY 	NONE
*
* SUBPROGRAMS	NONE
*
* REFERENCES 
*         Operating Manual
*         Nevzorov hot wire LWC/TWC Probe
*         (CWCM-U2.2)
*         Sky Tech resaerch Incorporated
*
* CHANGES      
*
* AUTHOR 	SAFIRE (Meteo-France/CNRS-INSU/CNES)
*
**********************************************************************/

#define _POSIX_SOURCE 1
#define _XOPEN_SOURCE 600

#include <stdio.h>
#include <string.h>
#include <math.h>

#include "unit.h"
#include "struct_oper.h"

void
liwc_mix_nev (unsigned long Nloop,
	      const float *V_lc,
	      const float *I_lc,
	      const float *V_lr,
	      const float *I_lr,
	      const float *V_tc,
	      const float *I_tc,
	      const float *V_tr,
	      const float *I_tr,
	      const float *Ta,
	      const float *Vp,
	      const float Sl,
	      const float St,
	      const float Te,
	      const float kl, const float kt, float *LWC, float *IWC)
{
  unsigned long i;
  int flag_cnvt_Ta;

  float Pl, Pt;
  float E_lw, E_tw, E_ti;
  float Beta, T0, x, y, CtoK, Ta_K;
  float x_Li, x_Lw;

  /* float Lw = 2260;            * chaleur latente de l'eau (T=100³C) J/g */
  float Cw = 4218;		/* chaleur specifique de l'eau J/g.K */
  float Li = 333;		/* chaleur latente de fonte de la glace J/g */
  float Ci = 2.1;		/* chaleur specifique de la glace J/g.K */
  float Pl0 = 0.4;		/* Offset empirique */
  float Pt0 = -1.17;		/* Offset empirique */

  T0 = 273.15;

  E_lw = 1.0;
  E_tw = 1.0;
  E_ti = 1.0;
  Beta = 0.11;

/* tempe en Kelvin ou Celsius */

  flag_cnvt_Ta = auto_tempe_unit (Nloop, Ta, &CtoK);
  /* cnvt_inf_Te = auto_tempe_unit (1, Te, &CtoK) */

  for (i = 0; i < Nloop; i++)
    {

      /* calcul des puissances */

      Ta_K = Ta[i] + CtoK;
      Pl = V_lc[i] * I_lc[i]/2.0 - (kl * V_lr[i] * I_lr[i]*2.0 + Pl0);
      Pt = V_tc[i] * I_tc[i]/2.0 - (kt * V_tr[i] * I_tr[i]*2.0 + Pt0);

      /* x_Lw = (Te - Ta_K) * Cw + Lw; */
      x_Lw = 2589;		/* Manuel page 14 : pas plus de  5% d'erreur. */
      x_Li = (T0 - Ta_K) * Ci + (Te - T0) * Cw + Li;
      /* x_Li = 1.13 * x_Lw;    * Korolev 1998. */

      /* Contenu en eau */
      x = Pl - Pt * (Beta * Sl / (E_ti * St));
      y = x_Lw * Sl * 1e-04 * Vp[i] * (E_lw - Beta * E_tw / E_ti);
      LWC[i] = x / y;

      /* Contenu en glace */
      x = Pt - Pl * (E_tw * St / (E_lw * Sl));
      y = x_Li * St * 1e-04 * Vp[i] * (E_ti - Beta * E_tw / E_lw);
      IWC[i] = x / y;
    }
  return;
}

/* fonction d'enrobage */

int
OP_liwc_mix_nev (unsigned long NbVal, void *ArgList[], char *DiagExec)
{
  int NCar;

  NCar = sprintf (DiagExec, 
                 "liwc_mix_nev (%ld ech), surf. col. liq = %g cm2, tot =%g, T= %gK; ",
                  NbVal, *((float *) ArgList[10]), *((float *) ArgList[11]),
		  *((float *) ArgList[12]));

  liwc_mix_nev (NbVal, (float *) ArgList[0],
		(float *) ArgList[1],
		(float *) ArgList[2],
		(float *) ArgList[3],
		(float *) ArgList[4],
		(float *) ArgList[5],
		(float *) ArgList[6],
		(float *) ArgList[7],
		(float *) ArgList[8],
		(float *) ArgList[9],
		*((float *) ArgList[10]),
		*((float *) ArgList[11]),
		*((float *) ArgList[12]),
		*((float *) ArgList[13]),
		*((float *) ArgList[14]),
		(float *) ArgList[15], 

                (float *) ArgList[16]);
  return OP_OK;
}

void
ID_liwc_mix_nev (oper * optr)
{
  strcpy (optr->Nom, "liwc_mix_nev");
  optr->Version = "$Revision$";
  optr->Date = "$Date$";
  optr->fctptr = OP_liwc_mix_nev;
  optr->NbArg = 17;

  /*  V_lc */
  optr->Arg_Car[0].direction = DIR_IN;
  optr->Arg_Car[0].categorie = VECTOR;
  optr->Arg_Car[0].typ = ATYC_IF32;
  optr->Arg_Car[0].array_dim = "1";
  optr->Arg_Car[0].type_sample = "any";
  optr->Arg_Car[0].sample = "any";
  optr->Arg_Car[0].unite = "volt";

  /* I_lc */
  optr->Arg_Car[1].direction = DIR_IN;
  optr->Arg_Car[1].categorie = VECTOR;
  optr->Arg_Car[1].typ = ATYC_IF32;
  optr->Arg_Car[1].array_dim = "1";
  optr->Arg_Car[1].type_sample = "any";
  optr->Arg_Car[1].sample = "any";
  optr->Arg_Car[1].unite = "ampere";

  /* V_lr */
  optr->Arg_Car[2].direction = DIR_IN;
  optr->Arg_Car[2].categorie = VECTOR;
  optr->Arg_Car[2].typ = ATYC_IF32;
  optr->Arg_Car[2].array_dim = "1";
  optr->Arg_Car[2].type_sample = "any";
  optr->Arg_Car[2].sample = "any";
  optr->Arg_Car[2].unite = "volt";

  /* I_lr */
  optr->Arg_Car[3].direction = DIR_IN;
  optr->Arg_Car[3].categorie = VECTOR;
  optr->Arg_Car[3].typ = ATYC_IF32;
  optr->Arg_Car[3].array_dim = "1";
  optr->Arg_Car[3].type_sample = "any";
  optr->Arg_Car[3].sample = "any";
  optr->Arg_Car[3].unite = "ampere";

  /*  V_tc */
  optr->Arg_Car[4].direction = DIR_IN;
  optr->Arg_Car[4].categorie = VECTOR;
  optr->Arg_Car[4].typ = ATYC_IF32;
  optr->Arg_Car[4].array_dim = "1";
  optr->Arg_Car[4].type_sample = "any";
  optr->Arg_Car[4].sample = "any";
  optr->Arg_Car[4].unite = "volt";

  /*  I_tc */
  optr->Arg_Car[5].direction = DIR_IN;
  optr->Arg_Car[5].categorie = VECTOR;
  optr->Arg_Car[5].typ = ATYC_IF32;
  optr->Arg_Car[5].array_dim = "1";
  optr->Arg_Car[5].type_sample = "any";
  optr->Arg_Car[5].sample = "any";
  optr->Arg_Car[5].unite = "ampere";

  /*  V_tr */
  optr->Arg_Car[6].direction = DIR_IN;
  optr->Arg_Car[6].categorie = VECTOR;
  optr->Arg_Car[6].typ = ATYC_IF32;
  optr->Arg_Car[6].array_dim = "1";
  optr->Arg_Car[6].type_sample = "any";
  optr->Arg_Car[6].sample = "any";
  optr->Arg_Car[6].unite = "volt";

  /*  I_tr */
  optr->Arg_Car[7].direction = DIR_IN;
  optr->Arg_Car[7].categorie = VECTOR;
  optr->Arg_Car[7].typ = ATYC_IF32;
  optr->Arg_Car[7].array_dim = "1";
  optr->Arg_Car[7].type_sample = "any";
  optr->Arg_Car[7].sample = "any";
  optr->Arg_Car[7].unite = "ampere";

  /* Ta */
  optr->Arg_Car[8].direction = DIR_IN;
  optr->Arg_Car[8].categorie = VECTOR;
  optr->Arg_Car[8].typ = ATYC_IF32;
  optr->Arg_Car[8].array_dim = "1";
  optr->Arg_Car[8].type_sample = "any";
  optr->Arg_Car[8].sample = "any";
  optr->Arg_Car[8].unite = "Celsius";

  /* Vp */
  optr->Arg_Car[9].direction = DIR_IN;
  optr->Arg_Car[9].categorie = VECTOR;
  optr->Arg_Car[9].typ = ATYC_IF32;
  optr->Arg_Car[9].array_dim = "1";
  optr->Arg_Car[9].type_sample = "any";
  optr->Arg_Car[9].sample = "any";
  optr->Arg_Car[9].unite = "m/s";

  /* Sl */
  optr->Arg_Car[10].direction = DIR_IN;
  optr->Arg_Car[10].categorie = COEFFICIENT;
  optr->Arg_Car[10].typ = ATYC_IF32;
  optr->Arg_Car[10].array_dim = "1";
  optr->Arg_Car[10].type_sample = NULL;
  optr->Arg_Car[10].sample = NULL;
  optr->Arg_Car[10].unite = "cm2";

  /* St */
  optr->Arg_Car[11].direction = DIR_IN;
  optr->Arg_Car[11].categorie = COEFFICIENT;
  optr->Arg_Car[11].typ = ATYC_IF32;
  optr->Arg_Car[11].array_dim = "1";
  optr->Arg_Car[11].type_sample = NULL;
  optr->Arg_Car[11].sample = NULL;
  optr->Arg_Car[11].unite = "cm2";

  /* Te */
  optr->Arg_Car[12].direction = DIR_IN;
  optr->Arg_Car[12].categorie = COEFFICIENT;
  optr->Arg_Car[12].typ = ATYC_IF32;
  optr->Arg_Car[12].array_dim = "1";
  optr->Arg_Car[12].type_sample = NULL;
  optr->Arg_Car[12].sample = NULL;
  optr->Arg_Car[12].unite = "kelvin";

  /* kl */
  optr->Arg_Car[13].direction = DIR_IN;
  optr->Arg_Car[13].categorie = COEFFICIENT;
  optr->Arg_Car[13].typ = ATYC_IF32;
  optr->Arg_Car[13].array_dim = "1";
  optr->Arg_Car[13].type_sample = NULL;
  optr->Arg_Car[13].sample = NULL;
  optr->Arg_Car[13].unite = "without";

  /* kt */
  optr->Arg_Car[14].direction = DIR_IN;
  optr->Arg_Car[14].categorie = COEFFICIENT;
  optr->Arg_Car[14].typ = ATYC_IF32;
  optr->Arg_Car[14].array_dim = "1";
  optr->Arg_Car[14].type_sample = NULL;
  optr->Arg_Car[14].sample = NULL;
  optr->Arg_Car[14].unite = "without";

  /* LWC */
  optr->Arg_Car[15].direction = DIR_OUT;
  optr->Arg_Car[15].categorie = VECTOR;
  optr->Arg_Car[15].typ = ATYC_IF32;
  optr->Arg_Car[15].array_dim = "1";
  optr->Arg_Car[15].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[15].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[15].sample = "$Arg1.sample";
  optr->Arg_Car[15].ref_time = "$Arg1.ref_time";
  optr->Arg_Car[15].unite = "gram/m3";
  optr->Arg_Car[15].famille = " \"eau_liquide\" ";
  optr->Arg_Car[15].name = " \"Contenu en eau liquide (Nevzorov) \" ";
  optr->Arg_Car[15].en_name = " \"Liquid water content (Nevzorov) \" ";

  /* IWC */
  optr->Arg_Car[16].direction = DIR_OUT;
  optr->Arg_Car[16].categorie = VECTOR;
  optr->Arg_Car[16].typ = ATYC_IF32;
  optr->Arg_Car[16].array_dim = "1";
  optr->Arg_Car[16].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[16].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[16].sample = "$Arg1.sample";
  optr->Arg_Car[16].ref_time = "$Arg1.ref_time";
  optr->Arg_Car[16].unite = "gram/m3";
  optr->Arg_Car[16].famille = " \"eau_liquide\" ";
  optr->Arg_Car[16].name = " \"Contenu en glace (Nevzorov)\" ";
  optr->Arg_Car[17].name = " \"Ice content (Nevzorov)\" ";
}
