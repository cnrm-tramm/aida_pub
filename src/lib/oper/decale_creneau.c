/*************************************************************************
*
* OPERATOR         decale_creneau.c  FUNCTION ANSI-C
*
* PURPOSE          Decale dans les temps les flancs montants ou descendants 
*                  de créneaux.
*
* DESCRIPTION      
*
*
* VERSION          $Revision$
*
* ARGUMENTS  
*            IN   float   X		vecteur d'origine
*            IN   double  time		datation de X
*            IN   float   seuil         Seuil
*            IN   float   decal_down    Décalage à appliquer aux flancs descendants.
*            IN   float   decal_up      Décalage à appliquer aux flancs montants.
*
*            OUT  float   Y             Résultat.
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

static void
process_up (unsigned long i,
	    const float *X,
	    const double *time,
	    double time_last_down, float last_down, double decal_up, float *Y)
{
  if (time[i] - time_last_down < decal_up)
    {
      Y[i] = last_down;
    }
  else
    {
      Y[i] = X[i];
    }
}

static void
process_down (unsigned long i,
	      const float *X,
	      const double *time,
	      double time_last_up, float last_up, double decal_down, float *Y)
{
  if (time[i] - time_last_up < decal_down)
    {
      Y[i] = last_up;
    }
  else
    {
      Y[i] = X[i];
    }
}

void
decale_creneau (unsigned long ndata,
		const float *X,
		const double *time,
		float seuil, float decal_down, float decal_up, float *Y)
{
  unsigned long i;
  double time_last_up;
  double time_last_down;
  float last_up;
  float last_down;

  typedef enum
  {
    e_inco,
    e_up,
    e_down
  } etat_t;
  etat_t etat = e_inco;

  time_last_up = K_NaN;
  time_last_down = K_NaN;
  last_up = K_NaN;
  last_down = K_NaN;


  for (i = 0; i < ndata; i++)
    {
      switch (etat)
	{
	case e_inco:
	  if (X[i] >= seuil)
	    {
	      etat = e_up;
	      last_up = X[i];
	      time_last_up = time[i];
	      Y[i] = X[i];
	    }
	  else if (X[i] < seuil)
	    {
	      etat = e_down;
	      last_down = X[i];
	      time_last_down = time[i];
	      Y[i] = X[i];
	    }
	  else
	    {			/* reste dans l'état inconnu. */
	      Y[i] = X[i];
	    }
	case e_up:
	  if (X[i] >= seuil)
	    {
	      process_up (i, X, time, time_last_down, last_down, decal_up, Y);
	      last_up = X[i];
	      time_last_up = time[i];
	    }
	  else if (X[i] < seuil)
	    {
	      etat = e_down;
	      process_down (i, X, time, time_last_up, last_up, decal_down, Y);
	      last_down = X[i];
	      time_last_down = time[i];
	    }
	  else
	    {
	      etat = e_inco;
	      Y[i] = X[i];
	    }
	case e_down:
	  if (X[i] >= seuil)
	    {
	      etat = e_up;
	      process_up (i, X, time, time_last_down, last_down, decal_up, Y);
	      last_up = X[i];
	      time_last_up = time[i];
	    }
	  else if (X[i] < seuil)
	    {
	      process_down (i, X, time, time_last_up, last_up, decal_down, Y);
	      last_down = X[i];
	      time_last_down = time[i];
	    }
	  else
	    {
	      etat = e_inco;
	      Y[i] = X[i];
	    }
	}
    }

  return;
}


/* la fonction d'enrobage classique */
#include <string.h>
#include <stdio.h>

int
OP_decale_creneau (unsigned long NbVal, void *ArgList[], char *DiagExec)
{
  sprintf (DiagExec,
	   "decale_creneau, %lu ech, seuil=%f, decal(descendant)=%f, decal(montant)=%f ",
	   NbVal, *(float *) ArgList[2], *(float *) ArgList[3],
	   *(float *) ArgList[4]);

  decale_creneau (NbVal, (float *) ArgList[0], (double *) ArgList[1],
		  *(float *) ArgList[2], *(float *) ArgList[3],
		  *(float *) ArgList[4], (float *) ArgList[5]);

  return OP_OK;
}

void
ID_decale_creneau (oper * optr)
{
  strcpy (optr->Nom, "decale_creneau");
  optr->Version = "$Revision$";
  optr->Date = "$Date$";
  optr->fctptr = OP_decale_creneau;
  optr->NbArg = 6;		/* doit rester inf. a FIL_MAX_ARG */

  /* X */
  optr->Arg_Car[0].direction = DIR_IN;
  optr->Arg_Car[0].categorie = VECTOR;
  optr->Arg_Car[0].typ = ATYC_IF32;
  optr->Arg_Car[0].array_dim = "1";
  optr->Arg_Car[0].type_sample = "any";
  optr->Arg_Car[0].sample = "any";
  optr->Arg_Car[0].unite = "any";

  /* time */
  optr->Arg_Car[1].direction = DIR_IN;
  optr->Arg_Car[1].categorie = VECTOR;
  optr->Arg_Car[1].typ = ATYC_IF64;
  optr->Arg_Car[1].array_dim = "1";
  optr->Arg_Car[1].type_sample = "any";
  optr->Arg_Car[1].sample = "any";
  optr->Arg_Car[1].unite = "any";

  /* seuil */
  optr->Arg_Car[2].direction = DIR_IN;
  optr->Arg_Car[2].categorie = COEFFICIENT;
  optr->Arg_Car[2].typ = ATYC_IF32;
  optr->Arg_Car[2].array_dim = "1";
  optr->Arg_Car[2].unite = "";

  /* decal_down */
  optr->Arg_Car[3].direction = DIR_IN;
  optr->Arg_Car[3].categorie = COEFFICIENT;
  optr->Arg_Car[3].typ = ATYC_IF32;
  optr->Arg_Car[3].array_dim = "1";
  optr->Arg_Car[3].unite = "";

  /* decal_up */
  optr->Arg_Car[4].direction = DIR_IN;
  optr->Arg_Car[4].categorie = COEFFICIENT;
  optr->Arg_Car[4].typ = ATYC_IF32;
  optr->Arg_Car[4].array_dim = "1";
  optr->Arg_Car[4].unite = "";

  /* Y */
  optr->Arg_Car[5].direction = DIR_OUT;
  optr->Arg_Car[5].categorie = VECTOR;
  optr->Arg_Car[5].typ = ATYC_IF32;
  optr->Arg_Car[5].array_dim = "1";
  optr->Arg_Car[5].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[5].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[5].sample = "$Arg1.sample";
  optr->Arg_Car[5].ref_time = "$Arg1.ref_time";
  optr->Arg_Car[5].unite = "$Arg1.unit";
  optr->Arg_Car[5].misval = "$Arg1.misval";
  optr->Arg_Car[5].famille = "$Arg1.famille";
  optr->Arg_Car[5].name = "$Arg1.name + \" dont les creneaux sont decales\"";
  optr->Arg_Car[5].en_name = "$Arg1.english_name";
}
