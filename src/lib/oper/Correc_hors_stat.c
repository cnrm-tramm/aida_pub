/****************************************************************
* OPERATOR 	Correc_hors_stat  FUNCTION  ANSI-C
* 
* PURPOSE	correction of out-of-range values 
*
* DESCRIPTION   Cette fonction "corrige" les valeurs en-dehors
*	   	d'une "statistique normale". 
*               
*               La nature de la correction est paramètrable : 
*                    Les series "hors stat" de durée <= seuil_duree
*                          sont remplacées par une interpolation
*                    Les series "hors stat" de durée > seuil_duree
*                          sont remplacées par des "valeur manquantes"
*
*
* VERSION         $Revision: 5097 $
*
* ARGUMENTS 	IN 	float 	X   	    parametre brut	
*		IN 	float 	MisVal      Special value for missing data
*		IN 	float 	borne_inf   valeur min. permise
*		IN 	float 	borne_sup   valeur maxG. permise
*		IN  float   Tolerance_X  L'ecart maximum toléré à la moyenne glissante (en nb d'ecart-type)
*		IN  float   Tolerance_dX 
*		IN 	int 	seuil_duree Nb pt max ou on interpolle.
*		IN 	int 	fenetre     largeur fenetre pour stat
* 		OUT 	float 	Xcor 	    parametre corrige
*
* ENTRY		NONE
*
* SUBPROGRAMS 	NONE
* 
* REFERENCES	NONE
*
* CHANGES       1.2   
* 
* COPYRIGHT 	Meteo-France
*		Centre de Recherches Meteorologiques
*		GMEI/TRAMM
*		42, av. G. Coriolis
*		31057	TOULOUSE cedex
*
******************************************************************/

#define _POSIX_SOURCE 1
#define _XOPEN_SOURCE 600

/* Pour la fonction isfinite */
#define _HPUX_SOURCE 1


#include <stdio.h>
#include <string.h>
#include <limits.h>
#include <math.h>
#include "struct_oper.h"

void
estim_stat_flt (const float *X,
		const size_t Nb_Val,
		const float missing_val,
		const float borne_inf,
		const float borne_sup,
		size_t * Nb_Stat_X,
		size_t * Nb_Stat_dX,
		float *Moy_X, float *Ect_X, float *Moy_dX, float *Ect_dX)
/*
 * Evalue la statistique d'une série de
 * données et de sa dérivée :
 *    Moy (X), EcTyp(X), Moy(dX), EcTyp(dX)
 *
 *  NB1: Attention : si le Nbre de valeurs (Nb_Val) est grand,
 * la somme progressive perd de sa précision. Penser à un
 * autre algorithme.
 *
 *  NB2: Attention : si le Nbre de valeurs (Nb_Val) est petit,
 * la statistique perd de son sens. 
 *
 *  NB3: si Nb_Val<0, ou borne_inf>borne_sup, vous obtiendrez
 * un résultat plus significatif par la méthode de Monte-Carlo.
 * Voir à ce sujet la fonction ramdom() (3M).
 */
{
  size_t i, N_X, N_dX;
  double Som_X, Som_ec2_X;
  double Som_dX, Som_ec2_dX;
  register float X_courant;
  double dX_courant;
  const float *last_X_ok;

  Som_X = 0.0;
  Som_dX = 0.0;
  last_X_ok = NULL;
  N_X = 0;
  N_dX = 0;

  /* First loop for Moy. */

  for (i = 0; i < Nb_Val; i++)
    {
      X_courant = X[i];
      if (isfinite (X_courant) && (X_courant != missing_val)
	  && (X_courant >= borne_inf) && (X_courant <= borne_sup))
	{
	  Som_X += X_courant;
	  N_X += 1;
	  if (last_X_ok != NULL)
	    {
	      dX_courant = X_courant - *last_X_ok;
	      Som_dX += dX_courant;
	      N_dX += 1;
	    }
	  last_X_ok = X;
	}
    }

  if (N_X == 0)
    {
      *Moy_X = 0.0;
    }
  else
    {
      *Moy_X = Som_X / N_X;
    }
  /* On recommence avec les Delta... */
  if (N_dX == 0)
    {
      *Moy_dX = 0.0;
    }
  else
    {
      *Moy_dX = Som_dX / N_dX;
    }

  *Nb_Stat_X = N_X;
  *Nb_Stat_dX = N_dX;

  /* And loop Again for std_dev. */

  Som_ec2_X = 0;
  Som_ec2_dX = 0;
  last_X_ok = NULL;
  N_X = 0;
  N_dX = 0;
  for (i = 0; i < Nb_Val; i++)
    {
      X_courant = X[i];
      if (isfinite (X_courant) && (X_courant != missing_val)
	  && (X_courant >= borne_inf) && (X_courant <= borne_sup))
	{
	  Som_ec2_X += (X_courant - *Moy_X) * (X_courant - *Moy_X);
	  N_X += 1;
	  if (last_X_ok != NULL)
	    {
	      dX_courant = X_courant - *last_X_ok;
	      Som_ec2_dX += (dX_courant - *Moy_dX) * (dX_courant - *Moy_dX);
	      N_dX += 1;
	    }
	  last_X_ok = X + i;
	}
    }
  if (*Nb_Stat_X != N_X)
    {
      (void) fprintf (stderr,
		      "++- BUG : Pas le meme nombre d'echant. X OK\n");
    }
  if (*Nb_Stat_dX != N_dX)
    {
      (void) fprintf (stderr,
		      "++- BUG : Pas le meme nombre d'echant. dX OK\n");
    }

  if (N_X == 0)
    {
      *Ect_X = 0.0;
    }
  else
    {
      *Ect_X = sqrt (Som_ec2_X / N_X);
    }
  if (N_dX == 0)
    {
      *Ect_dX = 0.0;
    }
  else
    {
      *Ect_dX = sqrt (Som_ec2_dX / N_dX);
    }
}

