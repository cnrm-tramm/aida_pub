/******************************************************************
*
* OPERATOR      TPrimew.c   ANSI-C
*
* PURPOSE       Calcul de la temperature pseudo-adiabatique
*               du thermometre mouille d'une particule donnee
*               definie par : pression, temperature, humidite .
*
* DESCRIPTION   Just a call to our "thermo" library.
*
* VERSION       $Revision$
*
* ARGUMENTS    ENTREE   float  Pression     hPa
*              ENTREE   float  Temperature  deg.Kelvin ou Celsius
*              ENTREE   float  Humidite     %
*              SORTIE   float  Tw           deg.Kelvin ou Celsius
*                                           (idem Temperature)
*
* SUBPROGRAMS  Appels a la Librairie thermo ainsi que la Librairie
*	       struct_oper
*
* FILES
*
* REFERENCES   bibmet-ct, d8 (bibliotheque D.Puech libmto)
*
* CHANGES      21/01/2000 C.Berne : valeur manquante si Tempe < -40 degC
*
* COPYRIGHT    Meteo-France
*
* AGREEMENT     
*#########################################################################*/

#define _POSIX_SOURCE 1
#define _XOPEN_SOURCE 600

#include <stdio.h>
#include <string.h>
#include "struct_oper.h"
#include "thermo.h"
#include "unit_def.h"

#define TWCURV_ECHEC (-999.)

/* La vraie fonction... */
int
TPrimew (unsigned long NLoop,
	 const float *Ps,
	 const float *Tempe,
	 const float *Hum,
	 float *Tw)
{
  unsigned long i;
  int flag_info;
  float CtoK;
  const float misval_out = K_NaN;
  float Tcondensation, Pcondensation;

  /* On devine l'unite Celsius/Kelvins */
  flag_info = auto_tempe_unit (NLoop, Tempe, &CtoK);

  for (i = 0; i < NLoop; i++)
    {
      if ((Tempe[i] + CtoK) > (273.15 - 40.))
	{
	  /* On calcule Tw uniquement si Ts > -40 deg C (sinon calcul idiot!) */
	  /*                                                                  */
	  /* On fait appel a plusieurs fonctions de notre librairie thermo    */
	  /* tcond, pcond et twcurv                                           */
	  /* Pas d'utilisation des pointeurs mais des indices de tableaux!    */

	  tcond ((Tempe[i] + CtoK), Hum[i], &Tcondensation);
	  pcond (Ps[i], (Tempe[i] + CtoK), Hum[i], &Pcondensation);
	  twcurv (Pcondensation, Tcondensation, Ps[i], &Tw[i]);
          if (Tw[i] == TWCURV_ECHEC)
	    Tw[i] = misval_out;
          else
	    Tw[i] = Tw[i] - CtoK;
	}
      else
	{
	  Tw[i] = misval_out;
	}
    }
  return flag_info;
}


/* la fonction d'enrobage classique */

int
OP_TPrimew (unsigned long NbVal, void *ArgList[], char *DiagExec)
{
  int CodRet;

  sprintf (DiagExec, "TPrimew(%lu ech.)", NbVal);

  CodRet = TPrimew (NbVal,
		    (float *) ArgList[0],
		    (float *) ArgList[1],
		    (float *) ArgList[2],
		    (float *) ArgList[3]);

  if (CodRet == T_EN_K)
    strcat (DiagExec, "; Tempé reconnue en K");
  else
    strcat (DiagExec, "; Tempé reconnue en °C");

  return OP_OK;
}

/* la fonction de description de l'operateur et ses arguments */

void
ID_TPrimew (oper * optr)
{
  strcpy (optr->Nom, "TPrimew");
  optr->Version = "$Revision$";
  optr->Date = "$Date$";
  optr->fctptr = OP_TPrimew;
  optr->misval_auto = 1;
  optr->NbArg = 4;

  /* Ps */
  optr->Arg_Car[0].direction = DIR_IN;
  optr->Arg_Car[0].categorie = VECTOR;
  optr->Arg_Car[0].typ = ATYC_IF32;
  optr->Arg_Car[0].array_dim = "1";
  optr->Arg_Car[0].type_sample = "any";
  optr->Arg_Car[0].sample = "any";
  optr->Arg_Car[0].unite = "hPa";

  /* Tempe */
  optr->Arg_Car[1].direction = DIR_IN;
  optr->Arg_Car[1].categorie = VECTOR;
  optr->Arg_Car[1].typ = ATYC_IF32;
  optr->Arg_Car[1].array_dim = "1";
  optr->Arg_Car[1].type_sample = "any";
  optr->Arg_Car[1].sample = "any";
  optr->Arg_Car[1].unite = "";

  optr->Arg_Car[2].direction = DIR_IN;
  optr->Arg_Car[2].categorie = VECTOR;
  optr->Arg_Car[2].typ = ATYC_IF32;
  optr->Arg_Car[2].array_dim = "1";
  optr->Arg_Car[2].type_sample = "any";
  optr->Arg_Car[2].sample = "any";
  optr->Arg_Car[2].unite = "%";

  optr->Arg_Car[3].direction = DIR_OUT;
  optr->Arg_Car[3].categorie = VECTOR;
  optr->Arg_Car[3].typ = ATYC_IF32;
  optr->Arg_Car[3].array_dim = "1";
  optr->Arg_Car[3].ref_time = "$Arg1.ref_time";
  optr->Arg_Car[3].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[3].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[3].sample = "$Arg1.sample";
  optr->Arg_Car[3].unite = "Celsius";
  optr->Arg_Car[3].misval = "$Arg1.misval";
  optr->Arg_Car[3].famille = " \"temperature\" ";
  optr->Arg_Car[3].name =
                " \"temperature pseudo-adiabatique du thermometre mouille\" ";

}
