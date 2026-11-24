/*************************************************************************************
*
* OPERATOR       Poly_exp_domain.c   FUNCTION  ANSI-C
*
* PURPOSE        Fonction exponentielle polynomiale dans un domaine de définition
*
* DESCRIPTION    Idem Poly_exp mais avec test sur la variable en entree (? domaine ou pas)
* 		 --> Si la variable en entree n'est pas dans le domaine de définition
* 		 (inf < variable < max) alors en sortie --> valeur manquante
* 		 --> Si la variable en entree est dans le domaine de définition
* 		 alors --> Fonction exponentielle polynomiale
*
*                  L'unite du vecteur en sortie fait partie des arguments d'entree (9ième arg)
*
* VERSION        1.1
*
* ARGUMENTS    IN    float   Var_In    any     La variable d'entree
*              IN    float   coef_a            coef_a
*              IN    float   coef_b            coef_b
*              IN    float   coef_c            coef_c
*              IN    float   coef_d            coef_d
*              IN    float   coef_e            coef_e
*              IN    float   Borne_min         Borne/valeur Mini pour Var_In
*              IN    float   Borne_max         Borne/valeur Maxi pour Var_In
*              IN    char*   unit              unite en sortie 
*              OUT   float   Var_Out           Le resultat
*          
* ENTRY        
*          
* SUBPROGRAMS    
*
* FILES     
*
* REFERENCES 
*
* CHANGES        1.1 Initial release
*
* COPYRIGHT      Meteo-France
*
* AGREEMENT      The author wishes that .....
*#########################################################################*/

#define _POSIX_SOURCE 1
#define _XOPEN_SOURCE 600

#include <math.h>
#include <stdio.h>
#include <string.h>
#include "struct_oper.h"

/* Convention pour CR_tab :
 *  0 : nb_elt
 *  1 : nb_sup_borne_max
 *  2 : nb_inf_borne_sup
 */
typedef enum {idx_compte_tot, idx_compte_inf_borne, idx_compte_sup_borne}idx_CR;

void
Poly_exp_domain (const unsigned long NLoop,
                 float *Var_In,	/* Variable d'entree */
		 const double coef_a,
                 const double coef_b,
                 const double coef_c,
                 const double coef_d,
                 const double coef_e,
                 const double Borne_min,
                 const double Borne_max,
                 unsigned long *CR_tab,
                 float *Var_Out)/* Variable resultat */
{
  unsigned long i;
  double Var_Y;
  const float misval_out = K_NaN;

  CR_tab[idx_compte_inf_borne] = 0;
  CR_tab[idx_compte_sup_borne] = 0;
  for (i = 0; i < NLoop; i++)
    {
      if (Var_In[i] < Borne_max)
	{
	  if (Var_In[i] > Borne_min)
	    {
	      /* Variable Var_Y : variable intermédiaire qui sera ensuite portée puissance e */
	      Var_Y = coef_e + Var_In[i] * (coef_d + Var_In[i] * coef_c);
	      Var_Out[i] = coef_a + (coef_b * exp (Var_Y));
	    }
	  else
	    {
              CR_tab[idx_compte_inf_borne] += 1;
	      Var_Out[i] = misval_out;	/* Cas ou Var_In < Borne_min */
	    }
	}
      else
	{
          CR_tab[idx_compte_sup_borne] += 1;
	  Var_Out[i] = misval_out;	/* Cas ou Var_In > Borne_max */
	}
    }
  CR_tab[idx_compte_tot] = i;
  return;
}

/* la fonction d'enrobage classique */

int
OP_Poly_exp_domain (unsigned long NbVal, void *ArgList[], char *DiagExec)
{
  unsigned long CR_tab[3];
  int NCar;

  NCar = sprintf (DiagExec,
           "Poly_exp_domain, NbVal=%lu, calcul pour x entre %g et %g",
           NbVal,
	    *((double *) ArgList[6]),
	    *((double *) ArgList[7]));
  if (NCar > 0)
    DiagExec += NCar;

  Poly_exp_domain (NbVal,
		    (float *) ArgList[0],
		    *((double *) ArgList[1]),
		    *((double *) ArgList[2]),
		    *((double *) ArgList[3]),
		    *((double *) ArgList[4]),
		    *((double *) ArgList[5]),
		    *((double *) ArgList[6]),
		    *((double *) ArgList[7]),
		    CR_tab, (float *) ArgList[9]);

  sprintf (DiagExec,
	   " %lu valeurs, %lu calculées, %lu < %g, %lu > %g",
	   NbVal, CR_tab[idx_compte_tot],
           CR_tab[idx_compte_inf_borne], *((double *) ArgList[6]),
           CR_tab[idx_compte_sup_borne], *((double *) ArgList[7]));

  return OP_OK;
}