void
copie_in_stat (const float *X,
	       const size_t Nb_Val,
	       const float MisVal,
	       const float borne_inf,
	       const float borne_sup,
	       size_t * nb_sup,
	       size_t * nb_inf,
	       size_t * nb_abs,
	       size_t * nb_NaN,
	       size_t * nb_ecart,
	       size_t * nb_ecart_dX,
	       size_t * nbOK,
	       size_t fenetre,
	       const float Tolerance_X,
	       const float Tolerance_dX, float *X_cor)
/*
 * copie dans X_cor les valeurs de X qui
 * passent un certain nombre de test.
 */
{
  size_t nb_stat, nb_stat_X, nb_stat_dX;
  float Glob_Moy_X, Glob_Ect_X;
  float Glob_Moy_dX, Glob_Ect_dX;
  float Glob_seuil_ecart_moy;
  float Glob_seuil_dX;
  float Loc_Moy_X, Loc_Ect_X;
  float Loc_Moy_dX, Loc_Ect_dX;
  float Loc_seuil_ecart_moy;
  float Loc_seuil_dX;
  const float *last_X_ok;
  size_t duree_trou;
  size_t demi_fen, deci_fen;
  size_t i;
  int idx_deb, idx_fin;
  int Flag_OK;
  register float X_courant;
  register double dX_courant;
  const float *X_p;
  const float *X_depart;
  float *Xcor_p;
  /* Pour le debug... */
  /****************************************************************************
  FILE *fic_lim_inf, *fic_lim_sup;
  float tmp_flt;
  char en_tete[512];
  ****************************************************************************/

  demi_fen = fenetre / 2;
  deci_fen = fenetre / 10;

  /*  Premier appel a stat pour calculer une moyenne et une */
  /* variance sur les valeurs "plausibles" de TOUTE la serie */
  estim_stat_flt (X, Nb_Val, MisVal, borne_inf, borne_sup,
		  &nb_stat_X, &nb_stat_dX,
		  &Glob_Moy_X, &Glob_Ect_X, &Glob_Moy_dX, &Glob_Ect_dX);

  /* petite parade contre les cas de signaux constants */
  /* qu'on risquerait d'éliminer un peu vite */
  if (Glob_Ect_X == 0.0)
    {
      if (Glob_Moy_X == 0)
	Glob_Ect_X = 1.0;
      else
	Glob_Ect_X = Glob_Moy_X;
    }

  if (Glob_Ect_dX == 0.0)
    {
      if (Glob_Moy_dX == 0)
	Glob_Ect_dX = 1.0;
      else
	Glob_Ect_dX = Glob_Moy_dX;
    }

  /*
     (void) fprintf (stderr, "Moy_X = %g, Ect_X = %g\n", Glob_Moy_X, Glob_Ect_X);
     (void) fprintf (stderr, "Moy_dX = %g, Ect_dX = %g\n", Glob_Moy_dX, Glob_Ect_dX);
   */

  if (nb_stat_X > 30)
    Glob_seuil_ecart_moy = Tolerance_X * Glob_Ect_X;
  else
    Glob_seuil_ecart_moy = Tolerance_X * 1.5 * Glob_Ect_X;

  /* Seuils qui serviront en l'absence de stat. locale. */
  if (nb_stat_dX > 30)
    Glob_seuil_dX = Tolerance_dX * 1.5 * Glob_Ect_dX;
  else
    Glob_seuil_dX = Tolerance_dX * 3.0 * Glob_Ect_dX;

  /* Pour le Debug... */
  /****************************************************************************
  strcpy (en_tete,
	  "VECT-DATA\n       512\n\002\n[lim_stat_sup]\nformat = Ieeefloat_32\ndimension = 4\ndim_array = 1\nref_time = rft_TIME_25\nFIN_HDR\n\014\003\032");
  fic_lim_sup = fopen ("/tmp/lim_stat_sup.vbn", "wb");
  if (fic_lim_sup != NULL)
    {
      (void) fwrite (en_tete, 512, 1, fic_lim_sup);
    }
  fic_lim_inf = fopen ("/tmp/lim_stat_inf.vbn", "wb");
  en_tete[33] = 'i';
  en_tete[34] = 'n';
  en_tete[35] = 'f';
  if (fic_lim_inf != NULL)
    {
      (void) fwrite (en_tete, 512, 1, fic_lim_inf);
    }
  ****************************************************************************/

  /* */
  *nb_sup = 0;
  *nb_inf = 0;
  *nb_abs = 0;
  *nb_NaN = 0;
  *nb_ecart = 0;
  *nb_ecart_dX = 0;
  *nbOK = 0;
  last_X_ok = NULL;
  /* Le premier élement est après un trou ... infini */
  /* On approxime +INF par NbVal. */
  duree_trou = Nb_Val;
  Loc_Moy_X = Glob_Moy_X;
  Loc_seuil_ecart_moy = Glob_seuil_ecart_moy;
  Loc_Moy_dX = Glob_Moy_dX;
  Loc_seuil_dX = Glob_seuil_dX;
  X_p = X;
  Xcor_p = X_cor;
  for (i = 0; i < Nb_Val; i++)
    {
      if ((i % deci_fen) == 0)
	{			/* On met a jour la stat glissante.  */
	  idx_deb = i - demi_fen;
	  idx_fin = i + demi_fen;
	  if (idx_deb < 0)
            {
	     idx_deb = 0;
             idx_fin = fenetre;
	    }
	  if (idx_fin > Nb_Val -1 ) 
            { 
             idx_fin = Nb_Val -1; 
	     idx_deb = idx_fin -fenetre;
	    }
	    
	  X_depart = X + idx_deb;
	  nb_stat = idx_fin - idx_deb + 1;

	  estim_stat_flt (X_depart, nb_stat, MisVal, borne_inf, borne_sup,
			  &nb_stat_X, &nb_stat_dX,
			  &Loc_Moy_X, &Loc_Ect_X, &Loc_Moy_dX, &Loc_Ect_dX);

	  /* Cas rare, mais a envisager..  */
	  if (Loc_Ect_X == 0.0)
	    {
	      if (Loc_Moy_X == 0)
		Loc_Ect_X = 1.0;
	      else
		Loc_Ect_X = Loc_Moy_dX;
	    }
	  if (Loc_Ect_dX == 0.0)
	    {
	      if (Loc_Moy_dX == 0)
		Loc_Ect_dX = 1.0;
	      else
		Loc_Ect_dX = Loc_Moy_dX;
	    }

	  /* Si la stat est significative, on selectionne */
	  /* Sinon, on est beaucoup plus large...         */

	  if (nb_stat_X > 25)
	    Loc_seuil_ecart_moy = Tolerance_X * Loc_Ect_X;
	  else if (nb_stat_X > 10)
	    Loc_seuil_ecart_moy = Glob_seuil_ecart_moy;
	  else
	    {
	      Loc_seuil_ecart_moy = Glob_seuil_ecart_moy;
	      Loc_Moy_X = Glob_Moy_X;
	    }

	  if (nb_stat_dX > 25)
	    Loc_seuil_dX = Tolerance_dX * Loc_Ect_dX;
	  else if (nb_stat_dX > 10)
	    Loc_seuil_dX = Glob_seuil_dX;
	  else
	    {
	      Loc_seuil_dX = Glob_seuil_dX;
	      Loc_Moy_dX = Glob_Moy_dX;
	    }

	}

  /****************************************************************************
      tmp_flt = Loc_Moy_X + Loc_seuil_ecart_moy;
      if (fic_lim_sup != NULL)
	{
	  (void) fwrite (&tmp_flt, sizeof (tmp_flt), 1, fic_lim_sup);
	}
      tmp_flt = Loc_Moy_X - Loc_seuil_ecart_moy;
      if (fic_lim_inf != NULL)
	{
	  (void) fwrite (&tmp_flt, sizeof (tmp_flt), 1, fic_lim_inf);
	}
  ****************************************************************************/

      X_courant = *X_p;
      /* Valeur correctement représentée par un float ?   */
      if (!isfinite (X_courant))
	{
	  *nb_NaN = *nb_NaN + 1;
	  Flag_OK = 0;
	}
      else if (X_courant == MisVal)
	{
	  *nb_abs = *nb_abs + 1;
	  Flag_OK = 0;
	}
      else if (X_courant > borne_sup)
	{
	  *nb_sup = *nb_sup + 1;
	  Flag_OK = 0;
	}
      else if (X_courant < borne_inf)
	{
	  *nb_inf = *nb_inf + 1;
	  Flag_OK = 0;
	}
      else
	{
	  /* On utilise la statistique "glissante" calculée ci-dessus */

	  if (fabs (X_courant - Loc_Moy_X) > Loc_seuil_ecart_moy)
	    {
	      *nb_ecart = *nb_ecart + 1;
	      Flag_OK = 0;
	    }
	  else if ((duree_trou == 0) && (last_X_ok != NULL))
	    {			/* On peut faire le test sur la dérivée... */
	      dX_courant = X_courant - *last_X_ok;
	      if (fabs (dX_courant - Loc_Moy_dX) > Loc_seuil_dX)
		{
		  /* pistes d'évolution : */
		  /* Rejeter le pt le plus éloigné de la moyenne */
		  *nb_ecart_dX = *nb_ecart_dX + 1;
		  Flag_OK = 0;
		}
	      else
		{
		  *nbOK = *nbOK + 1;
		  Flag_OK = 1;
		}
	    }
	  else
	    {			/* On approuve sans test sur dérivée... */
	      *nbOK = *nbOK + 1;
	      Flag_OK = 1;
	    }
	}

      if (Flag_OK == 1)
	{
	  last_X_ok = X_p;
	  duree_trou = 0;
	  *Xcor_p = *X_p;
	}
      else
	{
	  duree_trou = duree_trou + 1;
	  *Xcor_p = MisVal;
	}

      X_p++;
      Xcor_p++;
    }

  /* Test de validité interne */
  if (*nb_NaN + *nb_sup + *nb_inf + *nb_abs + *nb_ecart + *nb_ecart_dX +
      *nbOK != Nb_Val)
    {
      (void) fprintf (stderr, "Internal error : %lu\n", (unsigned long) nbOK);
    }

  /****************************************************************************
  if (fic_lim_sup != NULL)
    fclose (fic_lim_sup);
  if (fic_lim_inf != NULL)
    fclose (fic_lim_inf);
  ****************************************************************************/
}

