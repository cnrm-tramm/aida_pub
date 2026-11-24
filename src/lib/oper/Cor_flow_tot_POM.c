/******************************************************************
*
* OPERATOR      Cor_flow_tot_POM.c   FUNCTION  ANSI-C
*
* PURPOSE       Application d'une correction de distortion d'ecoulement
*              a une mesure de vitesse.
*
* DESCRIPTION   calcul d'un coefficient de correction par application
*              de 2 polynomes (1 sur l'incidence, l'autre sur la direction).
*
* VERSION       1.1
*
* ARGUMENTS   IN   float  FF         Any          Vitesse d'ecoulement.
*             IN   float  DD         degree       Azimut X
*             IN   float  Coef_0     Any          Constant coefficient
*             IN   float  Coef_1     Any          coefficient of X
*             IN   float  Coef_2     Any          coefficient of X^2
*             IN   float  Coef_3     Any          coefficient of X^3
*             IN   float  Coef_4     Any          coefficient of X^4
*             IN   float  B_min      Any          mini de la gamme d'application
*             IN   float  B_max      Any          maxi de la gamme d'application
*	      IN   float  inc	     degree       angle of incidence Y
*             IN   float  Coef_0     Any          Constant coefficient for Y
*             IN   float  Coef_1     Any          coefficient of Y
*             IN   float  Coef_2     Any          coefficient of Y^2
*             IN   float  Coef_3     Any          coefficient of Y^3
*             IN   float  C_min      Any          mini de la gamme d'application
*             IN   float  C_max      Any          maxi de la gamme d'application
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
Cor_flow_tot_POM (unsigned long NLoop,
	     const float *FF,
	     const float *DD,
	     const float C0_DD,
	     const float C1_DD,
	     const float C2_DD,
	     const float C3_DD,
	     const float C4_DD,
	     const float min_DD,
	     const float max_DD,
	     const float *INC,
	     const float C0_ii,
	     const float C1_ii,
	     const float C2_ii,
	     const float C3_ii,
	     const float min_ii,
	     const float max_ii,
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

      if ( (dir < min_DD) || (INC[i] < min_ii) )
	coef_cor = 1.0;
      else if ( (dir > max_DD) || (INC[i] > max_ii) )
	coef_cor = 1.0;
      else
	coef_cor = (C0_DD + C0_ii)/2 + dir*(C1_DD + dir*C2_DD + dir*dir*C3_DD + dir*dir*dir*C4_DD) + INC[i]*(C1_ii +INC[i]*C2_ii + INC[i]*INC[i]*C3_ii) ;


      FF_cor[i] = FF[i] * coef_cor;
    }
  return i;
}


/* la fonction d'enrobage classique */

int
OP_Cor_flow_tot_POM (unsigned long NbVal, void *ArgList[], char *DiagExec)
{
  unsigned long CodRet;

  (void) sprintf (DiagExec,
		  "Cor_flow_tot_POM(%lu ech), C_dd=[%g, %g, %g, %g]", NbVal,
		  *((float *) ArgList[2]),
		  *((float *) ArgList[3]),
		  *((float *) ArgList[4]),
		  *((float *) ArgList[5]));

  CodRet = Cor_flow_tot_POM (NbVal,
			(float *) ArgList[0],
			(float *) ArgList[1],
			*((float *) ArgList[2]),
			*((float *) ArgList[3]),
			*((float *) ArgList[4]),
			*((float *) ArgList[5]),
			*((float *) ArgList[6]),
			*((float *) ArgList[7]),
			*((float *) ArgList[8]),
			(float *) ArgList[9],
			*((float *) ArgList[10]),
			*((float *) ArgList[11]),
			*((float *) ArgList[12]),
			*((float *) ArgList[13]),
			*((float *) ArgList[14]),
			*((float *) ArgList[15]),
			(float *) ArgList[16]);
  if (CodRet == NbVal)
    return OP_OK;
  else
    return OP_FAIL;
}

/* la fonction de description de l'operateur et ses arguments */

