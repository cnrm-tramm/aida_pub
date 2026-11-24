/******************************************************************
*
* OPERATOR      Correc_Tdf_P.c   FUNCTION  ANSI-C
*
* PURPOSE       Correction de l'influence de la pression sur la mesure de Tdf
*
* DESCRIPTION   Toute variation de pression d'une parcelle d'air change
*               proportionnellement la pression partielle de vapeur d'eau,
*               et donc son Td (ou Tf) (rappel : Td est tel que ewt(Td) = e)
*               Lorsqu'une mesure de Td est faite à une pression
*               différente de celle de l'air qu'on souhaite caractériser
*               il faut la corriger. Le principe de calcul est le 
*               suivant : 
*               Soit une parcelle d'air caractérisée par Ps, e et Td.
*               On mesure Td_m à Ps_m.
*               On a :   Td = ew-1(e)
*                       e_m = ew(Td_m)
*                       e/P = e_m/Pm (Loi de Dalton)
*               Donc Td = ew-1 (ew(Td_m) . P/P_m)
*
* VERSION       $Revision$
*
* ARGUMENTS   IN   float  Tdf_m    Any    Température de rosée ou givre mesurée
*             IN   float  Ps_m     hPa    Pression de mesure
*             IN   float  Ps       hPa    Pression de l'air
*
*             OUT  float  Tdf   same as 1  Température corrigée
*
* ENTRY
*
* SUBPROGRAMS   none
*
* FILES
*
* REFERENCES   
*
* CHANGES       1
*
* COPYRIGHT     Meteo-France
*
* AGREEMENT     The author wishes that .....
*#########################################################################*/

#define _POSIX_SOURCE 1
#define _XOPEN_SOURCE 600

#include <stdio.h>
#include <string.h>
#include "struct_oper.h"

#include "unit.h"
#include "thermo.h"

/* La vraie fonction... */
unsigned long
Correc_Tdf_P (unsigned long NLoop,
	      const float *Tdf_m,
	      const float *Ps_m, const float *Ps, float *Tdf)
{
  unsigned long i;
  float Tdf_to_K;
  int flag_info_Tdf;
  float Tdf_m_K;
  float e_m, e;

  /*** conversion de la tempe. Celsius en Kelvin ***/
  flag_info_Tdf = auto_tempe_unit (NLoop, Tdf, &Tdf_to_K);


  for (i = 0; i < NLoop; i++)
    {
      Tdf_m_K = Tdf_m[i] + Tdf_to_K;
      if (Tdf_m_K > 273.15)
	ew (Tdf_m_K, &e_m);
      else
	ewi (Tdf_m_K, &e_m);

      e = e_m * Ps[i] / Ps_m[i];
      if (e > 6.11)		/* 6.11 hPa : pression du point triple de l'eau */
	/* ATTENTION : inv_ew_Bolton : seule fonction a travailler en Pa (pas hPa) */
	inv_ew_Bolton (e * 100.0, &Tdf[i]);
      else
	inv_ewi_OMM (e, &Tdf[i]);
      Tdf[i] -= Tdf_to_K;
    }
  return i;
}


/* la fonction d'enrobage classique */

int
OP_Correc_Tdf_P (unsigned long NbVal, void *ArgList[], char *DiagExec)
{
  unsigned long CodRet;

  (void) sprintf (DiagExec, "Correc_Tdf_P(%ld ech.)", NbVal);

  CodRet = Correc_Tdf_P (NbVal,
			 (float *) ArgList[0],
			 (float *) ArgList[1],
			 (float *) ArgList[2], (float *) ArgList[3]);
  if (CodRet == NbVal)
    return OP_OK;
  else
    return OP_FAIL;
}

/* la fonction de description de l'operateur et ses arguments */

void
ID_Correc_Tdf_P (oper * optr)
{
  int idx = 0;

  strcpy (optr->Nom, "Correc_Tdf_P");
  optr->Version = "$Revision$";
  optr->Date = "$Date$";
  optr->fctptr = OP_Correc_Tdf_P;
  optr->NbArg = 4;

  /* Tdf_m */
  optr->Arg_Car[idx].direction = DIR_IN;
  optr->Arg_Car[idx].categorie = VECTOR;
  optr->Arg_Car[idx].typ = ATYC_IF32;
  optr->Arg_Car[idx].array_dim = "1";
  optr->Arg_Car[idx].type_sample = "any";
  optr->Arg_Car[idx].sample = "any";
  optr->Arg_Car[idx].unite = "any";
  idx++;

  /* Ps_m */
  optr->Arg_Car[idx].direction = DIR_IN;
  optr->Arg_Car[idx].categorie = VECTOR;
  optr->Arg_Car[idx].typ = ATYC_IF32;
  optr->Arg_Car[idx].array_dim = "1";
  optr->Arg_Car[idx].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[idx].type_sample = "any";
  optr->Arg_Car[idx].sample = "any";
  optr->Arg_Car[idx].unite = "hPa";
  idx++;

  /* Ps */
  optr->Arg_Car[idx].direction = DIR_IN;
  optr->Arg_Car[idx].categorie = VECTOR;
  optr->Arg_Car[idx].typ = ATYC_IF32;
  optr->Arg_Car[idx].array_dim = "1";
  optr->Arg_Car[idx].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[idx].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[idx].sample = "$Arg1.sample";
  optr->Arg_Car[idx].unite = "$Arg2.unit";
  idx++;

  optr->Arg_Car[idx].direction = DIR_OUT;
  optr->Arg_Car[idx].categorie = VECTOR;
  optr->Arg_Car[idx].typ = ATYC_IF32;
  optr->Arg_Car[idx].array_dim = "1";
  optr->Arg_Car[idx].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[idx].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[idx].sample = "$Arg1.sample";
  optr->Arg_Car[idx].ref_time = "$Arg1.ref_time";
  optr->Arg_Car[idx].misval = "$Arg1.misval";
  optr->Arg_Car[idx].unite = "$Arg1.unit";
  optr->Arg_Car[idx].famille = "$Arg1.famille";
  optr->Arg_Car[idx].name = "$Arg1.name + \" corrige de la pression\"";
  optr->Arg_Car[idx].en_name = "$Arg1.english_name + \" pressure-corrected\"";
  idx++;
}
