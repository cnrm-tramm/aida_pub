/*************************************************************************
*
* OPERATOR         select_sur_vect.c  FUNCTION ANSI-C
*
* PURPOSE          Fabrication d'un vecteur contenant : 
*                     - Soit les valeurs d'un premier vecteurs, si elles satisfont a 
*                     un test dont les critères sont passés en argument,
*                     - soit celles d'un deuxieme vecteur.
*
* DESCRIPTION      Les données de vect1 sont remplacées par les donnees de vect2 
*                  si les données de vect1 ne sont pas comprises entre crit1_min 
*                  et crit1_max.
*		   On peut ne renseigner qu'un seul critère, dans cas on passe
*	  	   pour les critères non renseignés la valeur Nan (0.0/0.0). 	
*	  	   Idem si la donnee de vect1 est manquante.
*		   
* VERSION          1.0 
*
* ARGUMENTS  
*            IN   float   vect1         Vecteur sur lequel on appliquera le test
*            IN   float   vect2	       	Vecteur sur lequel on prend les donnees si besoin.
*            IN   float   crit1_min     Borne min du premier test.
*            IN   float   crit1_max    	Borne max du premier test.
*            OUT  float   new_vect1     Vecteur contenant les nouvelles données de vect1
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

unsigned long
select_sur_vect (unsigned long ndata,
		 const float *vect1,
		 const float *vect2,
		 float crit1_min,
                 float crit1_max, float *new_vect1)
{
  unsigned long i;
  unsigned long nb_rempla = 0;

  for (i = 0; i < ndata; i++)
    {
      new_vect1[i] = K_NaN;

      if (!isfinite (vect2[i]))
	continue;
      /* Si vect2[i] est manquant, les valeurs correspondantes de vect1
       * en sortie le seront aussi. */
      if (vect1[i] >= crit1_min && vect1[i] <= crit1_max)
	new_vect1[i] = vect1[i];
      else
	{
	  new_vect1[i] = vect2[i];
	  nb_rempla++;
	}
      if (!isfinite (vect1[i]))
	{
	  new_vect1[i] = vect2[i];
	  nb_rempla++;
	}
    }

  return nb_rempla;
}


/* la fonction d'enrobage classique */
#include <string.h>
#include <stdio.h>

int
OP_select_sur_vect (unsigned long NbVal, void *ArgList[], char *DiagExec)
{
  int NCar;
  unsigned long CodRet;

  NCar = sprintf (DiagExec, "select_sur_vect, selection entre %g et %g",
		  *(float *) ArgList[2], *(float *) ArgList[3]);
  if (NCar > 0)
    {
      DiagExec += NCar;
    }

  CodRet =
    select_sur_vect (NbVal, (float *) ArgList[0], (float *) ArgList[1],
		     *(float *) ArgList[2], *(float *) ArgList[3],
		     (float *) ArgList[4]);

  sprintf (DiagExec, ", rempla = %lu (/%lu)", CodRet, NbVal);
  return OP_OK;
}

void
ID_select_sur_vect (oper * optr)
{
  strcpy (optr->Nom, "select_sur_vect");
  optr->Version = "$Revision$";
  optr->Date = "$Date$";
  optr->fctptr = OP_select_sur_vect;
  optr->NbArg = 5;

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
  /* vect1 et vect2 doivent être synchrones, 
   * ou au moins avoir le meme nombre d'echantillons. */
  optr->Arg_Car[1].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[1].type_sample = "any";
  optr->Arg_Car[1].sample = "any";
  optr->Arg_Car[1].unite = "any";

  optr->Arg_Car[2].direction = DIR_IN;
  optr->Arg_Car[2].categorie = COEFFICIENT;
  optr->Arg_Car[2].typ = ATYC_IF32;
  optr->Arg_Car[2].array_dim = "1";
  optr->Arg_Car[2].unite = "";

  optr->Arg_Car[3].direction = DIR_IN;
  optr->Arg_Car[3].categorie = COEFFICIENT;
  optr->Arg_Car[3].typ = ATYC_IF32;
  optr->Arg_Car[3].array_dim = "1";
  optr->Arg_Car[3].unite = "";

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

}
