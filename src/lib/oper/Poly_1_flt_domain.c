/******************************************************************
*
* OPERATOR      Poly_1_flt_domain.c   FUNCTION  ANSI-C
*
* PURPOSE       Polynome de 1er degre appliqué à un paramètre Float avec
*               un filtre . Le polynome est calculé uniquement
*               si le parametre Float est dans un domaine de definition, c.a.d 
*               compris entre Val_min et Val_max , sinon Valeur manquante.
*
* DESCRIPTION   Standard calculation.... 
*
* VERSION       1.1
*
* ARGUMENTS   IN   float  Var_in     Any          "X" value
*             IN   float  Coef_0     Any          Constant coefficient
*             IN   float  Coef_1     Any          coefficient of X
*             IN   float  Borne_min		  Borne/Valeur Mini pour Var_in
*             IN   float  Borne_max		  Borne/Valeur Maxi pour Var_in
*             IN   string unit_out                Unit of the result
*             IN   string name_out                Name of the result
*             IN   string en_name_out             English name of the result
*             OUT  float  Var_out  same as 2      Result
*
* ENTRY
*
* SUBPROGRAMS   none
*
* FILES
*
* REFERENCES
*
* CHANGES       1
*
* COPYRIGHT     Meteo-France
*
* AGREEMENT     The author wishes that .....
*#########################################################################*/

#define _POSIX_SOURCE 1
#define _XOPEN_SOURCE 600

#include <stdio.h>
#include <string.h>
#include "struct_oper.h"

/* La vraie fonction... */
unsigned long
Poly_1_flt_domain (unsigned long NLoop,
		   const float *Var_in,
		   const float Coef_0,
		   const float Coef_1,
		   const float Borne_min,
		   const float Borne_max, float *Var_out)
{
  unsigned long i;

  for (i = 0; i < NLoop; i++)
    {
      if ((Var_in[i] < Borne_max) || (Var_in[i] > Borne_min))
	Var_out[i] = Coef_0 + Var_in[i] * Coef_1;
      /* Relecture du 2013-07-11 : 
       *  1) la condition est étrange, on aurait attendu :
       *     if ((Var_in[i] <= Borne_max) && (Var_in[i] >= Borne_min))
       *  2) L'absence d'un "else Var_out[i] = k_NaN;" est surprenante
       * Mais on laisse en l'état, pour compatibilité historique. 
       */
    }
  return i;
}


/* la fonction d'enrobage classique */

int
OP_Poly_1_flt_domain (unsigned long NbVal, void *ArgList[], char *DiagExec)
{
  unsigned long CodRet;

  (void) sprintf (DiagExec, 
                 "Poly_1_flt_domain(%lu ech.), y=%g+%g*x, pour x entre %g et %g, unite = %s)\n",
                  NbVal, *((float *) ArgList[1]), 
                  *((float *) ArgList[2]),
                  *((float *) ArgList[3]),
                  *((float *) ArgList[4]),
                  (char *) ArgList[5]	/*,
	(char *) ArgList[6],
	(char *) ArgList[7] */ );

/*
 * Le lecteur attentif aura remarqué que les arguments Nr 5, 6, 7
 * ne sont pas passés à la routine de calcul. En fait, ils ne servent
 * qu'à remplir le champ "unit", "name", "english_name" du vecteur de sortie.
 */
  CodRet = Poly_1_flt_domain (NbVal,
			      (float *) ArgList[0],
			      *((float *) ArgList[1]),
			      *((float *) ArgList[2]),
			      *((float *) ArgList[3]),
			      *((float *) ArgList[4]), (float *) ArgList[8]);
  if (CodRet == NbVal)
    return OP_OK;
  else
    return OP_FAIL;
}

/* la fonction de description de l'operateur et ses arguments */

void
ID_Poly_1_flt_domain (oper * optr)
{
  strcpy (optr->Nom, "Poly_1_flt_domain");
  optr->Version = "$Revision$";
  optr->Date = "$Date$";
  optr->fctptr = OP_Poly_1_flt_domain;
  optr->NbArg = 9;

  /* Var_in */
  optr->Arg_Car[0].direction = DIR_IN;
  optr->Arg_Car[0].categorie = VECTOR;
  optr->Arg_Car[0].typ = ATYC_IF32;
  optr->Arg_Car[0].array_dim = "1";
  optr->Arg_Car[0].type_sample = "any";
  optr->Arg_Car[0].sample = "any";
  optr->Arg_Car[0].unite = "any";

  /* Coef_0 */
  optr->Arg_Car[1].direction = DIR_IN;
  optr->Arg_Car[1].categorie = COEFFICIENT;
  optr->Arg_Car[1].array_dim = "1";
  optr->Arg_Car[1].typ = ATYC_IF32;
  optr->Arg_Car[1].unite = "any";

  /* Coef_0 */
  optr->Arg_Car[2].direction = DIR_IN;
  optr->Arg_Car[2].categorie = COEFFICIENT;
  optr->Arg_Car[2].array_dim = "1";
  optr->Arg_Car[2].typ = ATYC_IF32;
  optr->Arg_Car[2].unite = "any";

  /* Borne_min */
  optr->Arg_Car[3].direction = DIR_IN;
  optr->Arg_Car[3].categorie = COEFFICIENT;
  optr->Arg_Car[3].array_dim = "1";
  optr->Arg_Car[3].typ = ATYC_IF32;
  optr->Arg_Car[3].unite = "any";

  /* Borne_max */
  optr->Arg_Car[4].direction = DIR_IN;
  optr->Arg_Car[4].categorie = COEFFICIENT;
  optr->Arg_Car[4].array_dim = "1";
  optr->Arg_Car[4].typ = ATYC_IF32;
  optr->Arg_Car[4].unite = "any";

  optr->Arg_Car[5].direction = DIR_IN;	/* Unite du resultat */
  optr->Arg_Car[5].categorie = COEFFICIENT;
  optr->Arg_Car[5].array_dim = "1";
  optr->Arg_Car[5].typ = ATYC_STRING;

  optr->Arg_Car[6].direction = DIR_IN;	/* Nom du resultat: champ Name pour le vecteur en sortie */
  optr->Arg_Car[6].categorie = COEFFICIENT;
  optr->Arg_Car[6].array_dim = "1";
  optr->Arg_Car[6].typ = ATYC_STRING;
  optr->Arg_Car[6].unite = "any";

  optr->Arg_Car[7].direction = DIR_IN;	/* English Name du resultat : Champ English_Name ... */
  optr->Arg_Car[7].categorie = COEFFICIENT;
  optr->Arg_Car[7].array_dim = "1";
  optr->Arg_Car[7].typ = ATYC_STRING;
  optr->Arg_Car[7].unite = "any";

  /* Var_out */
  optr->Arg_Car[8].direction = DIR_OUT;
  optr->Arg_Car[8].categorie = VECTOR;
  optr->Arg_Car[8].typ = ATYC_IF32;
  optr->Arg_Car[8].array_dim = "1";
  optr->Arg_Car[8].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[8].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[8].sample = "$Arg1.sample";
  optr->Arg_Car[8].ref_time = "$Arg1.ref_time";
  optr->Arg_Car[8].misval = "$Arg1.misval";
  optr->Arg_Car[8].unite = "$Arg6";
  optr->Arg_Car[8].name = "$Arg7";
  optr->Arg_Car[8].en_name = "$Arg8";
  optr->Arg_Car[8].famille = " \"auto\" ";
}
