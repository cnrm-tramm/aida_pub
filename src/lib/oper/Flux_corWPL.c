/******************************************************************
*
* OPERATOR      Flux_corWPL.c   FUNCTION  ANSI-C
*
* PURPOSE 	Applique la correction de flux de densité de WPL au flux vertical
* d'une quantité C
*
* DESCRIPTION    
*
* VERSION       $Revision: 5097 $
*
* ARGUMENTS   IN  float  rhoa 	    	kg/m3 	Densité de l'air sec 
* 	      IN  float  rhov		g/m3	Densité de la vapeur d'eau
*             IN  float  rhoc    	g/m3    Densité du gaz dont on veut calculer le flux  
*             IN  float  t      	C ou K  Température de l'air  
*             IN  float  cov_wrhov     	g.s-1.m-2   Covariance vitesse verticale*rhov 
*             IN  float  cov_wt    	K.m.s-1   Covariance vitesse verticale*T
*             IN  float  cov_wrhoc    	K.m.s-1   Covariance vitesse verticale*rhoc (flux a corriger)
*
*             OUT float  wdens   	m/s	    Vitesse verticale moyenne due au flux de densité 
*             OUT float  flx_c   	g.s-1.m-2   Flux de C corrigé 
*
* ENTRY
*
* SUBPROGRAMS   none
*
* FILES
*
* REFERENCES
*
* E.K. Webb, G.I. Pearman, R.Leuning, 1980 
* Correction of flux measurements for density effects due to heat and water
* vapour transfer
* QJRMS 106, pp 85-100
*
* CHANGES       
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

#include "unit_def.h"


/* La vraie fonction... */
unsigned long
Flux_corWPL (unsigned long NLoop,
		  const float *rhoa,
		  const float *rhov,
		  const float *rhoc,
		  const float *t,
		  const float *cov_wrhov,
		  const float *cov_wt,
		  const float *cov_wrhoc,
                  float *wdens, 
                  float *flx_c)
{
  unsigned long i;
  float CtoK, ma, mv, mu, sigma;
  float a, b;
  int flag_info_tempe;

  /* Détermination automatique Kelvin/Celsius */
  flag_info_tempe = auto_tempe_unit (NLoop, t, &CtoK);

  /* masses molaires de l'air sec et la vapeur d'eau */
  mv = 18.015;
  ma = 28.98; 
  mu = ma/mv; 

  /* attention on considere que rhov, rhoc sont en g/m3 
   * et cov_wrhoc en g.m-2.s-1 
   * et rhoa en kg/m3 !*/

  for (i = 0; i < NLoop; i++)
    {
     sigma = rhov[i]/(rhoa[i]*1000.);
     a = mu*(cov_wrhov[i]/(rhoa[i]*1000.)); 
     b =  (1.+ mu*sigma)*(cov_wt[i]/(t[i] + CtoK) );
     wdens[i] = a +  b ;
     flx_c[i] =  cov_wrhoc[i] + rhoc[i]*wdens[i];

    }
  return flag_info_tempe;
}


/* la fonction d'enrobage classique */

int
OP_Flux_corWPL (unsigned long NbVal, void *ArgList[], char *DiagExec)
{
  int nc;
  int CodRet;

  CodRet = Flux_corWPL (NbVal,
			     (float *) ArgList[0],
			     (float *) ArgList[1],
			     (float *) ArgList[2],
			     (float *) ArgList[3],
			     (float *) ArgList[4],
			     (float *) ArgList[5],
			     (float *) ArgList[6],
			     (float *) ArgList[7],
                             (float *) ArgList[8]);
  switch (CodRet)
    {
    case T_EN_K:
      strcat (DiagExec, " Tempe reconnue en Kelvins");
      break;;
    case T_EN_C:
      strcat (DiagExec, " Tempe reconnue en degres Celsius");
      break;;
    case MANQUANTES:
      strcat (DiagExec, "Unite tempe non reconnue");
      return OP_FAIL;
      break;
    }
  return OP_OK;
}

/* la fonction de description de l'operateur et ses arguments */

