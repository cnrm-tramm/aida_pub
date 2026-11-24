/*********************************************************
* OPERATOR 	Correl.c FUNCTION ANSI-C
*
* PURPOSE 	calibrate 2 aida vectors.
*
* Cette fonction calibre le vecteur1 avec le vecteur2 par régression linéaire
* selon le principe des moindres carrés ordinaires appliqué de proche en proche
* sur un intervalle défini par l'argument fenetre (en secondes).
* Les 2 vecteurs doivent être synchrones.
*
* VERSION       $Revision: $
*
* ARGUMENTS 	IN	float	vect1 vecteur à calibrer
*		IN 	float	vect2 vecteur référence pour la régression
*		IN 	float 	fr 	frequence de l'échantillon
*		IN	float 	fenetre glissante de calcul de la régression en secondes  
*
*		OUT float 	vect    vecteur résultat
*       OUT float 	vect_a  vecteur coef a de la droite de régression
*       OUT float 	vect_b  vecteur coef b de la droite de régression
*       OUT float 	vect_r2 vecteur coef R2 de la régression
*
* ENTRY		NONE
*
* SUBPROGRAMS 	NONE
* 
* REFERENCES	
*
*
* COPYRIGHT 	Meteo-France
*		Centre National de Recherches Meteorologiques
*		GMEI/TRAMM
*		42, av. G. Coriolis
* 		31057 	TOULOUSE cedex
*
************************************************************/

#define _POSIX_SOURCE 1
#define _XOPEN_SOURCE 600
#define _XOPEN_SOURCE_EXTENDED 1

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>

#include "struct_oper.h"

int
Correl (unsigned long Nloop,
	const float *vect1,
	const float *vect2,
	const float fr,
	float fenetre,
	float *vect,
        float *vect_a,
        float *vect_b,
        float *vect_r2)
{
  long nbpt;
  long deb, pt, pt_en_moins;
  long i;
  double s1, s2, m1, m2;	/* sommes et moyennes */
  double svar1, svar2, scov1_2, var1, var2, cov1_2;	/* variance et covariance */
  double a, b, R2;		/* coeffs de la droite de régression */

  /**** Initialisations ****/

  /* nbpt = nb de points de la fenetre de regression */
  nbpt = (int) (fr * fenetre);
  if (nbpt > Nloop)
    nbpt = Nloop;

  /*************************************/

  i = 0;
  deb = 0;
  while (i < Nloop)
    {
      /* Calcul des moyennes m1 et m2 */
      s1 = 0;
      s2 = 0;
      pt_en_moins = 0;
      for (pt = deb; pt < deb + nbpt && pt < Nloop; pt++)
	{
	  if (isfinite (vect1[pt]) && isfinite (vect2[pt]))
	    {
	      s1 += vect1[pt];
	      s2 += vect2[pt];
	    }
	  else
	    pt_en_moins++;
	}
      m1 = s1 / (nbpt - pt_en_moins);
      m2 = s2 / (nbpt - pt_en_moins);

      /* Calcul des variances var1, var2  et de la covariance cov1_2 */
      pt_en_moins = 0;
      svar1 = 0;
      svar2 = 0;
      scov1_2 = 0;
      for (pt = deb; pt < deb + nbpt && pt < Nloop; pt++)
	{
	  if (isfinite (vect1[pt]) && isfinite (vect2[pt]))
	    {
	      svar1 += (vect1[pt] - m1) * (vect1[pt] - m1);
	      svar2 += (vect2[pt] - m2) * (vect2[pt] - m2);
	      scov1_2 = scov1_2 + (vect1[pt] * vect2[pt]);
	    }
	  else
	    pt_en_moins++;
	}

      var1 = svar1 / (nbpt - pt_en_moins - 1);
      var2 = svar2 / (nbpt - pt_en_moins - 1);
      cov1_2 = (scov1_2 / (nbpt - pt_en_moins)) - (m1 * m2);

      /* Calcul des coefficients de la droite de regression */
      a = cov1_2 / var1;
      b = m2 - a * m1;

      /* Calcul de R2 */
      R2 = (cov1_2 / sqrt (var1 * var2)) * (cov1_2 / sqrt (var1 * var2));

      /* Application de la droite de regression */
      for (pt = deb; pt < deb + nbpt && pt < Nloop; pt++)
	{
	  if (isfinite (vect1[pt]) && isfinite (vect2[pt]))
	    {
	      vect[pt] = a * vect1[pt] + b;
	      vect_a[pt] = a;
	      vect_b[pt] = b;
	      vect_r2[pt] = R2;
	    }
	  else			/* on met un nan */
	    {
	      if (isfinite (vect1[pt]))
		{
		  vect[pt] = vect2[pt];
		  vect_a[pt] = vect2[pt];
		  vect_b[pt] = vect2[pt];
		  vect_r2[pt] = vect2[pt];
		}
	      else
		{
		  vect[pt] = vect1[pt];
		  vect[pt] = vect1[pt];
		  vect_a[pt] = vect1[pt];
		  vect_b[pt] = vect1[pt];
		  vect_r2[pt] = vect1[pt];
		}
	    }
	}
      i = pt;
      deb = pt;
    }

  return OP_OK;
}