void
ID_Cor_flow_tot_POM (oper * optr)
{
  strcpy (optr->Nom, "Cor_flow_tot_POM");
  optr->Version = "1.0";
  optr->Date = "21/05/02";
  optr->fctptr = OP_Cor_flow_tot_POM;
  optr->NbArg = 17;

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

  /* C0_DD */
  optr->Arg_Car[2].direction = DIR_IN;
  optr->Arg_Car[2].categorie = COEFFICIENT;
  optr->Arg_Car[2].array_dim = "1";
  optr->Arg_Car[2].typ = ATYC_IF32;
  optr->Arg_Car[2].unite = "any";

  /* C1_DD */
  optr->Arg_Car[3].direction = DIR_IN;
  optr->Arg_Car[3].categorie = COEFFICIENT;
  optr->Arg_Car[3].array_dim = "1";
  optr->Arg_Car[3].typ = ATYC_IF32;
  optr->Arg_Car[3].unite = "any";

  /* C2_DD */
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

  /* INC */
  optr->Arg_Car[9].direction = DIR_IN;
  optr->Arg_Car[9].categorie = VECTOR;
  optr->Arg_Car[9].typ = ATYC_IF32;
  optr->Arg_Car[9].array_dim = "1";
  optr->Arg_Car[9].type_sample = "any";
  optr->Arg_Car[9].sample = "any";
  optr->Arg_Car[9].unite = "degree";

  optr->Arg_Car[10].direction = DIR_IN;
  optr->Arg_Car[10].categorie = COEFFICIENT;
  optr->Arg_Car[10].array_dim = "1";
  optr->Arg_Car[10].typ = ATYC_IF32;
  optr->Arg_Car[10].type_sample = NULL;	/* sans signification pour COEFFICIENT */
  optr->Arg_Car[10].sample = NULL;
  optr->Arg_Car[10].unite = "any";

  optr->Arg_Car[11].direction = DIR_IN;
  optr->Arg_Car[11].categorie = COEFFICIENT;
  optr->Arg_Car[11].array_dim = "1";
  optr->Arg_Car[11].typ = ATYC_IF32;
  optr->Arg_Car[11].type_sample = NULL;	/* sans signification pour COEFFICIENT */
  optr->Arg_Car[11].sample = NULL;
  optr->Arg_Car[11].unite = "any";

  optr->Arg_Car[12].direction = DIR_IN;
  optr->Arg_Car[12].categorie = COEFFICIENT;
  optr->Arg_Car[12].array_dim = "1";
  optr->Arg_Car[12].typ = ATYC_IF32;
  optr->Arg_Car[12].type_sample = NULL;	/* sans signification pour COEFFICIENT */
  optr->Arg_Car[12].sample = NULL;
  optr->Arg_Car[12].unite = "any";

  optr->Arg_Car[13].direction = DIR_IN;
  optr->Arg_Car[13].categorie = COEFFICIENT;
  optr->Arg_Car[13].array_dim = "1";
  optr->Arg_Car[13].typ = ATYC_IF32;
  optr->Arg_Car[13].type_sample = NULL;	/* sans signification pour COEFFICIENT */
  optr->Arg_Car[13].sample = NULL;
  optr->Arg_Car[13].unite = "any";

  optr->Arg_Car[14].direction = DIR_IN;
  optr->Arg_Car[14].categorie = COEFFICIENT;
  optr->Arg_Car[14].array_dim = "1";
  optr->Arg_Car[14].typ = ATYC_IF32;
  optr->Arg_Car[14].type_sample = NULL;	/* sans signification pour COEFFICIENT */
  optr->Arg_Car[14].sample = NULL;
  optr->Arg_Car[14].unite = "any";

  optr->Arg_Car[15].direction = DIR_IN;
  optr->Arg_Car[15].categorie = COEFFICIENT;
  optr->Arg_Car[15].array_dim = "1";
  optr->Arg_Car[15].typ = ATYC_IF32;
  optr->Arg_Car[15].type_sample = NULL;	/* sans signification pour COEFFICIENT */
  optr->Arg_Car[15].sample = NULL;
  optr->Arg_Car[15].unite = "any";

  optr->Arg_Car[16].direction = DIR_OUT;
  optr->Arg_Car[16].categorie = VECTOR;
  optr->Arg_Car[16].typ = ATYC_IF32;
  optr->Arg_Car[16].array_dim = "1";
  optr->Arg_Car[16].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[16].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[16].sample = "$Arg1.sample";
  optr->Arg_Car[16].ref_time = "$Arg1.ref_time";
  optr->Arg_Car[16].misval = "$Arg1.misval";
  optr->Arg_Car[16].unite = "$Arg1.unit";
  optr->Arg_Car[16].famille = "$Arg1.famille";

}
