/****************************************************
*
* OPERATOR      Filtre_RC_sdph.c   FUNCTION  ANSI-C
*
* PURPOSE       Numerical filtering similar to a electric RC circuit
*
* DESCRIPTION   Réalise numériquement un filtrage équivalent à 
*               un circuit électrique RC.
*                 C'est un filtre simple dont les caractéristiques sont
*               les suivantes :
*                  Reponse à un créneau : exponentielle approchant
*               asymptotiquement de la valeur finale du créneau
*               sous une forme Vo .(1 - exp (-t/tau) )
* 		   Fonction de transfert (en transformée en Z) :
*		     Z.(1 - exp(-Te/tau)) / (Z - exp(-Te/tau))
*                  Frequence de coupure a 3 dB : 1/(2.pi.tau)
*
*		Cet opérateur est le petite frère de Filtre_RC.
*
*		La fonction de transfert est similaire en module
*		à celle de l'opérateur Filtre_RC, mais pas en 
*		phase.
*		Cet opérateur ne déphase pas le signal de sortie 
*		par rapport au signal d'entrée. 
*		
*		Il a été aussi rajouté la possibilité de faire un
*		pseudo filtre passe-haut en enlevant la composante
*		BF au signal d'origine.
*		
*		On passe la fréquence de coupure plutot que
*		la constante de temps 
*
* VERSION       $Revision$
*
* ARGUMENTS   IN   float  datai      any        	Original data
*             IN   float  fi	     Hz   		Original data frequency
*             IN   float  fc        second   	        time constant
*	      IN   float  typ	     any		Type of filter (0 = Low Band Pass, 1= High Band Pass)
*             OUT  float  datao      same as datai	Filtered data
*
* REFERENCES
*
*	Ce filtre est la "running mean" utilisé dans les programmes de calcul
*	de flux 4M.
*	Note de travail ENM n° 750 : Qualification de filières de calcul de
*		flux turbulents.
*		Olivier Dupont, Denis Robin.
*	  	Juin 2000
*
* COPYRIGHT     Meteo-France
*
*#########################################################################*/

#define _POSIX_SOURCE 1
#define _XOPEN_SOURCE 600

/* pour pouvoir utiliser la fonction isfinite */
#define _HPUX_SOURCE 1


#include <stdio.h>
#include <math.h>
#include <string.h>
#include <limits.h>
#include "struct_oper.h"

/* La vraie fonction... */


#include <stdlib.h>
#include <stdio.h>

int
Filtre_RC_sdph (const unsigned long Ndata,
		const float *data,
		const float fe,
		const float fc,
		const int type,
		float *data_fil)
{
  unsigned long i;
  register double b1, a1, tau;
  register float memoire;

  tau = 1. / (2 * M_PI * fc);

  if (tau <= 0.0)
    {
      return -1;
    }
  if (fe <= 0.0)
    {
      return -2;
    }

  if ((type != 0) && (type != 1))
    {
      return -3;
    }

  a1 = exp (-1.0 / (fe * tau));
  b1 = 1.0 - a1;

  i = 0;
  while ((!isfinite (data[i])) && (i < Ndata))
    {
      data_fil[i] = data[i];
      i++;
    }

  if (i >= Ndata)
    {
      /* On n'a eu que des valeurs manquantes. */
      return 0;
    }

  /* TODO : au lieu de prendre data[i], faire une
   * moyenne de N valeurs de data, N étant calculé
   * en fonction de fe et tau. */
  data_fil[i] = data[i];
  memoire = data_fil[i];
  /* Puisqu'on va faire des [i-1] dans la boucle, il 
   * est capital de s'assurer que i>0. 
   * Le cas i=0 est traité soit dans le while ((!isfinite ...
   * soit dans les lignes ci-dessus. 
   * On fait donc i++
   * */
  i++;
  for (; i < Ndata; i++)
    {
      if (!isfinite (data[i]))
	{
	  data_fil[i] = 0. / 0.;
	  if (isfinite (data[i - 1]))
	    memoire = data_fil[i - 1];
	  /* la condition (i-1 > 0) est assurée car i>0,
	   * car le cas  !isfinite (data[0]) a été traité 
	   * par la boucle préliminaire  while (...)*/
	}
      else
	{
	  if (!isfinite (data[i - 1]))
	    /* TODO : calculer la longueur du trou.
	     * Si trou > N(tau, fe), repartir comme en début 
	     * de vecteur (calcul de moyenne).  */
	    data_fil[i] = a1 * memoire + b1 * data[i];
	  else
	    data_fil[i] = a1 * data_fil[i - 1] + b1 * data[i];
	}
    }

  if (type == 1)
    {
      for (i = 0; i < Ndata; i++)
	{
	  data_fil[i] = data[i] - data_fil[i];
	}
    }

  return 0;
}

