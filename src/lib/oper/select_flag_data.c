/*************************************************************************
*
* OPERATOR         select_flag_data.c  FUNCTION ANSI-C
*
* PURPOSE          Selection des données d'un vecteur selon des
*                  critères appliqués à un second vecteur "flag".
*
* DESCRIPTION      Selection des données pour lesquelles la valeur du
*                  "flag" sont comprises entre crit1_min et 
* 		   crit1_max OU entre crit2_min et crit2_max.
*		   On peut ne renseigner qu'un seul critère, dans cas on passe
*	  	   pour les critères non renseignés la valeur (0./0.) . 	
*                  Les données non selectionnées sont remplacées par des NaN.
*
*                  Particularité : les bornes de validité sont passées sous
*                  forme de float (même si elles doivent être appliqués à des int)
*                  pour pouvoir être NaN (pour signifier : pas de critère à appliquer).
*
* VERSION          1.0 
*
* ARGUMENTS  
*            IN   float   vect		vecteur de données quelconque
*            IN   int	  flag		vecteur "flag" 
*            IN   float   crit1_min     on prend les valeurs supérieures à crit1_min 
*            IN   float   crit1_max	on prend les valeurs inférieures à crit1_max
*            IN   float   crit2_min	on prend les valeurs supérieures à crit2_min
*            IN   float   crit2_max	on prend les valeurs inférieures à crit2_max
*           
*            OUT  float   select_vect   vecteur ne contenant que les données selectionnées
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
*############################################################################*/

#define _POSIX_SOURCE 1
#define _XOPEN_SOURCE 600
#define _HPUX_SOURCE 1

#include <stdio.h>
#include <string.h>
#include <math.h>
#include "struct_oper.h"


void
select_flag_data (unsigned long ndata,
		  const float *vect,
		  const int *flag,
		  const float crit1_min,
		  const float crit1_max,
		  const float crit2_min,
		  const float crit2_max, float *select_vect)
{
  unsigned long i;
  float tempo1, tempo2;

  for (i = 0; i < ndata; i++)
    {
      select_vect[i] = K_NaN;
      tempo1 = K_NaN;
      tempo2 = K_NaN;

      if (!isfinite (vect[i]))
	continue;

      if (isfinite (crit1_min))
	{
	  if (flag[i] >= (int) crit1_min)
	    tempo1 = vect[i];
	  else
	    {
	      tempo1 = K_NaN;
	    }
	}
      if (isfinite (crit1_max))
	{

	  if (isfinite (crit1_min) && isfinite (tempo1))
	    {
	      /*if (tempo1 > crit1_max) tempo1= K_NaN; */
	      if (flag[i] > (int) crit1_max)
		{
		  tempo1 = K_NaN;
		}
	    }
	  else if (!isfinite (crit1_min))
	    {
	      if (flag[i] <= (int) crit1_max)
		tempo1 = vect[i];
	      else
		tempo1 = K_NaN;
	    }
	}

      if (0 != isfinite (crit2_min))
	{
	  if (flag[i] >= (int) crit2_min)
	    tempo2 = vect[i];
	  else
	    tempo2 = K_NaN;

	}
      if (isfinite (crit2_max))
	{
	  if (isfinite (crit2_min) && isfinite (tempo2))
	    {
	      /*if (tempo2 > crit2_max) tempo2= K_NaN; */
	      if (flag[i] > (int) crit2_max)
		tempo2 = K_NaN;
	    }
	  else if (!isfinite (crit2_min))
	    {
	      if (flag[i] <= (int) crit2_max)
		tempo2 = vect[i];
	      else
		tempo2 = K_NaN;
	    }

	}
      if (isfinite (tempo1))
	select_vect[i] = tempo1;
      if (isfinite (tempo2))
	select_vect[i] = tempo2;
    }

  return;
}


/* la fonction d'enrobage classique */

int
OP_select_flag_data (unsigned long NbVal, void *ArgList[], char *DiagExec)
{
  sprintf (DiagExec,
	   "select_flag_data (%lu ech); OK si %g<flag<%g, ou %g<flag<%g",
	   NbVal, *(float *) ArgList[2], *(float *) ArgList[3],
	   *(float *) ArgList[4], *(float *) ArgList[5]);

  select_flag_data (NbVal,
		    (float *) ArgList[0],
		    (int *) ArgList[1],
		    *(float *) ArgList[2],
		    *(float *) ArgList[3],
		    *(float *) ArgList[4],
		    *(float *) ArgList[5],
                    (float *) ArgList[6]);

  return OP_OK;
}

void
ID_select_flag_data (oper * optr)
{
  strcpy (optr->Nom, "select_flag_data");
  optr->Version = "$Revision$";
  optr->Date = "$Date$";
  optr->fctptr = OP_select_flag_data;
  optr->NbArg = 7;		/* doit rester inf. a FIL_MAX_ARG */

  /* vect */
  optr->Arg_Car[0].direction = DIR_IN;
  optr->Arg_Car[0].categorie = VECTOR;
  optr->Arg_Car[0].typ = ATYC_IF32;
  optr->Arg_Car[0].array_dim = "1";
  optr->Arg_Car[0].type_sample = "any";
  optr->Arg_Car[0].sample = "any";
  optr->Arg_Car[0].unite = "any";

  /* flag */
  optr->Arg_Car[1].direction = DIR_IN;
  optr->Arg_Car[1].categorie = VECTOR;
  optr->Arg_Car[1].typ = ATYC_I32;
  optr->Arg_Car[1].array_dim = "1";
  /* vect et flag doivent être synchrones, 
   * ou au moins avoir le meme nombre d'echantillons. */
  optr->Arg_Car[1].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[1].type_sample = "any";
  optr->Arg_Car[1].sample = "any";
  optr->Arg_Car[1].unite = "any";

  /* crit1_min */
  optr->Arg_Car[2].direction = DIR_IN;
  optr->Arg_Car[2].categorie = COEFFICIENT;
  optr->Arg_Car[2].typ = ATYC_IF32;
  optr->Arg_Car[2].array_dim = "1";
  optr->Arg_Car[2].unite = "";

  /* crit1_max */
  optr->Arg_Car[3].direction = DIR_IN;
  optr->Arg_Car[3].categorie = COEFFICIENT;
  optr->Arg_Car[3].typ = ATYC_IF32;
  optr->Arg_Car[3].array_dim = "1";
  optr->Arg_Car[3].unite = "";

  optr->Arg_Car[4].direction = DIR_IN;
  optr->Arg_Car[4].categorie = COEFFICIENT;
  optr->Arg_Car[4].typ = ATYC_IF32;
  optr->Arg_Car[4].array_dim = "1";
  optr->Arg_Car[4].unite = "";

  optr->Arg_Car[5].direction = DIR_IN;
  optr->Arg_Car[5].categorie = COEFFICIENT;
  optr->Arg_Car[5].typ = ATYC_IF32;
  optr->Arg_Car[5].array_dim = "1";
  optr->Arg_Car[5].unite = "";

  optr->Arg_Car[6].direction = DIR_OUT;
  optr->Arg_Car[6].categorie = VECTOR;
  optr->Arg_Car[6].typ = ATYC_IF32;
  optr->Arg_Car[6].array_dim = "1";
  optr->Arg_Car[6].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[6].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[6].sample = "$Arg1.sample";
  optr->Arg_Car[6].ref_time = "$Arg1.ref_time";
  optr->Arg_Car[6].unite = "$Arg1.unit";
  optr->Arg_Car[6].misval = "$Arg1.misval";
  optr->Arg_Car[6].famille = "$Arg1.famille";
}
