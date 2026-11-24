/*********************************************************
* OPERATOR 	select_X_selon_Y.c FUNCTION ANSI-C
*
* PURPOSE       Selectionne les valeurs d'un vecteur X (temperature par ex.) en
*		fonction d'un critère sur un second vecteur Y (tension ventilateur
*		par ex.) dont la fourchette de validité est "connue".
*		Cet opérateur remplace les valeurs "invalides" par 
*		la valeur invalide choisie par l'utilisateur (valeur manquante le + souvent).
*
* VERSION       $Revision$
*
* ARGUMENTS 	IN	float	X		vecteur à valider 
*		IN 	float	Y   		vecteur dont on connait la
*						fourchette de fonctionnement (Y_inf et Y_sup) 
*		IN	float 	Y_inf		valeur min tolérée de Y 
*		IN 	float 	Y_sup		valeur max tolérée de Y
*		IN 	float 	Y_mnq		valeur correspondant à la valeur mnq du vecteur Y
*						si celle-ci est différente de NaN (ex : -32000, -999...)
*		IN 	float 	inv_val	 	valeur de remplacement de X, le + souvent valeur
*						manquante (ex : -32000, -999...)
*
*		OUT 	float 	X_valid		vecteur X "validé" en sortie 
*
* ENTRY		NONE
*
* SUBPROGRAMS 	NONE
* 
* REFERENCES	
*
* COPYRIGHT 	Meteo-France
*		Centre National de Recherches Meteorologiques
*		GMEI/TRAMM
*		42, av. G. Coriolis
* 		31057 	TOULOUSE cedex
*
* 		C.Berne 29/08/2006
*
************************************************************/

#define _POSIX_SOURCE 1
#define _XOPEN_SOURCE 600
/* Le #define _HPUX_SOURCE n'est la que pour "voir" strdup */
#define _HPUX_SOURCE 1

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>

#include "struct_oper.h"

unsigned long
select_X_selon_Y (unsigned long Nloop,
		  const float *X,
		  const float *Y,
		  const float Y_inf,
		  const float Y_sup,
		  const float Y_mnq,
		  const float inv_val,
		  float *X_valid, unsigned long *Diag_tab)
{

  unsigned long i;
  unsigned long nb_sup, nb_inf, nb_mnq, nb_NaN_X, nb_NaN_Y, nb_ok;

  /*********************************************************
   * Initialisation des compteurs de valeurs trop ...
   * grandes, trop petites, égales à Y_mnq ou à NaN ...
   * ou "correctes" 
   * *******************************************************/
  nb_sup = 0;
  nb_inf = 0;
  nb_mnq = 0;
  nb_NaN_X = 0;
  nb_NaN_Y = 0;
  nb_ok = 0;

  /***********************************************************
   Le vecteur X est considere bon si ces criteres sont verifies :
   	1) Y_inf <= Y <= Y_sup
   	2) Y est different de Y_mnq (au cas où)
   	3) Y est different de NaN (valeur infinie...) , test souvent
	redondant avec Y différent de Y_mnq mais au cas où... !
  ************************************************************/

  for (i = 0; i < Nloop; i++)
    {
      if (isfinite (Y[i]))
	{

	  if (Y[i] > Y_sup)
	    {
	      X_valid[i] = inv_val;
	      nb_sup = nb_sup + 1;
	    }
	  else if (Y[i] < Y_inf)
	    {
	      X_valid[i] = inv_val;
	      nb_inf = nb_inf + 1;
	    }
	  else if (Y[i] == Y_mnq)
	    {
	      X_valid[i] = inv_val;
	      nb_mnq = nb_mnq + 1;
	    }
	  else
	    {
	      X_valid[i] = X[i];
	      nb_ok = nb_ok + 1;
	      /* Si X est NaN (au départ!), on le comptabilise aussi!  */
	      if (!isfinite (X[i]))
		{
		  nb_NaN_X = nb_NaN_X + 1;
		  /* On met la valeur inv_val dans X_valid, car
		   * il y a une petite bug de WriteVect qui écrit des NaN
		   * à la place de la valeur choisie pour "mnq" (dans entete) */
		  X_valid[i] = inv_val;
		}
	    }
	}
      else
	/* Si Y est NaN , on le comptabilise comme tel !  */
	{
	  X_valid[i] = inv_val;
	  nb_NaN_Y = nb_NaN_Y + 1;
	}
    }

  /*  On renvoie les compteurs d'anomalies pour l'entete du nouveau vecteur */
  Diag_tab[0] = nb_ok;
  Diag_tab[1] = nb_sup;
  Diag_tab[2] = nb_inf;
  Diag_tab[3] = nb_mnq;
  Diag_tab[4] = nb_NaN_X;
  Diag_tab[5] = nb_NaN_Y;
  return nb_sup + nb_inf + nb_mnq + nb_NaN_Y;
}

