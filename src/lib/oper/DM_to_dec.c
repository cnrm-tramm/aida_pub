/******************************************************************
*
* OPERATOR      DM_to_dec.c   ANSI-C
*
* PURPOSE       Conversion de couple degres_absolus-minutes et d'un indicateur
*               géographique en degres decimaux.
*
* DESCRIPTION   Calcul de  : degre + minutes/60, et affectation d'un 
*               signe selon la valeur de "flag" (négatif pour Sud et Ouest)
*
* VERSION       $Revision$
*
* ARGUMENTS    ENTREE   int    Degres           degres entier, valeur absolue
*              ENTREE   float  Minutes          minutes
*              ENTREE   char   Flag             ['N','S','E','W']
*              SORTIE   float  Valeur decimale  degrés décimaux signés.
*
* SUBPROGRAMS  Aucun
*
* FILES        Inclusion de "./struct_oper.h"
*
* REFERENCES   
*
* CHANGES      11/01/2001 C.Berne : premiere version Campagne POMME
*
* COPYRIGHT    Meteo-France
*	       Centre National de Recherches Meteorologiques 
*	       GMEI/ TRAMM
*	       42, av G. Coriolis
*	       31057 TOULOUSE cedex  
*
*
* AGREEMENT     
*#########################################################################*/

#define _POSIX_SOURCE 1
#define _XOPEN_SOURCE 600

#include <stdio.h>
#include <string.h>
#include <strings.h>
#include "struct_oper.h"

/* La vraie fonction... */
void
DM_to_dec (unsigned long NLoop,
		const int *Ldeg,
		const float *Lmin,
		const char *flag,
		float *Ldegmin)
{
  unsigned long i;

  for (i = 0; i < NLoop; i++)
    {
      Ldegmin[i] = Ldeg[i] + (Lmin[i] / 60.);
      if ((!strcasecmp (flag, "W")) || (!strcasecmp (flag, "S")))
	{
	  Ldegmin[i] = -Ldegmin[i];
	}
    }

}

/* la fonction d'enrobage classique */

int
OP_DM_to_dec (unsigned long NbVal, void *ArgList[], char *DiagExec)
{

  sprintf (DiagExec, "DM_to_dec : %lu ech, flag = %s)", NbVal,
	   (char *) ArgList[2]);

  DM_to_dec (NbVal,
		  (int *) ArgList[0],
		  (float *) ArgList[1],
		  (char *) ArgList[2],
		  (float *) ArgList[3]);

  return OP_OK;
}

/* la fonction de description de l'operateur et ses arguments */

void
ID_DM_to_dec (oper * optr)
{
  strcpy (optr->Nom, "DM_to_dec");
  optr->Version = "$Revision$";
  optr->Date = "$Date$";
  optr->fctptr = OP_DM_to_dec;
  optr->misval_auto = 1;
  optr->NbArg = 4;

  /* Ldeg */
  optr->Arg_Car[0].direction = DIR_IN;
  optr->Arg_Car[0].categorie = VECTOR;
  optr->Arg_Car[0].typ = ATYC_I32;
  optr->Arg_Car[0].array_dim = "1";
  optr->Arg_Car[0].type_sample = "any";
  optr->Arg_Car[0].sample = "any";
  optr->Arg_Car[0].unite = "degree";

  /*  Lmin */
  optr->Arg_Car[1].direction = DIR_IN;
  optr->Arg_Car[1].categorie = VECTOR;
  optr->Arg_Car[1].typ = ATYC_IF32;
  optr->Arg_Car[1].array_dim = "1";
  optr->Arg_Car[1].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[1].type_sample = "any";
  optr->Arg_Car[1].sample = "any";
  optr->Arg_Car[1].unite = "min";

  /* flag */
  optr->Arg_Car[2].direction = DIR_IN;
  optr->Arg_Car[2].categorie = COEFFICIENT;
  optr->Arg_Car[2].typ = ATYC_STRING;
  optr->Arg_Car[2].array_dim = "1";
  optr->Arg_Car[2].type_sample = NULL;
  optr->Arg_Car[2].sample = NULL;
  optr->Arg_Car[2].unite = "";

  optr->Arg_Car[3].direction = DIR_OUT;
  optr->Arg_Car[3].categorie = VECTOR;
  optr->Arg_Car[3].typ = ATYC_IF32;
  optr->Arg_Car[3].array_dim = "1";
  optr->Arg_Car[3].ref_time = "$Arg1.ref_time";
  optr->Arg_Car[3].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[3].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[3].sample = "$Arg1.sample";
  optr->Arg_Car[3].unite = "$Arg1.unit";
  optr->Arg_Car[3].misval = "-999.";
  optr->Arg_Car[3].famille = "$Arg1.famille";
  optr->Arg_Car[3].name = "$Arg1.name, en degres decimaux";
}

