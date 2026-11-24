/****************************************************
*
* OPERATOR      Filtre_RC.c   FUNCTION  ANSI-C
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
* 		   Fonction de transfert (en transformée de Laplace) :
*		     (1/tau) / (p . ( p + 1/tau) )
* 		   Fonction de transfert (en transformée en Z) :
*		     (1 - exp(-Te/tau)) / (Z - exp(-Te/tau))
*                  Frequence de coupure a 3 dB : 1/(2.pi.tau)
*
* VERSION       $Revision$
*
* ARGUMENTS   IN   float  datai      any        	Original data
*             IN   float  fi	     Hz   		Original data frequency
*             IN   float  tau        second   	        time constant
*             OUT  float  datao      same as datai	Filtered data
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

int
Filtre_RC (const unsigned long Ndata,
	   const float *data,
	   const float fe,
	   const float tau,
	   float *data_fil)
{
  unsigned long i;
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

  data_fil[0] = data[0];
  for (i = 1; i < Ndata; i++)
    {
      data_fil[i] = a1 * data_fil[i - 1] + b1 * data[i - 1];
    }

  return 0;
}

/* la fonction d'enrobage classique */

int
OP_Filtre_RC (unsigned long NbVal, void *ArgList[], char *DiagExec)
{
  int CodRet;
  int NCar;

  NCar = sprintf (DiagExec, "Filtre_RC : (%ld echant.) ", NbVal) ;
  if (NCar < 0)
    NCar = 0;
  DiagExec += NCar;

  CodRet = Filtre_RC (NbVal,
		      (float *) ArgList[0],
		      *((float *) ArgList[1]),
		      *((float *) ArgList[2]),
		      (float *) ArgList[3]);

  switch (CodRet)
    {
    case 0:
      sprintf (DiagExec, "OK.");
      return OP_OK;
    case -1:
      fprintf (stderr, " Constante de temps négative !!\n");
      sprintf (DiagExec, "ERR: Constante de temps négative.");
      return OP_FAIL;
    case -2:
      fprintf (stderr, " Fréquence d'échantillonnage négative !!\n");
      sprintf (DiagExec, "ERR: Fréquence d'échantillonnage négative.");
      return OP_FAIL;
    default:
      sprintf (DiagExec, "ERR: Erreur %d", CodRet);
      return OP_FAIL;
    }
}

void
ID_Filtre_RC (oper * optr)
{
  strcpy (optr->Nom, "Filtre_RC");
  optr->Version = "$Revision$";
  optr->Date = "$Date$";
  optr->fctptr = OP_Filtre_RC;
  optr->NbArg = 4;
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
  optr->Arg_Car[2].unite = "second";
  optr->Arg_Car[2].type_sample = NULL;
  optr->Arg_Car[2].sample = NULL;

  optr->Arg_Car[3].direction = DIR_OUT;
  optr->Arg_Car[3].categorie = VECTOR;
  optr->Arg_Car[3].typ = ATYC_IF32;
  optr->Arg_Car[3].array_dim = "1";
  optr->Arg_Car[3].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[3].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[3].sample = "$Arg1.sample";
  optr->Arg_Car[3].ref_time = "$Arg1.ref_time";
  optr->Arg_Car[3].unite = "$Arg1.unit";
  optr->Arg_Car[3].famille = "$Arg1.famille";

}
