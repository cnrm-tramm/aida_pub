/********************************************************
*
* OPERATOR     Pression.c   FUNCTION    ANSI-C
*
* PURPOSE      Calculates pressures and angles from radome and fusel. probes
*
* DESCRIPTION  Computes a corrected static pressure, a corrected dynamic
*              pressure, and angles of attitudes. 
*      
*              Angle differential presssures and static pressure
*              may come from whatever probe that can be polynomially
*              corrected, while dynamical pressure should come
*              from a pitot tube (no angle-related corrections are applied).
*              These quantities are calculated altogether because the
*              "Static defect" may depend on angles (but this is not 
*              the case by now).
*
*              Static defect (erreur de statique) is calculated from
*              dynamic pressure through a 3rd order polynom in the 
*              [25,90] hPa range, and an interpolated value in the 
*              [0,25] hPa range.
*
* VERSION      1.4
*
* ARGUMENTS  IN       Psc  float     hPa   Pression Statique calibree    
*            IN       dPc  float     hPa   Surpression dynamique calibree 
*            IN      dPhc  float     hPa   Pression differ. horiz. calibree
*            IN      dPvc  float     hPa   Pression differ. vert. calibree  
*
*            IN    C_alpha[2] float  arb.  Coefficients for alpha
*            IN     C_beta[2] float  arb.  Coefficients for beta
*            IN  C_ErrStat[4] float  arb.  Coefficients for static defect
*                                           
*            OUT       Ps  float*    hPa   Pression statique
*            OUT    alpha  float*    rad   angle d'incidence
*            OUT     beta  float*    rad   angle de derapage
*            OUT   deltaP  float*    hPa   corrected dynamical pressure.
*
*
* ENTRY       
*         
* SUBPROGRAMS  uses the "Poly1" and "Poly3" fonctions
*
*
* FILES        NONE
*
* REFERENCES    
*
* CHANGES      1.3 adapted to changes in categorie's definition
*              1.2 switched arg. order
*
* COPYRIGHT    I guess it's Meteo-France, here...
*
* AGREEMENT    The author wishes that .....
*#########################################################################*/

#define _POSIX_SOURCE 1
#define _XOPEN_SOURCE 600
/* Le #define _HPUX_SOURCE n'est la que pour "voir" strdup */
#define _HPUX_SOURCE 1
#define _XOPEN_SOURCE_EXTENDED 1

#include <math.h>
#include <stdio.h>
#include <string.h>
#include "struct_oper.h"

#include "poly.h"

int
Pression (const unsigned long NLoop,
	  const float *Psc,	/* variables d'entree   */
	  const float *dPc,
	  const float *dPhc,
	  const float *dPvc,
	  const float C_alpha[],	/* parameters de calib alpha */
	  const float C_beta[],	/* parameters de calib beta */
	  const float C_ErrStat[],	/* parameters ErrStat */
	  float *Ps,		/* variables de sortie  */
	  float *alpha,
	  float *beta,
	  float *deltaP)
{
  float ErrStat;
  unsigned long i;

  for (i = 0; i < NLoop; i++)
    {
      if (*dPc < 1.0)
	{
	  *Ps = *Psc;
	  *alpha = 0;
	  *beta = 0;
	  *deltaP = 0;
	}
/**** Calcul d'Errstat *****/

      if (*dPc > 25.0)
	{
	  ErrStat = Poly3 (*dPc, C_ErrStat);
	}
      else
	{
	  ErrStat = *dPc * Poly3 (25.0, C_ErrStat) / 25.0;
	}

/**** Calculs de Ps, etc... ****/

      *Ps = *Psc - ErrStat;

      *deltaP = *dPc + ErrStat;

      if (*deltaP <= 0.0)
	{
	  *deltaP = 0.0;
	  *alpha = 0.0;
	  *beta = 0.0;
	}
      else
	{
	  *alpha = Poly1 (*dPvc / *deltaP, C_alpha);
	  *beta = Poly1 (*dPhc / *deltaP, C_beta);
	}

      dPc++;
      Psc++;
      Ps++;
      dPvc++;
      dPhc++;
      alpha++;
      beta++;
      deltaP++;
    }
  return 0;
}

