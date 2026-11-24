/****************************************************
*
* OPERATOR      Remplace_par_filtre_RC.c   FUNCTION  ANSI-C
*
* PURPOSE       Replace missing values bye an estimation calculated
*               as a numerical filtering similar to a electric RC circuit
*
* DESCRIPTION   Remplace les valeurs manquantes par les résultats
*               d'une estimation calculée pat un filtrage numérique 
*               équivalent à un circuit électrique RC.
*                 C'est un filtre simple dont les caractéristiques sont
*               les suivantes :
*                  Reponse à un créneau : exponentielle approchant
*               asymptotiquement de la valeur finale du créneau
*               sous une forme Vo .(1 - exp (-t/tau) )
* 		   Fonction de transfert (en transformée de Laplace) :
*		     (1/tau) / (p . ( p + 1/tau) )
* 		   Fonction de transfert (en transformée en Z) :
*		     (1 - exp(-Te/tau)) / (Z - exp(-Te/tau))
*                  Frequence de coupure a 3 dB : 1/(2.pi.tau)
*
* VERSION       $Revision$
*
* ARGUMENTS   IN   float  data       any            Original data
*             IN   float  borne_min  same as data   min allowed value for data
*             IN   float  borne_max  same as data   max allowed value for data
*             IN   float  base_estim same as data   base data for estimation
*             IN   float  fi	     Hz   	    Original data frequency
*             IN   float  tau        second   	    time constant
*             IN   float  offset     same as data   décalage à appliquer a base_estim
*             OUT  float  datao      same as data   estimated data
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
#include "struct_oper.h"

/* La vraie fonction... */


#include <stdlib.h>
#include <stdio.h>

long
Remplace_par_filtre_RC (unsigned long Ndata,
			const float *data,
			const float borne_min,
			const float borne_max,
			const float *base_estim,
			const float fe,
			const float tau,
			const float offset,
			float *data_fil)
{
  unsigned long i;
  long Nb_rempl;
  register double b1, a1;

  if (tau <= 0.0)
    {
      return -1;
    }
  if (fe <= 0.0)
    {
      return -2;
    }
  a1 = exp (-1.0 / (fe * tau));
  b1 = 1.0 - a1;

  Nb_rempl = 0;
/*
 * Recherche d'un point de départ OK, soit 
 * dans data, soit dans base-estim, soit
 * éventuellement absent.
 */
  if ((data[0] >= borne_min) && (data[0] <= borne_max))
    {
      data_fil[0] = data[0];
    }
  else
    {
      data_fil[0] = base_estim[0] + offset;
      Nb_rempl++;
    }

  for (i = 1; i < Ndata; i++)
    if ((data[i] >= borne_min) && (data[i] <= borne_max))
      data_fil[i] = data[i];
    else
      {
	data_fil[i] = a1 * data_fil[i - 1] + b1 * (base_estim[i - 1] + offset);
	Nb_rempl++;
      }

  return Nb_rempl;
}

/* la fonction d'enrobage classique */

int
OP_Remplace_par_filtre_RC (unsigned long NbVal, void *ArgList[], char *DiagExec)
{
  long CodRet;
  int NCar;

  NCar = 
    sprintf (DiagExec, 
             "Remplace_par_filtre_RC (%ld ech), donnees hors de [%f, %f] remplacées par",
             NbVal, *((float *) ArgList[1]), *((float *) ArgList[2]));
  if (NCar < 0)
    NCar = 0;
  DiagExec += NCar;

  CodRet = Remplace_par_filtre_RC (NbVal,
				   (float *) ArgList[0],
				   *((float *) ArgList[1]),
				   *((float *) ArgList[2]),
				   (float *) ArgList[3],
				   *((float *) ArgList[4]),
				   *((float *) ArgList[5]),
				   *((float *) ArgList[6]),
				   (float *) ArgList[7]);
  if (CodRet >= 0)
    {
      sprintf (DiagExec, "%lu valeur(s) (sur %lu) remplacée(s)",
	       CodRet, NbVal);
      return OP_OK;
    }
  switch (CodRet)
    {
    case -1:
      sprintf (DiagExec, "ERR: Constante de temps négative.");
    case -2:
      sprintf (DiagExec, "ERR: Fréquence d'échantillonnage négative.");
    default:
      sprintf (DiagExec, "ERR: Erreur %ld", CodRet);
    }
  return OP_FAIL;
}