unsigned long
Correc_hors_stat (unsigned long Nloop,
		  const float *X,
		  const float MisVal,
		  const float borne_inf,
		  const float borne_sup,
		  float Tolerance_X,
		  float Tolerance_dX,
		  const int fenetre,
		  const int seuil_duree, float *Xcor, unsigned long *Diag_tab)
{
  unsigned long i, j;
  long nb_passe;
  size_t nb_sup, nb_inf, nb_abs, nb_NaN, nb_ecart, nb_ecart_dX, nbOK;
  size_t loc_nb_sup, loc_nb_inf, loc_nb_abs, loc_nb_NaN;
  size_t loc_nb_ecart, loc_nb_ecart_dX;
  unsigned long duree_trou;
  float *Xcor_p;
  const float *last_X_ok;
  double Tmp_coeff;

  if (borne_inf >= borne_sup)
    {
      Diag_tab[0] = 0;
      Diag_tab[1] = Nloop;
      Diag_tab[2] = Nloop;
      Diag_tab[3] = Nloop;
      return ULONG_MAX;
    }

  if ((MisVal > borne_inf) && (MisVal < borne_sup))
    {
      (void) fprintf (stderr,
		      "Bizarre : Misval(%g) est dans l'intervalle [min, max] ([%g, %g])\n",
		      MisVal, borne_inf, borne_sup);
    }

  if ((fenetre > 10000) || (fenetre < 50))
    {
      (void) fprintf (stderr,
		      "Attention : valeur inutilisable de fenetre (%d) \n",
		      fenetre);
    }

  if (fenetre > Nloop)
    {
      (void) fprintf (stderr,
		      "Attention : fenetre (%d) plus grande que Nb_valeurs (%ld)\n",
		      fenetre, Nloop);
	  return -2 ;
    }

  if (Tolerance_X < 0.0)
    {
      (void) fprintf (stderr,
		      "Attention : Tolerance_X négatif (%f)\n", Tolerance_X);
      Tolerance_X = fabs (Tolerance_X);
    }
  if (Tolerance_X > 15)
    {
      (void) fprintf (stderr,
		      "Attention : Tolerance_X énorme (%f)\n", Tolerance_X);
    }
  if (Tolerance_X < 0.5)
    {
      (void) fprintf (stderr,
		      "Attention : Tolerance_X petite (%f)\n", Tolerance_X);
    }

  if (Tolerance_dX < 0.0)
    {
      (void) fprintf (stderr,
		      "Attention : Tolerance_dX négatif (%f)\n",
		      Tolerance_dX);
      Tolerance_dX = fabs (Tolerance_dX);
    }
  if (Tolerance_dX > 15)
    {
      (void) fprintf (stderr,
		      "Attention : Tolerance_dX énorme (%f)\n", Tolerance_dX);
    }
  if (Tolerance_dX < 0.5)
    {
      (void) fprintf (stderr,
		      "Attention : Tolérance_dX petite (%f)\n", Tolerance_dX);
    }


  /*  Premier travail : élimination des valeurs manquantes */

  copie_in_stat (X, Nloop, MisVal, borne_inf, borne_sup,
		 &nb_sup, &nb_inf, &nb_abs, &nb_NaN,
		 &nb_ecart, &nb_ecart_dX, &nbOK,
		 fenetre, Tolerance_X, Tolerance_dX, Xcor);
  nb_passe = 1;
  /* Et on boucle jusqu'à ce qu'on ne fasse plus d'élimination d'ecart */
  loc_nb_ecart = nb_ecart;
  loc_nb_ecart_dX = nb_ecart_dX;
  while (loc_nb_ecart + loc_nb_ecart_dX != 0)
    {
      /* Puisqu'on est déjà passé une fois, on a soit des MisVal, soit
         des écarts */
      copie_in_stat (Xcor, Nloop, MisVal, borne_inf, borne_sup,
		     &loc_nb_sup, &loc_nb_inf, &loc_nb_abs, &loc_nb_NaN,
		     &loc_nb_ecart, &loc_nb_ecart_dX, &nbOK,
		     fenetre, Tolerance_X, Tolerance_dX, Xcor);
      nb_passe += 1;
      /* (void) fprintf (stderr, "%d, %d\n", loc_nb_ecart, loc_nb_ecart_dX); */
      nb_ecart += loc_nb_ecart;
      nb_ecart_dX += loc_nb_ecart_dX;
    }

  /* Second travail : remplacement des valeurs, quand c'est possible */

  last_X_ok = NULL;
  duree_trou = 0;
  for (i = 0; i < Nloop; i++)
    {
      if (*Xcor != MisVal)
	{
	  /*   Si cette valeur OK suit un "trou" (suite continue de */
	  /* valeurs invalides), il faut d'abord "boucher ce trou". */
	  Xcor_p = Xcor - duree_trou;
	  if (duree_trou > seuil_duree)
	    {			/* Le trou entre last_X_ok et X. est "long" */
	      /* on remplit par des "valeurs manquantes" */
	      for (j = 0; j < duree_trou; j++)
		{
		  *Xcor_p = MisVal;
		  Xcor_p++;
		}
	    }
	  else if (duree_trou != 0)
	    {			/* Le trou entre last_X_ok et X. est "court" */
	      if (last_X_ok == NULL)
		{		/* Que faire ? */
		  for (j = 0; j < duree_trou; j++)
		    {
		      *Xcor_p = *Xcor;
		      Xcor_p++;
		    }
		}
	      else
		{		/* Interpolation */
		  Tmp_coeff = 1.0 / (duree_trou + 1);
		  for (j = 0; j < duree_trou; j++)
		    {
		      *Xcor_p =
			((duree_trou - j) * *last_X_ok +
			 (j + 1) * *Xcor) * Tmp_coeff;
		      Xcor_p++;
		    }
		}
	    }
	  last_X_ok = Xcor;
	  duree_trou = 0;
	}
      else
	{
	  duree_trou = duree_trou + 1;
	}

      Xcor++;
    }
  /* La boucle est finie... */
  /* Mais toutes les corrections n'ont peut-être pas été faites */

  Xcor_p = Xcor - duree_trou;
  if (last_X_ok == NULL)
    {				/* Y'a pas une seule valeur bonne !! */
      for (j = 0; j < duree_trou; j++)
	{
	  *Xcor_p = MisVal;
	  Xcor_p++;
	}
    }
  else if (duree_trou > seuil_duree)
    {				/* Il y a un GRAND trou avant la fin.  */
      for (j = 0; j < duree_trou; j++)
	{
	  *Xcor_p = MisVal;
	  Xcor_p++;
	}

    }
  else if (duree_trou > 0)
    {				/* Il y a un petit trou avant la fin.  */
      for (j = 0; j < duree_trou; j++)
	{
	  *Xcor_p = *last_X_ok;
	  Xcor_p++;
	}
    }

  Diag_tab[0] = nb_passe;
  Diag_tab[1] = nbOK;
  Diag_tab[2] = nb_sup;
  Diag_tab[3] = nb_inf;
  Diag_tab[4] = nb_abs;
  Diag_tab[5] = nb_NaN;
  Diag_tab[6] = nb_ecart;
  Diag_tab[7] = nb_ecart_dX;
  return nb_sup + nb_inf + nb_abs + nb_NaN + nb_ecart + nb_ecart_dX;
}

