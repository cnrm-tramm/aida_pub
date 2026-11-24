/****************************************************
*
* OPERATOR      Mol_approx.c   FUNCTION  ANSI-C
*
* PURPOSE      	Calcul de la longueur de Monin Obukhov (MOL)
*		de mouvement par la méthode des corrélations
*		a partir des covariances ; la base de temps doit etre commune.
*
* DESCRIPTION  	Cet opérateur calcule la MOL sur des périodes
*		de temps consécutives définies par l'utilisateur.
*
*		Les parametres d'entrée dit "moyens" sont des vecteurs
*		à la meme fréquence que les vecteurs de sorties.
*
* VERSION       $Revision$
*
* ARGUMENTS   	
*             IN   float  cov_wt    	mK/s	Covariance w't'	
*             IN   float  cov_wu    	m2/s2	Covariance w'u'	
*             IN   float  cov_wv    	m2/s2	Covariance w'v'	
*	      IN   float  Tamoy		C ou K	Temperature moyenne
*             IN   float  Tint		s	Temps d'intégration pour le calcul
*                                                     (inutilisé)
*             OUT  float  lmon	 	m	Longueur de MO
*
* REFERENCES
*
*
* COPYRIGHT     Meteo-France
*
*#########################################################################*/

#define _POSIX_SOURCE 1
#define _XOPEN_SOURCE 600

#include <stdio.h>
#include <math.h>
#include <string.h>
#include <limits.h>
#include <stdlib.h>

#include "thermo.h"

#include "struct_oper.h"
#include "unit_def.h"

/* La vraie fonction... */
long
Mol_approx (unsigned long NLoop,
	    const float *cov_wt,
	    const float *cov_wu,
	    const float *cov_wv,
            const float *Tamoy,
            float *lmon)
{
  int flag_info;
  unsigned long k;

  float C_to_K_moy;
  const float Kol = 0.4;
  const float g = 9.81;

  double ustar;

/* Calcul du nombre de points sur lequels on va calculer LMON */
/* vérification de la température  et initialisation
du coef de conversion */

  flag_info = auto_tempe_unit (NLoop, Tamoy, &C_to_K_moy);

  if (flag_info == MANQUANTES)
   {
    for (k = 0; k < NLoop; k++)
      {
       lmon[k] = 0./0.; 
      }
    return flag_info;
   }
  

  for (k = 0; k < NLoop; k++)
    {
      /* calcul de ustar = sqrt(Cov_wu_wv); */
      ustar =
	((double)
	 (sqrt (sqrt (cov_wu[k] * cov_wu[k] + cov_wv[k] * cov_wv[k]))));

      /* calcul de LMON */
      /* LMON=-1*(ustar**3)*(Tamoy)/K*g*cov_wTv */
      /* on arrondit en prenant T a la place de Tv  */

      lmon[k] =
	(float) ((ustar * ustar * ustar) * (-1) * (Tamoy[k] + C_to_K_moy) /
		 (Kol * g * cov_wt[k]));
    }

  return flag_info;
}

/* la fonction d'enrobage classique */

int
OP_Mol_approx (unsigned long NbVal, void *ArgList[], char *DiagExec)
{
  int NCar;
  long CodRet;

  NCar = sprintf (DiagExec,
                  "Mol_approx (%lu ech.), temps integ. = %f (inutilisé)",
                  NbVal, *((float *) ArgList[4]));
  if (NCar < 0)
    NCar = 0;
  DiagExec += NCar;

  CodRet = Mol_approx (NbVal,
		       (float *) ArgList[0],
		       (float *) ArgList[1],
		       (float *) ArgList[2],
		       (float *) ArgList[3],
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
      strcat (DiagExec, "Trop de valeurs manquantes. Unite tempe non reconnue");
      break;
    }

  return OP_OK;
}

void
ID_Mol_approx (oper * optr)
{
  int i;

  strcpy (optr->Nom, "Mol_approx");
  optr->Version = "$Revision$";
  optr->Date = "$Date$";
  optr->fctptr = OP_Mol_approx;
  optr->NbArg = 6;
  optr->misval_auto = 1;

  for (i = 0; i <= 3; i++)
    {
      optr->Arg_Car[i].direction = DIR_IN;
      optr->Arg_Car[i].categorie = VECTOR;
      optr->Arg_Car[i].typ = ATYC_IF32;
      optr->Arg_Car[i].array_dim = "1";
      optr->Arg_Car[i].type_sample = "any";
      optr->Arg_Car[i].sample = "any";
    }
  optr->Arg_Car[0].unite = "m.K/s";      /* cov_wt */
  optr->Arg_Car[1].unite = "m2/s2";     /* cov_wu */
  optr->Arg_Car[2].unite = "m2/s2";     /* cov_wv */
  optr->Arg_Car[3].unite = "any";	/* Tamoy, donc en fait c'est C ou K */
  /* Tous les vecteurs d'entree doivent avoir le même nombre d'echantillons. */
  optr->Arg_Car[1].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[2].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[3].NbVal = "$Arg1.NbVal";

  /* Tint */
  i = 4;
  optr->Arg_Car[i].direction = DIR_IN;
  optr->Arg_Car[i].categorie = COEFFICIENT;
  optr->Arg_Car[i].array_dim = "1";
  optr->Arg_Car[i].typ = ATYC_IF32;
  optr->Arg_Car[i].unite = "any";
  optr->Arg_Car[i].type_sample = NULL;
  optr->Arg_Car[i].sample = NULL;

  /* lmon */
  i = 5;
  optr->Arg_Car[i].direction = DIR_OUT;
  optr->Arg_Car[i].categorie = VECTOR;
  optr->Arg_Car[i].typ = ATYC_IF32;
  optr->Arg_Car[i].array_dim = "1";
  optr->Arg_Car[i].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[i].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[i].sample = "1./$Arg5";
  optr->Arg_Car[i].ref_time = "$Arg3.ref_time";
  optr->Arg_Car[i].unite = "m";
  optr->Arg_Car[i].famille = " \"turbulence\" ";
  optr->Arg_Car[i].name = " \"Longueur de Monin-Obukhov\" ";
  optr->Arg_Car[i].en_name = " \"Monin-Obukhov length\" ";
}
