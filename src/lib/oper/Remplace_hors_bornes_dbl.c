/****************************************************************
* OPERATOR 	Remplace_hors_bornes_dbl  FUNCTION  ANSI-C
* 
* PURPOSE	replacement of out-of-range values 
*
* DESCRIPTION   Cette fonction remplace les valeurs
*	   	en-dehors d'un intervale défini par des bornes. 
*
* VERSION         1.1
*
* ARGUMENTS 	IN 	double 	X   	    parametre brut	
*		IN 	double 	borne_inf   valeur min. permise
*		IN 	double 	borne_sup   valeur max. permise
*		IN 	double  X_rempla    Paramètre de remplacement
* 		OUT 	double 	Xcor 	    parametre corrige
*
* ENTRY		NONE
*
* SUBPROGRAMS 	NONE
* 
* REFERENCES	NONE
*
* CHANGES       1.2   
* 
* COPYRIGHT 	Meteo-France
*		Centre de Recherches Meteorologiques
*		GMEI/TRAMM
*		42, av. G. Coriolis
*		31057	TOULOUSE cedex
*
******************************************************************/

#define _POSIX_SOURCE 1
#define _XOPEN_SOURCE 600


#include <stdio.h>
#include <string.h>
#include <limits.h>
#include <math.h>
#include "struct_oper.h"

unsigned long
Remplace_hors_bornes_dbl (unsigned long Nloop,
			  const double *X,
			  const double borne_inf,
			  const double borne_sup,
			  const double *X_rempla,
			  double *Xcor, unsigned long *Tab_diagno)
{
  unsigned long i;
  unsigned long nb_sup, nb_inf, nb_abs, nbOK;
  int Flag_OK;
  register double X_courant;

  if (borne_inf >= borne_sup)
    {
      Tab_diagno[0] = 0;
      Tab_diagno[1] = Nloop;
      Tab_diagno[2] = Nloop;
      Tab_diagno[3] = Nloop;
      Tab_diagno[4] = Nloop;
      return ULONG_MAX;
    }

  nb_sup = 0;
  nb_inf = 0;
  nb_abs = 0;
  nbOK = 0;
  for (i = 0; i < Nloop; i++)
    {
      X_courant = *X;
      /* Valeur correctement représentée par un float ?   */
      if (!isfinite (X_courant))
	{
	  nb_abs = nb_abs + 1;
	  Flag_OK = 1;		/* On ne remplace pas les absents */
	}
      else if (X_courant > borne_sup)
	{
	  nb_sup = nb_sup + 1;
	  Flag_OK = 0;
	}
      else if (X_courant < borne_inf)
	{
	  nb_inf = nb_inf + 1;
	  Flag_OK = 0;
	}
      else
	{
	  nbOK = nbOK + 1;
	  Flag_OK = 1;
	}

      if (Flag_OK == 1)
	{
	  *Xcor = *X;
	}
      else
	{
	  *Xcor = *X_rempla;
	}
      Xcor++;
      X++;
      X_rempla++;
    }
  /* La boucle est finie... */
  /* Test de validité interne */
  if (nb_sup + nb_inf + nb_abs + nbOK != Nloop)
    {
      (void) fprintf (stderr, "Internal error : \n");
    }
  /* Et Nb_cor (si on le calculait) doit être égal à  nb_sup + nb_inf + nb_abs */

  Tab_diagno[0] = nbOK;
  Tab_diagno[1] = nb_sup;
  Tab_diagno[2] = nb_inf;
  Tab_diagno[3] = nb_abs;
  return nb_sup + nb_inf + nb_abs;
}

/* fonction d'enrobage */

int
OP_Remplace_hors_bornes_dbl (unsigned long Nbval, void *ArgList[],
			     char *DiagExec)
{
  unsigned long CodRet;
  unsigned long toto[4];

  /* sprintf (DiagExec,""); */

  CodRet = Remplace_hors_bornes_dbl (Nbval,
				     (double *) ArgList[0],
				     *((double *) ArgList[1]),
				     *((double *) ArgList[2]),
				     (double *) ArgList[3],
				     (double *) ArgList[4], toto);

  if (CodRet == ULONG_MAX)
    {
      sprintf (DiagExec, "Error : borne_min >= borne_max");
      return OP_FAIL;
    }
  else
    {
      sprintf (DiagExec,
	       "%lu valeur(s) (sur %lu) remplacée(s) [s:%lu, i:%lu, a:%lu]",
	       CodRet, Nbval, toto[1], toto[2], toto[3]);
      return OP_OK;
    }

}

void
ID_Remplace_hors_bornes_dbl (oper * optr)
{
  strcpy (optr->Nom, "Remplace_hors_bornes_dbl");
  optr->Version = "$Revision: 4985 $";
  optr->Date = "$Date: 2017-06-10 13:59:12 +0200 (lun. 17 juin 2017) $";
  optr->fctptr = OP_Remplace_hors_bornes_dbl;
  optr->misval_auto = 1;
  optr->NbArg = 5;

  /* X */
  optr->Arg_Car[0].direction = DIR_IN;
  optr->Arg_Car[0].categorie = VECTOR;
  optr->Arg_Car[0].typ = ATYC_IF64;
  optr->Arg_Car[0].array_dim = "1";
  optr->Arg_Car[0].unite = "";
  optr->Arg_Car[0].type_sample = "any";
  optr->Arg_Car[0].sample = "any";

  /* borne_inf */
  optr->Arg_Car[1].direction = DIR_IN;
  optr->Arg_Car[1].categorie = COEFFICIENT;
  optr->Arg_Car[1].typ = ATYC_IF64;
  optr->Arg_Car[1].array_dim = "1";
  optr->Arg_Car[1].unite = "";

  /* borne_sup */
  optr->Arg_Car[2].direction = DIR_IN;
  optr->Arg_Car[2].categorie = COEFFICIENT;
  optr->Arg_Car[2].typ = ATYC_IF64;
  optr->Arg_Car[2].array_dim = "1";
  optr->Arg_Car[2].unite = "";

  /* X_rempla */
  optr->Arg_Car[3].direction = DIR_IN;
  optr->Arg_Car[3].categorie = VECTOR;
  optr->Arg_Car[3].typ = ATYC_IF64;
  optr->Arg_Car[3].array_dim = "1";
  optr->Arg_Car[3].unite = "";
  optr->Arg_Car[3].type_sample = NULL;
  optr->Arg_Car[3].sample = NULL;

  /* Xcor */
  optr->Arg_Car[4].direction = DIR_OUT;
  optr->Arg_Car[4].categorie = VECTOR;
  optr->Arg_Car[4].typ = ATYC_IF64;
  optr->Arg_Car[4].array_dim = "1";
  optr->Arg_Car[4].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[4].sample = "$Arg1.sample";
  optr->Arg_Car[4].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[4].ref_time = "$Arg1.ref_time";
  optr->Arg_Car[4].unite = "$Arg1.unit";
  optr->Arg_Car[4].famille = "$Arg1.famille";
  optr->Arg_Car[4].misval = "$Arg1.misval";
}
