/*************************************************************************
*
* OPERATOR         select_data.c  FUNCTION ANSI-C
*
* PURPOSE          Creation d'un vecteur ne contenant que la partie des données
*                  selectionnées selon les critères passés en argument .
*
* DESCRIPTION      on selectionne les données comprises entre crit1_min et 
* 		   crit1_max et éventuellement entre crit2_min et crit2_max.
*		   On peut ne renseigner qu'un seul critère, dans cas on passe
*	  	   pour les critères non renseignés la valeur (0./0.) . 	
*                  Les données non selectionnées sont remplacées par "val" (la
*                  plupart du temps on y passera "misval").
*
* VERSION          1.0 
*
* ARGUMENTS  
*            IN   float   vect		vecteur de données quelconque
*            IN   float   crit1_min     on prend les valeurs supérieures à crit1_min 
*            IN   float   crit1_max	on prend les valeurs inférieures à crit1_max
*            IN   float   crit2_min	on prend les valeurs supérieures à crit2_min
*            IN   float   crit2_max	on prend les valeurs inférieures à crit2_max
*            IN   float   val           valeur de remplacement des données non
*                                       selectionnées qui ne sont pas manquantes
*                                       (misval, 0, autre valeur)
*
*            OUT  float   select_vect   vecteur ne contenant que les données selectionnées
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
*############################################################################*/

#define _POSIX_SOURCE 1
#define _XOPEN_SOURCE 600
#define _HPUX_SOURCE 1

#include <math.h>
#include <stdio.h>
#include <string.h>
#include <math.h>
#include "struct_oper.h"





size_t
select_data (unsigned long ndata,
	     const float *vect,
	     float crit1_min,
	     float crit1_max,
	     float crit2_min,
	     float crit2_max,
	     float val, float *select_vect, int *flag_val_interv_p)
{
  unsigned long i;
  size_t nb_elim = 0;
  float tempo1, tempo2;

  /* Test de la valeur de remplacement.
   *     En général, les valeurs en-dehors des intervalles
   *  définis par les critères sont considérées comme des
   *  "mauvaises" valeur. La valeur de substitution doit
   *  donc plutot correspondre à un code "misval" ou "invval",
   *  et ne pas être confondue avec les valeurs normales.
   *     Donc, si "val" est dans un des intervalles définis
   *  par crit1_min, crit1_max, crit2_min, crit2_max, on le
   *  signale en levant un flag (bit 0 pour intervalle 1, bit 1
   *  pour intervalle2).
   */
  *flag_val_interv_p = 0;
  if (isfinite (val))
    {
      /* (val < crit1_min) est vrai si :
       *   (crit1_min non_NaN) et (val < crit1_min)
       * Donc sa négation est vraie si :
       *   (crit1_min NaN) ou (val >= crit1_min)
       */
      if (!(val < crit1_min))
	{
	  if (!(val > crit1_max))
	    {
	      /* Cas particulier : si min et max sont NaN, jamais
	       * d'elimination, donc pas de test. */
	      if (isfinite (crit1_min) || isfinite (crit1_max))
		*flag_val_interv_p = *flag_val_interv_p | 1;
	    }
	}

      /* La même chose en compact sur intervalle nr 2  */
      if (!(val < crit2_min) && !(val > crit2_max))
	{
	  if (isfinite (crit2_min) || isfinite (crit2_max))
	    *flag_val_interv_p |= 2;
	}
    }

  for (i = 0; i < ndata; i++)
    {
      select_vect[i] = K_NaN;
      tempo1 = K_NaN;
      tempo2 = K_NaN;

      if (!isfinite (vect[i]))
	continue;

      if (isfinite (crit1_min))
	{

	  if (vect[i] >= crit1_min)
	    tempo1 = vect[i];
	  else
	    tempo1 = val;
	}

      if (isfinite (crit1_max))
	{
	  if (isfinite (crit1_min) && isfinite (tempo1))
	    {
	      /*if (tempo1 > crit1_max) tempo1= K_NaN; */
	      if (tempo1 > crit1_max)
		tempo1 = val;
	    }
	  else if (!isfinite (crit1_min))
	    {
	      if (vect[i] <= (crit1_max))
		tempo1 = vect[i];
	      else
		tempo1 = val;
	    }
	}

      if (isfinite (crit2_min))
	{
	  if (vect[i] >= crit2_min)
	    tempo2 = vect[i];
	  else
	    tempo2 = val;
	}

      if (isfinite (crit2_max))
	{
	  if (isfinite (crit2_min) && isfinite (tempo2))
	    {
	      /*if (tempo2 > crit2_max) tempo2= K_NaN; */
	      if (tempo2 > crit2_max)
		tempo2 = val;
	    }
	  else if (!isfinite (crit2_min))
	    {
	      if (vect[i] <= crit2_max)
		tempo2 = vect[i];
	      else
		tempo2 = val;
	    }
	}

      if (isfinite (tempo1))
	select_vect[i] = tempo1;
      if (isfinite (tempo2))
	select_vect[i] = tempo2;

      if (select_vect[i] != vect[i])
	nb_elim++;
    }

  return nb_elim;
}


