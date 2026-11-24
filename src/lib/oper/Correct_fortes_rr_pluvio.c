/*************************************************************************
*
* OPERATOR         Correct_fortes_rr_pluvio.c  FUNCTION ANSI-C
*
* PURPOSE          Correction des données des pluvio en fonction des fortes précipitation suivant un algorithme fournit
*                  par la DSO.  pas de temps : la journée, donc on risque de perdre des précipitaiton s'il pleut a la
*                  fin de la journée
*             
* DESCRIPTION     
*                 
*                 
*
* VERSION          1.0 
*
* ARGUMENTS  
*            IN   int     Ni        nb de basculement à la minute	
*            IN   float   coef_A	coefficient d'étalonnage en fonction du pluvio
*            IN   float   coef_B	coefficient d'étalonnage
*            IN   float   coef_C    coefficient d'étalonnage  
*            IN   float   R         résolution du pluvio                            
*
*            OUT  float   Ii        intensité des précipitations à la minute en mm/s
*            
*            
*
* ENTRY        NONE
*        
* SUBPROGRAMS  NONE
*        
* REFERENCES   Document DSO (Algorithme de traitement des données de précipitation du Préci-mécanique )
*
* COPYRIGHT    Meteo-France
*	       Centre National de Recherches Meteorologiques 
*	       GMEI/ TRAMM
*	       42, av G. Coriolis
*	       31057 TOULOUSE cedex  
*
*
*############################################################################*/

#define _POSIX_SOURCE 1
#define _XOPEN_SOURCE 600
#define _HPUX_SOURCE 1
#ifndef K_T0
#define K_T0 273.15
#endif

#include <math.h>
#include <stdio.h>
#include <string.h>
#include <math.h>
#include "struct_oper.h"


int
Correct_fortes_rr_pluvio (unsigned long ndata,
	  float *RRB, /* cumul brut de precipitation a la minute */
	  const float coef_A,
	  const float coef_B,
	  const float coef_C,
	  const float coef_R, /* resolutiuon pluvio */
      float *RRCi /* cumul corrigé de précipitation à la minute */
      )
{
  unsigned long i;
  double precRRBi; /* valeur précédente du cumul brut de précipitation a la minute */
  double Ii; /* intensite minute*/
  double Ki; /*coefficient de correction à la minute */
  double Ci; /*correction totale a appliquer à la minute */
  double RESi; /*reste de de la minute en cours */
  double RESav; /*reste de de la minute précédente */
  double INCi; /*correction a rajouter à la minute i */
  /*int iINCi; *//* partie entiere de INCi*/
  
  RESav=0;
  precRRBi=0;
  for (i = 0; i < ndata; i++)
    {
    /* on verifie si RRB n'est pas une valeur manquante avant de faire le calcul sinon on réinitialise les cumuls */
    if (!isfinite(RRB[i]))
        {
        printf("WARN: valeur manquante trouvée pour RRB[%ld], on réinitialise les restes de pluie\n",i);
        RESav=0;
        precRRBi=0;
        RRCi[i]=RRB[i];
        continue;
        }
    /* cumul brut des précipitation a la minute */
    /*RRBi=Ni[i]*coef_R;*/
    /* Intensité minute         */
    Ii=RRB[i]/60;
    if (Ii> 0.07) 
        Ii=0.07;
    /* calcul du coefficient de correction */
    Ki= coef_A * Ii*Ii + coef_B * Ii + coef_C;
    /* correction totale à  appliquer à la minute */
     Ci = Ki * RRB[i]; 
    /* cumul des corrections a rajouter: on n'ajoute que des multiples de 0.1 mm, le reste est gardé en mémoire */
    /* détail du calcul:
     * iINCi=10 *  (Ci +RESi)  ; INCi= iINCi/10.;*/ 
    INCi=(int)(10 *  (Ci +RESav) ) /10.;
    /* reste pour l'échéance suivante */
    RESi=RESav+Ci-INCi;
    /* s'il n'a pas plu depuis 2 minutes on réinitialse le reste */
    if ( (RRB[i] == 0) && (precRRBi == 0) )
        RESi=0;
    /* cumul corrigé */
    RRCi[i]=RRB[i]+INCi;
    precRRBi=RRB[i];
    if (RRB[i]>0)
        printf("RRBi[%ld]: %f Ci:%f cumul: %f Inci:%f (%f) RESi:%f RRCI:%f precRRBi:%f\n",i,RRB[i], Ci, (Ci+RESav) , INCi ,(10*(Ci+RESav)), RESi ,  RRCi[i], precRRBi);

    RESav=RESi;
    }

  return 0;
}