/* fonction d'enrobage */

int
OP_Correl (unsigned long Nbval, void *ArgList[], char *DiagExec)
{
  int CodRet;

  sprintf (DiagExec, "OP_Correl. (%lu ech, freq=%f, fenetre=%fs",
	   Nbval,
	   *((float *) ArgList[2]),
	   *((float *) ArgList[3]));

  CodRet = Correl (Nbval,
		   (float *) ArgList[0],
		   (float *) ArgList[1],
		   *((float *) ArgList[2]),
		   *((float *) ArgList[3]),
		   (float *) ArgList[4],
		   (float *) ArgList[5],
		   (float *) ArgList[6],
                   (float *) ArgList[7]);

  return CodRet;
}

void
ID_Correl (oper * optr)
{
  strcpy (optr->Nom, "Correl");
  optr->Version = "$Revision: $";
  optr->Date = "$Date: $";
  optr->fctptr = OP_Correl;
  optr->NbArg = 8;

  /* vect2 */
  optr->Arg_Car[0].direction = DIR_IN;
  optr->Arg_Car[0].categorie = VECTOR;
  optr->Arg_Car[0].typ = ATYC_IF32;
  optr->Arg_Car[0].array_dim = "1";
  optr->Arg_Car[0].type_sample = "any";
  optr->Arg_Car[0].sample = "any";
  optr->Arg_Car[0].misval = "$Arg1.misval";
  optr->Arg_Car[0].unite = "";

  /* vect2 */
  optr->Arg_Car[1].direction = DIR_IN;
  optr->Arg_Car[1].categorie = VECTOR;
  optr->Arg_Car[1].typ = ATYC_IF32;
  optr->Arg_Car[1].array_dim = "1";
  optr->Arg_Car[1].type_sample = "any";
  optr->Arg_Car[1].sample = "any";
  optr->Arg_Car[1].misval = "$Arg2.misval";
  optr->Arg_Car[1].unite = "";

  /* fr */
  optr->Arg_Car[2].direction = DIR_IN;
  optr->Arg_Car[2].categorie = COEFFICIENT;
  optr->Arg_Car[2].typ = ATYC_IF32;
  optr->Arg_Car[2].array_dim = "1";
  optr->Arg_Car[2].unite = "Hz";

  /* fenetre */
  optr->Arg_Car[3].direction = DIR_IN;
  optr->Arg_Car[3].categorie = COEFFICIENT;
  optr->Arg_Car[3].typ = ATYC_IF32;
  optr->Arg_Car[3].array_dim = "1";
  optr->Arg_Car[3].unite = "s";

  optr->Arg_Car[4].direction = DIR_OUT;
  optr->Arg_Car[4].categorie = VECTOR;
  optr->Arg_Car[4].typ = ATYC_IF32;
  optr->Arg_Car[4].array_dim = "1";
  optr->Arg_Car[4].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[4].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[4].sample = "$Arg1.sample";
  optr->Arg_Car[4].ref_time = " $Arg1.ref_time";
  optr->Arg_Car[4].unite = "$Arg2.unit";

  optr->Arg_Car[5].direction = DIR_OUT;
  optr->Arg_Car[5].categorie = VECTOR;
  optr->Arg_Car[5].typ = ATYC_IF32;
  optr->Arg_Car[5].array_dim = "1";
  optr->Arg_Car[5].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[5].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[5].sample = "$Arg1.sample";
  optr->Arg_Car[5].ref_time = " $Arg1.ref_time";
  optr->Arg_Car[5].unite = "";

  optr->Arg_Car[6].direction = DIR_OUT;
  optr->Arg_Car[6].categorie = VECTOR;
  optr->Arg_Car[6].typ = ATYC_IF32;
  optr->Arg_Car[6].array_dim = "1";
  optr->Arg_Car[6].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[6].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[6].sample = "$Arg1.sample";
  optr->Arg_Car[6].ref_time = " $Arg1.ref_time";
  optr->Arg_Car[6].unite = "";

  optr->Arg_Car[7].direction = DIR_OUT;
  optr->Arg_Car[7].categorie = VECTOR;
  optr->Arg_Car[7].typ = ATYC_IF32;
  optr->Arg_Car[7].array_dim = "1";
  optr->Arg_Car[7].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[7].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[7].sample = "$Arg1.sample";
  optr->Arg_Car[7].ref_time = " $Arg1.ref_time";
  optr->Arg_Car[7].unite = "";
}
