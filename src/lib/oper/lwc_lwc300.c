/*******************************************************************
* OPERATOR	lwc_lwc300.c FUNCTION ANSI-C
* 
* PURPOSE 	computation of liquid water content from lwc300 data
*
* DESCRIPTION   Cette fonction calcule le contenu en eau liquide » 
*                partir des donn≈es issues d'une sonde lwc300. 
* 
* VERSION       1.4
*
* ARGUMENTS 	 IN 	float 	Pw	total power delivered to
*					the master coil (W)
*	 	
*		 IN 	float 	Ta 	static air temperature (K)
*		 IN 	float	Ps 	static air pressure (hPa)
*		 IN 	float 	Vp	true air speed (m/s)
*		 IN 	float 	l 	master coil's length (cm)
*		 IN 	float 	d 	master coil's diameter (cm)
*		 IN 	float 	Tw 	temperature of the wire (K)
*		
*		OUT 	float 	LWC  	liquid water content (g/m3)	
*
* ENTRY 	NONE
*
* SUBPROGRAMS	NONE
*
* REFERENCES 	DROPLET MEASUREMENT TECHNOLOGIES
* 		Particle Analysis and Display System (PADS)
*		Hotwire LWC Module Manual
*		DOC-0290 Rev A
*		PADS 3.5
*		Hotwire LWC Module 3.5.0
*
* COPYRIGHT 	Meteo-France
*		Centre National de Recherches Meteorologiques
*		GMEI/MMA
*		42, av. G. Coriolis
*		31057 	TOULOUSE cedex
*
**********************************************************************/

#define _POSIX_SOURCE 1
#define _XOPEN_SOURCE 600

#include <stdio.h>
#include <string.h>
#include <math.h>
#include "struct_oper.h"

int
lwc_lwc300 (unsigned long Nloop,
       const float *Pw,
       const float *Ta,
       const float *Ps,
       const float *Vp,
       const float l,
       const float d,
       const float *Tw,
       float *LWC)
{
     unsigned long i;

    float dens, Pdry, Pwet, TaCtoK, TwCtoK, Tair, Twir;
    float Tflm, Kd, Vd, Prd, Da, Re, Pd, Tb;
    float Kw, Vw, Prw, Dd, Lv, Pwc;

    float Kcst1 = 0.00264638;
    float Kcst2 = 418.68;
    float Kcst3 = 245.4;
    float Vcst1 = 0.0001718;
    float Vcst2 = 393.16;
    float Dcst = 0.348388;
    float Pcst1 = 0.26;
    float Pcst2 = 0.23885;
    float Tcst1 = 57.579;
    float Tcst2 = 199.53;
    float Lcst1 = 597.3;
    float Lcst2 = 0.000367;
    float Lcst3 = 0.167;
    float Fcst1 = 238850;
/*  float Lv = 2.264e6;*/		/* chaleur latente de l'eau (T=100≥C) */
    float c = 4218;		/* chaleur specifique de l'eau */
    float K0 = 273.16;

/* tempe en Kelvin ou Celsius */

    if (Ta[Nloop / 2] < 100.)
        TaCtoK = 273.15;
    else
        TaCtoK = 0.;
    fprintf (stderr, " Constante de conversion degre C en K : %f\n", TaCtoK);

/* La temperature du fil est donnÈe en Celsius */
    
    TwCtoK = 273.15;

    for (i = 0; i < Nloop; i++)
    {
/* Seuil de 3.0 Watt fixÈ arbitrairement et empiriquement */
        if ((*Vp > 50.) && (*Pw > 3.0))
        {
            Tair = *Ta + TaCtoK;
            Twir = *Tw + TwCtoK;
            Tflm = (Tair + Twir)/2;

          /* thermal conductivity */
            Kd = (pow(Tflm,1.5) * Kcst1)/(Kcst2*(Tflm + Kcst3 * pow(10,(-12/Tflm))));
            Kw = (pow(Twir,1.5) * Kcst1)/(Kcst2*(Twir + Kcst3 * pow(10,(-12/(Twir)))));

          /* Viscosity */
            Vd = Vcst1 * (Vcst2 / (120 + Tflm)) * pow(Tflm/K0,1.5);
            Vw = Vcst1 * (Vcst2 / (120 + Twir)) * pow(Twir/K0,1.5);

          /* Prandtl number */
            Prd = 0.24*Vd / Kd;
            Prw = 0.24*Vw / Kw;

          /* Air density */
            Da = (*Ps / Tair) * Dcst;
            Dd = (*Ps / Tflm) * Dcst;

          /* Reynolds number */
            Re = (Dd * (*Vp) * d * 0.1) / Vd ;

          /* Power Calculated */
            Pd = (Pcst1 * M_PI * Kd * (Twir - Tair) * pow(Re,0.6) * pow(Prd,0.37) * pow(Prd/Prw,0.25) * l)/ Pcst2;

          /* Boiling Point Water */
            Tb = log10(*Ps) * Tcst1 + Tcst2;

          /* Latent Heat of Vaporization */
            Lv = Lcst1 * pow((K0 / Tb),Tb*Lcst2 + Lcst3);

          /* Power Wet Calculated */
            Pwc = *Pw - Pd;

          /* liquid water content */
            *LWC = (Pwc * Fcst1) / ( l * d * (*Vp) * 100 * (Lv +Tb - Tair));
	    }
        else
	    {
	      *LWC = K_NaN;
	    }

        Pw++;
        Ta++;
        Ps++;
        Vp++;
/*En cas de changement dans la config de la tempÈrature du fil, cela ne
change pas la tempÈrature effective du fil.
Dans cette version, l'opÈrateur utilise la premiËre valeur de
tempÈrature de fil diffÈrente de nan pour le calcul de lwc.
Le cas de changement rÈel de tempÈrature du fil en vol sera rÈsolu dans
une version ultÈrieur */
	if (!isfinite (*Tw))
	{
           Tw++;
	}
        LWC++;
    }
    return 0;
}

