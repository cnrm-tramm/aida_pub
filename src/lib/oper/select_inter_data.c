/*************************************************************************
*
* OPERATOR         select_inter_data.c  FUNCTION ANSI-C
*
* PURPOSE          Fabrication de deux vecteurs ne contenant que la partie
*                  des données selectionnées selon les critères passés 
*                  en argument appliqués à un des deux vecteurs d'entrée.
*
* DESCRIPTION      on selectionne les données de vect1 et vect2 si les 
*                  données de vect2 sont comprises entre crit1_min et 
*                  crit1_max et éventuellement entre crit2_min et crit2_max.
*		   On peut ne renseigner qu'un seul critère, dans cas on passe
*	  	   pour les critères non renseignés la valeur Nan (0.0/0.0). 	
*                  Les données non selectionnées sont remplacées par "val"(la
*                  plupart du temps on y passera "misval").
*
* VERSION          1.0 
*
* ARGUMENTS  
*            IN   float   vect1         vecteur de données quelconque
*            IN   float   vect2		vecteur sur lequel on appliquera le test.
*            IN   float   crit1_min     Borne min du premier test.
*            IN   float   crit1_max	Borne max du premier test.
*            IN   float   crit2_min	Borne min du second test.
*            IN   float   crit2_max	Borne max du second test.
*            IN   float   val1           valeur de remplacement des données non
*                                       selectionnées qui ne sont pas manquantes
*                                       (misval, 0, autre valeur) pour vect1
*            IN   float   val2           valeur de remplacement des données non
*                                       selectionnées qui ne sont pas manquantes
*                                       (misval, 0, autre valeur) pour vect2
*
*            OUT  float   select_vect1   vecteur contenant les données 
*                                        selectionnées de vect1
*            OUT  float   select_vect2   vecteur contenant les données 
*                                        sélectionnées de vect2.
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
#include "struct_oper.h"

int
select_inter_data (unsigned long ndata,
		   const float *vect1,
		   const float *vect2,
		   const float crit1_min,
		   const float crit1_max,
		   const float crit2_min,
		   const float crit2_max,
		   const float val1,
		   const float val2, float *select_vect1, float *select_vect2)
{
  unsigned long i;
  int flag, flag1, flag2;

  for (i = 0; i < ndata; i++)
    {
      select_vect1[i] = K_NaN;
      select_vect2[i] = K_NaN;
      flag1 = 0;
      flag2 = 0;

      /* Si vect2[i] est manquant, les valeurs correpondantes en sortie 
       * le seront aussi. */
      if (!isfinite (vect2[i]))
	      continue;

      if (isfinite (crit1_min) && isfinite(crit1_max))
	      {
          if ( (vect2[i] >= crit1_min) && (vect2[i] <= crit1_max) )
            flag1 = 1;
	      }

      if (isfinite (crit2_min) && isfinite(crit2_max))
	      {
          if ( (vect2[i] >= crit2_min) && (vect2[i] <= crit2_max) )
            flag2 = 1;
	      }
      flag = flag1 | flag2;
      
      if (flag == 1)
        {
          select_vect1[i] = vect1[i];
          select_vect2[i] = vect2[i];
        }
      else
        {
          if (isfinite(vect1[i]))
            select_vect1[i] = val1;
          select_vect2[i] = val2;
        }
      /*fprintf(stderr,"flag %d flag1 %d flag2 %d select_vect1 %f select_vect2 %f\n", flag, flag1, flag2,select_vect1[i], select_vect2[i]);*/
	  }


  return 0;
}


/* la fonction d'enrobage classique */
#include <string.h>
#include <stdio.h>

int
OP_select_inter_data (unsigned long NbVal, void *ArgList[], char *DiagExec)
{
  sprintf (DiagExec,
	   "select_inter_data (%lu ech.), crit1 = [%f, %f], crit2 = [%f, %f]",
	   NbVal, *(float *) ArgList[2], *(float *) ArgList[3],
	   *(float *) ArgList[4], *(float *) ArgList[5]);

  (void) select_inter_data (NbVal,
			      (float *) ArgList[0],
			      (float *) ArgList[1],
			      *(float *) ArgList[2],
			      *(float *) ArgList[3],
			      *(float *) ArgList[4],
			      *(float *) ArgList[5],
			      *(float *) ArgList[6],
			      *(float *) ArgList[7],
			      (float *) ArgList[8], (float *) ArgList[9]);

  return OP_OK;
}