/* la fonction d'enrobage classique */

int
OP_Pression (unsigned long NbVal, void *ArgList[], char *DiagExec)
{
  int CodRet;
  float C_alpha[2];
  float C_beta[2];
  float C_ErrStat[4];

  sprintf (DiagExec, "OP_Pression, NbVal=%lu", NbVal);

  C_alpha[0] = *((float *) ArgList[4]);
  C_alpha[1] = *((float *) ArgList[5]);

  C_beta[0] = *((float *) ArgList[6]);
  C_beta[1] = *((float *) ArgList[7]);

  C_ErrStat[0] = *((float *) ArgList[8]);
  C_ErrStat[1] = *((float *) ArgList[9]);
  C_ErrStat[2] = *((float *) ArgList[10]);
  C_ErrStat[3] = 0.0;

  sprintf (&DiagExec[strlen (DiagExec)],
	   "C_alpha = [%f, %f], C_beta = [%f, %f], C_ErrStat = [%f, %f, %f]",
	   C_alpha[0], C_alpha[1], C_beta[0], C_beta[1],
	   C_ErrStat[0], C_ErrStat[1], C_ErrStat[2]);

  CodRet = Pression (NbVal,
		     (float *) ArgList[0],	/* Psc */
		     (float *) ArgList[1],
		     (float *) ArgList[2],
		     (float *) ArgList[3],
		     C_alpha,
		     C_beta,
		     C_ErrStat,
		     (float *) ArgList[11],
		     (float *) ArgList[12],
		     (float *) ArgList[13],
		     (float *) ArgList[14]);
  switch (CodRet)
    {
    case 0:
      sprintf (&DiagExec[strlen (DiagExec)], "OK.");
      return OP_OK;
    default:
      sprintf (&DiagExec[strlen (DiagExec)], "ERR: CodRet=%d, ", CodRet);
      return OP_FAIL;
    }
}