void
ID_Remplace_par_filtre_RC (oper * optr)
{
  strcpy (optr->Nom, "Remplace_par_filtre_RC");
  optr->Version = "$Revision$";
  optr->Date = "$Date$";
  optr->fctptr = OP_Remplace_par_filtre_RC;
  optr->NbArg = 8;
  optr->misval_auto = 1;

  /* data */
  optr->Arg_Car[0].direction = DIR_IN;
  optr->Arg_Car[0].categorie = VECTOR;
  optr->Arg_Car[0].typ = ATYC_IF32;
  optr->Arg_Car[0].array_dim = "1";
  optr->Arg_Car[0].type_sample = "any";
  optr->Arg_Car[0].sample = "any";
  optr->Arg_Car[0].unite = "any";

  /* borne_min */
  optr->Arg_Car[1].direction = DIR_IN;
  optr->Arg_Car[1].categorie = COEFFICIENT;
  optr->Arg_Car[1].array_dim = "1";
  optr->Arg_Car[1].typ = ATYC_IF32;
  optr->Arg_Car[1].unite = "any";
  optr->Arg_Car[1].type_sample = NULL;
  optr->Arg_Car[1].sample = NULL;

  /* borne_max */
  optr->Arg_Car[2].direction = DIR_IN;
  optr->Arg_Car[2].categorie = COEFFICIENT;
  optr->Arg_Car[2].typ = ATYC_IF32;
  optr->Arg_Car[2].array_dim = "1";
  optr->Arg_Car[2].unite = "any";
  optr->Arg_Car[2].type_sample = NULL;
  optr->Arg_Car[2].sample = NULL;

  /*  base_estim  */
  optr->Arg_Car[3].direction = DIR_IN;
  optr->Arg_Car[3].categorie = VECTOR;
  optr->Arg_Car[3].typ = ATYC_IF32;
  optr->Arg_Car[3].array_dim = "1";
  optr->Arg_Car[3].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[3].type_sample = "any";
  optr->Arg_Car[3].sample = "any";
  optr->Arg_Car[3].unite = "any";

  /* fe */
  optr->Arg_Car[4].direction = DIR_IN;
  optr->Arg_Car[4].categorie = COEFFICIENT;
  optr->Arg_Car[4].array_dim = "1";
  optr->Arg_Car[4].typ = ATYC_IF32;
  optr->Arg_Car[4].unite = "Hz";
  optr->Arg_Car[4].type_sample = NULL;
  optr->Arg_Car[4].sample = NULL;

  /* tau */
  optr->Arg_Car[5].direction = DIR_IN;
  optr->Arg_Car[5].categorie = COEFFICIENT;
  optr->Arg_Car[5].array_dim = "1";
  optr->Arg_Car[5].typ = ATYC_IF32;
  optr->Arg_Car[5].unite = "second";
  optr->Arg_Car[5].type_sample = NULL;
  optr->Arg_Car[5].sample = NULL;

  optr->Arg_Car[6].direction = DIR_IN;
  optr->Arg_Car[6].categorie = COEFFICIENT;
  optr->Arg_Car[6].typ = ATYC_IF32;
  optr->Arg_Car[6].array_dim = "1";
  optr->Arg_Car[6].type_sample = NULL;
  optr->Arg_Car[6].sample = NULL;

  optr->Arg_Car[7].direction = DIR_OUT;
  optr->Arg_Car[7].categorie = VECTOR;
  optr->Arg_Car[7].typ = ATYC_IF32;
  optr->Arg_Car[7].array_dim = "1";
  optr->Arg_Car[7].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[7].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[7].sample = "$Arg1.sample";
  optr->Arg_Car[7].ref_time = "$Arg1.ref_time";
  optr->Arg_Car[7].misval = "$Arg1.misval";
  optr->Arg_Car[7].unite = "$Arg1.unit";
  optr->Arg_Car[7].famille = "$Arg1.famille";
  optr->Arg_Car[7].name = "composite";
  optr->Arg_Car[7].en_name = "composite";
}
