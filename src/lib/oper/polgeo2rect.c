/*****************************************************
*
* OPERATOR         polgeo2rect.c   FUNCTION  ANSI-C
*
* PURPOSE          Convert Polar coordinates with respect to
*                  geographic frame (angles clokwise from North)
*                  to cartesian coordinates.
*
* DESCRIPTION      
*
* VERSION          $Revision$
*
* ARGUMENTS  IN    float   M      any            module
*            IN    float   alpha  Degree/radian  angle
*            IN    string  unite                 unite de l'angle
*            OUT   float   Comp_E Same as M      Composante sur l'axe Ouest-Est
*            OUT   float   Comp_N Same as M      Composante sur l'axe Sud-Nord
*
*                                                
* ENTRY            NONE
*               
* SUBPROGRAMS      NONE
*
* FILES            NONE
*
* REFERENCES       
*
*
* CHANGES          1.3  adapted to follow categorie's definition change
*                  1.2  added args' sampling description
*
*
* COPYRIGHT        Meteo-France/CNRM
*
* AGREEMENT        
*########################################################################*/

#define _POSIX_SOURCE 1
#define _XOPEN_SOURCE 600
/* Le #define _HPUX_SOURCE est la pour utiliser la fonction finitef */
#define _HPUX_SOURCE 1

#include <math.h>
#include <stdio.h>
#include <string.h>
#include <strings.h>
#include "struct_oper.h"


int
polgeo2rect (unsigned long NLoop,
	     const float *M,
	     const float *alpha,
	     const char *unite,
	     float *Comp_E,
	     float *Comp_N)
{
  unsigned long i;
  double D_to_R;
  int Flag_unit;

  /*  TODO : utiliser reconnait_deg_rad() */
  if (!strcasecmp (unite, "degree"))
    {
      D_to_R = M_PI / 180.0;
      Flag_unit = 1;
    }
  else if (!strcasecmp (unite, "radian"))
    {
      D_to_R = 1.0;
      Flag_unit = 0;
    }
  else
    Flag_unit = -1;

  for (i = 0; i < NLoop; i++)
    {
      if (!isfinite (*M) || !isfinite (*alpha))
	{			/* Valeur non correctement représentées par un float */
	  *Comp_E = 0. / 0.;
	  *Comp_N = 0. / 0.;
	}
      else
	{
	  *Comp_E = *M * sin (*alpha * D_to_R);
	  *Comp_N = *M * cos (*alpha * D_to_R);
	}

      M++;
      alpha++;
      Comp_E++;
      Comp_N++;
    }

  return Flag_unit;
}


/* la fonction d'enrobage classique */

int
OP_polgeo2rect (unsigned long NbVal, void *ArgList[], char *DiagExec)
{
  int CodRet;

  (void) sprintf (DiagExec, "polgeo2rect, NbVal=%lu", NbVal);

  CodRet = polgeo2rect (NbVal,
			(float *) ArgList[0],
			(float *) ArgList[1],
			(char *) ArgList[2],
			(float *) ArgList[3],
			(float *) ArgList[4]);

  switch (CodRet)
    {
    case 1:
      strcat (DiagExec, ", Unite angle reconnue : degree");
      return OP_OK;
    case 0:
      strcat (DiagExec, ", Unite angle reconnue : radian");
      return OP_OK;
    case -1:
      strcat (DiagExec, ",ERR : Unite angle non reconnue");
      return OP_FAIL;
    default:
      strcat (DiagExec, ",Erreur inattendue");
      return OP_FAIL;
    }

  return OP_OK;
}

void
ID_polgeo2rect (oper * optr)
{
  strcpy (optr->Nom, "polgeo2rect");
  optr->Version = "$Revision$";
  optr->Date = "$Date$";
  optr->fctptr = OP_polgeo2rect;
  optr->misval_auto = 1;	/* gestion auto des misval */
  optr->NbArg = 5;

/*  Pour l'instant, les specifications d'unites sont approximatives.
 *  L'ideal serait : Arg_Car[1].unit = "degree OR radian". 
 *  Helas; l'interpreteur actuel ne sait pas gérer ça.
 */

  /* M  (module) */
  optr->Arg_Car[0].direction = DIR_IN;
  optr->Arg_Car[0].categorie = VECTOR;
  optr->Arg_Car[0].typ = ATYC_IF32;
  optr->Arg_Car[0].array_dim = "1";
  optr->Arg_Car[0].type_sample = "any";
  optr->Arg_Car[0].sample = "any";
  optr->Arg_Car[0].unite = "any";

  /* alpha */
  optr->Arg_Car[1].direction = DIR_IN;
  optr->Arg_Car[1].categorie = VECTOR;
  optr->Arg_Car[1].typ = ATYC_IF32;
  optr->Arg_Car[1].array_dim = "1";
  optr->Arg_Car[1].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[1].type_sample = "any";
  optr->Arg_Car[1].sample = "any";
  optr->Arg_Car[1].unite = "any";	/* en vrai : degre ou radian */

  /* unite */
  optr->Arg_Car[2].direction = DIR_IN;
  optr->Arg_Car[2].categorie = COEFFICIENT;
  optr->Arg_Car[2].typ = ATYC_STRING;
  optr->Arg_Car[2].array_dim = "1";
  optr->Arg_Car[2].type_sample = "";
  optr->Arg_Car[2].sample = "";
  optr->Arg_Car[2].unite = "";

  /* Comp_E */
  optr->Arg_Car[3].direction = DIR_OUT;
  optr->Arg_Car[3].categorie = VECTOR;
  optr->Arg_Car[3].typ = ATYC_IF32;
  optr->Arg_Car[3].array_dim = "1";
  optr->Arg_Car[3].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[3].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[3].sample = "$Arg1.sample";
  optr->Arg_Car[3].ref_time = "$Arg1.ref_time";
  optr->Arg_Car[3].misval = "$Arg1.misval";
  optr->Arg_Car[3].unite = "$Arg1.unit";
  optr->Arg_Car[3].famille = "$Arg1.famille";
  optr->Arg_Car[3].name = "Composante zonale de $Arg1.name";

  /* Comp_N */
  optr->Arg_Car[4].direction = DIR_OUT;
  optr->Arg_Car[4].categorie = VECTOR;
  optr->Arg_Car[4].typ = ATYC_IF32;
  optr->Arg_Car[4].array_dim = "1";
  optr->Arg_Car[4].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[4].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[4].sample = "$Arg1.sample";
  optr->Arg_Car[4].ref_time = "$Arg1.ref_time";
  optr->Arg_Car[4].misval = "$Arg1.misval";
  optr->Arg_Car[4].unite = "$Arg1.unit";
  optr->Arg_Car[4].famille = "$Arg1.famille";
  optr->Arg_Car[4].name = "Composante meridienne de $Arg1.name";

}