/* la fonction d'enrobage classique */

int
OP_Correct_fortes_rr_pluvio (unsigned long NbVal, void *ArgList[], char *DiagExec)
{
  (void) sprintf (DiagExec, "Correct_fortes_rr_pluvio, %lu echant.", NbVal);

  Correct_fortes_rr_pluvio (NbVal, (float *) ArgList[0], *(float *) ArgList[1], *(float *) ArgList[2],
	    *(float *) ArgList[3], *(float *) ArgList[4], (float *) ArgList[5]);

  return OP_OK;
}

void
ID_Correct_fortes_rr_pluvio (oper * optr)
{
  strcpy (optr->Nom, "Correct_fortes_rr_pluvio");
  optr->Version = "$Revision: 5268 $";
  optr->Date = "$Date: 2015-08-11 12:06:01 +0200 (mer. 11 aout. 2015) $";
  optr->fctptr = OP_Correct_fortes_rr_pluvio;
  optr->NbArg = 6;		/* doit rester inf. a FIL_MAX_ARG */

  /* RRB :cumul brut des précipitations en 1 minute (Nb basculement Ni* résolution du pluvio R) */
  optr->Arg_Car[0].direction = DIR_IN;
  optr->Arg_Car[0].categorie = VECTOR;
  optr->Arg_Car[0].typ = ATYC_IF32;
  optr->Arg_Car[0].array_dim = "1";
  optr->Arg_Car[0].type_sample = "any";
  optr->Arg_Car[0].sample = "any";
  optr->Arg_Car[0].unite = "";

  /* coef_A */
  optr->Arg_Car[1].direction = DIR_IN;
  optr->Arg_Car[1].categorie = COEFFICIENT;
  optr->Arg_Car[1].typ = ATYC_IF32;
  optr->Arg_Car[1].array_dim = "1";
  optr->Arg_Car[1].unite = "";

  /* coef_B */
  optr->Arg_Car[2].direction = DIR_IN;
  optr->Arg_Car[2].categorie = COEFFICIENT;
  optr->Arg_Car[2].typ = ATYC_IF32;
  optr->Arg_Car[2].array_dim = "1";
  optr->Arg_Car[2].unite = "";

  /* coef_C */
  optr->Arg_Car[3].direction = DIR_IN;
  optr->Arg_Car[3].categorie = COEFFICIENT;
  optr->Arg_Car[3].typ = ATYC_IF32;
  optr->Arg_Car[3].array_dim = "1";
  optr->Arg_Car[3].unite = "";

  /* coef_R */
  optr->Arg_Car[4].direction = DIR_IN;
  optr->Arg_Car[4].categorie = COEFFICIENT;
  optr->Arg_Car[4].typ = ATYC_IF32;
  optr->Arg_Car[4].array_dim = "1";
  optr->Arg_Car[4].unite = "";

  /* RRCi */
  optr->Arg_Car[5].direction = DIR_OUT;
  optr->Arg_Car[5].categorie = VECTOR;
  optr->Arg_Car[5].typ = ATYC_IF32;
  optr->Arg_Car[5].array_dim = "1";
  optr->Arg_Car[5].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[5].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[5].sample = "$Arg1.sample";
  optr->Arg_Car[5].ref_time = "$Arg1.ref_time";
  optr->Arg_Car[5].unite = "$Arg1.unit";
  optr->Arg_Car[5].misval = "$Arg1.misval";
  optr->Arg_Car[5].name = "$Arg1.name";
  optr->Arg_Car[5].en_name = "$Arg1.english_name";
}
