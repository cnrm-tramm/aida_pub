/*****************************************************
*
* OPERATOR        volumic_to_mass_concentration.c   FUNCTION  ANSI-C
*
* PURPOSE         Compute the mass concentration in g/m3 with volumic concentration of a gaz 
*
* DESCRIPTION 	  
*
*
* VERSION         1.0
*
* ARGUMENTS  IN   float      Cv  	m3/m3	Volumic concentration of a gaz	
*            IN   float      T  	C or K 	Air temperature	
*            IN   float      P  	hPa 	Air pressure	
*            IN   float      M  	g/mol 	Gaz molar mass	
*
*            OUT  float      C		g/m3 	Gaz mass concentration	
*                                                
*                                                
* ENTRY           NONE
*               
*
* SUBPROGRAMS     NONE
*
* FILES           NONE
*
* REFERENCES     
*
* CHANGES        
*
*
* COPYRIGHT       Meteo-France/CNRM
*
* AGREEMENT       
*########################################################################*/

#define _POSIX_SOURCE 1
#define _XOPEN_SOURCE 600
/* Le #define _HPUX_SOURCE n'est la que pour "voir" isfinite() */
#define _HPUX_SOURCE 1

#include <math.h>
#include <stdio.h>
#include <string.h>

#include "struct_oper.h"

/* Pour reconnaissance auto d'unité */
#include "unit_def.h"

int
volumic_to_mass_concentration (unsigned long NLoop,
	 const float *Cv,
	 const float *T,
	 const float *P,
	 const double M,
	 float *C)
{
  unsigned long i;
  int flag_info_tempe;
  float CtoK;

  /* constante des gaz parfait*/
  float R = 8.314;

  flag_info_tempe = auto_tempe_unit (NLoop, T, &CtoK);

  if (flag_info_tempe == MANQUANTES)
   {
    for (i = 0; i < NLoop; i++)
      {
       C[i] = 0./0.; 
      }
    return flag_info_tempe;
   }

  for (i = 0; i < NLoop; i++)
    {
      /* test valeur physiquement plausible */
      if (((T[i] + CtoK) < 173.) ||
	  ((T[i] + CtoK) > 373.) || (P[i] < 1.) || (P[i] > 1500.0))
	{
	  C[i] = K_NaN;
	}
      else
	{
	  C[i] = Cv[i]*M*P[i]*100./(R * (T[i] + CtoK)); 
	}
    }

    return flag_info_tempe;
}


/* la fonction d'enrobage classique */

int
OP_volumic_to_mass_concentration (unsigned long NbVal, void *ArgList[], char *DiagExec)
{
  int CodRet;

  sprintf (DiagExec, "volumic_to_mass_concentration, NbVal=%lu, Ra = %g, Rv = %g",
	   NbVal, *((double *) ArgList[3]), *((double *) ArgList[4]));

  CodRet = volumic_to_mass_concentration (NbVal,
		    (float *) ArgList[0],
		    (float *) ArgList[1],
		    (float *) ArgList[2],
		    *((double *) ArgList[3]),
		    (float *) ArgList[4]);
  switch (CodRet)
    {
    case T_EN_C:
      strcat (DiagExec, "OK : T reconnue en Celsius");
      return OP_OK;
    case T_EN_K:
      strcat (DiagExec, "OK: T reconnue en Kelvin");
      return OP_OK;
    case MANQUANTES:
      strcat (DiagExec,
	      "; Trop de valeurs manquantes : unité de température non reconnue.");
      return OP_OK;
    default:
      sprintf (DiagExec, "ERR: Erreur %d", CodRet);
      return OP_FAIL;
    }
}

void
ID_volumic_to_mass_concentration (oper * optr)
{
  strcpy (optr->Nom, "volumic_to_mass_concentration");
  optr->Version = "$Revision: 6998 $";
  optr->Date = "$Date: 2017-10-25 16:50:18 +0200 (mer. 25 oct. 2017) $";
  optr->fctptr = OP_volumic_to_mass_concentration;
  optr->misval_auto = 1;	/* Gestion auto des misval */
  optr->NbArg = 5;

  /* Cv */
  optr->Arg_Car[0].direction = DIR_IN;
  optr->Arg_Car[0].categorie = VECTOR;
  optr->Arg_Car[0].typ = ATYC_IF32;
  optr->Arg_Car[0].array_dim = "1";
  optr->Arg_Car[0].type_sample = "any";
  optr->Arg_Car[0].sample = "any";
  optr->Arg_Car[0].unite = "m3/m3";
  optr->Arg_Car[0].famille = "any";

  /* T */
  optr->Arg_Car[1].direction = DIR_IN;
  optr->Arg_Car[1].categorie = VECTOR;
  optr->Arg_Car[1].typ = ATYC_IF32;
  optr->Arg_Car[1].type_sample = "any";
  optr->Arg_Car[1].sample = "any";
  optr->Arg_Car[1].array_dim = "1";
  optr->Arg_Car[1].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[1].unite = "K";
  optr->Arg_Car[1].famille = "\"temperature\"";

  /* P */
  optr->Arg_Car[2].direction = DIR_IN;
  optr->Arg_Car[2].categorie = VECTOR;
  optr->Arg_Car[2].typ = ATYC_IF32;
  optr->Arg_Car[2].type_sample = "any";
  optr->Arg_Car[2].sample = "any";
  optr->Arg_Car[2].array_dim = "1";
  optr->Arg_Car[2].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[2].unite = "hPa";
  optr->Arg_Car[2].famille = "\"pression\"";

  /* M */
  optr->Arg_Car[3].direction = DIR_IN;
  optr->Arg_Car[3].categorie = COEFFICIENT;
  optr->Arg_Car[3].array_dim = "1";
  optr->Arg_Car[3].typ = ATYC_IF64;
  optr->Arg_Car[3].unite = "any";

  /* La variable produite : Cv  */
  optr->Arg_Car[4].direction = DIR_OUT;
  optr->Arg_Car[4].categorie = VECTOR;
  optr->Arg_Car[4].typ = ATYC_IF32;
  optr->Arg_Car[4].array_dim = "1";
  optr->Arg_Car[4].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[4].sample = "$Arg1.sample";
  optr->Arg_Car[4].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[4].ref_time = "$Arg1.ref_time";
  optr->Arg_Car[4].misval = "$Arg1.misval";
  optr->Arg_Car[4].unite = "g/m3";
  optr->Arg_Car[4].famille = "$Arg1.famille";
  optr->Arg_Car[4].name = "Concentration massique";
  optr->Arg_Car[4].en_name = "Mass concentration";

}
