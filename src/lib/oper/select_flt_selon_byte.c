/*************************************************************************
*
* OPERATOR         select_flt_selon_byte.c  FUNCTION ANSI-C
*
* PURPOSE          Selection des données d'un vecteur de type float selon des
*                  critères appliqués à un second vecteur "flag" de type uint8.
*
* DESCRIPTION      Selection des données pour lesquelles la valeur du
*                  "flag" sont comprises entre crit1_min et 
* 		   crit1_max OU entre crit2_min et crit2_max.
*		   Si on n'a besoin que d'un seul , on peut passer deux fois les
*	  	   mêmes bornes.
*                  Les données non selectionnées sont remplacées par des NaN.
*
*
* VERSION          1.0 
*
* ARGUMENTS  
*            IN   float   vect		vecteur de données quelconque
*            IN   uint_8  flag		vecteur "flag" 
*            IN   uint_8  crit1_min     on prend les valeurs supérieures à crit1_min 
*            IN   uint_8  crit1_max	on prend les valeurs inférieures à crit1_max
*            IN   uint_8  crit2_min	on prend les valeurs supérieures à crit2_min
*            IN   uint_8  crit2_max	on prend les valeurs inférieures à crit2_max
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

#include <stdio.h>
#include <string.h>
#include <math.h>
#include "struct_oper.h"


long
select_flt_selon_byte (unsigned long ndata,
		       const float *vect,
		       const uint8_t * flag,
		       const uint8_t crit1_min,
		       const uint8_t crit1_max,
		       const uint8_t crit2_min,
		       const uint8_t crit2_max, float *select_vect)
{
  unsigned long i;
  unsigned long nb_OK = 0;

  for (i = 0; i < ndata; i++)
    {
      select_vect[i] = K_NaN;

      if (!isfinite (vect[i]))
	continue;

      if (((flag[i] >= crit1_min) && (flag[i] <= crit1_max)) ||
	  ((flag[i] >= crit2_min) && (flag[i] <= crit2_max)))
	{
	  select_vect[i] = vect[i];
	  nb_OK++;
	}
      else
	{
	  select_vect[i] = K_NaN;
	}

    }

  return nb_OK;
}


/* la fonction d'enrobage classique */

int
OP_select_flt_selon_byte (unsigned long NbVal, void *ArgList[],
			  char *DiagExec)
{
  long CodRet;
  sprintf (DiagExec,
	   "select_flt_selon_byte (%lu Ech),  %d<=OK<=%d, ou %d<=OK<=%d",
	   NbVal, *(uint8_t *) ArgList[2], *(uint8_t *) ArgList[3],
	   *(uint8_t *) ArgList[4], *(uint8_t *) ArgList[5]);

  CodRet = select_flt_selon_byte (NbVal,
				  (float *) ArgList[0],
				  (uint8_t *) ArgList[1],
				  *(uint8_t *) ArgList[2],
				  *(uint8_t *) ArgList[3],
				  *(uint8_t *) ArgList[4],
				  *(uint8_t *) ArgList[5],
				  (float *) ArgList[6]);

  sprintf (&(DiagExec[strlen (DiagExec)]), "; %ld valeurs selectionnees",
	   CodRet);
  if (NbVal != 0)
    {
      sprintf (&(DiagExec[strlen (DiagExec)]), " (%g%%).",
	       100.0 * CodRet / NbVal);
    }

  return OP_OK;
}

void
ID_select_flt_selon_byte (oper * optr)
{
  strcpy (optr->Nom, "select_flt_selon_byte");
  optr->Version = "$Revision$";
  optr->Date = "$Date$";
  optr->fctptr = OP_select_flt_selon_byte;
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
  optr->Arg_Car[1].typ = ATYC_UI8;
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
  optr->Arg_Car[2].typ = ATYC_UI8;
  optr->Arg_Car[2].array_dim = "1";
  optr->Arg_Car[2].type_sample = NULL;
  optr->Arg_Car[2].sample = NULL;
  optr->Arg_Car[2].unite = "";

  /* crit1_max */
  optr->Arg_Car[3].direction = DIR_IN;
  optr->Arg_Car[3].categorie = COEFFICIENT;
  optr->Arg_Car[3].typ = ATYC_UI8;
  optr->Arg_Car[3].array_dim = "1";
  optr->Arg_Car[3].type_sample = NULL;
  optr->Arg_Car[3].sample = NULL;
  optr->Arg_Car[3].unite = "";

  /* crit2_min */
  optr->Arg_Car[4].direction = DIR_IN;
  optr->Arg_Car[4].categorie = COEFFICIENT;
  optr->Arg_Car[4].typ = ATYC_UI8;
  optr->Arg_Car[4].array_dim = "1";
  optr->Arg_Car[4].type_sample = NULL;
  optr->Arg_Car[4].sample = NULL;
  optr->Arg_Car[4].unite = "";

  /* crit2_max */
  optr->Arg_Car[5].direction = DIR_IN;
  optr->Arg_Car[5].categorie = COEFFICIENT;
  optr->Arg_Car[5].typ = ATYC_UI8;
  optr->Arg_Car[5].array_dim = "1";
  optr->Arg_Car[5].type_sample = NULL;
  optr->Arg_Car[5].sample = NULL;
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
  optr->Arg_Car[6].name = "\"Valeurs selectionnes de \" + $Arg1.name";
  optr->Arg_Car[6].en_name = "\"Selected values from \" + $Arg1.english_name";
}
