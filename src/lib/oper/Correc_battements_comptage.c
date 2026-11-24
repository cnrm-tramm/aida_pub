/****************************************************
*
* OPERATOR      Correc_battements_comptage.c   FUNCTION  ANSI-C
*
* PURPOSE       Corriger des battements dans l'acquisition de voies de type comptage.
*
* DESCRIPTION   
*              
*             
*            
*           
*          
*         
*        
*       
*      
*
* VERSION       $Revision$
*
* ARGUMENTS   IN   float  Var_in     any        Original data
*             IN   float  Seuil      any        ecart max permis
*             IN   int    Decal      sec/freq   delay between first values
*             OUT  float  Var_out    same as 1  Interpolated data
*
* REFERENCES
*
* CHANGES       
*               This function replace the old "Moy.c" 12/4/1999
*               1.3 followed Categorie definition's change.
*               1.2 added comments/switched arg. orders
*
* COPYRIGHT     Meteo-France
*
*#########################################################################*/

#define _POSIX_SOURCE 1
#define _XOPEN_SOURCE 600

#include <stdio.h>
#include <math.h>
#include <string.h>
#include <limits.h>
#include "struct_oper.h"

/* La vraie fonction... */

long
Correc_battements_comptage (unsigned long NbValIn,
			    const float *Var_in,
			    const float Seuil,
			    float *Var_out,
			    long NbValCor)
{
  long i;
  float Delta_1, Delta_2, ecart, ecart_total;

  /* Réglons immédiatement le cas ou y'a rien a faire : "NbValIn = 0" */
  if (NbValIn == 0)
    return 0;

  for (i = 0; i < NbValIn; i++)
    {
      Var_out[i] = Var_in[i];
    }

  for (i = 0; i < NbValIn - 2; i++)
    {
      Delta_1 = Var_in[i + 1] - Var_in[i];
      Delta_2 = Var_in[i + 2] - Var_in[i];
      if (Delta_1 > 0.0)
	{
	  ecart_total = fabs (Delta_2) + fabs (Delta_1);
	  ecart = (Delta_1 - Delta_2) / 2;
	  if ((ecart_total > 2 * Seuil) && (fabs (ecart) > Seuil))
	    {
	      Var_out[i + 1] = Var_in[i + 1] - ecart;
	      Var_out[i + 2] = Var_in[i + 2] + ecart;
	      NbValCor++;
	    }
	}
    }

  return NbValCor;
}

/* la fonction d'enrobage classique */

int
OP_Correc_battements_comptage (unsigned long NbVal, void *ArgList[], char *DiagExec)
{
  long CodRet;
  long NbValCor;
  int NCar;

  NbValCor = 0;

  NCar = sprintf (DiagExec, "Correc_battements_comptage : (%ld echant.) ", NbVal) ;
  if (NCar < 0)
    NCar = 0;
  DiagExec += NCar;

  CodRet = Correc_battements_comptage (NbVal,
				       (float *) ArgList[0],
				       *((float *) ArgList[1]),
				       (float *) ArgList[2],
				       NbValCor);

  if (CodRet >= 0)
    {
      sprintf (DiagExec, "Nombre de valeurs corrigees : %ld\n", CodRet);
      return OP_OK;
    }
  return OP_FAIL;
}

void
ID_Correc_battements_comptage (oper * optr)
{
  strcpy (optr->Nom, "Correc_battements_comptage");
  optr->Version = "$Revision$";
  optr->Date = "$Date$";
  optr->fctptr = OP_Correc_battements_comptage;
  optr->NbArg = 3;
  optr->misval_auto = 1;	/* On s'en remet au mécanisme automatique.  */
  optr->Arg_Car[0].direction = DIR_IN;
  optr->Arg_Car[0].categorie = VECTOR;
  optr->Arg_Car[0].typ = ATYC_IF32;
  optr->Arg_Car[0].array_dim = "1";
  optr->Arg_Car[0].type_sample = "any";
  optr->Arg_Car[0].sample = "any";
  optr->Arg_Car[0].unite = "any";
  optr->Arg_Car[0].famille = "any";

  optr->Arg_Car[1].direction = DIR_IN;
  optr->Arg_Car[1].categorie = COEFFICIENT;
  optr->Arg_Car[1].array_dim = "1";
  optr->Arg_Car[1].typ = ATYC_IF32;
  optr->Arg_Car[1].unite = "any";
  optr->Arg_Car[1].type_sample = NULL;
  optr->Arg_Car[1].sample = NULL;

  optr->Arg_Car[2].direction = DIR_OUT;
  optr->Arg_Car[2].categorie = VECTOR;
  optr->Arg_Car[2].typ = ATYC_IF32;
  optr->Arg_Car[2].array_dim = "1";
  optr->Arg_Car[2].name = "$Arg1.name";
  optr->Arg_Car[2].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[2].sample = "$Arg1.sample";
  optr->Arg_Car[2].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[2].ref_time = " \"time_\" + $Arg3.sample";
  optr->Arg_Car[2].misval = "$Arg1.misval";
  optr->Arg_Car[2].unite = "$Arg1.unit";
  optr->Arg_Car[2].famille = "$Arg1.famille";

}
