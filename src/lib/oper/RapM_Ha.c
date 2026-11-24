/*******************************************************************
* OPERATOR      RapM_Ha.c FUNCTION ANSI-C
*
* PURPOSE       Calcul du rapport de melange en vapeur d'eau (g/kg) a
*		partir de l'humidite absolue (g/m3) 
*
* DESCRIPTION     r = Ra Ha T /(P- Ha Rv T)
*
*               Justification :
*               Loi des gaz parfaits (en masse) : P = m/V R/M T  (M= Masse molaire)
*               Loi de Dalton+GP, pour la vapeur d'eau : e = mv/V Rv T
*               et mv/V = Ha = humidité absolue.
*               r = mv/ma.
*               Loi de Dalton+GP, pour l'air sec : (P-e) = ma/V Ra T
*
*               r = mv/V * V/ma = Ha * Ra T /(P-e)
*               On remplace e par son expression en fonction de Ha :
*                    r = Ha * Ra T / (P-Ha Rv T)
*		 
* VERSION       1.0
*
* ARGUMENTS     IN      float   Ha	Humidite absolue (g/m3)
*               IN      float   Ps	pression statique (hPa) 
*               IN      float   Ts      temperature statique (K or Celsius)
*
*               OUT 	float   RapM 	rapport de melange en vapeur d'eau
*
* ENTRY         NONE
*
* SUBPROGRAMS   NONE
*
* REFERENCES    NONE  
*             
* COPYRIGHT     Meteo-France
*               Centre National de Recherches Meteorologiques
*               GMEI/MMA
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
#include "unit_def.h"

int
RapM_Ha (unsigned long ndata, float *Ha, float *Ps, float *Ts, float *RapM)
{
  long i;

  /* Ra, Cste spécifique de l'air sec, en J / (K*kg) (= R/Ma)  */
  double Ra = 287.05;
  /* Rv, Cste spécifique de la vapeur d'eau, en J / (K*kg)  (= R/Mv) */
  double Rv = 461.51;
  int flag_info_tempe;
  float CtoK;

  double T, P, H;

  /* Détermination automatique Kelvin/Celsius */
  flag_info_tempe = auto_tempe_unit (ndata, Ts, &CtoK);

  /*fprintf(stderr,"CtoK : %g \n", CtoK);*/

  if (flag_info_tempe == MANQUANTES)
   {
    for (i = 0; i < ndata; i++)
      {
       RapM[i] = 0./0.; 
      }
    return flag_info_tempe;
   }



  for (i = 0; i < ndata; i++)
    {
      T = ((double) Ts[i]) + (double)CtoK;
      P = (double) Ps[i] * 100.;	/* Conversion hPa-> Pa */
      H = (double) Ha[i] / 1000.;	/* Conversion gram/m3 en kg/m3 */

      RapM[i] = H * Ra * T / (P - H * Rv * T);

      RapM[i] *= 1000.0;	/* Conversion kg/kg -> g/kg     */

      if (RapM[i] < 0.0)
	RapM[i] = 0;
    }

  return flag_info_tempe;
}

/* fonction d'enrobage */

int
OP_RapM_Ha (unsigned long Nbval, void *ArgList[], char *DiagExec)
{
  int CodRet = RapM_Ha (Nbval,
			(float *) ArgList[0],
			(float *) ArgList[1],
			(float *) ArgList[2],
			(float *) ArgList[3]);

   switch (CodRet)
    {
    case T_EN_C:
      strcat (DiagExec, "; Tempé reconnue en °C.");
      break;
    case T_EN_K:
      strcat (DiagExec, "; Tempé reconnue en K.");
      break;
    case MANQUANTES:
      strcat (DiagExec,
	      "; Trop de valeurs manquantes : unité de température non reconnue.");
      break;
    default:
      strcat (DiagExec, "; BUG!! Code retour inattendu.");
      return OP_FAIL;
    }

  return OP_OK;
}

void
ID_RapM_Ha (oper * optr)
{
  strcpy (optr->Nom, "RapM_Ha");
  optr->Version = "$Revision$";
  optr->Date = "$Date$";
  optr->fctptr = OP_RapM_Ha;
  optr->NbArg = 4;

  /*  Ha  */
  optr->Arg_Car[0].direction = DIR_IN;
  optr->Arg_Car[0].categorie = VECTOR;
  optr->Arg_Car[0].typ = ATYC_IF32;
  optr->Arg_Car[0].array_dim = "1";
  optr->Arg_Car[0].type_sample = "any";
  optr->Arg_Car[0].sample = "any";
  optr->Arg_Car[0].unite = "gram/m3";

  /*  Ps  */
  optr->Arg_Car[1].direction = DIR_IN;
  optr->Arg_Car[1].categorie = VECTOR;
  optr->Arg_Car[1].typ = ATYC_IF32;
  optr->Arg_Car[1].array_dim = "1";
  optr->Arg_Car[1].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[1].type_sample = "any";
  optr->Arg_Car[1].sample = "any";
  optr->Arg_Car[1].unite = "hPa";

  /* Ts  */
  optr->Arg_Car[2].direction = DIR_IN;
  optr->Arg_Car[2].categorie = VECTOR;
  optr->Arg_Car[2].typ = ATYC_IF32;
  optr->Arg_Car[2].array_dim = "1";
  optr->Arg_Car[2].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[2].type_sample = "any";
  optr->Arg_Car[2].sample = "any";
  optr->Arg_Car[2].unite = "";

  /* RapM  */
  optr->Arg_Car[3].direction = DIR_OUT;
  optr->Arg_Car[3].categorie = VECTOR;
  optr->Arg_Car[3].typ = ATYC_IF32;
  optr->Arg_Car[3].array_dim = "1";
  optr->Arg_Car[3].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[3].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[3].sample = "$Arg1.sample";
  optr->Arg_Car[3].ref_time = "$Arg1.ref_time";
  optr->Arg_Car[3].misval = "$Arg1.misval";
  optr->Arg_Car[3].unite = "gram/kg";
  optr->Arg_Car[3].famille = "auto";
  optr->Arg_Car[3].name = " \"Rapport de melange a partir de \" + $Arg1.name";
  optr->Arg_Car[3].en_name = " \"Mixing ratio from \" + $Arg1.english_name";
}
