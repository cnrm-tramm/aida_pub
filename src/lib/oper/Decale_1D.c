/****************************************************
*
* OPERATOR      Decale_1D.c   FUNCTION  ANSI-C
*
* PURPOSE       Shifting of a 1D parameter
*
* DESCRIPTION   Routine de decalage temporel d'une
*		d'un parametre.  
*		Le parametre decale est calcule par
*		interpolation lineaire du parametre
*		initial.
*		Si le decalage est multiple de la 
*		periode d'echantillonnage alors cela
*		revient a un simple decalage des 
*		valeurs du tableau. Dans ce cas, cet
*		operateur peut s'appliquer a un parametre
*		discret (comptage par ex) et continu. 
*		Sinon on ne peut l'appliquer qu'a un 
*		parametre continu (interpolation 
*		lineaire) !!!  
*	
*			decal > 0 on retarde 
*			decal < 0 on avance 
*
* VERSION       $Revision$
*
* ARGUMENTS   IN   float  X     	any     Original data
*	      IN   float  NbCol		any	Number of element 
*	      					in 1 sample 
*             IN   double  fr    	Hz   	sample frequency of X
*             IN   int    decal      	sec   	delay 
*             OUT  float  X_decal   same as X	Shifting data
*
* REFERENCES
*
* CHANGES       
*
* COPYRIGHT     Meteo-France
*
*#########################################################################*/

#define _POSIX_SOURCE 1
#define _XOPEN_SOURCE 600
/* Le #define _HPUX_SOURCE n'est la que pour "voir" strdup */
#define _HPUX_SOURCE 1
#define _XOPEN_SOURCE_EXTENDED 1

#include <stdio.h>
#include <math.h>
#include <string.h>
#include "struct_oper.h"

/* La fonction */

int
Decale_1D (unsigned long Nbval,
	   short *X, int NbCol, double fr, float decal, short *X_decal)
{
  unsigned long i;
  int k;
  unsigned long borne_inf, borne_sup;

  int I;
  float Z, F;
  double s, D;

  if (NbCol < 0)
    {
      return -1;
    }

  if (fr < 0.0)
    {
      return -2;
    }

  /* Cas facile où il n'y a rien à faire. */
  if (Nbval == 0)
    {
      return 0;
    }

  s = 1.E-4; /** precision du temps **/

  /* seance de gymnastique pour s'affranchir
     de la precision du float.
     On considere que la precision de "decal" 
     vaut "s" et on arrondit a "s" pret. */

  if (modf (decal / s, &D) > 0.5)
    D = D + 1.;
  D = D * s;

  /** on multiplie decal par -1 pour avoir :
	decal > 0 on retarde 
	decal < 0 on avance 
  **/
  Z = -1. * D * fr;

  I = (int) (floor (Z));
  F = Z - (float) I;

  if (F == 1.)
    {
      I = I + 1;
      F = 0.;
    }

/** Avertissement **/
  if (F != 0.)
    {
      fprintf (stderr,
	       " *** ATTENTION : la valeur du decalage temporel (%g s)\n ",
	       decal);
      fprintf (stderr,
	       " n'est pas multiple de la periode d'echantillonnage !\n");
      fprintf (stderr, " L'operateur procede par interpolation lineaire.\n");
      fprintf (stderr, " => Lissage inevitable du signal original !!! \n");
    }
  fprintf (stderr, " Formule utilisee : \n");
  fprintf (stderr, " X_decal[i] = X[i+%d] + %f.(X[i+%d+1] - X[i+%d])\n",
	   I, F, I, I);

  /*********
  on definit les bornes dans lesquelles
  on va pouvoir apliquer le decalage :    
  borne_inf = max(0,-I)
  borne_sup = min(Nbval, Nbval -I -1) - 1
  *********/

  borne_inf = 0;
  borne_sup = Nbval - 1;
  if (I < 0)
    borne_inf = -1 * I;

  if ((Nbval - I - 1) < Nbval)
    borne_sup = Nbval - I - 2;


/*** application du decalage ***/
  for (i = borne_inf; i <= borne_sup; i++)
    {
      for (k = 0; k < NbCol; k++)
	{
	  X_decal[i * NbCol + k] = X[(i + I) * NbCol + k] +
	    F * (X[(i + I + 1) * NbCol + k] - X[(i + I) * NbCol + k]);
	}
    }

/*** traitement des bords ***/
  for (i = 0; i < borne_inf; i++)
    {
      for (k = 0; k < NbCol; k++)
	{
	  X_decal[i * NbCol + k] = X_decal[borne_inf * NbCol + k];
	}
    }
  for (i = borne_sup + 1; i < Nbval; i++)
    {
      for (k = 0; k < NbCol; k++)
	{
	  X_decal[i * NbCol + k] = X_decal[borne_sup * NbCol + k];
	}
    }

  return 0;
}

