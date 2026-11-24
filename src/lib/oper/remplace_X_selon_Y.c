/*********************************************************
* OPERATOR 	remplace_X_selon_Y.c FUNCTION ANSI-C
*
* PURPOSE       Remplace les valeurs d'un vecteur X (temperature par ex.) en
*		fonction d'un critère sur un second vecteur Y (tension ventilateur
*		par ex.) dont la fourchette de validité est "connue".
*		Cet opérateur remplace les valeurs "invalides" par 
*		la valeur invalide choisie par l'utilisateur.
*
* VERSION       $Revision: 4858 $
*
* ARGUMENTS 	IN	float	X		vecteur à valider 
*		IN 	float	Y   		vecteur dont on connait la
*						fourchette de fonctionnement (Y_inf et Y_sup) 
*		IN 	int 	Hors_intervalle 0 ou 1 pour invalider les valeurs dans [Y_inf,Y_sup] ou en dehors	
*		IN	float 	Y_inf		valeur min tolérée de Y 
*		IN 	float 	Y_sup		valeur max tolérée de Y
*		IN 	float 	Y_mnq		valeur correspondant à la valeur mnq du vecteur Y
*						si celle-ci est différente de NaN (ex : -32000, -999...)
*		IN 	float 	rpl_val	 	valeur de remplacement de X, le + souvent valeur
*						manquante (ex : -32000, -999...)
*
*		OUT 	float 	X_rpl		vecteur X avec valeurs remplacees 
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
remplace_X_selon_Y (unsigned long Nloop,
		  const float *X,
		  const float *Y,
		  const int   Hors_intervalle,  
		  const float Y_inf,
		  const float Y_sup,
		  const float Y_mnq,
		  const float rpl_val,
		  float *X_rpl, unsigned long *Diag_tab)
{

  unsigned long i;
  unsigned long nb_rpl, nb_ok;

  /*********************************************************
   * Initialisation des compteurs de valeurs trop ...
   * grandes, trop petites, égales à Y_mnq ou à NaN ...
   * ou "correctes" 
   * *******************************************************/
  nb_rpl = 0;
  nb_ok = 0;

  for (i = 0; i < Nloop; i++)
    {
      if (isfinite (Y[i]))
	{
          

	  if ( (( Y[i] < Y_inf) || (Y[i] > Y_sup)) &&
	      (Hors_intervalle == 1 ) )   
            {
	     X_rpl[i] = rpl_val;
	     nb_rpl = nb_rpl + 1;
	    }
	  else if ( (( Y[i] >= Y_inf) && (Y[i] <=  Y_sup)) &&
	      (Hors_intervalle == 0 ) ) 
	    {
	      X_rpl[i] = rpl_val;
	      nb_rpl = nb_rpl + 1;
	    }
	  else
	    {
	      X_rpl[i] = X[i];
	      nb_ok = nb_ok + 1;
	    }
	}
      else
	/* Si Y est NaN , on ne peut pas choisir et on ne remplace pas la valeur  */
	{
	  X_rpl[i] = X[i];
	  nb_ok = nb_ok + 1;
	}
    }

  /*  On renvoie les compteurs d'anomalies pour l'entete du nouveau vecteur */
  Diag_tab[0] = nb_ok;
  Diag_tab[1] = nb_rpl;
  return 0;
}

/* fonction d'enrobage */

int
OP_remplace_X_selon_Y (unsigned long Nbval, void *ArgList[], char *DiagExec)
{
  unsigned long CodRet;
  int NCar;
  unsigned long Diag_tab[6];

  NCar = sprintf (DiagExec, "remplace_X_selon_Y (%lu ech), %g<Y<%g", Nbval,
		  *((float *) ArgList[2]), *((float *) ArgList[3]));
  DiagExec += (NCar < 0 ? 0 : NCar);

  CodRet = remplace_X_selon_Y (Nbval,
			     (float *) ArgList[0],
			     (float *) ArgList[1],
			     *((float *) ArgList[2]),
			     *((float *) ArgList[3]),
			     *((float *) ArgList[4]),
			     *((float *) ArgList[5]),
			     *((float *) ArgList[6]),
			     (float *) ArgList[7], Diag_tab);

  sprintf (DiagExec, ", %lu valeur(s) acceptée(s) -et- %lu valeur(s) rejetée(s)",
           Diag_tab[0], Diag_tab[1]);

  return OP_OK;
}

void
ID_remplace_X_selon_Y (oper * optr)
{
  strcpy (optr->Nom, "remplace_X_selon_Y");
  optr->Version = "$Revision: 4858 $";
  optr->Date = "$Date: 2012-10-11 16:28:11 +0200 (jeu. 11 oct. 2012) $";
  optr->fctptr = OP_remplace_X_selon_Y;
  optr->NbArg = 8;

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

  /* Hors_intervale */
  optr->Arg_Car[2].direction = DIR_IN;
  optr->Arg_Car[2].categorie = COEFFICIENT;
  optr->Arg_Car[2].typ = ATYC_IF32;
  optr->Arg_Car[2].array_dim = "1";

  /* Y_inf */
  optr->Arg_Car[3].direction = DIR_IN;
  optr->Arg_Car[3].categorie = COEFFICIENT;
  optr->Arg_Car[3].typ = ATYC_IF32;
  optr->Arg_Car[3].array_dim = "1";

  /* Y_sup */
  optr->Arg_Car[4].direction = DIR_IN;
  optr->Arg_Car[4].categorie = COEFFICIENT;
  optr->Arg_Car[4].typ = ATYC_IF32;
  optr->Arg_Car[4].array_dim = "1";

  /* Y_mnq */
  optr->Arg_Car[5].direction = DIR_IN;
  optr->Arg_Car[5].categorie = COEFFICIENT;
  optr->Arg_Car[5].typ = ATYC_IF32;
  optr->Arg_Car[5].array_dim = "1";
  optr->Arg_Car[5].unite = "without";

  /* rpl_val */
  optr->Arg_Car[6].direction = DIR_IN;
  optr->Arg_Car[6].categorie = COEFFICIENT;
  optr->Arg_Car[6].typ = ATYC_IF32;
  optr->Arg_Car[6].array_dim = "1";
  optr->Arg_Car[6].unite = "without";

  /* X_rpl */
  optr->Arg_Car[7].direction = DIR_OUT;
  optr->Arg_Car[7].categorie = VECTOR;
  optr->Arg_Car[7].typ = ATYC_IF32;
  optr->Arg_Car[7].array_dim = "1";
  optr->Arg_Car[7].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[7].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[7].sample = "$Arg1.sample";
  optr->Arg_Car[7].ref_time = " $Arg1.ref_time";
  optr->Arg_Car[7].unite = "$Arg1.unit";
  optr->Arg_Car[7].famille = "$Arg1.famille";
  optr->Arg_Car[7].misval = "$Arg1.misval";
  optr->Arg_Car[7].name =
    "$Arg1.name + \" avec valeurs remplacees par\" + $Arg7 + \" lorsque \" + $Arg2.name + \" est entre/hors \" + $Arg4 +  \" et \" + $Arg5";
  optr->Arg_Car[6].en_name =
    "$Arg1.english_name + \" with replaced values by \" + $Arg7 + \" when \" + $Arg2.name +\" is between/oustside \" + $arg4 + \" and \" + $Arg5";
}
