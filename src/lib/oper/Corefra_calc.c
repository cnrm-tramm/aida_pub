/*******************************************************************
* OPERATOR      Corefra_calc.c FUNCTION ANSI-C
*
* PURPOSE       Calcul du coindice de refraction a partir de
* 		parametres thermodynamiques de base
*
* DESCRIPTION   N s'exprime en fonction de la temperature "T", de la 
*		pression "P", et du rapport de mélange "R"
*		par la formule : N = 1e06 * Ko * ( 1+r ) / ( 1+1.608*r) * P / T 
*               avec Ko = (No-1) * ((1+1.608*Ro)/(1+Ro)*To/Po)
*		 
* VERSION       1.0
*
* ARGUMENTS     
*               IN      float   Ps	pression statique (hPa) 
*               IN      float   Ts      temperature statique (K or Celsius)
*		IN	float   r	rapport de melange (g/kg) 
*
*               OUT 	float   Corefra	coindice de refraction 
*
* ENTRY         NONE
*
* SUBPROGRAMS   NONE
*
* REFERENCES      
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
#define _XOPEN_SOURCE_EXTENDED
/* Le #define _HPUX_SOURCE n'est la que pour "voir" strdup */
#define _HPUX_SOURCE 1

#include <stdio.h>
#include <string.h>
#include <math.h>

#include "struct_oper.h"
#include "unit.h"

#ifndef K_Ra
#define K_Ra (8.314510 / 0.028964)
#endif
#ifndef K_Rv
#define K_Rv (461.51)
#endif

int
Corefra_calc (unsigned long ndata,
	      float *Ps, float *Ts, float *r, float *Corefra)
{
  unsigned long i;
  int flag_info;
  double C1 = 77.604;
  double C2 = 64.79;
  double C3 = 3.776e05;
  float CtoK;
  double T, P, rapm, To, Po, ro, Ko;
  double Ra_sur_Rv;
  double e, tempo, tempi;

  Ra_sur_Rv = K_Ra / K_Rv;

  /*** conversion de la tempe. Celsius en Kelvin ***/
  flag_info = auto_tempe_unit (ndata, Ts, &CtoK);

  /******************************************
  ** Calcul des valeurs de reference Ko 
  ** avec To=273.15 Po=1013.25 Ro=0     
  ******************************************/

  Ko = C1;
  /* 2010-08-02 : 'e', 'ro', 'Po', 'To', 'C3', 'C2'
   * sont des variables inutilisées. Reste du passé ??? */

  /********************
  ** Refractivite 
  ********************/

  for (i = 0; i < ndata; i++)
    {
      if (!isfinite (Ts[i]) || !isfinite (Ps[i]))
	{
	  Corefra[i] = K_NaN;
	  continue;
	}
      T = (double) (Ts[i] + CtoK);
      P = (double) Ps[i];
      rapm = (double) r[i];

   /**********************************************************************************
    * Attention aux unités: P doit etre en Pa dans la formule, rapm doit etre en kg/kg 
    *********************************************************************************/

      tempo = (1. + rapm) / (1 + 1.608 * rapm) * 
              P / 1.33322 / 8.314510 / T * (3.96 + 2.077 * 1e4 / T);

      tempi = (1. + 2. * tempo) / (1. - tempo);
      Corefra[i] = (float) ((sqrt (tempi) - 1.) * 1e9);
    }

  return (flag_info);
}

/* fonction d'enrobage */
int
OP_Corefra_calc (unsigned long Nbval, void *ArgList[], char *DiagExec)
{
  int CodRet = Corefra_calc (Nbval,
			     (float *) ArgList[0],
			     (float *) ArgList[1],
			     (float *) ArgList[2],
			     (float *) ArgList[3]);
  switch (CodRet)
    {
    case 0:
      strcat (DiagExec, "; Tempé reconnue en °C.");
      break;
    case 1:
      strcat (DiagExec, "; Tempé reconnue en °K.");
      break;
    default:
      strcat (DiagExec,
	      "; Trop de valeurs manquantes : unité de température non reconnue.");
      return OP_FAIL;
    }

  return OP_OK;
}

void
ID_Corefra_calc (oper * optr)
{
  strcpy (optr->Nom, "Corefra_calc");
  optr->Version = "$Revision$";
  optr->Date = "$Date$";
  optr->fctptr = OP_Corefra_calc;
  optr->NbArg = 4;

  /* Ps */
  optr->Arg_Car[0].direction = DIR_IN;
  optr->Arg_Car[0].categorie = VECTOR;
  optr->Arg_Car[0].typ = ATYC_IF32;
  optr->Arg_Car[0].array_dim = "1";
  optr->Arg_Car[0].type_sample = "any";
  optr->Arg_Car[0].sample = "any";
  optr->Arg_Car[0].unite = "hPa";

  /* Ts */
  optr->Arg_Car[1].direction = DIR_IN;
  optr->Arg_Car[1].categorie = VECTOR;
  optr->Arg_Car[1].typ = ATYC_IF32;
  optr->Arg_Car[1].array_dim = "1";
  optr->Arg_Car[1].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[1].type_sample = "any";
  optr->Arg_Car[1].sample = "any";
  optr->Arg_Car[1].unite = "";

  /* r */
  optr->Arg_Car[2].direction = DIR_IN;
  optr->Arg_Car[2].categorie = VECTOR;
  optr->Arg_Car[2].typ = ATYC_IF32;
  optr->Arg_Car[2].array_dim = "1";
  optr->Arg_Car[2].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[2].type_sample = "any";
  optr->Arg_Car[2].sample = "any";
  optr->Arg_Car[2].unite = "gram/kg";

  optr->Arg_Car[3].direction = DIR_OUT;
  optr->Arg_Car[3].categorie = VECTOR;
  optr->Arg_Car[3].typ = ATYC_IF32;
  optr->Arg_Car[3].array_dim = "1";
  optr->Arg_Car[3].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[3].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[3].sample = "$Arg1.sample";
  optr->Arg_Car[3].ref_time = "$Arg1.ref_time";
  optr->Arg_Car[3].unite = "";	/*  co-indice dans udunits ? 1e-06 ? */
  optr->Arg_Car[3].misval = "$Arg2.misval";
  optr->Arg_Car[3].name = "Co-indice de réfraction de l'air";
  optr->Arg_Car[3].en_name = "Air refractive co-index";
}