void
ID_Flux_corWPL (oper * optr)
{
  int i;
  strcpy (optr->Nom, "Flux_corWPL");
  optr->Version = "$Revision: 5097 $";
  optr->Date = "$Date: 2013-03-25 13:23:40 +0100 (lun. 25 mars 2013) $";
  optr->fctptr = OP_Flux_corWPL;
  optr->NbArg = 9;

  /*  rhoa */
  optr->Arg_Car[0].direction = DIR_IN;
  optr->Arg_Car[0].categorie = VECTOR;
  optr->Arg_Car[0].typ = ATYC_IF32;
  optr->Arg_Car[0].array_dim = "1";
  optr->Arg_Car[0].type_sample = "any";
  optr->Arg_Car[0].sample = "any";
  optr->Arg_Car[0].unite = "kg.m-3";
  optr->Arg_Car[0].famille = "\"thermodynamique\"";

  /* rhov */
  optr->Arg_Car[1].direction = DIR_IN;
  optr->Arg_Car[1].categorie = VECTOR;
  optr->Arg_Car[1].typ = ATYC_IF32;
  optr->Arg_Car[1].array_dim = "1";
  optr->Arg_Car[1].type_sample = "any";
  optr->Arg_Car[1].sample = "any";
  optr->Arg_Car[1].unite = "g/m3";
  optr->Arg_Car[1].famille = "\"eau_vapeur\"";

  /* rhoc */
  optr->Arg_Car[2].direction = DIR_IN;
  optr->Arg_Car[2].categorie = VECTOR;
  optr->Arg_Car[2].typ = ATYC_IF32;
  optr->Arg_Car[2].array_dim = "1";
  optr->Arg_Car[2].type_sample = "any";
  optr->Arg_Car[2].sample = "any";
  optr->Arg_Car[2].unite = "g/m3";
  optr->Arg_Car[2].famille = "any";

  /* t */
  optr->Arg_Car[3].direction = DIR_IN;
  optr->Arg_Car[3].categorie = VECTOR;
  optr->Arg_Car[3].typ = ATYC_IF32;
  optr->Arg_Car[3].array_dim = "1";
  optr->Arg_Car[3].type_sample = "any";
  optr->Arg_Car[3].sample = "any";
  optr->Arg_Car[3].unite = "any";
  optr->Arg_Car[3].famille = "temperature";

  /* cov_wrhov */
  optr->Arg_Car[4].direction = DIR_IN;
  optr->Arg_Car[4].categorie = VECTOR;
  optr->Arg_Car[4].typ = ATYC_IF32;
  optr->Arg_Car[4].array_dim = "1";
  optr->Arg_Car[4].type_sample = "any";
  optr->Arg_Car[4].sample = "any";
  optr->Arg_Car[4].unite = "g.s-1.m-2";
  optr->Arg_Car[4].famille = "any";

  /* cov_wt */
  optr->Arg_Car[5].direction = DIR_IN;
  optr->Arg_Car[5].categorie = VECTOR;
  optr->Arg_Car[5].typ = ATYC_IF32;
  optr->Arg_Car[5].array_dim = "1";
  optr->Arg_Car[5].type_sample = "any";
  optr->Arg_Car[5].sample = "any";
  optr->Arg_Car[5].unite = "m.K.s-1";
  optr->Arg_Car[5].famille = "any";

  /*cov_wrhoc*/
  optr->Arg_Car[6].direction = DIR_IN;
  optr->Arg_Car[6].categorie = VECTOR;
  optr->Arg_Car[6].typ = ATYC_IF32;
  optr->Arg_Car[6].array_dim = "1";
  optr->Arg_Car[6].type_sample = "any";
  optr->Arg_Car[6].sample = "any";
  optr->Arg_Car[6].unite = "g.s-1.m-2";
  optr->Arg_Car[6].famille = "any";

  /* wdens */
  optr->Arg_Car[7].direction = DIR_OUT;
  optr->Arg_Car[7].categorie = VECTOR;
  optr->Arg_Car[7].typ = ATYC_IF32;
  optr->Arg_Car[7].array_dim = "1";
  optr->Arg_Car[7].NbVal = "$Arg7.NbVal";
  optr->Arg_Car[7].misval = "$Arg7.misval";
  optr->Arg_Car[7].type_sample = "$Arg7.type_sample";
  optr->Arg_Car[7].sample = "$Arg7.sample";
  optr->Arg_Car[7].ref_time = "$Arg7.ref_time";
  optr->Arg_Car[7].unite = "m/s";
  optr->Arg_Car[7].famille = "\"vent\"";
  optr->Arg_Car[7].name = "\"Vitesse verticale de courant de densite\"";
  optr->Arg_Car[7].en_name = "\"Vertical density wind\"";

  /* flx_c */
  optr->Arg_Car[8].direction = DIR_OUT;
  optr->Arg_Car[8].categorie = VECTOR;
  optr->Arg_Car[8].typ = ATYC_IF32;
  optr->Arg_Car[8].array_dim = "1";
  optr->Arg_Car[8].NbVal = "$Arg7.NbVal";
  optr->Arg_Car[8].misval = "$Arg7.misval";
  optr->Arg_Car[8].type_sample = "$Arg7.type_sample";
  optr->Arg_Car[8].sample = "$Arg7.sample";
  optr->Arg_Car[8].ref_time = "$Arg7.ref_time";
  optr->Arg_Car[8].unite = "$Arg7.unit";
  optr->Arg_Car[8].famille = "\"flux\"";
  optr->Arg_Car[8].name = "$Arg7.name+\" avec correction WPL\"";
  optr->Arg_Car[8].en_name = "$Arg7.english_name+\"with WPL correction\"";

}