/* fonction d'enrobage */

int
OP_Correc_hors_stat (unsigned long Nbval, void *ArgList[], char *DiagExec)
{
  unsigned long CodRet;
  unsigned long Diag_tab[8];

  /* sprintf (DiagExec,""); */
  /*
   * Le choix des valeurs 7.0 (pour la série) et 10.0
   * (pour la dérivée) est un peu arbitraire...
   * On trouve dans la littérature (libraire QK du BLG)
   * des valeurs plus faibles (3.0).
   * Mais l'expérience a montré que des séries normales
   * (par exemple, pendant TRAC, la vit. verticale de la station 6,
   * le 21 juin 1998) pouvaient présenter des valeurs jusqu'à 6.5 fois
   * l'écart-type, et les dérivées jusqu'à 9 fois.
   * On ne peut donc pas filtrer "plus serré".
   */
  /* Tolerance_X = 7.0;
     Tolerance_dX = 10.0; */

  CodRet = Correc_hors_stat (Nbval, (float *) ArgList[0], *((float *) ArgList[1]),	/* MisVal */
			     *((float *) ArgList[2]),	/* borne_inf */
			     *((float *) ArgList[3]),	/* borne_sup */
			     *((float *) ArgList[4]),	/* Tolerance_X */
			     *((float *) ArgList[5]),	/* Tolerance_dX */
			     *((int *) ArgList[6]),	/* fenetre */
			     *((int *) ArgList[7]),	/* seuil_duree */
			     (float *) ArgList[8],	/* Xcor */
			     Diag_tab);

  if (CodRet == ULONG_MAX)
    {
      sprintf (DiagExec, "Error : borne_min >= borne_max");
      return OP_FAIL;
    }
  else if (CodRet == -2)
    {
      sprintf (DiagExec, "Error : fenetre > Nloop");
      return OP_FAIL;
    }
  else
    {
      sprintf (DiagExec,
	       "%lu valeurs (sur %lu) rejetées [s:%lu, i:%lu, a:%lu, n:%lu, e:%lu, d:%lu], %lu passes",
	       CodRet, Nbval, Diag_tab[2], Diag_tab[3], Diag_tab[4],
	       Diag_tab[5], Diag_tab[6], Diag_tab[7], Diag_tab[0]);
      return OP_OK;
    }

}

