/****************************************************
*
* OPERATOR       HumCapa.c   FUNCTION  ANSI-C
*
* PURPOSE        Computation of relative Humidity from "Capacitive probe"
*
* DESCRIPTION    Calcul de l'humidité à partir de la fréquence de la 
*                sonde capacitive.
*		 Cet opérateur utilise une loi de calibration du capteur
*		 sous la forme d'un polynôme du second degré.
*
* VERSION        1.4
*
* ARGUMENTS  IN   float  ucapf		Hz	Mesure
*            IN   float  ts      	K or C  Tempe Air.
*            IN   float  ps         	hPa     Pression statique
*            IN   float  delta_p    	hPa     Surpression dynamique
*	     IN	  float	 Ct 		%/°C	Correction de temperature
*	     IN	  float	 Fmin		Hz 	Frequence minimale acceptee 
*            IN   float  C0           		Coeffs terme degre 0 
*            IN   float  C1           		Coeffs terme degre 1 
*            IN   float  C2           		Coeffs terme degre 2 
*            OUT  float  *hu       	%       Humidité relative.
*
* ENTRY            
*                 
* FILES   
*
* REFERENCES 
*		Note de centre n°9 du CAM
*		Appareils de mesure de l'hygrometrie sur le Merlin IV
*		H. Bellec et G. Duverneuil   
*
* CHANGES       
*
* COPYRIGHT        Meteo-France
*
* AGREEMENT        The author wishes that .....
*#########################################################################*/

#define _POSIX_SOURCE 1
#define _XOPEN_SOURCE 600
/* Le #define _HPUX_SOURCE n'est la que pour "voir" strdup */
#define _HPUX_SOURCE 1
#define _XOPEN_SOURCE_EXTENDED 1


#include <stdio.h>
#include <string.h>
#include "struct_oper.h"

int
HumCapa (unsigned long NLoop,
	 const float *Ucapf,	/* en Hz */
	 const float *Ts,	/* en Kelvin ou Celsius  */
	 const float *Ps,	/* Pression statique */
	 const float *Delta_P,	/* comme son nom l'indique.. */
	 const float Ct,
	 const float Fmin,
	 const float C0,
	 const float C1,
	 const float C2,
	 float *Hu)
{
  unsigned long i;

  double Cv, KtoC;
  double calib, cor_tempe, F;
  double dC0, dC1, dC2, dCt;

  if (Ts[NLoop / 2] > 100)
    KtoC = -273.15;
  else
    KtoC = 0.;

  fprintf (stderr, " C0 : %15.8f, C1 : %15.8f, C2 : %15.8f \n", C0, C1, C2);

  dC0 = (double) C0;
  dC1 = (double) C1;
  dC2 = (double) C2;
  dCt = (double) Ct;

  for (i = 0; i < NLoop; i++)
    {
      if (Ucapf[i] < Fmin)
	F = (double) Fmin;
      else
	F = (double) (Ucapf[i]);

/** correction de vitesse **/
      Cv = (double) (Ps[i] / (Ps[i] + Delta_P[i]));

/** correction de temperature **/
      cor_tempe = (double) (dCt * (Ts[i] + KtoC - 20.));

/** application des coefs de calib **/
      calib = dC0 + (dC1 * F) + (dC2 * F * F);

/** calcul de l'hum. relative **/
      Hu[i] = (float) (Cv * (calib + cor_tempe));

    }

  return 0;
}


/* la fonction d'enrobage classique */

int
OP_HumCapa (unsigned long NbVal, void *ArgList[], char *DiagExec)
{
  int CodRet;

  sprintf (DiagExec, "HumCapa :  C0=%15.8f, C1=%15.8f, C2=%15.8f;",
	   *((float *) ArgList[6]), *((float *) ArgList[7]),
	   *((float *) ArgList[8]));

  CodRet = HumCapa (NbVal,
		    (float *) ArgList[0],
		    (float *) ArgList[1],
		    (float *) ArgList[2],
		    (float *) ArgList[3],
		    *((float *) ArgList[4]),
		    *((float *) ArgList[5]),
		    *((float *) ArgList[6]),
		    *((float *) ArgList[7]),
		    *((float *) ArgList[8]),
		    (float *) ArgList[9]);

  return OP_OK;
}

