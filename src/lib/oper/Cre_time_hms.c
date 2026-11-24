/****************************************************
*
* OPERATOR       Cre_time_hms.c   FUNCTION  ANSI-C
*
* PURPOSE        Creation time vector
*
* DESCRIPTION    Création d'un vecteur temps à partir des vecteurs  
*                heure , minute et seconde 
*
* VERSION        $Revision$
*
* ARGUMENTS  IN   short    Var_heure 
*            IN   short    Var_minute   
*            IN   short    Var_seconde   
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
/* Le #define _HPUX_SOURCE n'est la que pour "voir" strdup */
#define _HPUX_SOURCE 1
#define _XOPEN_SOURCE_EXTENDED 1

#include <stdio.h>
#include <math.h>
#include <string.h>
#include "struct_oper.h"

/* La vraie fonction... */

int
Cre_time_hms (unsigned long Nloop,
	      short *Var_heure,
	      short *Var_minute,
	      short *Var_seconde,
	      double *Var_time)
{
  unsigned long i;
  double last = -1.0e6;
  int nb_recul = 0;

  /* Boucle standard */
  for (i = 0; i < Nloop; i++)
    {
      *Var_time = (*Var_heure * 3600.) + (*Var_minute * 60.) + (*Var_seconde);
      if (*Var_time <= last)
	{
	  nb_recul++;
	}
      last = *Var_time;

      Var_time++;
      Var_heure++;
      Var_minute++;
      Var_seconde++;
    }

  return nb_recul;
}

/* la fonction d'enrobage classique */

int
OP_Cre_time_hms (unsigned long NbVal, void *ArgList[], char *DiagExec)
{
  int CodRet;

  CodRet = sprintf (DiagExec, "Cre_time_hms, NbVal=%lu;", NbVal);
  DiagExec += CodRet;

  CodRet = Cre_time_hms (NbVal,
			 (short *) ArgList[0],
			 (short *) ArgList[1],
			 (short *) ArgList[2],
			 (double *) ArgList[3]);
  if (CodRet > 0)
    {
      CodRet = sprintf (DiagExec, "WARN : %d reculs ou stagnations", CodRet);
    }
  else
    {
      CodRet = sprintf (DiagExec, "OK : serie croissante monotone.");
    }
  return OP_OK;
}

void
ID_Cre_time_hms (oper * optr)
{
  strcpy (optr->Nom, "Cre_time_hms");
  optr->Version = "$Revision$";
  optr->Date = "$Date$";
  optr->fctptr = OP_Cre_time_hms;
  optr->NbArg = 4;

  /* Var_heure, */
  optr->Arg_Car[0].direction = DIR_IN;
  optr->Arg_Car[0].categorie = VECTOR;
  optr->Arg_Car[0].typ = ATYC_I16;
  optr->Arg_Car[0].array_dim = "1";
  optr->Arg_Car[0].type_sample = "any";
  optr->Arg_Car[0].sample = "any";
  optr->Arg_Car[0].famille = "any";
  optr->Arg_Car[0].unite = "any";

  /* Var_minute */
  optr->Arg_Car[1].direction = DIR_IN;
  optr->Arg_Car[1].categorie = VECTOR;
  optr->Arg_Car[1].typ = ATYC_I16;
  optr->Arg_Car[1].array_dim = "1";
  optr->Arg_Car[1].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[1].type_sample = "any";
  optr->Arg_Car[1].sample = "any";
  optr->Arg_Car[1].famille = "any";
  optr->Arg_Car[1].unite = "any";

  /* Var_seconde */
  optr->Arg_Car[2].direction = DIR_IN;
  optr->Arg_Car[2].categorie = VECTOR;
  optr->Arg_Car[2].typ = ATYC_I16;
  optr->Arg_Car[2].array_dim = "1";
  optr->Arg_Car[2].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[2].type_sample = "any";
  optr->Arg_Car[2].sample = "any";
  optr->Arg_Car[2].famille = "any";
  optr->Arg_Car[2].unite = "any";

  optr->Arg_Car[3].direction = DIR_OUT;
  optr->Arg_Car[3].categorie = VECTOR;
  optr->Arg_Car[3].typ = ATYC_IF64;
  optr->Arg_Car[3].array_dim = "1";
  optr->Arg_Car[3].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[3].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[3].sample = "$Arg1.sample";
  optr->Arg_Car[3].unite = "second";
  optr->Arg_Car[3].misval = "-1";
  optr->Arg_Car[3].famille = "\"temps\"";

}