void
ID_select_inter_data (oper * optr)
{
  strcpy (optr->Nom, "select_inter_data");
  optr->Version = "2.0";
  optr->Date = "25/05/00";
  optr->fctptr = OP_select_inter_data;
  optr->NbArg = 10;		/* doit rester inf. a FIL_MAX_ARG */

  /* vect1 */
  optr->Arg_Car[0].direction = DIR_IN;
  optr->Arg_Car[0].categorie = VECTOR;
  optr->Arg_Car[0].typ = ATYC_IF32;
  optr->Arg_Car[0].array_dim = "1";
  optr->Arg_Car[0].type_sample = "any";
  optr->Arg_Car[0].sample = "any";
  optr->Arg_Car[0].unite = "any";

  /* vect2 */
  optr->Arg_Car[1].direction = DIR_IN;
  optr->Arg_Car[1].categorie = VECTOR;
  optr->Arg_Car[1].typ = ATYC_IF32;
  optr->Arg_Car[1].array_dim = "1";
  optr->Arg_Car[1].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[1].type_sample = "any";
  optr->Arg_Car[1].sample = "any";
  optr->Arg_Car[1].unite = "any";

  optr->Arg_Car[2].direction = DIR_IN;
  optr->Arg_Car[2].categorie = COEFFICIENT;
  optr->Arg_Car[2].typ = ATYC_IF32;
  optr->Arg_Car[2].array_dim = "1";
  optr->Arg_Car[2].type_sample = NULL;
  optr->Arg_Car[2].sample = NULL;
  optr->Arg_Car[2].unite = "";

  optr->Arg_Car[3].direction = DIR_IN;
  optr->Arg_Car[3].categorie = COEFFICIENT;
  optr->Arg_Car[3].typ = ATYC_IF32;
  optr->Arg_Car[3].array_dim = "1";
  optr->Arg_Car[3].type_sample = NULL;
  optr->Arg_Car[3].sample = NULL;
  optr->Arg_Car[3].unite = "";

  optr->Arg_Car[4].direction = DIR_IN;
  optr->Arg_Car[4].categorie = COEFFICIENT;
  optr->Arg_Car[4].typ = ATYC_IF32;
  optr->Arg_Car[4].array_dim = "1";
  optr->Arg_Car[4].type_sample = NULL;
  optr->Arg_Car[4].sample = NULL;
  optr->Arg_Car[4].unite = "";

  optr->Arg_Car[5].direction = DIR_IN;
  optr->Arg_Car[5].categorie = COEFFICIENT;
  optr->Arg_Car[5].typ = ATYC_IF32;
  optr->Arg_Car[5].array_dim = "1";
  optr->Arg_Car[5].type_sample = NULL;
  optr->Arg_Car[5].sample = NULL;
  optr->Arg_Car[5].unite = "";

  optr->Arg_Car[6].direction = DIR_IN;
  optr->Arg_Car[6].categorie = COEFFICIENT;
  optr->Arg_Car[6].typ = ATYC_IF32;
  optr->Arg_Car[6].array_dim = "1";
  optr->Arg_Car[6].type_sample = NULL;
  optr->Arg_Car[6].sample = NULL;
  optr->Arg_Car[6].unite = "";

  optr->Arg_Car[7].direction = DIR_IN;
  optr->Arg_Car[7].categorie = COEFFICIENT;
  optr->Arg_Car[7].typ = ATYC_IF32;
  optr->Arg_Car[7].array_dim = "1";
  optr->Arg_Car[7].type_sample = NULL;
  optr->Arg_Car[7].sample = NULL;
  optr->Arg_Car[7].unite = "";

  optr->Arg_Car[8].direction = DIR_OUT;
  optr->Arg_Car[8].categorie = VECTOR;
  optr->Arg_Car[8].typ = ATYC_IF32;
  optr->Arg_Car[8].array_dim = "1";
  optr->Arg_Car[8].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[8].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[8].sample = "$Arg1.sample";
  optr->Arg_Car[8].ref_time = "$Arg1.ref_time";
  optr->Arg_Car[8].unite = "$Arg1.unit";
  optr->Arg_Car[8].misval = "$Arg1.misval";
  optr->Arg_Car[8].famille = "$Arg1.famille";

  optr->Arg_Car[9].direction = DIR_OUT;
  optr->Arg_Car[9].categorie = VECTOR;
  optr->Arg_Car[9].typ = ATYC_IF32;
  optr->Arg_Car[9].array_dim = "1";
  optr->Arg_Car[9].NbVal = "$Arg2.NbVal";
  optr->Arg_Car[9].type_sample = "$Arg2.type_sample";
  optr->Arg_Car[9].sample = "$Arg2.sample";
  optr->Arg_Car[9].ref_time = "$Arg2.ref_time";
  optr->Arg_Car[9].unite = "$Arg2.unit";
  optr->Arg_Car[9].misval = "$Arg2.misval";
  optr->Arg_Car[9].famille = "$Arg2.famille";
}
