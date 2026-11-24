/****************************************************************
* OPERATOR 	Constante_dans_plage  FUNCTION  ANSI-C
* 
* PURPOSE	Remplacement de deonnées par une constante 
*               dans une plage de valeurs choisies.
*
* DESCRIPTION   Cette fonction "corrige" les valeurs
*	   	dans une plage. La nature de la correction
*		est le remplacement par une valeur fixe (choisie
*		par l'utilisateur)
*               Ce peut etre aussi des "valeur manquante"
*
*
* VERSION         1.1
*
* ARGUMENTS 	IN 	float 	X   	    parametre brut	
*		IN 	float 	plage_inf   valeur min. plage
*		IN 	float 	plage_sup   valeur max. plage
*		IN 	float 	ValCor      valeur de remplacement
* 		OUT 	float 	Xcor 	    parametre corrige
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

/* Pour la fonction isfinite */
#define _HPUX_SOURCE 1


#include <stdio.h>
#include <string.h>
#include <limits.h>
#include <math.h>
#include "struct_oper.h"

unsigned long
Constante_dans_plage (unsigned long Nloop,
		      const float *X,
		      const float borne_inf,
		      const float borne_sup,
		      const float ValCor,
		      float *Xcor, unsigned long *Tab_diagno)
{
  unsigned long i;
  unsigned long nb_borne, nb_NaN, nbOK;
  int Flag_OK;
  float X_courant;

  if (borne_inf >= borne_sup)
    {
      Tab_diagno[0] = 0;
      Tab_diagno[1] = Nloop;
      Tab_diagno[2] = Nloop;
      Tab_diagno[3] = Nloop;
      return ULONG_MAX;
    }

  nb_borne = 0;
  nb_NaN = 0;
  nbOK = 0;

  /*  Boucle sur le vecteur d'entree */
  for (i = 0; i < Nloop; i++)
    {
      X_courant = *X;
      /* Valeur correctement représentée par un float ?   */
      if (!isfinite (X_courant))
	{
	  nb_NaN = nb_NaN + 1;
	  Flag_OK = 0;
	}
      else if ((X_courant <= borne_sup) && (X_courant >= borne_inf))
	{
	  nb_borne = nb_borne + 1;
	  Flag_OK = 0;
	}
      else
	{
	  nbOK = nbOK + 1;
	  Flag_OK = 1;
	}

      if (Flag_OK == 1)
	{
	  /* on recopie la valeur actuelle. */
	  *Xcor = *X;
	  Xcor++;
	}
      else
	{
	  /* on met la valeur de remplacement */
	  *Xcor = ValCor;
	  Xcor++;
	}

      X++;
    }
  /* La boucle est finie... */

  /* Test de validité interne */
  if (nb_borne + nb_NaN + nbOK != Nloop)
    {
      (void) fprintf (stderr, "internal error : \n");
    }
  /* Et Nb_cor (si on le calculait) doit être égal à  nb_sup + nb_inf */

  Tab_diagno[0] = nbOK;
  Tab_diagno[1] = nb_borne;
  Tab_diagno[2] = nb_NaN;
  return nbOK + nb_borne + nb_NaN;
}

/* fonction d'enrobage */

int
OP_Constante_dans_plage (unsigned long Nbval, void *ArgList[], char *DiagExec)
{
  unsigned long CodRet;
  unsigned long toto[4];

  sprintf (DiagExec,
	   "Constante_dans_plage : Valeurs entre %g et %g remplacees par %g",
	   (*(float *) ArgList[1]), *((float *) ArgList[2]),
	   *((float *) ArgList[3]));

  CodRet = Constante_dans_plage (Nbval,
				 (float *) ArgList[0],
				 *((float *) ArgList[1]),
				 *((float *) ArgList[2]),
				 *((float *) ArgList[3]),
				 (float *) ArgList[4], toto);

  if (CodRet == ULONG_MAX)
    {
      sprintf (DiagExec, "Error : borne_min >= borne_max");
      return OP_FAIL;
    }
  else
    {
      sprintf (DiagExec,
	       "%lu valeurs (sur %lu) rejetée(s) [s:%lu, i:%lu, a:%lu, n:%lu]",
	       CodRet, Nbval, toto[1], toto[2], toto[3], toto[4]);
      return OP_OK;
    }

}

void
ID_Constante_dans_plage (oper * optr)
{
  strcpy (optr->Nom, "Constante_dans_plage");
  optr->Version = "1.0";
  optr->Date = "01/18/04";
  optr->fctptr = OP_Constante_dans_plage;
  optr->NbArg = 5;
  optr->misval_auto = 0;	/*On traite explicitement misval */

  /* X */
  optr->Arg_Car[0].direction = DIR_IN;
  optr->Arg_Car[0].categorie = VECTOR;
  optr->Arg_Car[0].typ = ATYC_IF32;
  optr->Arg_Car[0].array_dim = "1";
  optr->Arg_Car[0].unite = "";
  optr->Arg_Car[0].type_sample = "any";
  optr->Arg_Car[0].sample = "any";

  /* borne_inf */
  optr->Arg_Car[1].direction = DIR_IN;
  optr->Arg_Car[1].categorie = COEFFICIENT;
  optr->Arg_Car[1].typ = ATYC_IF32;
  optr->Arg_Car[1].array_dim = "1";
  optr->Arg_Car[1].unite = "";
  optr->Arg_Car[1].type_sample = NULL;
  optr->Arg_Car[1].sample = NULL;

  /* borne_sup */
  optr->Arg_Car[2].direction = DIR_IN;
  optr->Arg_Car[2].categorie = COEFFICIENT;
  optr->Arg_Car[2].typ = ATYC_IF32;
  optr->Arg_Car[2].array_dim = "1";
  optr->Arg_Car[2].unite = "";
  optr->Arg_Car[2].type_sample = NULL;
  optr->Arg_Car[2].sample = NULL;

  /* ValCor */
  optr->Arg_Car[3].direction = DIR_IN;
  optr->Arg_Car[3].categorie = COEFFICIENT;
  optr->Arg_Car[3].typ = ATYC_IF32;
  optr->Arg_Car[3].array_dim = "1";
  optr->Arg_Car[3].unite = "";
  optr->Arg_Car[3].type_sample = NULL;
  optr->Arg_Car[3].sample = NULL;

  /* Xcor */
  optr->Arg_Car[4].direction = DIR_OUT;
  optr->Arg_Car[4].categorie = VECTOR;
  optr->Arg_Car[4].typ = ATYC_IF32;
  optr->Arg_Car[4].array_dim = "1";
  optr->Arg_Car[4].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[4].sample = "$Arg1.sample";
  optr->Arg_Car[4].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[4].ref_time = "$Arg1.ref_time";
  optr->Arg_Car[4].unite = "$Arg1.unit";
  /* optr->Arg_Car[4].famille = "$Arg1.famille"; */
  optr->Arg_Car[4].misval = "$Arg1.misval";
}
