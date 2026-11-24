/****************************************************
*
* OPERATOR      Transforme_flag_mat_CAPITOUL.c   FUNCTION  ANSI-C
*
* PURPOSE       
*
* DESCRIPTION   transforms value according to time : 
*                        1->1 Always
*                        2->2 Between T1 and T2, 2->3 otherwise. 
*                               (if T2<T1, alwas 2->3
*                        3->4 Always
*
* VERSION       $Revision$
*
* ARGUMENTS   IN   short int  flag_in    Any  Original flag
*             IN   double     time_in    s    time of flag_in         
*             IN   double     T_1        s    Start time of 2->2
*             IN   double     T_2        s    End time of 2->2
*             OUT  short int  flag_out same as 1  modified flag
*
* ENTRY            
*                 
* SUBPROGRAMS   none
*
* FILES   
*
* REFERENCES   
*
* CHANGES
*
*
* COPYRIGHT     Meteo-France
*
* AGREEMENT
*#########################################################################*/

#define _POSIX_SOURCE 1
#define _XOPEN_SOURCE 600

#include <stdio.h>
#include <string.h>
#include "struct_oper.h"


void
Transforme_flag_mat_CAPITOUL (unsigned long NLoop, const short int *flag_in,	/* en ... any */
			      const double *time_in,	/* en secondes */
			      const double T_1,	/* en secondes */
			      const double T_2,	/* en secondes */
			      short int *flag_out)
{
  unsigned long i;

  for (i = 0; i < NLoop; i++)
    {
      switch (*flag_in)
	{
	case 1:
	  *flag_out = 1;
	  break;
	case 2:
	  if ((*time_in >= T_1) && (*time_in <= T_2))
	    {
	      *flag_out = 2;
	    }
	  else
	    {
	      *flag_out = 3;
	    }
	  break;
	case 3:
	  *flag_out = 4;
	  break;
	default:		/* Valeur bizarre (probablement manquante)
				   que l'on conserve telle-quelle. */
	  *flag_out = *flag_in;
	}

      flag_in++;
      time_in++;
      flag_out++;
    }
}

/* la fonction d'enrobage classique */

int
OP_Transforme_flag_mat_CAPITOUL (unsigned long NbVal, void *ArgList[],
				 char *DiagExec)
{
  (void) sprintf (DiagExec,
		  "Transforme_flag_mat_CAPITOUL, NbVal=%lu,  T1=%g, T2=%g",
		  NbVal,
		  *((double *) ArgList[2]),
		  *((double *) ArgList[3]));

  Transforme_flag_mat_CAPITOUL (NbVal,
				(short int *) ArgList[0],
				(double *) ArgList[1],
				*((double *) ArgList[2]),
				*((double *) ArgList[3]),
				(short int *) ArgList[4]);
  return OP_OK;
}

void
ID_Transforme_flag_mat_CAPITOUL (oper * optr)
{
  strcpy (optr->Nom, "Transforme_flag_mat_CAPITOUL");
  optr->Version = "$Revision$";
  optr->Date = "$Date$";
  optr->fctptr = OP_Transforme_flag_mat_CAPITOUL;
  optr->NbArg = 5;		/* doit rester inf. a FIL_MAX_ARG */

  /* flag_in */
  optr->Arg_Car[0].direction = DIR_IN;
  optr->Arg_Car[0].categorie = VECTOR;
  optr->Arg_Car[0].typ = ATYC_I16;
  optr->Arg_Car[0].array_dim = "1";
  optr->Arg_Car[0].type_sample = "any";
  optr->Arg_Car[0].sample = "any";
  optr->Arg_Car[0].unite = "any";

  /* time_in */
  optr->Arg_Car[1].direction = DIR_IN;
  optr->Arg_Car[1].categorie = VECTOR;
  optr->Arg_Car[1].typ = ATYC_IF64;
  optr->Arg_Car[1].array_dim = "1";
  optr->Arg_Car[1].type_sample = "any";
  optr->Arg_Car[1].sample = "any";
  optr->Arg_Car[1].unite = "sec";

  /* T_1 */
  optr->Arg_Car[2].direction = DIR_IN;
  optr->Arg_Car[2].categorie = COEFFICIENT;
  optr->Arg_Car[2].typ = ATYC_IF64;
  optr->Arg_Car[2].array_dim = "1";
  optr->Arg_Car[2].type_sample = "any";
  optr->Arg_Car[2].sample = "any";
  optr->Arg_Car[2].unite = "sec";

  /* T_2 */
  optr->Arg_Car[3].direction = DIR_IN;
  optr->Arg_Car[3].categorie = COEFFICIENT;
  optr->Arg_Car[3].typ = ATYC_IF64;
  optr->Arg_Car[3].array_dim = "1";
  optr->Arg_Car[3].type_sample = "any";
  optr->Arg_Car[3].sample = "any";
  optr->Arg_Car[3].unite = "sec";

  /* flag_out */
  optr->Arg_Car[4].direction = DIR_OUT;
  optr->Arg_Car[4].categorie = VECTOR;
  optr->Arg_Car[4].typ = ATYC_I16;
  optr->Arg_Car[4].array_dim = "1";
  optr->Arg_Car[4].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[4].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[4].sample = "$Arg1.sample";
  optr->Arg_Car[4].ref_time = "$Arg1.ref_time";
  optr->Arg_Car[4].unite = "$Arg1.unit";
  optr->Arg_Car[4].famille = "$Arg1.famille";
  optr->Arg_Car[4].misval = "$Arg1.misval";
}
