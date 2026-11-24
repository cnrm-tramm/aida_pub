/****************************************************
*
* OPERATOR      Filtre_moy.c   FUNCTION  ANSI-C
*
* PURPOSE       Sliding-Averaging of a time serie
*
* DESCRIPTION   Routine de moyenne pour variables "float".
* 		Il n'y a pas de sous-échantillonnage, et le signal de 
*               sortie n'est pas dephase par rapport au signal d'entree
*
* VERSION       $Revision$
*     modifications au 24/08/2000 :
*         - suppression de l'algorithme de calcul de 
*	moyenne glissante par recurrence dans le cas ou on re
*       rencontre une valeur manquante, car il les propage
*	  - recalcul de la moyenne regulierement
*	pour eviter que la recurence derive trop
*     modifications au 08/09/2000 : 
*	  - suppression de l'allocation d'un 2eme tableau
*	pour ranger les donnees filtrees a la frequence d'interpolation
*
* ARGUMENTS   IN   float  datai      any        	Original data
*             IN   double  fi	     Hz   		Original data frequency
*             IN   double  fc         Hz   	        Cut-off frequency
*             OUT  float  datao      same as datai	Averaged-filtered data
*
* REFERENCES
*
*
* COPYRIGHT     Meteo-France
*
*#########################################################################*/

#define _POSIX_SOURCE 1
#define _XOPEN_SOURCE 600
#define _XOPEN_SOURCE_EXTENDED
#define _HPUX_SOURCE

#include <stdio.h>
#include <math.h>
#include <string.h>
#include <limits.h>
#include <stdlib.h>

#include "struct_oper.h"

/* La vraie fonction... */


