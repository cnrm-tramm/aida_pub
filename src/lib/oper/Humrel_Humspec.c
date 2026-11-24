/******************************************************************
*
* OPERATOR      Humrel_Humspec.c   ANSI-C
*
* PURPOSE       Compute relative humidity  with specific humidity
*
* DESCRIPTION   Formulas used :
*
*                   Ra: Constante de l'air sec en Joule /kg/KRa, Ra=R * Md, avec R constante des gaz R = N * k, nb d'avogadro N = 6,0221367 10+23 mol-1 et cste Boltzman k = 1,380658 10-23 J K-1 et Md: masse moléculaire de l'air sec: Md = 28,9644 10+3 Kg mol-1
*                   Ra=287.05;
*                   Rv: constante de vapeur d'eau Rv = R /Mv J Kg-1 K-1, avec Mv: Masse moléculaire de l¿eau Mv = 18,0153 10+3 Kg mol-1
*                   Rv=461.51;
*                   #T en kelvin
*                   T0=273.15;
*                   if (T>=T0):
*                       on prend ewt (tension de vapeur saturante au dessus de l'eau)
*                   else :
*                       on prend ewi (tension de vapeur saturante au dessus de la glace)
*                      
*
*                   #pression en hpascal
*                   #Humidité spécifique a saturation en g/kg
*                   Qs=SH[i]/1000.;
*                   # Pression de vapeur 
*                   Es = Qs * Ps / (Ra/Rv + Qs * (1-Ra/Rv)); 
*                   #humidite relative
*                   RH = 100 * Es / ewt;

*
* VERSION       $Revision: 4912 $
*
* ARGUMENTS    IN   float  SH      g/Kg          Specific humidity 
*
*              OUT  float  RH      %             Relative humidity 
*
* ENTRY
*
* SUBPROGRAMS   none
*
* FILES
*
* REFERENCES
*
* CHANGES       
*
* COPYRIGHT     Meteo-France
*
* AGREEMENT     The author wishes that .....
*#########################################################################*/

#define _POSIX_SOURCE 1
#define _XOPEN_SOURCE 600
#define _HPUX_SOURCE 1

#include <math.h>

#include <stdio.h>
#include <string.h>
#include "struct_oper.h"
#include "unit.h"

#include "thermo.h"
#include "unit_def.h"

#ifndef K_Ra
    #define  K_Ra ( 8.314510 / 0.028964)
#endif
#ifndef K_Rv
    #define K_Rv ( 461.51)
#endif
#ifndef K_T_0
    #define  K_T_0 ( 273.15)
#endif


/* La vraie fonction... */
int
Humrel_Humspec (unsigned long NLoop, const float *SH, float *P, float *T, float *RH)
{
  unsigned long i;
  float Es;  /* Pression de vapeur */
  float Qs; /* humidite specifique en  g/kg */

  /*float e;*/ /*tension de vapeur*/
  float ewt; /* tension de vapeur saturante*/
  int flag_info_T; /* flag temperature Kelvin ou Celsius*/
  float CnvtoK_T; /*DT pour avoir des températures en Kelvin*/
  float l_T;

    /* calcul avec des celsius ou des kelvin*/
    flag_info_T = auto_tempe_unit (NLoop, T, &CnvtoK_T);

    for (i = 0; i < NLoop; i++)
        {
        l_T = T[i] + CnvtoK_T; /* Celsius ou Kelvin*/
        Qs=SH[i]/1000.;
        Es = Qs * P[i] / (K_Ra/K_Rv + Qs * (1-K_Ra/K_Rv)); /* pression de vapeur*/
        if (l_T>=K_T_0)
            ew(l_T,&ewt); /* calcul pression de vapeur saturante*/
        else
            ewi(l_T,&ewt); /* calcul pression de vapeur saturante par raport a la glace*/
        RH[i] = 100 * Es / ewt;
        }

}


/* la fonction d'enrobage classique */

int
OP_Humrel_Humspec (unsigned long NbVal, void *ArgList[], char *DiagExec)
{
  int CodRet;

  sprintf (DiagExec, "Hum_rel_Humspec (%lu ech); ", NbVal);

  /*CodRet = */Humrel_Humspec (NbVal, (float *) ArgList[0], (float *) ArgList[1], (float *) ArgList[2], (float *) ArgList[3] );

  return OP_OK;
}

/* la fonction de description de l'operateur et ses arguments */

void
ID_Humrel_Humspec (oper * optr)
{
  strcpy (optr->Nom, "Humrel_Humspec");
  optr->Version = "$Revision: 4912 $";
  optr->Date = "$Date: 2012-11-26 11:05:33 +0100 (lun. 26 nov. 2012) $";
  optr->fctptr = OP_Humrel_Humspec;
  optr->NbArg = 4;

  /* SH */
  optr->Arg_Car[0].direction = DIR_IN;
  optr->Arg_Car[0].categorie = VECTOR;
  optr->Arg_Car[0].typ = ATYC_IF32;
  optr->Arg_Car[0].array_dim = "1";
  optr->Arg_Car[0].type_sample = "any";
  optr->Arg_Car[0].sample = "any";
  optr->Arg_Car[0].unite = "g/kg";
  optr->Arg_Car[0].famille = " \"eau vapeur\" ";

  /* P */
  optr->Arg_Car[1].direction = DIR_IN;
  optr->Arg_Car[1].categorie = VECTOR;
  optr->Arg_Car[1].typ = ATYC_IF32;
  optr->Arg_Car[1].array_dim = "1";
  optr->Arg_Car[1].type_sample = "any";
  optr->Arg_Car[1].sample = "any";
  optr->Arg_Car[1].unite = "hPa";

  /* T */
  optr->Arg_Car[2].direction = DIR_IN;
  optr->Arg_Car[2].categorie = VECTOR;
  optr->Arg_Car[2].typ = ATYC_IF32;
  optr->Arg_Car[2].array_dim = "1";
  optr->Arg_Car[2].type_sample = "any";
  optr->Arg_Car[2].sample = "any";
  optr->Arg_Car[2].unite = "kelvin";

  /* RH */
  optr->Arg_Car[3].direction = DIR_OUT;
  optr->Arg_Car[3].categorie = VECTOR;
  optr->Arg_Car[3].typ = ATYC_IF32;
  optr->Arg_Car[3].array_dim = "1";
  optr->Arg_Car[3].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[3].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[3].sample = "$Arg1.sample";
  optr->Arg_Car[3].ref_time = "$Arg1.ref_time";
  optr->Arg_Car[3].misval = "$Arg1.misval";
  optr->Arg_Car[3].unite = "percent";
  optr->Arg_Car[3].famille = " \"eau_vapeur\" ";
  optr->Arg_Car[3].name = "\"Humidite relative a partir de \" + $Arg1.name ";

}