/* la fonction d'enrobage */

int
OP_Decale_1D (unsigned long NbVal, void *ArgList[], char *DiagExec)
{
  int CodRet;

  sprintf (DiagExec,
	   "Decale_1D, nb_ech = %lu, dim_tab=%d, freq=%g, decal=%g.", NbVal,
	   *((int *) ArgList[1]), *((double *) ArgList[2]),
	   *((float *) ArgList[3]));

  CodRet = Decale_1D (NbVal,
		      (short *) ArgList[0],
		      *((int *) ArgList[1]),
		      *((double *) ArgList[2]),
		      *((float *) ArgList[3]), (short *) ArgList[4]);

  if (CodRet == 0)
    return OP_OK;
  else
    {
      return OP_FAIL;
    }
}

void
ID_Decale_1D (oper * optr)
{
  strcpy (optr->Nom, "Decale_1D");
  optr->Version = "$Revision$";
  optr->Date = "$Date$";
  optr->fctptr = OP_Decale_1D;
  optr->NbArg = 5;

  optr->Arg_Car[0].direction = DIR_IN;
  optr->Arg_Car[0].categorie = VECTOR;
  optr->Arg_Car[0].typ = ATYC_I16;
  optr->Arg_Car[0].array_dim = "*";
  optr->Arg_Car[0].type_sample = "any";
  optr->Arg_Car[0].sample = "any";
  optr->Arg_Car[0].unite = "any";

  /* NbCol */
  optr->Arg_Car[1].direction = DIR_IN;
  optr->Arg_Car[1].categorie = COEFFICIENT;
  optr->Arg_Car[1].array_dim = "1";
  optr->Arg_Car[1].typ = ATYC_I32;
  optr->Arg_Car[1].unite = "any";

  /* fr */
  optr->Arg_Car[2].direction = DIR_IN;
  optr->Arg_Car[2].categorie = COEFFICIENT;
  optr->Arg_Car[2].array_dim = "1";
  optr->Arg_Car[2].typ = ATYC_IF64;
  optr->Arg_Car[2].unite = "any";


  optr->Arg_Car[3].direction = DIR_IN;
  optr->Arg_Car[3].categorie = COEFFICIENT;
  optr->Arg_Car[3].array_dim = "1";
  optr->Arg_Car[3].typ = ATYC_IF32;
  optr->Arg_Car[3].unite = "any";
  optr->Arg_Car[3].type_sample = NULL;
  optr->Arg_Car[3].sample = NULL;

  optr->Arg_Car[4].direction = DIR_OUT;
  optr->Arg_Car[4].categorie = VECTOR;
  optr->Arg_Car[4].typ = ATYC_I16;
  optr->Arg_Car[4].array_dim = "$Arg1.array_dim";
  optr->Arg_Car[4].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[4].sample = "$Arg1.sample";
  optr->Arg_Car[4].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[4].ref_time = "$Arg1.ref_time";
  optr->Arg_Car[4].unite = "$Arg1.unit";
  optr->Arg_Car[4].famille = "$Arg1.famille";

}
