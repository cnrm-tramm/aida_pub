/*************************************************
* OPERATOR 	Stat_Spectr.c 	FUNCTION ANSI-C
*
* PURPOSE	Calcule la moyenne des diamètres à la puissance N 
*               d'un spectre de goutelettes.
*
* ARGUMENTS 	IN 	float[]	tabin 	       Vecteur-tableau d'entree
* 		IN 	int	Nb_Col_Tab_in  taille du vecteur d'entree
* 		IN 	float[]	Tabphi         Tableau des diamètres moyens
* 		IN 	int	Puiss          Puissance a laquelle elever le diamete
*
*		OUT	float 	moy 	       Résultat
*		
* ENTRY		NONE
*
* SUBPROGRAMS 	NONE
*
* REFERENCE	NONE
*
* COPYRIGHT	Meteo-France
*		Centre National de Recherches Meteorologiques
*		GMEI/ MMA
*		42, av G. Coriolis 
*		31057	TOULOUSE cedex
*
*****************************************************************/

#define _POSIX_SOURCE 1
#define _XOPEN_SOURCE 600

#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <math.h>
#include "struct_oper.h"

long
Stat_Spectr (unsigned long ndata,
	     const float *tabin,	/* tabin est en fait un tableau 2D */
	     const int Nb_Col_Tab_in,
	     const float *tabphi,
	     const double puissance,
	     float *result)

{
  long i, j, j_in;
  double *tabphi_n;
  double Som_C_Phi_n, Som_C;
  double racine;


  if (0 > Nb_Col_Tab_in)
    return -1;

  if (Nb_Col_Tab_in > 65535)
    return -2;

  if (puissance > 15.0)
    return -3;

  /* On commence par calculer les phi^n */
  tabphi_n = malloc (Nb_Col_Tab_in * sizeof (double));
  if (tabphi_n == NULL)
    return -4;
  for (j = 0; j < Nb_Col_Tab_in; j++)
    {
      tabphi_n[j] = pow (tabphi[j], puissance);
    }

  /* Boucle sur tous les spectres. */
  for (i = 0; i < ndata; i++)
    {
      j_in = i * Nb_Col_Tab_in;
      Som_C_Phi_n = 0.0;
      Som_C = 0.0;
      /* Boucle sur toutes les classes */
      for (j = 0; j < Nb_Col_Tab_in; j++)
	{
	  Som_C_Phi_n = Som_C_Phi_n + tabphi_n[j] * tabin[j_in];
	  Som_C = Som_C + tabin[j_in];
	  j_in++;
	}
      if (Som_C == 0.0)
	result[i] = 0.0;
      else
	result[i] = Som_C_Phi_n / Som_C;
    }
  racine=1./puissance;
  for (i = 0; i < ndata; i++)
    {
	result[i] = pow(result[i],racine);
    }

  free (tabphi_n);
  return i;
}

/* fonction d'enrobage */

int
OP_Stat_Spectr (unsigned long Nbval, void *ArgList[], char *DiagExec)
{
  long CodRet, i;
  float tabdiam[15];

  /* Le mécanisme pour passer des tableaux de coefficients */
  /* -> passage par une var. intermédiaire.  */
  for (i = 0; i < 15; i++)
    {
      tabdiam[i] = *((float *) ArgList[2 + i]);
    }

  CodRet = Stat_Spectr (Nbval,
			(float *) ArgList[0],
			*((int *) ArgList[1]),
			tabdiam,
			*((double *) ArgList[17]),
			(float *) ArgList[18]);

  if (CodRet > 0)
    {
      sprintf (DiagExec, "%d classes, diamètres=[%f,%f,%f,%f,%f,%f,%f,%f,%f,%f,%f,%f,%f,%f,%f], %ld instants traités",
	       *((int *) ArgList[1]), 
               tabdiam[0], tabdiam[1], tabdiam[2], tabdiam[3], tabdiam[4],
               tabdiam[5], tabdiam[6], tabdiam[7], tabdiam[8], tabdiam[9],
               tabdiam[10], tabdiam[11], tabdiam[12], tabdiam[13], tabdiam[14],
               CodRet);
      return OP_OK;
    }
  switch (CodRet)
    {
    case 0:
      strcpy (DiagExec, "WARN : 0 instants traités !!!");
      return OP_OK;
    case -1:
      strcpy (DiagExec, "Nombre de classes négatives ?!");
      return OP_FAIL;
    case -2:
      strcpy (DiagExec, "Nombre de classes trop grande.");
      return OP_FAIL;
    case -3:
      strcpy (DiagExec, "Puissance trop grande.");
      return OP_FAIL;
    case -4:
      strcpy (DiagExec, "Impossible allouer mémoire pour tableau de travail.");
      return OP_FAIL;
    default:
      strcpy (DiagExec, "Unexpected error !!");
      return OP_FAIL;
    }
}

void
ID_Stat_Spectr (oper * optr)
{
  int i;

  strcpy (optr->Nom, "Stat_Spectr");
  optr->Version = "1.0";
  optr->Date = "10/15/96";
  optr->fctptr = OP_Stat_Spectr;
  optr->NbArg = 19;

  optr->Arg_Car[0].direction = DIR_IN;
  optr->Arg_Car[0].categorie = VECTOR;
  optr->Arg_Car[0].typ = ATYC_IF32;
  optr->Arg_Car[0].array_dim = "15";
  optr->Arg_Car[0].type_sample = "any";
  optr->Arg_Car[0].sample = "any";
  optr->Arg_Car[0].unite = "";

  /* Le nombre de colonnes du vecteur d'entrée */
  optr->Arg_Car[1].direction = DIR_IN;
  optr->Arg_Car[1].categorie = COEFFICIENT;
  optr->Arg_Car[1].typ = ATYC_I32;
  optr->Arg_Car[1].array_dim = "1";
  optr->Arg_Car[1].unite = "";

  /* Les valeurs de diamètre */
  for (i = 0; i < 15; i++)
    {
      optr->Arg_Car[2 + i].direction = DIR_IN;
      optr->Arg_Car[2 + i].categorie = COEFFICIENT;
      optr->Arg_Car[2 + i].typ = ATYC_IF32;
      optr->Arg_Car[2 + i].array_dim = "1";
      optr->Arg_Car[2 + i].unite = "";
    }

  /* La puissance à laquelle il faut élever le diamètre */
  optr->Arg_Car[17].direction = DIR_IN;
  optr->Arg_Car[17].categorie = COEFFICIENT;
  optr->Arg_Car[17].typ = ATYC_IF64;
  optr->Arg_Car[17].array_dim = "1";
  optr->Arg_Car[17].unite = "";

  optr->Arg_Car[18].direction = DIR_OUT;
  optr->Arg_Car[18].categorie = VECTOR;
  optr->Arg_Car[18].typ = ATYC_IF32;
  optr->Arg_Car[18].array_dim = "1";
  optr->Arg_Car[18].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[18].ref_time = "$Arg1.ref_time";
  optr->Arg_Car[18].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[18].sample = "$Arg1.sample";
  optr->Arg_Car[18].unite = "$Arg1.unit";
  optr->Arg_Car[18].famille = "$Arg1.famille";
  optr->Arg_Car[18].misval = "$Arg1.misval";
}