/* fonction d'enrobage */

int
OP_lwc_lwc300 (unsigned long Nbval, void *ArgList[], char *DiagExec)
{
  int CodRet = lwc_lwc300 (Nbval,
		      (float *) ArgList[0],
		      (float *) ArgList[1],
		      (float *) ArgList[2],
		      (float *) ArgList[3],
		      *((float *) ArgList[4]),
		      *((float *) ArgList[5]),
		      (float *) ArgList[6],
		      (float *) ArgList[7]);


  return OP_OK;
}

void
ID_lwc_lwc300 (oper * optr)
{
  strcpy (optr->Nom, "lwc_lwc300");
  optr->Version = "$Revision: 5097 $";
  optr->Date = "08/26/96";
  optr->fctptr = OP_lwc_lwc300;
  optr->NbArg = 8;

  /* Pw */
  optr->Arg_Car[0].direction = DIR_IN;
  optr->Arg_Car[0].categorie = VECTOR;
  optr->Arg_Car[0].typ = ATYC_IF32;
  optr->Arg_Car[0].array_dim = "1";
  optr->Arg_Car[0].type_sample = "any";
  optr->Arg_Car[0].sample = "any";
  optr->Arg_Car[0].unite = "watt";

  /* Ta */
  optr->Arg_Car[1].direction = DIR_IN;
  optr->Arg_Car[1].categorie = VECTOR;
  optr->Arg_Car[1].typ = ATYC_IF32;
  optr->Arg_Car[1].array_dim = "1";
  optr->Arg_Car[1].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[1].type_sample = "any";
  optr->Arg_Car[1].sample = "any";
  optr->Arg_Car[1].unite = "Kelvin";

  /* Ps */
  optr->Arg_Car[2].direction = DIR_IN;
  optr->Arg_Car[2].categorie = VECTOR;
  optr->Arg_Car[2].typ = ATYC_IF32;
  optr->Arg_Car[2].array_dim = "1";
  optr->Arg_Car[2].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[2].unite = "hPa";

  /* Vp */
  optr->Arg_Car[3].direction = DIR_IN;
  optr->Arg_Car[3].categorie = VECTOR;
  optr->Arg_Car[3].typ = ATYC_IF32;
  optr->Arg_Car[3].array_dim = "1";
  optr->Arg_Car[3].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[3].type_sample = "any";
  optr->Arg_Car[3].sample = "any";
  optr->Arg_Car[3].unite = "m/s";
  /* l */
  optr->Arg_Car[4].direction = DIR_IN;
  optr->Arg_Car[4].categorie = COEFFICIENT;
  optr->Arg_Car[4].typ = ATYC_IF32;
  optr->Arg_Car[4].array_dim = "1";
  optr->Arg_Car[4].type_sample = NULL;
  optr->Arg_Car[4].sample = NULL;
  optr->Arg_Car[4].unite = "mm";

  /* d */
  optr->Arg_Car[5].direction = DIR_IN;
  optr->Arg_Car[5].categorie = COEFFICIENT;
  optr->Arg_Car[5].typ = ATYC_IF32;
  optr->Arg_Car[5].array_dim = "1";
  optr->Arg_Car[5].type_sample = NULL;
  optr->Arg_Car[5].sample = NULL;
  optr->Arg_Car[5].unite = "mm";

  /* Tw */
  optr->Arg_Car[6].direction = DIR_IN;
  optr->Arg_Car[6].categorie = VECTOR;
  optr->Arg_Car[6].typ = ATYC_IF32;
  optr->Arg_Car[6].array_dim = "1";
  optr->Arg_Car[6].type_sample = NULL;
  optr->Arg_Car[6].sample = NULL;
  optr->Arg_Car[6].unite = "Kelvin";

  optr->Arg_Car[7].direction = DIR_OUT;
  optr->Arg_Car[7].categorie = VECTOR;
  optr->Arg_Car[7].typ = ATYC_IF32;
  optr->Arg_Car[7].array_dim = "1";
  optr->Arg_Car[7].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[7].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[7].sample = "$Arg1.sample";
  optr->Arg_Car[7].ref_time = "$Arg1.ref_time";
  /* Pour le futur...  */
  /* optr->Arg_Car[10].misval = "-99"; */
  optr->Arg_Car[7].unite = "gram/m3";
  /*** SB correction famille ***/
  optr->Arg_Car[7].famille = "\"eau_liquide\"";
  optr->Arg_Car[7].name = " \"Contenu en eau liquide issu du Lwc300\" ";
  optr->Arg_Car[7].en_name = " \"Liquid water content from Lwc300\" ";

}
