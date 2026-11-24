/*************************************************************************
*
* OPERATOR         Oliver_lisse.c  FUNCTION ANSI-C
*
* PURPOSE          opérateur de lissage de données
*
* DESCRIPTION      on lisse les données selon une méthode fournie par Olivier
*                  Traullé à savoir:
*                  On remplace chaque valeur par une moyenne pondérée des n
*                  dernières valeurs en affectant à chaque valeur un poids
*                  inversement proportionnel à son éloignement
*                   
*
*
* VERSION          1.0 
*
* ARGUMENTS  
*            IN   float   vect		vecteur de données quelconque
*            IN   float   pas           nombre de valeurs entrant dans la moyenne          
*            OUT  float   liss_vect   vecteur contenant les données lissées
*            
*            
*
* ENTRY        NONE
*        
* SUBPROGRAMS  NONE
*        
* REFERENCES   Olivier Traullé / GMEI /4M
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





int
Oliver_lisse(unsigned long ndata,
	  const float *vect,
	  const float pas,	  
	  float *liss_vect
	  )
	  
{
  unsigned long i,j;
  float tempo,somme;
  
  for (i = 0; i < ndata; i++)
    {
       tempo = 0.0;
       somme = 0.0;
       
       if (i < pas) 
          {
             liss_vect[i] = tempo / somme;
             continue;
	  }
       else 
       {
          for ( j = 0 ; j<pas ; ++j)
             {
                if (!isfinite(vect[i-j]))
	           { 
	              tempo = 0.0;
                      somme = 0.0;
	     	      break; 
	           }
                else
                   {
		      tempo += (pas-j)*vect[i-j];
		      somme += pas-j;
	           }
             }
           liss_vect[i] = tempo / somme;
	}
    }
  
  return 0;
}


/* la fonction d'enrobage classique */

int
OP_Oliver_lisse(unsigned long NbVal, void *ArgList[], char *DiagExec)
{
  
  sprintf (DiagExec, "OP_Oliver_lisse");
  Oliver_lisse(NbVal,
		     (float *) ArgList[0],
		     *(float *) ArgList[1],
		     (float *) ArgList[2] );
  	     
  return OP_OK;
  
}

void
ID_Oliver_lisse(oper * optr)
{
  strcpy (optr->Nom, "Oliver_lisse");
  optr->Version = "1.0";
  optr->Date = "25/04/00";
  optr->fctptr = OP_Oliver_lisse;
  optr->NbArg = 3;		/* doit rester inf. a FIL_MAX_ARG */

  optr->Arg_Car[0].direction = DIR_IN;
  optr->Arg_Car[0].categorie = VECTOR;
  optr->Arg_Car[0].typ = ATYC_IF32;
  optr->Arg_Car[0].array_dim = "1";
  optr->Arg_Car[0].type_sample = "any";
  optr->Arg_Car[0].sample ="any";
  optr->Arg_Car[0].unite = "any";
  
  optr->Arg_Car[1].direction = DIR_IN;
  optr->Arg_Car[1].categorie = COEFFICIENT;
  optr->Arg_Car[1].typ = ATYC_IF32;
  optr->Arg_Car[1].array_dim = "1";
  optr->Arg_Car[1].type_sample = NULL;
  optr->Arg_Car[1].sample = NULL;
  optr->Arg_Car[1].unite = "";
  
  optr->Arg_Car[2].direction = DIR_OUT;
  optr->Arg_Car[2].categorie = VECTOR;
  optr->Arg_Car[2].typ = ATYC_IF32;
  optr->Arg_Car[2].array_dim = "1";
  optr->Arg_Car[2].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[2].type_sample ="$Arg1.type_sample";
  optr->Arg_Car[2].sample = "$Arg1.sample";
  optr->Arg_Car[2].ref_time = "$Arg1.ref_time";
  optr->Arg_Car[2].unite ="$Arg1.unit";
  optr->Arg_Car[2].misval = "$Arg1.misval";
}
