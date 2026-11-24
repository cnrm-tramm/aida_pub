/*************************************************************************
*
* OPERATOR         Complete_X_avec_Y_dbl.c  FUNCTION ANSI-C
*
* PURPOSE          Complete le vecteur X avec le vecteur Y :
* 		   Fabrication d'un vecteur ou les valeurs sont soit les siennes,
*                  soit celles d'un deuxieme vecteur si le premier vecteur est
*                  une valeur manquante. On cree un flag : flag=1 si on
*                  prend une valeur du vecteur 1, flag=2 si on prend une valeur
*                  du vecteur 2.
*
* DESCRIPTION      on cree un vecteur contenant les valeurs du vecteur 1 si elles
*                  ne sont pas manquantes, sinon on prend les valeurs du vecteur 2.
*		   
* VERSION          1.0 
*
* ARGUMENTS  
*            IN   double   vect1        Vecteur sur lequel on appliquera le test (valeur manquante?)
*            IN   double   vect2       	Vecteur sur lequel on prend les donnees pour completer si besoin.
*            IN   double   valmnq1      Valeur manquante du vecteur 1
*            OUT  float   flag    	Flag (1=vect1 , 2=vect2)
*            OUT  double   new_vect1    Vecteur contenant les nouvelles données de vect1
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
Complete_X_avec_Y_dbl (unsigned long ndata,
		   const double *vect1,
		   const double *vect2,
		   const float valmnq1, float *flag, double *new_vect1)
{
  unsigned long i;
  unsigned long nb_mnq = 0;

  for (i = 0; i < ndata; i++)
    {
      new_vect1[i] = K_NaN;

      if ((!isfinite (vect1[i])) || (vect1[i] == valmnq1))
	{
	  /* Si vect1[i] est manquant, on remplace par les valeurs de vect2 */
	  new_vect1[i] = vect2[i];
	  flag[i] = 2;
	  nb_mnq++;
	}
      else
	{
	  /* Si vect1[i] est present, on garde les valeurs de vect1 */
	  new_vect1[i] = vect1[i];
	  flag[i] = 1;
	}
    }

  return nb_mnq;
}


/* la fonction d'enrobage classique */
#include <string.h>
#include <stdio.h>

int
OP_Complete_X_avec_Y_dbl (unsigned long NbVal, void *ArgList[], char *DiagExec)
{
  unsigned long CodRet;
  sprintf (DiagExec, "Complete_X_avec_Y_dbl, %lu ech", NbVal);
  CodRet = Complete_X_avec_Y_dbl (NbVal,
			      (double *) ArgList[0],
			      (double *) ArgList[1],
			      *(double *) ArgList[2],
			      (float *) ArgList[3], (double *) ArgList[4]);

  sprintf (DiagExec + strlen (DiagExec), ", %lu val remplacees", CodRet);
  return OP_OK;
}

void
ID_Complete_X_avec_Y_dbl (oper * optr)
{
  strcpy (optr->Nom, "Complete_X_avec_Y_dbl");
  optr->Version = "$Revision:$";
  optr->Date = "$Date:";
  optr->fctptr = OP_Complete_X_avec_Y_dbl;
  optr->NbArg = 5;

  /* vect_1 */
  optr->Arg_Car[0].direction = DIR_IN;
  optr->Arg_Car[0].categorie = VECTOR;
  optr->Arg_Car[0].typ = ATYC_IF64;
  optr->Arg_Car[0].array_dim = "1";
  optr->Arg_Car[0].type_sample = "any";
  optr->Arg_Car[0].sample = "any";
  optr->Arg_Car[0].unite = "any";

  /* vect_2 */
  optr->Arg_Car[1].direction = DIR_IN;
  optr->Arg_Car[1].categorie = VECTOR;
  optr->Arg_Car[1].typ = ATYC_IF64;
  optr->Arg_Car[1].array_dim = "1";
  optr->Arg_Car[1].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[1].type_sample = "any";
  optr->Arg_Car[1].sample = "any";
  optr->Arg_Car[1].unite = "any";

  optr->Arg_Car[2].direction = DIR_IN;
  optr->Arg_Car[2].categorie = COEFFICIENT;
  optr->Arg_Car[2].typ = ATYC_IF64;
  optr->Arg_Car[2].array_dim = "1";
  optr->Arg_Car[2].type_sample = NULL;
  optr->Arg_Car[2].sample = NULL;
  optr->Arg_Car[2].unite = "";

  /* flag  */
  optr->Arg_Car[3].direction = DIR_OUT;
  optr->Arg_Car[3].categorie = VECTOR;
  optr->Arg_Car[3].typ = ATYC_IF32;
  optr->Arg_Car[3].array_dim = "1";
  optr->Arg_Car[3].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[3].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[3].sample = "$Arg1.sample";
  optr->Arg_Car[3].ref_time = "$Arg1.ref_time";
  optr->Arg_Car[3].unite = "$Arg1.unit";
  optr->Arg_Car[3].misval = "$Arg1.misval";
  optr->Arg_Car[3].famille = "\"controle\"";

  /* new_vect1  */
  optr->Arg_Car[4].direction = DIR_OUT;
  optr->Arg_Car[4].categorie = VECTOR;
  optr->Arg_Car[4].typ = ATYC_IF64;
  optr->Arg_Car[4].array_dim = "1";
  optr->Arg_Car[4].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[4].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[4].sample = "$Arg1.sample";
  optr->Arg_Car[4].ref_time = "$Arg1.ref_time";
  optr->Arg_Car[4].unite = "$Arg1.unit";
  optr->Arg_Car[4].misval = "$Arg1.misval";
  optr->Arg_Car[4].famille = "$Arg1.famille";
}
