/***************************************************************************
*
* OPERATOR      Cor_deltah.c   FUNCTION  ANSI-C
*
* PURPOSE       Application d'une correction de distortion d'ecoulement
*              a une mesure de vitesse.
*
* DESCRIPTION   calcul d'un coeeficient de correction par application
*              de 2 polynomes (1 sur le tangage, l'autre sur la direction).
*
* VERSION       1.1
*
*             IN   float  Im         degree       angle d'incidence
*             IN   float  Coef_0     Any          Constant coefficient
*             IN   float  Coef_1     Any          coefficient of X
*             IN   float  Coef_2     Any          coefficient of X^2
*             IN   float  Coef_3     Any          coefficient of X^3
*             IN   float  B_min      Any          mini de la gamme d'application
*             IN   float  B_max      Any          maxi de la gamme d'application
*
*             OUT  float  deltah     metres       variation de hauteur d'ecoulement
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
Cor_deltah (unsigned long NLoop,
	     const float *Im,
	     const float C0_DD,
	     const float C1_DD,
	     const float C2_DD,
	     const float C3_DD,
	     const float min_DD,
	     const float max_DD,
	     float *dh)
{
  unsigned long i;

  for (i = 0; i < NLoop; i++)
    {
      if ( Im[i] < min_DD)
	dh[i] = 0.5;
      else if ( Im[i] > max_DD)
	dh[i] = 2.0;
      else
	dh[i] = C0_DD + Im[i] * (C1_DD + Im[i] * C2_DD + Im[i] * Im[i] * C3_DD);

    }
  return i;
}


/* la fonction d'enrobage classique */

int
OP_Cor_deltah (unsigned long NbVal, void *ArgList[], char *DiagExec)
{
  unsigned long CodRet;
  int NCar;

  NCar = sprintf (DiagExec, "Cor_deltah : (%ld echant.) ", NbVal) ;
  if (NCar < 0)
    NCar = 0;
  DiagExec += NCar;

  CodRet = Cor_deltah (NbVal,
			(float *) ArgList[0],
			*((float *) ArgList[1]),
			*((float *) ArgList[2]),
			*((float *) ArgList[3]),
			*((float *) ArgList[4]),
			*((float *) ArgList[5]),
			*((float *) ArgList[6]),
			(float *) ArgList[7]);
  if (CodRet == NbVal)
    return OP_OK;
  else
    return OP_FAIL;
}

/* la fonction de description de l'operateur et ses arguments */

void
ID_Cor_deltah (oper * optr)
{
  strcpy (optr->Nom, "Cor_deltah");
  optr->Version = "1.0";
  optr->Date = "20/06/02";
  optr->fctptr = OP_Cor_deltah;
  optr->NbArg = 8;
  /* Im */
  optr->Arg_Car[0].direction = DIR_IN;
  optr->Arg_Car[0].categorie = VECTOR;
  optr->Arg_Car[0].typ = ATYC_IF32;
  optr->Arg_Car[0].array_dim = "1";
  optr->Arg_Car[0].type_sample = "any";
  optr->Arg_Car[0].sample = "any";
  optr->Arg_Car[0].unite = "degree";

  /* C0 */
  optr->Arg_Car[1].direction = DIR_IN;
  optr->Arg_Car[1].categorie = COEFFICIENT;
  optr->Arg_Car[1].typ = ATYC_IF32;
  optr->Arg_Car[1].array_dim = "1";
  optr->Arg_Car[1].type_sample = NULL;
  optr->Arg_Car[1].sample = NULL;
  optr->Arg_Car[1].unite = "any";

  /* C1 */
  optr->Arg_Car[2].direction = DIR_IN;
  optr->Arg_Car[2].categorie = COEFFICIENT;
  optr->Arg_Car[2].array_dim = "1";
  optr->Arg_Car[2].typ = ATYC_IF32;
  optr->Arg_Car[2].type_sample = NULL;	/* sans signification pour COEFFICIENT */
  optr->Arg_Car[2].sample = NULL;
  optr->Arg_Car[2].unite = "any";

  /* C2 */
  optr->Arg_Car[3].direction = DIR_IN;
  optr->Arg_Car[3].categorie = COEFFICIENT;
  optr->Arg_Car[3].array_dim = "1";
  optr->Arg_Car[3].typ = ATYC_IF32;
  optr->Arg_Car[3].type_sample = NULL;	/* sans signification pour COEFFICIENT */
  optr->Arg_Car[3].sample = NULL;
  optr->Arg_Car[3].unite = "any";

  /* C3 */
  optr->Arg_Car[4].direction = DIR_IN;
  optr->Arg_Car[4].categorie = COEFFICIENT;
  optr->Arg_Car[4].array_dim = "1";
  optr->Arg_Car[4].typ = ATYC_IF32;
  optr->Arg_Car[4].type_sample = NULL;	/* sans signification pour COEFFICIENT */
  optr->Arg_Car[4].sample = NULL;
  optr->Arg_Car[4].unite = "any";

  /* Im_min*/
  optr->Arg_Car[5].direction = DIR_IN;
  optr->Arg_Car[5].categorie = COEFFICIENT;
  optr->Arg_Car[5].array_dim = "1";
  optr->Arg_Car[5].typ = ATYC_IF32;
  optr->Arg_Car[5].type_sample = NULL;	/* sans signification pour COEFFICIENT */
  optr->Arg_Car[5].sample = NULL;
  optr->Arg_Car[5].unite = "any";

  /* Im_max*/
  optr->Arg_Car[6].direction = DIR_IN;
  optr->Arg_Car[6].categorie = COEFFICIENT;
  optr->Arg_Car[6].array_dim = "1";
  optr->Arg_Car[6].typ = ATYC_IF32;
  optr->Arg_Car[6].type_sample = NULL;	/* sans signification pour COEFFICIENT */
  optr->Arg_Car[6].sample = NULL;
  optr->Arg_Car[6].unite = "any";

  /* deltah */
  optr->Arg_Car[7].direction = DIR_OUT;
  optr->Arg_Car[7].categorie = VECTOR;
  optr->Arg_Car[7].typ = ATYC_IF32;
  optr->Arg_Car[7].array_dim = "1";
  optr->Arg_Car[7].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[7].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[7].sample = "$Arg1.sample";
  optr->Arg_Car[7].ref_time = "$Arg1.ref_time";
  optr->Arg_Car[7].misval = "$Arg1.misval";
  optr->Arg_Car[7].unite = "m";
  optr->Arg_Car[7].famille = "$Arg1.famille";

}