int
Filtre_moy (unsigned long Ndata,
	    float *data,
	    double fe,
	    double fc,
	    float *data_fil, double *finter, int *N_moy, long *ndatainter)
{
  long i, j, Nsur2;
  long k, ppcm, limit_ppcm, r;

  long indice;

  float *datainter;
  long n_recur, fresh;

  double c, fr;
  double moy, deb_fenetre, fin_fenetre, dN_moy;
  double recur;

  if (Ndata <= 0)
    {
      return -1;
    }
  if (fc > fe)
    {
      return -2;
    }

/* determination du ppcm */

  if (fc > 0)
    {
      /* fc positif : exprimé en Hz.  */
      limit_ppcm = (long) INT_MAX / Ndata;
      ppcm = 1;
      r = (int) (((double) ppcm * fe) / fc);
      fr = ((double) ppcm * fe) / fc;
      while ((ppcm < limit_ppcm) && ((fr > r) || (fr < r)))
	{
	  ppcm = ppcm + 1;
	  r = (int) (((double) ppcm * fe) / fc);
	  fr = ((double) ppcm * fe) / fc;
	}
    }
  else
    {
      /* fc négatif : exprimé en nombre de points.  */
      fc = fe / (-fc);
      ppcm = 1;
    }
  *finter = (double) ppcm *fe;
  *ndatainter = ppcm * Ndata;

/* allocation de tableaux pour l'interpolation et la moyenne */

  datainter = malloc (*ndatainter * sizeof (float));
  if (datainter == NULL)
    {
      fprintf (stderr, " Allocation impossible de datainter \n");
      fprintf (stderr, " frequence d'interpol. : %g \n", *finter);
      fprintf (stderr, " ndatainter : %ld \n", *ndatainter);
      return -3;
    }

/* interpolation lineaire de "data" a la frequence "finter" */

  for (i = 0; i < Ndata - 1; i++)
    {
      datainter[i * ppcm] = data[i];
      for (j = i * ppcm + 1; j < (i + 1) * ppcm; j++)
	{
	  c = ((double) (j - (i * ppcm))) / ((double) ppcm);
	  datainter[j] = (c * (data[i + 1] - data[i])) + data[i];
	}
    }

  for (j = (Ndata - 1) * ppcm; j < (Ndata) * ppcm; j++)
    {
      datainter[j] = data[Ndata - 1];
    }

/* moyennage et echantillonnage a la frequence initiale */
/* Aux bords on prend le symetrique de la fonction par rapport au
   premier et dernier terme */

  *N_moy = ppcm * (fe / fc);

/* Pour ne pas dephaser le signal d'entree par rapport au 
   signal de sortie il faut que la moyenne soit centree sur
   une valeur du signal d'entree.
   Il faut donc que le nombre de points de la moyenne soit
   impair */

  if (fmod ((float) *N_moy, 2) == 0)
    *N_moy = *N_moy + 1;

  Nsur2 = (*N_moy - 1) / 2;
  dN_moy = (double) *N_moy;

  /* calcul de la moyenne */
  /* On calcule par recurence si l'element precedent n'est pas 
     egal a valeur manquante, sinon on fait la somme sur toute
     la fenetre */

  n_recur = 1;
  fresh = 2000;

  /* on est oblige de calculer la moyenne sur toute le fenetre
     de temps en temps, pour eviter que la recurrence derive trop.
     "fresh" est le nombre de recurences au bout duquel on 
     recalcule une vraie moyenne */

  /* calcul du premier element */

  moy = (double) datainter[0];
  for (j = 1; j <= Nsur2; j++)
    {
      moy = moy + 2. * (double) datainter[j];
    }

  recur = (moy / dN_moy);
  data_fil[0] = (float) recur;

  /* calcul des N/2 premiers termes */
  /* (void) fprintf(stderr, 
   *                "calcul des N/2 premiers termes\n : [1, %ld]", 
   *                Nsur2);
   */

  for (i = 1; i < Nsur2 + 1; i++)
    {

      if (!isfinite (recur) || (n_recur % fresh == 0))
	{
	  /* valeur NaN */

	  moy = 0.;
	  for (j = i - Nsur2; j <= i + Nsur2; j++)
	    {
	      if (j < 0)
		k = -j;
	      else
		k = j;

	      moy = moy + (double) datainter[k];
	      if (!isfinite (moy))
		break;
	    }

	  recur = (moy / dN_moy);
	  n_recur = 1.;
	}
      else
	{
	  /* valeur valide */

	  fin_fenetre = (double) datainter[i + Nsur2];
	  deb_fenetre = (double) datainter[Nsur2 - 1 + i];
	  recur = recur + (fin_fenetre - deb_fenetre) / dN_moy;
	  n_recur = n_recur + 1;
	}

      if (i % ppcm == 0)
	{
	  indice = i / (long) ppcm;
	  data_fil[indice] = (float) recur;
	}
    }

  /* calcul de termes de Nsur2+1 a ndatainter -Nsur2 -1 */
  /* (void) fprintf (stderr,
   *              "calcul de termes de Nsur2+1 a ndatainter -Nsur2 -1 : [%ld, %ld]\n",
   *              Nsur2 + 1, *ndatainter - Nsur2);
   */

  for (i = Nsur2 + 1; i < *ndatainter - Nsur2; i++)
    {
      if (!isfinite (recur) || (n_recur % fresh == 0))
	{
	  /* valeur NaN */

	  moy = 0.;
	  for (j = i - Nsur2; j <= i + Nsur2; j++)
	    {
	      moy = moy + (double) datainter[j];
	      if (!isfinite (moy))
		break;
	    }
	  recur = (moy / dN_moy);
	  n_recur = 1.;
	}
      else
	{
	  /* valeur valide */
	  fin_fenetre = (double) datainter[i + Nsur2];
	  deb_fenetre = (double) datainter[i - Nsur2 - 1];
	  recur = recur + (fin_fenetre - deb_fenetre) / dN_moy;
	  n_recur = n_recur + 1;
	}
      if (i % ppcm == 0)
	{
	  indice = i / (long) ppcm;
	  data_fil[indice] = (float) recur;
	}
    }

  /* calcul des Nsur2 derniers termes */
  /* (void) fprintf (stderr, "calcul des N/2 derniers termes\n : [%ld, %ld]",
   *                 *ndatainter - Nsur2, *ndatainter);
   */

  for (i = *ndatainter - Nsur2; i < *ndatainter; i++)
    {
      if (!isfinite (recur) || (n_recur % fresh == 0))
	{
	  /* valeur NaN */

	  moy = 0.;
	  for (j = i - Nsur2; j <= i + Nsur2; j++)
	    {
	      if (j > *ndatainter - 1)
		k = 2 * (*ndatainter - 1) - j;
	      else
		k = j;

	      moy = moy + (double) datainter[k];
	      if (!isfinite (moy))
		break;
	    }
	  recur = (moy / dN_moy);
	  n_recur = 1.;
	}
      else
	{
	  /* valeur valide */
	  fin_fenetre = (double) datainter[2 * (*ndatainter - 1) - i - Nsur2];
	  deb_fenetre = (double) datainter[i - Nsur2 - 1];
	  recur = recur + (fin_fenetre - deb_fenetre) / dN_moy;
	  n_recur = n_recur + 1;
	}

      if (i % ppcm == 0)
	{
	  indice = i / (long) ppcm;
	  data_fil[indice] = (float) recur;
	}

    }

  /* On nettoie avant de sortir */
  free (datainter);
  return 0;
}