/* fonction d'enrobage */

int
OP_select_X_selon_Y (unsigned long Nbval, void *ArgList[], char *DiagExec)
{
  unsigned long CodRet;
  int NCar;
  unsigned long Diag_tab[6];

  NCar = sprintf (DiagExec, "select_X_selon_Y (%lu ech), %g<Y<%g", Nbval,
		  *((float *) ArgList[2]), *((float *) ArgList[3]));
  DiagExec += (NCar < 0 ? 0 : NCar);

  CodRet = select_X_selon_Y (Nbval,
			     (float *) ArgList[0],
			     (float *) ArgList[1],
			     *((float *) ArgList[2]),
			     *((float *) ArgList[3]),
			     *((float *) ArgList[4]),
			     *((float *) ArgList[5]),
			     (float *) ArgList[6], Diag_tab);

  sprintf (DiagExec, ", %lu valeurs acceptée(s) [dont %lu sont NaN] \
 -et- %lu valeurs (sur %lu) rejetée(s)  \
 [sup:%lu, inf:%lu, mnq_Y:%lu, nan_Y:%lu]", Diag_tab[0], Diag_tab[4],
  CodRet, Nbval, Diag_tab[1], Diag_tab[2], Diag_tab[3], Diag_tab[5]);

  return OP_OK;
}

void
ID_select_X_selon_Y (oper * optr)
{
  strcpy (optr->Nom, "select_X_selon_Y");
  optr->Version = "$Revision$";
  optr->Date = "$Date$";
  optr->fctptr = OP_select_X_selon_Y;
  optr->NbArg = 7;

  /* X */
  optr->Arg_Car[0].direction = DIR_IN;
  optr->Arg_Car[0].categorie = VECTOR;
  optr->Arg_Car[0].typ = ATYC_IF32;
  optr->Arg_Car[0].array_dim = "1";
  optr->Arg_Car[0].type_sample = "any";
  optr->Arg_Car[0].sample = "any";
  optr->Arg_Car[0].unite = "any";

  /* Y */
  optr->Arg_Car[1].direction = DIR_IN;
  optr->Arg_Car[1].categorie = VECTOR;
  optr->Arg_Car[1].typ = ATYC_IF32;
  optr->Arg_Car[1].array_dim = "1";
  /* Les deux variables doivent être synchrones */
  optr->Arg_Car[1].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[1].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[1].sample = "$Arg1.sample";
  optr->Arg_Car[1].ref_time = " $Arg1.ref_time";
  optr->Arg_Car[1].unite = "any";

  /* Y_inf */
  optr->Arg_Car[2].direction = DIR_IN;
  optr->Arg_Car[2].categorie = COEFFICIENT;
  optr->Arg_Car[2].typ = ATYC_IF32;
  optr->Arg_Car[2].array_dim = "1";

  /* Y_sup */
  optr->Arg_Car[3].direction = DIR_IN;
  optr->Arg_Car[3].categorie = COEFFICIENT;
  optr->Arg_Car[3].typ = ATYC_IF32;
  optr->Arg_Car[3].array_dim = "1";

  /* Y_mnq */
  optr->Arg_Car[4].direction = DIR_IN;
  optr->Arg_Car[4].categorie = COEFFICIENT;
  optr->Arg_Car[4].typ = ATYC_IF32;
  optr->Arg_Car[4].array_dim = "1";

  /* inv_val */
  optr->Arg_Car[5].direction = DIR_IN;
  optr->Arg_Car[5].categorie = COEFFICIENT;
  optr->Arg_Car[5].typ = ATYC_IF32;
  optr->Arg_Car[5].array_dim = "1";
  optr->Arg_Car[5].unite = "without";

  /* X_valid */
  optr->Arg_Car[6].direction = DIR_OUT;
  optr->Arg_Car[6].categorie = VECTOR;
  optr->Arg_Car[6].typ = ATYC_IF32;
  optr->Arg_Car[6].array_dim = "1";
  optr->Arg_Car[6].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[6].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[6].sample = "$Arg1.sample";
  optr->Arg_Car[6].ref_time = " $Arg1.ref_time";
  optr->Arg_Car[6].unite = "$Arg1.unit";
  optr->Arg_Car[6].famille = "$Arg1.famille";
  optr->Arg_Car[6].misval = "$Arg6";
  optr->Arg_Car[6].name =
    "$Arg1.name + \" lorsque \" + $Arg2.name + \" est entre \" + $Arg3 +  \" et \" + $Arg4";
  optr->Arg_Car[6].en_name =
    "$Arg1.english_name + \" when \" + $Arg2.english_name + \" is between \" + $Arg3 +  \" and \" + $Arg4";
}