void
ID_Poly_exp_domain (oper * optr)
{
  strcpy (optr->Nom, "Poly_exp_domain");
  optr->Version = "$Revision$";
  optr->Date = "$Date$";
  optr->fctptr = OP_Poly_exp_domain;
  optr->NbArg = 10;

  /* Var_In */
  optr->Arg_Car[0].direction = DIR_IN;
  optr->Arg_Car[0].categorie = VECTOR;
  optr->Arg_Car[0].typ = ATYC_IF32;
  optr->Arg_Car[0].array_dim = "1";
  optr->Arg_Car[0].type_sample = "any";
  optr->Arg_Car[0].sample = "any";
  optr->Arg_Car[0].unite = "";
  optr->Arg_Car[0].famille = "any";

  /* coef_a */
  optr->Arg_Car[1].direction = DIR_IN;
  optr->Arg_Car[1].categorie = COEFFICIENT;
  optr->Arg_Car[1].typ = ATYC_IF64;
  optr->Arg_Car[1].array_dim = "1";
  optr->Arg_Car[1].unite = "";

  /* coef_b */
  optr->Arg_Car[2].direction = DIR_IN;
  optr->Arg_Car[2].categorie = COEFFICIENT;
  optr->Arg_Car[2].typ = ATYC_IF64;
  optr->Arg_Car[2].array_dim = "1";
  optr->Arg_Car[2].unite = "";

  /* coef_c */
  optr->Arg_Car[3].direction = DIR_IN;
  optr->Arg_Car[3].categorie = COEFFICIENT;
  optr->Arg_Car[3].typ = ATYC_IF64;
  optr->Arg_Car[3].array_dim = "1";
  optr->Arg_Car[3].unite = "";

  /* coef_d */
  optr->Arg_Car[4].direction = DIR_IN;
  optr->Arg_Car[4].categorie = COEFFICIENT;
  optr->Arg_Car[4].typ = ATYC_IF64;
  optr->Arg_Car[4].array_dim = "1";
  optr->Arg_Car[4].unite = "";

  /* coef_e */
  optr->Arg_Car[5].direction = DIR_IN;
  optr->Arg_Car[5].categorie = COEFFICIENT;
  optr->Arg_Car[5].typ = ATYC_IF64;
  optr->Arg_Car[5].array_dim = "1";
  optr->Arg_Car[5].unite = "";

  /* Borne_max */
  optr->Arg_Car[6].direction = DIR_IN;
  optr->Arg_Car[6].categorie = COEFFICIENT;
  optr->Arg_Car[6].typ = ATYC_IF64;
  optr->Arg_Car[6].array_dim = "1";
  optr->Arg_Car[6].unite = "";

  /* Borne_max */
  optr->Arg_Car[7].direction = DIR_IN;
  optr->Arg_Car[7].categorie = COEFFICIENT;
  optr->Arg_Car[7].typ = ATYC_IF64;
  optr->Arg_Car[7].array_dim = "1";
  optr->Arg_Car[7].unite = "";

  optr->Arg_Car[8].direction = DIR_IN;
  optr->Arg_Car[8].categorie = COEFFICIENT;
  optr->Arg_Car[8].typ = ATYC_STRING;
  optr->Arg_Car[8].array_dim = "1";
  optr->Arg_Car[8].unite = "";

  /* Var_Out */
  optr->Arg_Car[9].direction = DIR_OUT;
  optr->Arg_Car[9].categorie = VECTOR;
  optr->Arg_Car[9].typ = ATYC_IF32;
  optr->Arg_Car[9].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[9].ref_time = "$Arg1.ref_time";
  optr->Arg_Car[9].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[9].sample = "$Arg1.sample";
  /* l'unite est obligatoirement l'unite donnee en 9ime argument  */
  optr->Arg_Car[9].unite = "$Arg9";
  optr->Arg_Car[9].famille = "$Arg1.famille";
}