/* la fonction d'enrobage classique */

int
OP_Filtre_RC_sdph (unsigned long NbVal, void *ArgList[], char *DiagExec)
{
  int CodRet;
  int NCar;

  NCar = sprintf (DiagExec, "Filtre_RC_sdph : (%ld echant.) ", NbVal) ;
  if (NCar < 0)
    NCar = 0;
  DiagExec += NCar;

  CodRet = Filtre_RC_sdph (NbVal,
			   (float *) ArgList[0],
			   *((float *) ArgList[1]),
			   *((float *) ArgList[2]),
			   *((int *) ArgList[3]),
			   (float *) ArgList[4]);

  switch (CodRet)
    {
    case 0:
      sprintf (DiagExec, "OK.");
      return OP_OK;
    case -1:
      fprintf (stderr, " Fréquence de coupure négative !!\n");
      sprintf (DiagExec, "ERR: Fréquence de coupure négative.");
      return OP_FAIL;
    case -2:
      fprintf (stderr, " Fréquence d'échantillonnage négative !!\n");
      sprintf (DiagExec, "ERR: Fréquence d'échantillonnage négative.");
      return OP_FAIL;
    case -3:
      fprintf (stderr,
	       " Type doit égal à 0 (passe-bas) ou 1 (passe-haut) !!\n");
      sprintf (DiagExec,
	       "ERR: Type doit égal à 0 (passe-bas) ou 1 (passe-haut).");
      return OP_FAIL;
    default:
      sprintf (DiagExec, "ERR: Erreur %d", CodRet);
      return OP_FAIL;
    }
}

void
ID_Filtre_RC_sdph (oper * optr)
{
  strcpy (optr->Nom, "Filtre_RC_sdph");
  optr->Version = "$Revision$";
  optr->Date = "$Date$";

  optr->fctptr = OP_Filtre_RC_sdph;
  optr->NbArg = 5;
  optr->misval_auto = 1;

  optr->Arg_Car[0].direction = DIR_IN;
  optr->Arg_Car[0].categorie = VECTOR;
  optr->Arg_Car[0].typ = ATYC_IF32;
  optr->Arg_Car[0].array_dim = "1";
  optr->Arg_Car[0].type_sample = "any";
  optr->Arg_Car[0].sample = "any";
  optr->Arg_Car[0].unite = "any";

  optr->Arg_Car[1].direction = DIR_IN;
  optr->Arg_Car[1].categorie = COEFFICIENT;
  optr->Arg_Car[1].array_dim = "1";
  optr->Arg_Car[1].typ = ATYC_IF32;
  optr->Arg_Car[1].unite = "Hz";
  optr->Arg_Car[1].type_sample = NULL;
  optr->Arg_Car[1].sample = NULL;

  optr->Arg_Car[2].direction = DIR_IN;
  optr->Arg_Car[2].categorie = COEFFICIENT;
  optr->Arg_Car[2].array_dim = "1";
  optr->Arg_Car[2].typ = ATYC_IF32;
  optr->Arg_Car[2].unite = "Hz";
  optr->Arg_Car[2].type_sample = NULL;
  optr->Arg_Car[2].sample = NULL;

  optr->Arg_Car[3].direction = DIR_IN;
  optr->Arg_Car[3].categorie = COEFFICIENT;
  optr->Arg_Car[3].array_dim = "1";
  optr->Arg_Car[3].typ = ATYC_I32;
  optr->Arg_Car[3].unite = "without";
  optr->Arg_Car[3].type_sample = NULL;
  optr->Arg_Car[3].sample = NULL;

  optr->Arg_Car[4].direction = DIR_OUT;
  optr->Arg_Car[4].categorie = VECTOR;
  optr->Arg_Car[4].typ = ATYC_IF32;
  optr->Arg_Car[4].array_dim = "1";
  optr->Arg_Car[4].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[4].misval = "$Arg1.misval";
  optr->Arg_Car[4].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[4].sample = "$Arg1.sample";
  optr->Arg_Car[4].ref_time = "$Arg1.ref_time";
  optr->Arg_Car[4].unite = "$Arg1.unit";
  optr->Arg_Car[4].famille = "$Arg1.famille";

}
