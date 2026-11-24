/******************************************************************
*
* OPERATOR      Cor_flow_azi_POM.c   FUNCTION  ANSI-C
*
* PURPOSE       Application d'une correction de distortion d'ecoulement
*              a une mesure de vitesse.
*
* DESCRIPTION   calcul d'un coeeficient de correction par application
*              de 2 polynomes (1 sur le tangage, l'autre sur la direction).
*
* VERSION       1.1
*
* ARGUMENTS   IN   float  FF         Any          Vitesse d'ecoulement.
*             IN   float  DD         degree       Azimut
*             IN   float  Coef_0     Any          Constant coefficient
*             IN   float  Coef_1     Any          coefficient of X
*             IN   float  Coef_2     Any          coefficient of X^2
*             IN   float  Coef_3     Any          coefficient of X^3
*             IN   float  Coef_4     Any          coefficient of X^4
*             IN   float  B_min      Any          mini de la gamme d'application
*             IN   float  B_max      Any          maxi de la gamme d'application
*
*             OUT  float  FF_cor   same as 1      Vitesse corrigee
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

/* La vraie fonction... */
unsigned long
Cor_flow_azi_POM (unsigned long NLoop,
	     const float *FF,
	     const float *DD,
	     const float C0_DD,
	     const float C1_DD,
	     const float C2_DD,
	     const float C3_DD,
	     const float C4_DD,
	     const float min_DD,
	     const float max_DD,
	     float *FF_cor)
{
  unsigned long i;
  double dir, coef_cor;


  for (i = 0; i < NLoop; i++)
    {
      dir = DD[i];
      if (dir > 180.0)
	dir -= 360.0;
      else if (dir < -180.0)
	dir += 360.0;

      if (dir < min_DD)
	coef_cor = 1.0;
      else if (dir > max_DD)
	coef_cor = 1.0;
      else
	coef_cor = C0_DD + dir * (C1_DD + dir * C2_DD + dir * dir * C3_DD + dir * dir * dir * C4_DD) ;


      FF_cor[i] = FF[i] * coef_cor;
    }
  return i;
}


/* la fonction d'enrobage classique */

int
OP_Cor_flow_azi_POM (unsigned long NbVal, void *ArgList[], char *DiagExec)
{
  unsigned long CodRet;
  int NCar;

  NCar = sprintf (DiagExec, "Cor_flow_azi_POM : (%ld echant.) ", NbVal) ;
  if (NCar < 0)
    NCar = 0;
  DiagExec += NCar;

/*
 * Le lecteur attentif aura remarqué que l'argument Nr 3
 * n'est pas passé à la routine de calcul. En fait, il ne sert
 * qu'à remplir le champ "unit" du vecteur de sortie.
 */
  CodRet = Cor_flow_azi_POM (NbVal,
			(float *) ArgList[0],
			(float *) ArgList[1],
			*((float *) ArgList[2]),
			*((float *) ArgList[3]),
			*((float *) ArgList[4]),
			*((float *) ArgList[5]),
			*((float *) ArgList[6]),
			*((float *) ArgList[7]),
			*((float *) ArgList[8]),
			(float *) ArgList[9]);
  if (CodRet == NbVal)
    return OP_OK;
  else
    return OP_FAIL;
}

/* la fonction de description de l'operateur et ses arguments */

