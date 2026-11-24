/******************************************************************
*
* OPERATOR      TPot_hum_Marquet.c   FUNCTION  ANSI-C
*
* PURPOSE  Calcul de temperature potentielle de l'air humide
* 	   selon la formulaion de Marquet-2015  
* 	   au second ordre en air clair (sans eau liquide)      
*
* DESCRIPTION    
*
* VERSION       $Revision: 5097 $
*
* ARGUMENTS   IN  float  Tpot 		C ou K    Temperature potentielle  
* 	      IN  float  r		g/kg      Rapport de melange en vapeur d'eau 
*             IN  float  Lambda     	without   Constante  
*             IN  float  Gamma     	without   Rapport Rv/Cp  
*             IN  float  r_star     	without   Constante de réglage  (kg/kg)
*
*             OUT float  Tpot_h   	C ou K    Temperature potentielle de l'air humide
*
* ENTRY
*
* SUBPROGRAMS   none
*
* FILES
*
* REFERENCES
* 
* Marquet 2015 - An improved approximation for the moist-air
* entropy potential temperature θs. WGNE Blue-book 2015
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
TPot_hum_Marquet (unsigned long NLoop,
		  const float *Tpot,
		  float *r,
		  float Lambda,
                  float Gamma,
                  float r_star,
                  float *Tpot_h)
{
  unsigned long i;
  double qv, rv;
  float CtoK, Tph;
  int flag_info_tempe;

  /* Détermination automatique Kelvin/Celsius */
  flag_info_tempe = auto_tempe_unit (NLoop, Tpot, &CtoK);

  if (flag_info_tempe == MANQUANTES)
   {
    for (i = 0; i < NLoop; i++)
      {
       Tpot_h[i] = 0./0.; 
      }
    return flag_info_tempe;
   }

  for (i = 0; i < NLoop; i++)
    {
      rv = r[i] * 0.001;
      qv = rv / (1. + rv);

      Tph =
	(Tpot[i] + CtoK) * exp (Lambda * qv) * pow ((r_star / rv), Gamma * qv);

      Tpot_h[i] = Tph - CtoK;
    }
  return flag_info_tempe;
}


/* la fonction d'enrobage classique */

int
OP_TPot_hum_Marquet (unsigned long NbVal, void *ArgList[], char *DiagExec)
{
  int nc;
  int CodRet;

  nc = sprintf (DiagExec,
		"TPot_hum_Marquet(%ld ech), Lambda=%g, Gamma=%g, r_star=%g",
		NbVal,
		*((float *) ArgList[2]),
		*((float *) ArgList[3]),
                *((float *) ArgList[4]));
  if (nc < 0)
    nc = 0;
  DiagExec += nc;

  /* L'argument Nr 6 n'est pas passé à la routine de calcul : il ne
   * sert qu'à remplir le champ "unit" du vecteur de sortie. */
  CodRet = TPot_hum_Marquet (NbVal,
			     (float *) ArgList[0],
			     (float *) ArgList[1],
			     *((float *) ArgList[2]),
			     *((float *) ArgList[3]),
			     *((float *) ArgList[4]),
                              (float *) ArgList[5]);
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
      break;
    default:
      strcat (DiagExec, "; BUG!! Code retour inattendu.");
      return OP_FAIL;

    }
  return OP_OK;
}

/* la fonction de description de l'operateur et ses arguments */

void
ID_TPot_hum_Marquet (oper * optr)
{
  int i;
  strcpy (optr->Nom, "TPot_hum_Marquet");
  optr->Version = "$Revision: 5097 $";
  optr->Date = "$Date: 2013-03-25 13:23:40 +0100 (lun. 25 mars 2013) $";
  optr->fctptr = OP_TPot_hum_Marquet;
  optr->NbArg = 6;

  /* Tpot */
  optr->Arg_Car[0].direction = DIR_IN;
  optr->Arg_Car[0].categorie = VECTOR;
  optr->Arg_Car[0].typ = ATYC_IF32;
  optr->Arg_Car[0].array_dim = "1";
  optr->Arg_Car[0].type_sample = "any";
  optr->Arg_Car[0].sample = "any";
  optr->Arg_Car[0].unite = "any";
  optr->Arg_Car[0].famille = "\"temperature\"";

  /* r */
  optr->Arg_Car[1].direction = DIR_IN;
  optr->Arg_Car[1].categorie = VECTOR;
  optr->Arg_Car[1].typ = ATYC_IF32;
  optr->Arg_Car[1].array_dim = "1";
  optr->Arg_Car[1].type_sample = "any";
  optr->Arg_Car[1].sample = "any";
  optr->Arg_Car[1].unite = "g/kg";
  optr->Arg_Car[1].famille = "\"eau_vapeur\"";

  for (i = 2; i <= 4; i++)
    {
      optr->Arg_Car[i].direction = DIR_IN;
      optr->Arg_Car[i].categorie = COEFFICIENT;
      optr->Arg_Car[i].array_dim = "1";
      optr->Arg_Car[i].typ = ATYC_IF32;
      optr->Arg_Car[i].unite = "any";
      optr->Arg_Car[i].type_sample = NULL;	/* sans signification pour COEFFICIENT */
      optr->Arg_Car[i].sample = NULL;
    }

  optr->Arg_Car[5].direction = DIR_OUT;
  optr->Arg_Car[5].categorie = VECTOR;
  optr->Arg_Car[5].typ = ATYC_IF32;
  optr->Arg_Car[5].array_dim = "1";
  optr->Arg_Car[5].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[5].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[5].sample = "$Arg1.sample";
  optr->Arg_Car[5].ref_time = "$Arg1.ref_time";
  optr->Arg_Car[5].unite = "$Arg1.unit";
  optr->Arg_Car[5].famille = "$Arg1.famille";
  optr->Arg_Car[3].name = "\"T. Potentielle humide selon Marquet";
  optr->Arg_Car[3].en_name =
    "\"Moist air potential temp. with respect to Marquet";
}
