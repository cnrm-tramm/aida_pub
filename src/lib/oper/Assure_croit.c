/*
*************************************************************************
*
* OPERATOR         Assure_croit.c  FUNCTION ANSI-C
*
* PURPOSE          Vérification de la croissance de la mesure ex: éviter les remises à 0
* du cumul des duree d'insolation en cas de redémarage de la campbel.
*
* DESCRIPTION
*                 On invalide les données a partir du moment ou valeur i+1 - valeur i < 0
*
*
* VERSION          1.0
*
* ARGUMENTS
*            IN   float   Ins       durée d'insolation depuis 0 heure
*            IN   float   valmanq	valeur manquante
*            IN   float   inv_val	valeur invalidée
*            OUT  float   Inscor    durée d'insolation corrigée
*
*
*
* ENTRY        NONE
*
* SUBPROGRAMS  NONE
*
* REFERENCES   
*
* COPYRIGHT    Meteo-France
*	       Centre National de Recherches Meteorologiques
*	       GMEI/ TRAMM
*	       42, av G. Coriolis
*	       31057 TOULOUSE cedex
*
*
*############################################################################
*/

#define _POSIX_SOURCE 1
#define _XOPEN_SOURCE 600

#include <stdio.h>
#include <string.h>

#include "struct_oper.h"


int
/* suppression des valeurs de cumul apres une remise a 0 du capteur suite a un arret*/
/* Impossible de definir quel ecart on garde en cas de remise partielle à 0*/
Assure_croit (unsigned long ndata, const float *Ins,	/* duree d'insolation depuis 0 heures brut de precipitation a la minute */
	      float val_manq, float inv_val, float *InsCor	/* durée d'insolation corrigée*/
  )
{
  unsigned long i;

  /* initialisation des valeurs corrigées pour gérer la première échéance*/
  InsCor[0] = Ins[0];

  for (i = 0; i < ndata; i++)
    {
    /*if ((InsCor[i] == inv_val) || (InsCor[i] == val_manq) || !(isfinite(InsCor[i])) || InsCor[i + 1] == inv_val || (Ins[i + 1] - Ins[i] < 0))*/
    /* + gestion des nans*/
    /* on vérifie a chaque echeance si la donnée corrigée n'est pas a mis_val ou nan et si la donnée suivante i+1 ne l'est pas non plus puis si la différence n'est pas < 0*/
    if ( !(isfinite(InsCor[i])) || InsCor[i] == inv_val || 
            (Ins[i+1] == inv_val) || (Ins[i+1] == val_manq) || !(isfinite(Ins[i+1])) || 
            (Ins[i + 1] - Ins[i] < 0))
	{
	  InsCor[i + 1] = inv_val;
	}
      else
	InsCor[i + 1] = Ins[i + 1];
    }
  return 0;
}


/* la fonction d'enrobage classique */

int
OP_Assure_croit (unsigned long NbVal, void *ArgList[], char *DiagExec)
{
  (void) sprintf (DiagExec, "Assure_croit %ld ", NbVal);

  Assure_croit (NbVal, (float *) ArgList[0], *(float *) ArgList[1],
		*(float *) ArgList[2], (float *) ArgList[3]);

  return OP_OK;
}

void
ID_Assure_croit (oper * optr)
{
  strcpy (optr->Nom, "Assure_croit");
  optr->Version = "$Revision$";
  optr->Date = "$Date$";
  optr->fctptr = OP_Assure_croit;
  optr->NbArg = 4;		/* doit rester inf. a FIL_MAX_ARG */

  /* Ins :cumul des durées d'insolation depuis 0 heures */
  optr->Arg_Car[0].direction = DIR_IN;
  optr->Arg_Car[0].categorie = VECTOR;
  optr->Arg_Car[0].typ = ATYC_IF32;
  optr->Arg_Car[0].array_dim = "1";
  optr->Arg_Car[0].type_sample = "any";
  optr->Arg_Car[0].sample = "any";
  optr->Arg_Car[0].unite = "";

  /* val_manq */
  optr->Arg_Car[1].direction = DIR_IN;
  optr->Arg_Car[1].categorie = COEFFICIENT;
  optr->Arg_Car[1].typ = ATYC_IF32;
  optr->Arg_Car[1].array_dim = "1";
  optr->Arg_Car[1].unite = "";

  /* inv_val */
  optr->Arg_Car[2].direction = DIR_IN;
  optr->Arg_Car[2].categorie = COEFFICIENT;
  optr->Arg_Car[2].typ = ATYC_IF32;
  optr->Arg_Car[2].array_dim = "1";
  optr->Arg_Car[2].unite = "";

  /* InsCor */
  optr->Arg_Car[3].direction = DIR_OUT;
  optr->Arg_Car[3].categorie = VECTOR;
  optr->Arg_Car[3].typ = ATYC_IF32;
  optr->Arg_Car[3].array_dim = "1";
  optr->Arg_Car[3].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[3].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[3].sample = "$Arg1.sample";
  optr->Arg_Car[3].ref_time = "$Arg1.ref_time";
  optr->Arg_Car[3].unite = "$Arg1.unit";
  optr->Arg_Car[3].misval = "$Arg1.misval";
  optr->Arg_Car[3].name = "$Arg1.name";
  optr->Arg_Car[3].en_name = "$Arg1.english_name";
}