void
ID_Correc_hors_stat (oper * optr)
{
  strcpy (optr->Nom, "Correc_hors_stat");
  optr->Version = "$Revision: 5097 $";
  optr->Date = "$Date: 2013-03-25 13:23:40 +0100 (lun. 25 mars 2013) $";
  optr->fctptr = OP_Correc_hors_stat;
  optr->NbArg = 9;

  /* X */
  optr->Arg_Car[0].direction = DIR_IN;
  optr->Arg_Car[0].categorie = VECTOR;
  optr->Arg_Car[0].typ = ATYC_IF32;
  optr->Arg_Car[0].array_dim = "1";
  optr->Arg_Car[0].unite = "";
  optr->Arg_Car[0].type_sample = "any";
  optr->Arg_Car[0].sample = "any";

  /* MisVal */
  optr->Arg_Car[1].direction = DIR_IN;
  optr->Arg_Car[1].categorie = COEFFICIENT;
  optr->Arg_Car[1].typ = ATYC_IF32;
  optr->Arg_Car[1].array_dim = "1";
  optr->Arg_Car[1].unite = "";
  optr->Arg_Car[1].type_sample = NULL;
  optr->Arg_Car[1].sample = NULL;

  /* borne_inf */
  optr->Arg_Car[2].direction = DIR_IN;
  optr->Arg_Car[2].categorie = COEFFICIENT;
  optr->Arg_Car[2].typ = ATYC_IF32;
  optr->Arg_Car[2].array_dim = "1";
  optr->Arg_Car[2].unite = "";
  optr->Arg_Car[2].type_sample = NULL;
  optr->Arg_Car[2].sample = NULL;

  /* borne_sup */
  optr->Arg_Car[3].direction = DIR_IN;
  optr->Arg_Car[3].categorie = COEFFICIENT;
  optr->Arg_Car[3].typ = ATYC_IF32;
  optr->Arg_Car[3].array_dim = "1";
  optr->Arg_Car[3].unite = "";
  optr->Arg_Car[3].type_sample = NULL;
  optr->Arg_Car[3].sample = NULL;

  /* Tolerance_X */
  optr->Arg_Car[4].direction = DIR_IN;
  optr->Arg_Car[4].categorie = COEFFICIENT;
  optr->Arg_Car[4].typ = ATYC_IF32;
  optr->Arg_Car[4].array_dim = "1";
  optr->Arg_Car[4].unite = "";
  optr->Arg_Car[4].type_sample = NULL;
  optr->Arg_Car[4].sample = NULL;

  /* Tolerance_dX */
  optr->Arg_Car[5].direction = DIR_IN;
  optr->Arg_Car[5].categorie = COEFFICIENT;
  optr->Arg_Car[5].typ = ATYC_IF32;
  optr->Arg_Car[5].array_dim = "1";
  optr->Arg_Car[5].unite = "";
  optr->Arg_Car[5].type_sample = NULL;
  optr->Arg_Car[5].sample = NULL;

  /* fenetre */
  optr->Arg_Car[6].direction = DIR_IN;
  optr->Arg_Car[6].categorie = COEFFICIENT;
  optr->Arg_Car[6].typ = ATYC_I32;
  optr->Arg_Car[6].array_dim = "1";
  optr->Arg_Car[6].unite = "";
  optr->Arg_Car[6].type_sample = NULL;
  optr->Arg_Car[6].sample = NULL;

  /* seuil_duree */
  optr->Arg_Car[7].direction = DIR_IN;
  optr->Arg_Car[7].categorie = COEFFICIENT;
  optr->Arg_Car[7].typ = ATYC_I32;
  optr->Arg_Car[7].array_dim = "1";
  optr->Arg_Car[7].unite = "";
  optr->Arg_Car[7].type_sample = NULL;
  optr->Arg_Car[7].sample = NULL;

  /* Xcor */
  optr->Arg_Car[8].direction = DIR_OUT;
  optr->Arg_Car[8].categorie = VECTOR;
  optr->Arg_Car[8].typ = ATYC_IF32;
  optr->Arg_Car[8].array_dim = "1";
  optr->Arg_Car[8].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[8].sample = "$Arg1.sample";
  optr->Arg_Car[8].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[8].ref_time = "$Arg1.ref_time";
  optr->Arg_Car[8].unite = "$Arg1.unit";
  optr->Arg_Car[8].famille = "$Arg1.famille";
  optr->Arg_Car[8].misval = "$Arg2";
  optr->Arg_Car[8].name = "$Arg1.name + \" sans valeurs hors stat\"";
  optr->Arg_Car[8].en_name = "$Arg1.english_name + \" without outliers\"";
}