void
ID_Pression (oper * optr)
{
  strcpy (optr->Nom, "Pression");
  optr->Version = "1.4";
  optr->Date = "08/26/96";
  optr->fctptr = OP_Pression;
  optr->NbArg = 15;

  /*  Psc  */ 
  optr->Arg_Car[0].direction = DIR_IN;
  optr->Arg_Car[0].categorie = VECTOR;
  optr->Arg_Car[0].typ = ATYC_IF32;
  optr->Arg_Car[0].array_dim = "1";
  optr->Arg_Car[0].type_sample = "any";
  optr->Arg_Car[0].sample = "any";
  optr->Arg_Car[0].unite = "hPa";

  /*  dPc */
  optr->Arg_Car[1].direction = DIR_IN;
  optr->Arg_Car[1].categorie = VECTOR;
  optr->Arg_Car[1].typ = ATYC_IF32;
  optr->Arg_Car[1].array_dim = "1";
  optr->Arg_Car[1].type_sample = "any";
  optr->Arg_Car[1].sample = "any";
  optr->Arg_Car[1].unite = "hPa";

  optr->Arg_Car[2].direction = DIR_IN;
  optr->Arg_Car[2].categorie = VECTOR;
  optr->Arg_Car[2].typ = ATYC_IF32;
  optr->Arg_Car[2].array_dim = "1";
  optr->Arg_Car[2].type_sample = "any";
  optr->Arg_Car[2].sample = "any";
  optr->Arg_Car[2].unite = "hPa";

  optr->Arg_Car[3].direction = DIR_IN;
  optr->Arg_Car[3].categorie = VECTOR;
  optr->Arg_Car[3].typ = ATYC_IF32;
  optr->Arg_Car[3].array_dim = "1";
  optr->Arg_Car[3].type_sample = "any";
  optr->Arg_Car[3].sample = "any";
  optr->Arg_Car[3].unite = "hPa";

/* Les Coeff pour Alpha */
  optr->Arg_Car[4].direction = DIR_IN;
  optr->Arg_Car[4].categorie = COEFFICIENT;
  optr->Arg_Car[4].array_dim = "1";	/* Dim > 1, ne passe pas  */
  optr->Arg_Car[4].typ = ATYC_IF32;
  optr->Arg_Car[4].type_sample = NULL;
  optr->Arg_Car[4].sample = NULL;

  optr->Arg_Car[5].direction = DIR_IN;
  optr->Arg_Car[5].categorie = COEFFICIENT;
  optr->Arg_Car[5].array_dim = "1";	/* Dim > 1, ne passe pas  */
  optr->Arg_Car[5].typ = ATYC_IF32;
  optr->Arg_Car[5].type_sample = NULL;
  optr->Arg_Car[5].sample = NULL;

/* Les Coeff pour Beta */
  optr->Arg_Car[6].direction = DIR_IN;
  optr->Arg_Car[6].categorie = COEFFICIENT;
  optr->Arg_Car[6].array_dim = "1";	/* Dim > 1, ne passe pas  */
  optr->Arg_Car[6].typ = ATYC_IF32;

  optr->Arg_Car[7].direction = DIR_IN;
  optr->Arg_Car[7].categorie = COEFFICIENT;
  optr->Arg_Car[7].array_dim = "1";	/* Dim > 1, ne passe pas  */
  optr->Arg_Car[7].typ = ATYC_IF32;

/* Les Coeff pour Errstat */
  optr->Arg_Car[8].direction = DIR_IN;
  optr->Arg_Car[8].categorie = COEFFICIENT;
  optr->Arg_Car[8].array_dim = "1";	/* Dim > 1, ne passe pas  */
  optr->Arg_Car[8].typ = ATYC_IF32;
  optr->Arg_Car[9].direction = DIR_IN;
  optr->Arg_Car[9].categorie = COEFFICIENT;
  optr->Arg_Car[9].array_dim = "1";	/* Dim > 1, ne passe pas  */
  optr->Arg_Car[9].typ = ATYC_IF32;

  optr->Arg_Car[10].direction = DIR_IN;
  optr->Arg_Car[10].categorie = COEFFICIENT;
  optr->Arg_Car[10].array_dim = "1";	/* Dim > 1, ne passe pas  */
  optr->Arg_Car[10].typ = ATYC_IF32;

/* Les variables de sortie */
  optr->Arg_Car[11].direction = DIR_OUT;
  optr->Arg_Car[11].categorie = VECTOR;
  optr->Arg_Car[11].typ = ATYC_IF32;
  optr->Arg_Car[11].array_dim = "1";
  optr->Arg_Car[11].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[11].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[11].sample = "$Arg1.sample";
  optr->Arg_Car[11].ref_time = "$Arg1.ref_time";
  /* l'unite se deduit de l'entree  */
  optr->Arg_Car[11].unite = "$Arg1.unit";

  optr->Arg_Car[12].direction = DIR_OUT;
  optr->Arg_Car[12].categorie = VECTOR;
  optr->Arg_Car[12].typ = ATYC_IF32;
  optr->Arg_Car[12].array_dim = "1";
  optr->Arg_Car[12].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[12].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[12].sample = "$Arg1.sample";
  optr->Arg_Car[12].ref_time = "$Arg1.ref_time";
  /* Par contre, l'unite est simple... */
  optr->Arg_Car[12].unite = "radian";

  optr->Arg_Car[13].direction = DIR_OUT;
  optr->Arg_Car[13].categorie = VECTOR;
  optr->Arg_Car[13].typ = ATYC_IF32;
  optr->Arg_Car[13].array_dim = "1";
  optr->Arg_Car[13].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[13].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[13].sample = "$Arg1.sample";
  optr->Arg_Car[13].ref_time = "$Arg1.ref_time";
  /* Par contre, l'unite est simple... */
  optr->Arg_Car[13].unite = "radian";

  optr->Arg_Car[14].direction = DIR_OUT;
  optr->Arg_Car[14].categorie = VECTOR;
  optr->Arg_Car[14].typ = ATYC_IF32;
  optr->Arg_Car[14].array_dim = "1";
  optr->Arg_Car[14].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[14].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[14].sample = "$Arg1.sample";
  optr->Arg_Car[14].ref_time = "$Arg1.ref_time";
  /* Par contre, l'unite est simple... */
  optr->Arg_Car[14].unite = "hPa";

}