void
ID_Cor_flow_azi_POM (oper * optr)
{
  strcpy (optr->Nom, "Cor_flow_azi_POM");
  optr->Version = "1.0";
  optr->Date = "21/05/02";
  optr->fctptr = OP_Cor_flow_azi_POM;
  optr->NbArg = 10;

  /* FF */
  optr->Arg_Car[0].direction = DIR_IN;
  optr->Arg_Car[0].categorie = VECTOR;
  optr->Arg_Car[0].typ = ATYC_IF32;
  optr->Arg_Car[0].array_dim = "1";
  optr->Arg_Car[0].type_sample = "any";
  optr->Arg_Car[0].sample = "any";
  optr->Arg_Car[0].unite = "any";

  /* DD */
  optr->Arg_Car[1].direction = DIR_IN;
  optr->Arg_Car[1].categorie = VECTOR;
  optr->Arg_Car[1].typ = ATYC_IF32;
  optr->Arg_Car[1].array_dim = "1";
  optr->Arg_Car[1].type_sample = "any";
  optr->Arg_Car[1].sample = "any";
  optr->Arg_Car[1].unite = "degree";

  optr->Arg_Car[2].direction = DIR_IN;
  optr->Arg_Car[2].categorie = COEFFICIENT;
  optr->Arg_Car[2].array_dim = "1";
  optr->Arg_Car[2].typ = ATYC_IF32;
  optr->Arg_Car[2].type_sample = NULL;	/* sans signification pour COEFFICIENT */
  optr->Arg_Car[2].sample = NULL;
  optr->Arg_Car[2].unite = "any";

  optr->Arg_Car[3].direction = DIR_IN;
  optr->Arg_Car[3].categorie = COEFFICIENT;
  optr->Arg_Car[3].array_dim = "1";
  optr->Arg_Car[3].typ = ATYC_IF32;
  optr->Arg_Car[3].type_sample = NULL;	/* sans signification pour COEFFICIENT */
  optr->Arg_Car[3].sample = NULL;
  optr->Arg_Car[3].unite = "any";

  optr->Arg_Car[4].direction = DIR_IN;
  optr->Arg_Car[4].categorie = COEFFICIENT;
  optr->Arg_Car[4].array_dim = "1";
  optr->Arg_Car[4].typ = ATYC_IF32;
  optr->Arg_Car[4].type_sample = NULL;	/* sans signification pour COEFFICIENT */
  optr->Arg_Car[4].sample = NULL;
  optr->Arg_Car[4].unite = "any";

  optr->Arg_Car[5].direction = DIR_IN;
  optr->Arg_Car[5].categorie = COEFFICIENT;
  optr->Arg_Car[5].array_dim = "1";
  optr->Arg_Car[5].typ = ATYC_IF32;
  optr->Arg_Car[5].type_sample = NULL;	/* sans signification pour COEFFICIENT */
  optr->Arg_Car[5].sample = NULL;
  optr->Arg_Car[5].unite = "any";

  optr->Arg_Car[6].direction = DIR_IN;
  optr->Arg_Car[6].categorie = COEFFICIENT;
  optr->Arg_Car[6].array_dim = "1";
  optr->Arg_Car[6].typ = ATYC_IF32;
  optr->Arg_Car[6].type_sample = NULL;	/* sans signification pour COEFFICIENT */
  optr->Arg_Car[6].sample = NULL;
  optr->Arg_Car[6].unite = "any";

  optr->Arg_Car[7].direction = DIR_IN;
  optr->Arg_Car[7].categorie = COEFFICIENT;
  optr->Arg_Car[7].array_dim = "1";
  optr->Arg_Car[7].typ = ATYC_IF32;
  optr->Arg_Car[7].type_sample = NULL;
  optr->Arg_Car[7].sample = NULL;
  optr->Arg_Car[7].unite = "any";

  optr->Arg_Car[8].direction = DIR_IN;
  optr->Arg_Car[8].categorie = COEFFICIENT;
  optr->Arg_Car[8].array_dim = "1";
  optr->Arg_Car[8].typ = ATYC_IF32;
  optr->Arg_Car[8].type_sample = NULL;	/* sans signification pour COEFFICIENT */
  optr->Arg_Car[8].sample = NULL;
  optr->Arg_Car[8].unite = "any";

  optr->Arg_Car[9].direction = DIR_OUT;
  optr->Arg_Car[9].categorie = VECTOR;
  optr->Arg_Car[9].typ = ATYC_IF32;
  optr->Arg_Car[9].array_dim = "1";
  optr->Arg_Car[9].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[9].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[9].sample = "$Arg1.sample";
  optr->Arg_Car[9].ref_time = "$Arg1.ref_time";
  optr->Arg_Car[9].misval = "$Arg1.misval";
  optr->Arg_Car[9].unite = "$Arg1.unit";
  optr->Arg_Car[9].famille = "$Arg1.famille";

}