void
ID_HumCapa (oper * optr)
{
  strcpy (optr->Nom, "HumCapa");
  optr->Version = "$Revision$";
  optr->Date = "$Date$";
  optr->fctptr = OP_HumCapa;
  optr->NbArg = 10;

  /* Ucapf */
  optr->Arg_Car[0].direction = DIR_IN;
  optr->Arg_Car[0].categorie = VECTOR;
  optr->Arg_Car[0].typ = ATYC_IF32;
  optr->Arg_Car[0].array_dim = "1";
  optr->Arg_Car[0].type_sample = "any";
  optr->Arg_Car[0].sample = "any";
  optr->Arg_Car[0].unite = "Hz";

  /* Ts */
  optr->Arg_Car[1].direction = DIR_IN;
  optr->Arg_Car[1].categorie = VECTOR;
  optr->Arg_Car[1].typ = ATYC_IF32;
  optr->Arg_Car[1].array_dim = "1";
  optr->Arg_Car[1].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[1].type_sample = "any";
  optr->Arg_Car[1].sample = "any";
  optr->Arg_Car[1].unite = "any";

  /* Ps */
  optr->Arg_Car[2].direction = DIR_IN;
  optr->Arg_Car[2].categorie = VECTOR;
  optr->Arg_Car[2].typ = ATYC_IF32;
  optr->Arg_Car[2].array_dim = "1";
  optr->Arg_Car[2].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[2].type_sample = "any";
  optr->Arg_Car[2].sample = "any";
  optr->Arg_Car[2].unite = "hPa";

  /* Delta_p */
  optr->Arg_Car[3].direction = DIR_IN;
  optr->Arg_Car[3].categorie = VECTOR;
  optr->Arg_Car[3].typ = ATYC_IF32;
  optr->Arg_Car[3].array_dim = "1";
  optr->Arg_Car[3].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[3].type_sample = "any";
  optr->Arg_Car[3].sample = "any";
  optr->Arg_Car[3].unite = "hPa";

  optr->Arg_Car[4].direction = DIR_IN;
  optr->Arg_Car[4].categorie = COEFFICIENT;
  optr->Arg_Car[4].typ = ATYC_IF32;
  optr->Arg_Car[4].array_dim = "1";
  optr->Arg_Car[4].type_sample = NULL;
  optr->Arg_Car[4].sample = NULL;
  optr->Arg_Car[4].unite = "";

  optr->Arg_Car[5].direction = DIR_IN;
  optr->Arg_Car[5].categorie = COEFFICIENT;
  optr->Arg_Car[5].typ = ATYC_IF32;
  optr->Arg_Car[5].array_dim = "1";
  optr->Arg_Car[5].type_sample = NULL;
  optr->Arg_Car[5].sample = NULL;
  optr->Arg_Car[5].unite = "";

  optr->Arg_Car[6].direction = DIR_IN;
  optr->Arg_Car[6].categorie = COEFFICIENT;
  optr->Arg_Car[6].typ = ATYC_IF32;
  optr->Arg_Car[6].array_dim = "1";
  optr->Arg_Car[6].type_sample = NULL;
  optr->Arg_Car[6].sample = NULL;
  optr->Arg_Car[6].unite = "";

  optr->Arg_Car[7].direction = DIR_IN;
  optr->Arg_Car[7].categorie = COEFFICIENT;
  optr->Arg_Car[7].typ = ATYC_IF32;
  optr->Arg_Car[7].array_dim = "1";
  optr->Arg_Car[7].type_sample = NULL;
  optr->Arg_Car[7].sample = NULL;
  optr->Arg_Car[7].unite = "";

  optr->Arg_Car[8].direction = DIR_IN;
  optr->Arg_Car[8].categorie = COEFFICIENT;
  optr->Arg_Car[8].typ = ATYC_IF32;
  optr->Arg_Car[8].array_dim = "1";
  optr->Arg_Car[8].type_sample = NULL;
  optr->Arg_Car[8].sample = NULL;
  optr->Arg_Car[8].unite = "";

  optr->Arg_Car[9].direction = DIR_OUT;
  optr->Arg_Car[9].categorie = VECTOR;
  optr->Arg_Car[9].typ = ATYC_IF32;
  optr->Arg_Car[9].array_dim = "1";
  optr->Arg_Car[9].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[9].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[9].sample = "$Arg1.sample";
  optr->Arg_Car[9].ref_time = "$Arg1.ref_time";
  optr->Arg_Car[9].unite = "%";
  optr->Arg_Car[9].misval = "$Arg1.misval";
  optr->Arg_Car[9].famille = " \"eau_vapeur\" ";

}