/* la fonction d'enrobage classique */

int
OP_Filtre_moy (unsigned long NbVal, void *ArgList[], char *DiagExec)
{
  int CodRet, NCar;
  int N_moy;
  long ndatainter;
  double finter;

  NCar = sprintf (DiagExec, "Filtre_moy (%ld ech), f_orig=%g, f_filt=%g); ",
		  NbVal,
		  *((double *) ArgList[1]), *((double *) ArgList[2]));

  if (NCar < 0)
    NCar = 0;
  DiagExec += NCar;

  CodRet = Filtre_moy (NbVal,
		       (float *) ArgList[0],
		       *((double *) ArgList[1]),
		       *((double *) ArgList[2]),
		       (float *) ArgList[3], &finter, &N_moy, &ndatainter);

  switch (CodRet)
    {
    case 0:
      sprintf (DiagExec,
	       "OK. Freq intermediaire d'interpol : %f (%ld éch, moy sur %d)",
	       finter, ndatainter, N_moy);
      return OP_OK;
    case -1:
      sprintf (DiagExec, "ERR: freq. sortie > freq. entree, pas de moyenne.");
      return OP_FAIL;
    case -2:
      sprintf (DiagExec, "ERR: freq. sortie > freq. entree, pas de moyenne.");
      return OP_FAIL;
    case -3:
      sprintf (DiagExec, "ERR: Allocation impossible de datainter \n");
      return OP_FAIL;
    default:
      sprintf (DiagExec, "ERR: Erreur %d", CodRet);
      return OP_FAIL;
    }
}

void
ID_Filtre_moy (oper * optr)
{
  strcpy (optr->Nom, "Filtre_moy");
  optr->Version = "$Revision$";
  optr->Date = "$Date$";
  optr->fctptr = OP_Filtre_moy;
  optr->NbArg = 4;

  /* data */
  optr->Arg_Car[0].direction = DIR_IN;
  optr->Arg_Car[0].categorie = VECTOR;
  optr->Arg_Car[0].typ = ATYC_IF32;
  optr->Arg_Car[0].array_dim = "1";
  optr->Arg_Car[0].type_sample = "any";
  optr->Arg_Car[0].sample = "any";
  optr->Arg_Car[0].unite = "any";

  /* fe */
  optr->Arg_Car[1].direction = DIR_IN;
  optr->Arg_Car[1].categorie = COEFFICIENT;
  optr->Arg_Car[1].array_dim = "1";
  optr->Arg_Car[1].typ = ATYC_IF64;
  optr->Arg_Car[1].unite = "any";
  optr->Arg_Car[1].type_sample = NULL;
  optr->Arg_Car[1].sample = NULL;

  /* fc */
  optr->Arg_Car[2].direction = DIR_IN;
  optr->Arg_Car[2].categorie = COEFFICIENT;
  optr->Arg_Car[2].array_dim = "1";
  optr->Arg_Car[2].typ = ATYC_IF64;
  optr->Arg_Car[2].unite = "any";
  optr->Arg_Car[2].type_sample = NULL;
  optr->Arg_Car[2].sample = NULL;

  /* data_fil */
  optr->Arg_Car[3].direction = DIR_OUT;
  optr->Arg_Car[3].categorie = VECTOR;
  optr->Arg_Car[3].typ = ATYC_IF32;
  optr->Arg_Car[3].array_dim = "1";
  optr->Arg_Car[3].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[3].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[3].sample = "$Arg1.sample";
  optr->Arg_Car[3].ref_time = "$Arg1.ref_time";
  optr->Arg_Car[3].unite = "$Arg1.unit";
  optr->Arg_Car[3].famille = "$Arg1.famille";
  optr->Arg_Car[3].misval = "$Arg1.misval";
  optr->Arg_Car[3].name = "$Arg1.name + \" filtre par moyenne mobile \"";	/* sur \" + ($Arg2/$Arg3) + \" sec\""; */
  optr->Arg_Car[3].en_name =
    "$Arg1.english_name + \" filtered by running mean \" ";
}