/* la fonction d'enrobage classique, sous le vieux nom */

int
OP_Convert_latlon (unsigned long NbVal, void *ArgList[], char *DiagExec)
{

  sprintf (DiagExec, "Convert_latlon : Appel de DM_to_dec avec %lu ech, flag = %s)", NbVal,
	   (char *) ArgList[2]);

  DM_to_dec (NbVal,
	     (int *) ArgList[0],
	     (float *) ArgList[1],
	     (char *) ArgList[2],
	     (float *) ArgList[3]);

  return OP_OK;
}

/* la fonction de description de l'operateur et ses arguments */

void
ID_Convert_latlon (oper * optr)
{
  strcpy (optr->Nom, "Convert_latlon");
  optr->Version = "$Revision$";
  optr->Date = "$Date$";
  optr->fctptr = OP_Convert_latlon;
  optr->misval_auto = 1;
  optr->repl_oper = "DM_to_dec";
  optr->repl_cause = "Nom plus explicite";
  optr->NbArg = 4;

  /* Ldeg */
  optr->Arg_Car[0].direction = DIR_IN;
  optr->Arg_Car[0].categorie = VECTOR;
  optr->Arg_Car[0].typ = ATYC_I32;
  optr->Arg_Car[0].array_dim = "1";
  optr->Arg_Car[0].type_sample = "any";
  optr->Arg_Car[0].sample = "any";
  optr->Arg_Car[0].unite = "degree";

  /*  Lmin */
  optr->Arg_Car[1].direction = DIR_IN;
  optr->Arg_Car[1].categorie = VECTOR;
  optr->Arg_Car[1].typ = ATYC_IF32;
  optr->Arg_Car[1].array_dim = "1";
  optr->Arg_Car[1].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[1].type_sample = "any";
  optr->Arg_Car[1].sample = "any";
  optr->Arg_Car[1].unite = "min";

  /* flag */
  optr->Arg_Car[2].direction = DIR_IN;
  optr->Arg_Car[2].categorie = COEFFICIENT;
  optr->Arg_Car[2].typ = ATYC_STRING;
  optr->Arg_Car[2].array_dim = "1";
  optr->Arg_Car[2].type_sample = NULL;
  optr->Arg_Car[2].sample = NULL;
  optr->Arg_Car[2].unite = "";

  optr->Arg_Car[3].direction = DIR_OUT;
  optr->Arg_Car[3].categorie = VECTOR;
  optr->Arg_Car[3].typ = ATYC_IF32;
  optr->Arg_Car[3].array_dim = "1";
  optr->Arg_Car[3].ref_time = "$Arg1.ref_time";
  optr->Arg_Car[3].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[3].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[3].sample = "$Arg1.sample";
  optr->Arg_Car[3].unite = "$Arg1.unit";
  optr->Arg_Car[3].misval = "-999.";
  optr->Arg_Car[3].name = "$Arg1.name, en degres decimaux";
}
