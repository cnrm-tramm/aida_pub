/*******************************************************************
* OPERATOR      Ha_RapM.c FUNCTION ANSI-C
*
* PURPOSE       Calcul de l'humidite absolue (g/m3) à partir 
*               du rapport de melange en vapeur d'eau (g/kg).
*
* DESCRIPTION     Ha = r P / (T . (Ra + r Rv))
*
*               Justification :
*                   Inversion de la formule établie pour RapM_Ha.
*		 
* VERSION       1.0
*
* ARGUMENTS     IN      float   r	rapport de melange en vapeur d'eau (g/kg)
*               IN      float   Ps	pression statique (hPa) 
*               IN      float   Ts      temperature statique (K or Celsius)
*
*               OUT     float   Ha	Humidite absolue (g/m3)
*
* ENTRY         NONE
*
* SUBPROGRAMS   NONE
*
* REFERENCES    NONE  
*             
* COPYRIGHT     Meteo-France
*               Centre National de Recherches Meteorologiques
*               GMEI/TRAMM
*               42, av. G. Coriolis
*               31057   TOULOUSE cedex
*              
*******************************************************************/

#define _POSIX_SOURCE 1
#define _XOPEN_SOURCE 600

#include <stdio.h>
#include <string.h>
#include <math.h>
#include "struct_oper.h"
#include "unit.h"

int
Ha_RapM (unsigned long ndata, float *RapM, float *Ps, float *Ts, float *Ha)
{
  unsigned long i;
  unsigned long nb_inval = 0;

  /* Ra, Cste spécifique de l'air sec, en J / (K*kg) (= R/Ma)  */
  double Ra = 287.05;
  /* Rv, Cste spécifique de la vapeur d'eau, en J / (K*kg)  (= R/Mv) */
  double Rv = 461.51;
  int flag_info_tempe;
  float CtoK;
  double T, P, r;

  /* Détermination automatique Kelvin/Celsius */
  flag_info_tempe = auto_tempe_unit (ndata, Ts, &CtoK);



  for (i = 0; i < ndata; i++)
    {
      T = ((double) Ts[i]) + (double)CtoK;
      if (T == 0.)
	{
	  Ha[i] = K_NaN;
	  nb_inval++;
	  continue;
	}
      P = (double) Ps[i] * 100.;	/* Conversion hPa-> Pa */
      if (r < 0.)
	{
	  Ha[i] = K_NaN;
	  nb_inval++;
	  continue;
	}
      r = (double) RapM[i] / 1000.;	/* Conversion gram/kg en kg/kg */

      Ha[i] = r * P / (T * (Ra + r * Rv));
      Ha[i] *= 1000.0;		/* Conversion kg/m3 -> g/m3     */

      /* Dernière protection contre les erreurs de mesure. */
      if (Ha[i] < 0.0)
	{
	  nb_inval++;
	  Ha[i] = 0;
	}
    }

  return nb_inval;
}

/* fonction d'enrobage */

int
OP_Ha_RapM (unsigned long NbVal, void *ArgList[], char *DiagExec)
{
  unsigned long CodRet;
  (void) sprintf (DiagExec, "Ha_RapM, %lu echant.", NbVal);

  CodRet = Ha_RapM (NbVal,
		    (float *) ArgList[0],
		    (float *) ArgList[1],
		    (float *) ArgList[2], (float *) ArgList[3]);

  if (CodRet > 0)
    sprintf (DiagExec + strlen (DiagExec), " %lu val. invalide(s)", CodRet);

  return OP_OK;
}

void
ID_Ha_RapM (oper * optr)
{
  strcpy (optr->Nom, "Ha_RapM");
  optr->Version = "$Revision$";
  optr->Date = "$Date$";
  optr->fctptr = OP_Ha_RapM;
  optr->NbArg = 4;

  /* RapM */
  optr->Arg_Car[0].direction = DIR_IN;
  optr->Arg_Car[0].categorie = VECTOR;
  optr->Arg_Car[0].typ = ATYC_IF32;
  optr->Arg_Car[0].array_dim = "1";
  optr->Arg_Car[0].type_sample = "any";
  optr->Arg_Car[0].sample = "any";
  optr->Arg_Car[0].unite = "gram/kg";

  /* Ps */
  optr->Arg_Car[1].direction = DIR_IN;
  optr->Arg_Car[1].categorie = VECTOR;
  optr->Arg_Car[1].typ = ATYC_IF32;
  optr->Arg_Car[1].array_dim = "1";
  optr->Arg_Car[1].sample = "$Arg1.sample";
  optr->Arg_Car[1].type_sample = "any";
  optr->Arg_Car[1].sample = "any";
  optr->Arg_Car[1].unite = "hPa";

  /* Ts */
  optr->Arg_Car[2].direction = DIR_IN;
  optr->Arg_Car[2].categorie = VECTOR;
  optr->Arg_Car[2].typ = ATYC_IF32;
  optr->Arg_Car[2].array_dim = "1";
  optr->Arg_Car[2].sample = "$Arg1.sample";
  optr->Arg_Car[2].type_sample = "any";
  optr->Arg_Car[2].sample = "any";
  optr->Arg_Car[2].unite = "";

  optr->Arg_Car[3].direction = DIR_OUT;
  optr->Arg_Car[3].categorie = VECTOR;
  optr->Arg_Car[3].typ = ATYC_IF32;
  optr->Arg_Car[3].array_dim = "1";
  optr->Arg_Car[3].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[3].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[3].sample = "$Arg1.sample";
  optr->Arg_Car[3].ref_time = "$Arg1.ref_time";
  optr->Arg_Car[3].misval = "$Arg1.misval";
  optr->Arg_Car[3].unite = "gram/m3";
  optr->Arg_Car[3].famille = " \"eau_vapeur\" ";
}
