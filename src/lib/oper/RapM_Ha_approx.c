/*******************************************************************
* OPERATOR      RapM_Ha_approx.c FUNCTION ANSI-C
*
* PURPOSE       Calcul approché du rapport de mélange en vapeur d'eau (g/kg) à
*		partir de l'humidité absolue (ou concentration) (g/m3).
*
* DESCRIPTION   Division par la masse volumique ("densité") de l'air (kg/m3).
*               L'approximation réside dans le fait qu'on fait ce calcul avec
*               les constantes de l'air sec (Ra). Cette approximation peut être
*               justifiée dans les cas où l'humidité est faible (haute atmosphère)
*               ou que l'on part d'une température virtuelle ou sonique.
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

int
RapM_Ha_approx (unsigned long ndata,
	   float *Ha,
	   float *Ps,
	   float *Ts,
	   float *RapM)
{
  long i;

  double Ra = 287.05;

  double CtoK;
  double ro, T, P, H;

/*** conversion de la tempe. Celsius en Kelvin ***/
  if (Ts[0] < 100.)
    CtoK = 273.15;
  else
    CtoK = 0.;

  for (i = 0; i < ndata; i++)
    {
      T = ((double)Ts[i]) + CtoK;
      P = (double)Ps[i];
      H = (double)Ha[i];

/*** densite de l'air  ***/

      ro = (P * 100.) / (Ra * T);
      RapM[i] = (float)(H/ro);

    }

  return 0;
}

/* fonction d'enrobage */

int
OP_RapM_Ha_approx (unsigned long Nbval, void *ArgList[], char *DiagExec)
{
  int CodRet = RapM_Ha_approx (Nbval,
			  (float *) ArgList[0],
			  (float *) ArgList[1],
			  (float *) ArgList[2],
			  (float *) ArgList[3]);

  return OP_OK;
}

void
ID_RapM_Ha_approx (oper * optr)
{
  strcpy (optr->Nom, "RapM_Ha_approx");
  optr->Version = "1.0";
  optr->Date = "02/21/97";
  optr->fctptr = OP_RapM_Ha_approx;
  optr->NbArg = 4;

  optr->Arg_Car[0].direction = DIR_IN;
  optr->Arg_Car[0].categorie = VECTOR;
  optr->Arg_Car[0].typ = ATYC_IF32;
  optr->Arg_Car[0].array_dim = "1";
  optr->Arg_Car[0].type_sample = "any";
  optr->Arg_Car[0].sample = "any";
  optr->Arg_Car[0].unite = "gram/m3";

  optr->Arg_Car[1].direction = DIR_IN;
  optr->Arg_Car[1].categorie = VECTOR;
  optr->Arg_Car[1].typ = ATYC_IF32;
  optr->Arg_Car[1].array_dim = "1";
  optr->Arg_Car[1].type_sample = "any";
  optr->Arg_Car[1].sample = "any";
  optr->Arg_Car[1].unite = "hPa";

  optr->Arg_Car[2].direction = DIR_IN;
  optr->Arg_Car[2].categorie = VECTOR;
  optr->Arg_Car[2].typ = ATYC_IF32;
  optr->Arg_Car[2].array_dim = "1";
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
  optr->Arg_Car[3].unite = "gram/kg";
  optr->Arg_Car[3].famille = " \"eau_vapeur\" ";
}
