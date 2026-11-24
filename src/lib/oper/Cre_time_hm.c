/****************************************************
*
* OPERATOR       Cre_time_hm.c   FUNCTION  ANSI-C
*
* PURPOSE        Creation time vector
*
* DESCRIPTION    Création d'un vecteur temps à partir des vecteurs  
*                heure et minute 
*                dans ce cas : le nb de secondes est à 0
*
* VERSION        $Revision$
*
* ARGUMENTS  IN   short    Var_heure 
*            IN   short    Var_minute   
*            OUT  double Var_time (en secondes)
*
* REFERENCES
*
* CHANGES        
*
* COPYRIGHT      Meteo-France
*
* AGREEMENT      The author wishes that .....
*
*#########################################################################*/

#define _POSIX_SOURCE 1
#define _XOPEN_SOURCE 600
#define _XOPEN_SOURCE_EXTENDED 1

#include <stdio.h>
#include <float.h>
#include <string.h>

#include "struct_oper.h"

/* La vraie fonction... */

unsigned long
Cre_time_hm (unsigned long Nloop,
	     short *Var_heure, short *Var_minute, double *Var_time)
{
  unsigned long i;
  unsigned long nb_recul = 0;
  double last_time = -DBL_MAX;

  /* Boucle standard */
  for (i = 0; i < Nloop; i++)
    {
      *Var_time = (*Var_heure * 3600.) + (*Var_minute * 60.);
      if (*Var_time < last_time)
	nb_recul++;

      last_time = *Var_time;
      Var_time++;
      Var_heure++;
      Var_minute++;
    }

  return nb_recul;
}

/* la fonction d'enrobage classique */

int
OP_Cre_time_hm (unsigned long NbVal, void *ArgList[], char *DiagExec)
{
  unsigned long CodRet;
  int NCar;

  NCar = sprintf (DiagExec, "Cre_time_hm, NbVal=%lu\n", NbVal);
  if (NCar > 0)
    DiagExec += NCar;

  CodRet = Cre_time_hm (NbVal,
			(short *) ArgList[0],
			(short *) ArgList[1], (double *) ArgList[2]);
  if (CodRet > 0)
    {
      sprintf (DiagExec, "Attention : %lu retours dans le passé", CodRet);
    }

  return OP_OK;
}

void
ID_Cre_time_hm (oper * optr)
{
  strcpy (optr->Nom, "Cre_time_hm");
  optr->Version = "$Revision$";
  optr->Date = "$Date$";
  optr->fctptr = OP_Cre_time_hm;
  optr->NbArg = 3;

  optr->Arg_Car[0].direction = DIR_IN;
  optr->Arg_Car[0].categorie = VECTOR;
  optr->Arg_Car[0].typ = ATYC_I16;
  optr->Arg_Car[0].array_dim = "1";
  optr->Arg_Car[0].type_sample = "any";
  optr->Arg_Car[0].sample = "any";
  optr->Arg_Car[0].famille = "any";
  optr->Arg_Car[0].unite = "any";

  optr->Arg_Car[1].direction = DIR_IN;
  optr->Arg_Car[1].categorie = VECTOR;
  optr->Arg_Car[1].typ = ATYC_I16;
  optr->Arg_Car[1].array_dim = "1";
  optr->Arg_Car[1].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[1].type_sample = "any";
  optr->Arg_Car[1].sample = "any";
  optr->Arg_Car[1].famille = "any";
  optr->Arg_Car[1].unite = "any";

  optr->Arg_Car[2].direction = DIR_OUT;
  optr->Arg_Car[2].categorie = VECTOR;
  optr->Arg_Car[2].typ = ATYC_IF64;
  optr->Arg_Car[2].array_dim = "1";
  optr->Arg_Car[2].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[2].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[2].sample = "$Arg1.sample";
  optr->Arg_Car[2].unite = "second";
  optr->Arg_Car[2].misval = "-1";
  optr->Arg_Car[2].famille = "\"temps\"";
  optr->Arg_Car[2].name = "$Arg1.name + \" et \" + $Arg2.name";
  optr->Arg_Car[2].en_name = "$Arg1.name + \" and \" + $Arg2.name";

}
