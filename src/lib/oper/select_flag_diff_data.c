
/*************************************************************************
*
* OPERATOR         select_flag_diff_data.c  FUNCTION ANSI-C
*
* PURPOSE          Selection des données d'un vecteur selon des
*                  critères appliqués à un second vecteur "flag".
*
* DESCRIPTION      Selection des données pour lesquelles la valeur du
*                  "flag" sont différentes de crit1 ET crit2
*
*                  Particularité : les bornes de validité sont passées sous
*                  forme de float (même si elles doivent être appliqués à des int)
*                  pour pouvoir être NaN (pour signifier : pas de critère à appliquer).
*
* VERSION          1.0 
*
* ARGUMENTS  
*            IN   float   vect		vecteur de données quelconque
*            IN   float	  flag		vecteur "flag" 
*            IN   float   crit1         on prend les valeurs différentes de crit1
*            IN   float   crit2         on prend les valeurs différentes de crit2
*            IN   float   val      	on remplace les valeurs rejetées par NaN
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


int
select_flag_diff_data (unsigned long ndata,
		       const float *vect,
		       const float *flag,
		       const float crit1,
		       const float crit2,
		       float *select_vect, unsigned long *Tab_diagno)
{
  unsigned long i;
  float eps = 1.0e-6;
  unsigned long nb_crit1, nb_crit2, nb_NaN, nb_OK;

  nb_crit1 = 0;
  nb_crit2 = 0;
  nb_NaN = 0;
  nb_OK = 0;

  for (i = 0; i < ndata; i++)
    {
      select_vect[i] = K_NaN;

      if (!isfinite (flag[i]))
	{
	  select_vect[i] = vect[i];
	  nb_NaN++;
	  continue;
	}

      if (isfinite (crit1))
	{
	  if (fabs (flag[i] - crit1) < eps)
	    {
	      select_vect[i] = K_NaN;
	      nb_crit1++;
	      continue;
	    }
	}

      if (isfinite (crit2))
	{
	  if (fabs (flag[i] - crit2) < eps)
	    {
	      select_vect[i] = K_NaN;
	      nb_crit2++;
	      continue;
	    }
	}
      select_vect[i] = vect[i];
      nb_OK++;

    }

  Tab_diagno[0] = nb_OK;
  Tab_diagno[1] = nb_crit1;
  Tab_diagno[2] = nb_crit2;
  Tab_diagno[3] = nb_NaN;

  return nb_crit1 + nb_crit2;
}


/* la fonction d'enrobage classique */

int
OP_select_flag_diff_data (unsigned long NbVal, void *ArgList[],
			  char *DiagExec)
{
  unsigned long CodRet;
  unsigned long compteur[4];

  CodRet = select_flag_diff_data (NbVal,
				  (float *) ArgList[0],
				  (float *) ArgList[1],
				  *(float *) ArgList[2],
				  *(float *) ArgList[3],
				  (float *) ArgList[4], compteur);

  sprintf (DiagExec,
	   "%lu valeurs (sur %lu) rejetée(s) [ok:%lu, crit1:%lu, crit2:%lu, n:%lu]",
	   CodRet, NbVal, compteur[0], compteur[1], compteur[2], compteur[3]);

  return OP_OK;
}

void
ID_select_flag_diff_data (oper * optr)
{
  strcpy (optr->Nom, "select_flag_diff_data");
  optr->Version = "$Revision$";
  optr->Date = "$Date$";
  optr->fctptr = OP_select_flag_diff_data;
  optr->NbArg = 5;		/* doit rester inf. a FIL_MAX_ARG */

  /* vect */
  optr->Arg_Car[0].direction = DIR_IN;
  optr->Arg_Car[0].categorie = VECTOR;
  optr->Arg_Car[0].typ = ATYC_IF32;
  optr->Arg_Car[0].array_dim = "1";
  optr->Arg_Car[0].type_sample = "any";
  optr->Arg_Car[0].sample = "any";
  optr->Arg_Car[0].unite = "any";

  /* flag  */
  optr->Arg_Car[1].direction = DIR_IN;
  optr->Arg_Car[1].categorie = VECTOR;
  optr->Arg_Car[1].typ = ATYC_IF32;
  optr->Arg_Car[1].array_dim = "1";
  optr->Arg_Car[1].type_sample = "any";
  optr->Arg_Car[1].sample = "any";
  optr->Arg_Car[1].unite = "any";

  /* crit1  */
  optr->Arg_Car[2].direction = DIR_IN;
  optr->Arg_Car[2].categorie = COEFFICIENT;
  optr->Arg_Car[2].typ = ATYC_IF32;
  optr->Arg_Car[2].array_dim = "1";
  optr->Arg_Car[2].type_sample = NULL;
  optr->Arg_Car[2].sample = NULL;
  optr->Arg_Car[2].unite = "";

  /* crit2  */
  optr->Arg_Car[3].direction = DIR_IN;
  optr->Arg_Car[3].categorie = COEFFICIENT;
  optr->Arg_Car[3].typ = ATYC_IF32;
  optr->Arg_Car[3].array_dim = "1";
  optr->Arg_Car[3].type_sample = NULL;
  optr->Arg_Car[3].sample = NULL;
  optr->Arg_Car[3].unite = "";

  /* select_vect */
  optr->Arg_Car[4].direction = DIR_OUT;
  optr->Arg_Car[4].categorie = VECTOR;
  optr->Arg_Car[4].typ = ATYC_IF32;
  optr->Arg_Car[4].array_dim = "1";
  optr->Arg_Car[4].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[4].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[4].sample = "$Arg1.sample";
  optr->Arg_Car[4].ref_time = "$Arg1.ref_time";
  optr->Arg_Car[4].unite = "$Arg1.unit";
  optr->Arg_Car[4].misval = "$Arg1.misval";
  optr->Arg_Car[4].famille = "$Arg1.famille";
  optr->Arg_Car[4].name = "$Arg1.name";
}

