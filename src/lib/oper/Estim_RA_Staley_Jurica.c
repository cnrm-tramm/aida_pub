/****************************************************
*
* OPERATOR      Estim_RA_Staley_Jurica.c   FUNCTION  ANSI-C
*
* PURPOSE       Estimation of incoming IR raditaion.
*
* DESCRIPTION  Calcul par estimation du rayonnement IR descendant
*              par ciel clair 
*
* VERSION       $Revision$
*
* ARGUMENTS   IN   float  humspe     g/kg       Humidite specifique de l'air
*             IN   float  tempe      Kelvin     Temperature de l'air
*
*             OUT  float ra_est_clear  W/m2     Rayt IR estime par ciel clair
*
* REFERENCES   Staley D.O. & Jurica G.M., Effective atmospheric 
*              emissivity under clear skies, JAM, 11:349-356, 1972 
*
* CHANGES       
*
* AUTHOR       C coding by B. Piguet/C.Berne
*
* COPYRIGHT    Meteo-France/CNRM
*
*#########################################################################*/

#define _POSIX_SOURCE 1
#define _XOPEN_SOURCE 600
#define _XOPEN_SOURCE_EXTENDED 1

#include <stdio.h>
#include <string.h>
#include <math.h>
#include "struct_oper.h"
#include "unit.h"

/*    Les vraies fonctions....  */

void
Estim_RA_Staley_Jurica (const unsigned long NLoop,
			float *humspe, float *tempe, float *ra_est_clear)
{
  float CtoK_S;			/* Pour la conversion C->K de T_Stat */
  float tempeK, T4;		/* tempe convertie en deg K si besoin et tempe puissance 4 */
  float stefan;			/* constante de stefan-boltzmann */
  int flag_info_Ts;
  float humkgkg;		/* hum spe en kg/kg */

  unsigned long i, nb_inval;

  /* Détermination automatique Kelvin/Celsius */
  flag_info_Ts = auto_tempe_unit (NLoop, tempe, &CtoK_S);

  stefan = 5.6693e-8;

  nb_inval = 0;
  for (i = 0; i < NLoop; i++)
    {
      tempeK = *tempe + CtoK_S;
      T4 = pow (tempeK, 4);
      if (*humspe < 0)
	{
	  humkgkg = 0.0;
	  nb_inval++;
	}
      else
	{
	  humkgkg = *humspe * 0.001;
	}
      ra_est_clear[i] = 0.67 * pow ((1670. * humkgkg), 0.08) * (stefan * T4);

      humspe++;
      tempe++;
    }
  return;
}

int
OP_Estim_RA_Staley_Jurica (unsigned long NbVal, void *ArgList[],
			   char *DiagExec)
{
  sprintf (DiagExec, "OP_Estim_RA_Staley_Jurica (%lu, ..)\n", NbVal);

  Estim_RA_Staley_Jurica (NbVal, (float *) ArgList[0],
			  (float *) ArgList[1], (float *) ArgList[2]);

  return OP_OK;
}

void
ID_Estim_RA_Staley_Jurica (oper * optr)
{
  strcpy (optr->Nom, "Estim_RA_Staley_Jurica");
  optr->Version = "$Revision$";
  optr->Date = "$Date$";
  optr->fctptr = OP_Estim_RA_Staley_Jurica;
  optr->NbArg = 3;		/* doit rester inf. a FIL_MAX_ARG */

  /* Humidite specifique */
  optr->Arg_Car[0].direction = DIR_IN;
  optr->Arg_Car[0].categorie = VECTOR;
  optr->Arg_Car[0].typ = ATYC_IF32;
  optr->Arg_Car[0].array_dim = "1";
  optr->Arg_Car[0].type_sample = "any";
  optr->Arg_Car[0].sample = "any";
  optr->Arg_Car[0].unite = "gram/kg";

  /* Temperature de l'air */
  optr->Arg_Car[1].direction = DIR_IN;
  optr->Arg_Car[1].categorie = VECTOR;
  optr->Arg_Car[1].typ = ATYC_IF32;
  optr->Arg_Car[1].array_dim = "1";
  optr->Arg_Car[1].type_sample = "any";
  optr->Arg_Car[1].sample = "any";
  optr->Arg_Car[1].unite = "K";

  /* Rayt IR desc estime */
  optr->Arg_Car[2].direction = DIR_OUT;
  optr->Arg_Car[2].categorie = VECTOR;
  optr->Arg_Car[2].typ = ATYC_IF32;
  optr->Arg_Car[2].array_dim = "1";
  optr->Arg_Car[2].ref_time = "$Arg1.ref_time";
  optr->Arg_Car[2].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[2].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[2].sample = "$Arg1.sample";
  optr->Arg_Car[2].unite = "W/m2";
  optr->Arg_Car[2].famille = " \"rayonnement\" ";
  optr->Arg_Car[2].name = " \"Rayonnement IR desc estime (ciel clair)\" ";

}