/* la fonction d'enrobage classique */

int
OP_select_data (unsigned long NbVal, void *ArgList[], char *DiagExec)
{
  size_t CodRet;
  int flag_val_interv = 0;

  CodRet = select_data (NbVal,
			(float *) ArgList[0],
			*(float *) ArgList[1],
			*(float *) ArgList[2],
			*(float *) ArgList[3],
			*(float *) ArgList[4],
			*(float *) ArgList[5],
			(float *) ArgList[6], &flag_val_interv);

  if (flag_val_interv & 1)
    {
      DiagExec +=
	sprintf (DiagExec, "Attention : %g in [%g, %g];",
		 *(float *) ArgList[5], *(float *) ArgList[1],
		 *(float *) ArgList[2]);
    }
  if (flag_val_interv & 2)
    {
      DiagExec +=
	sprintf (DiagExec, "Attention : %g in [%g, %g];",
		 *(float *) ArgList[5], *(float *) ArgList[3],
		 *(float *) ArgList[4]);
    }
  sprintf (DiagExec,
	   "select_data, %lu eliminees (sur %lu), hors de [%g, %g] ou [%g, %g]",
	   (unsigned long) CodRet, NbVal,
	   *(float *) ArgList[1], *(float *) ArgList[2],
	   *(float *) ArgList[3], *(float *) ArgList[4]);

  return OP_OK;
}

void
ID_select_data (oper * optr)
{
  strcpy (optr->Nom, "select_data");
  optr->Version = "$Revision$";
  optr->Date = "$Date$";
  optr->fctptr = OP_select_data;
  optr->NbArg = 7;		/* doit rester inf. a FIL_MAX_ARG */

  /* vect */
  optr->Arg_Car[0].direction = DIR_IN;
  optr->Arg_Car[0].categorie = VECTOR;
  optr->Arg_Car[0].typ = ATYC_IF32;
  optr->Arg_Car[0].array_dim = "1";
  optr->Arg_Car[0].type_sample = "any";
  optr->Arg_Car[0].sample = "any";
  optr->Arg_Car[0].unite = "any";

  /* crit1_min */
  optr->Arg_Car[1].direction = DIR_IN;
  optr->Arg_Car[1].categorie = COEFFICIENT;
  optr->Arg_Car[1].typ = ATYC_IF32;
  optr->Arg_Car[1].array_dim = "1";
  optr->Arg_Car[1].type_sample = NULL;
  optr->Arg_Car[1].sample = NULL;
  optr->Arg_Car[1].unite = "";

  /* crit1_max */
  optr->Arg_Car[2].direction = DIR_IN;
  optr->Arg_Car[2].categorie = COEFFICIENT;
  optr->Arg_Car[2].typ = ATYC_IF32;
  optr->Arg_Car[2].array_dim = "1";
  optr->Arg_Car[2].type_sample = NULL;
  optr->Arg_Car[2].sample = NULL;
  optr->Arg_Car[2].unite = "";

  /* crit2_min */
  optr->Arg_Car[3].direction = DIR_IN;
  optr->Arg_Car[3].categorie = COEFFICIENT;
  optr->Arg_Car[3].typ = ATYC_IF32;
  optr->Arg_Car[3].array_dim = "1";
  optr->Arg_Car[3].type_sample = NULL;
  optr->Arg_Car[3].sample = NULL;
  optr->Arg_Car[3].unite = "";

  /* crit2_max */
  optr->Arg_Car[4].direction = DIR_IN;
  optr->Arg_Car[4].categorie = COEFFICIENT;
  optr->Arg_Car[4].typ = ATYC_IF32;
  optr->Arg_Car[4].array_dim = "1";
  optr->Arg_Car[4].type_sample = NULL;
  optr->Arg_Car[4].sample = NULL;
  optr->Arg_Car[4].unite = "";

  /* val */
  optr->Arg_Car[5].direction = DIR_IN;
  optr->Arg_Car[5].categorie = COEFFICIENT;
  optr->Arg_Car[5].typ = ATYC_IF32;
  optr->Arg_Car[5].array_dim = "1";
  optr->Arg_Car[5].type_sample = NULL;
  optr->Arg_Car[5].sample = NULL;
  optr->Arg_Car[5].unite = "";

  /* select_vect */
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
  optr->Arg_Car[6].name = "$Arg1.name";
  optr->Arg_Car[6].en_name = "$Arg1.english_name";
}
