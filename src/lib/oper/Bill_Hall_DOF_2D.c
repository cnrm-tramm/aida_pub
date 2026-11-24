/*******************************************************************
* OPERATOR      Bill_Hall_DOF_2D.c FUNCTION ANSI-C
*
* PURPOSE 	Utilise la methode developpee par Bill_Hall
*               afin d'analyser les donnees d'une sonde PMS-2DC.
*               Une amelioration a ete apportee afin de tenir compte du
*               depth-of-field DOF. Une correction a ete implementee afin de 
*               calculer les concentrations a l'aide du DOF selon
*               Baumgardner et Korolev (1997) (JAOT).
*		
* DESCRIPTION	
*		 
* VERSION       1.0
*
* ARGUMENTS     IN   double *  time_rg  second  base de temps d'arrivee
*               IN   int    *  img2d     any    donnees de la sonde PMS-2DC 
*               IN   double *  time_as  second  base de temps de depart
*               IN   short int *tas2d    any    clock TAS
*               IN   char *    codei     any    code d'identification de la sonde en hexadecimal
*                                               encadre par des guillemets. Ex.: "0x55000000"
*               IN   char *    maskds    any    masque en hexadecimal qui indique quels bits
*                                               utiliser dans les donnees. Ceci afin de pouvoir
*                                               supprimer certaines diodes. Doit etre specifie
*                                               encadre par des guillemets. Ex.: "0xffffffff"
*               IN   short int tempsb    any    nombre de bits de l'info de temps interne, soit
*                                               24 ou 32.
*               IN   long  int Nloop_as  any    nombre d'elements asynchrones selon time_as
*               IN   long  int tdebut    any    heure du debut d'analyse en secondes depuis minuit
*               IN   long  int tfin      any    heure de fin d'analyse en secondes depuis minuit
*               IN   short int tronqdeb  any    tronquature debut diode
*               IN   short int tronqfin  any    tronquature fin diode
*               IN   short int DOF_ok    any    si on calcule le spectre en nombre (0) ou
*                                               en concentrations cm-3 micron-1 (1)
*               IN   short int dof_pms   any    0 si on fait la correction du DOF, 1 si on veut utiliser
*                                               les valeurs non-corrigees de PMS
*               IN   float     xwid      any    dimensions en microns en X
*               IN   float     ywid      any    dimensions en microns en Y
*               OUT  float *spec2d    any    spectre total 2D de chaque bloc selon la methode Bill_Hall
*               OUT  float *specm2d   any    spectre moyen 2D selon la methode Bill Hall (non-tronquees)
*               OUT  float *specmt2d  any    spectre moyen 2D selon la methode Bill Hall (tronquees)
*               OUT  float *conc2d    any    spectre 2D de chaque bloc selon la methode Bill_Hall
*                                            (non-tronquees)
*               OUT  float *conct2d   any    spectre 2D de chaque bloc selon la methode Bill_Hall
*                                            (tronquees)
*
* ENTRY         NONE
*
* SUBPROGRAMS   NONE
*
* REFERENCES     
*             
* COPYRIGHT     Meteo-France
*               Centre National de Recherches Meteorologiques
*               GMEI/MNP
*               42, av. G. Coriolis
*               31057   TOULOUSE cedex
*              
*******************************************************************/

#define _POSIX_SOURCE 1
#define _XOPEN_SOURCE 600

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include <limits.h>

#include "struct_oper.h"

#include "2D_common.h"

typedef struct
{
  int *x, *y;
  int numpts;
}
dim_struct;

#define BYTES 32
#define TRUE 1
#define FALSE 0
#define NBINS 200
#define PANX 1024
#define PANY BYTES
#define NDIODES 32


/** Operateur mathematique morphologique erode pour une colonne */
void
erode_col (const int *imgin, int *imgout, int elem)
{
  int tmpimg = 0x00000000;
  unsigned long int mask = 0x00000001;
  int pos, left, right;

  tmpimg = imgin[elem];

  for (pos = 1; pos < (BYTES - 1); pos++)
    {
      right = pos - 1;
      left = pos + 1;
      if (((tmpimg >> right) & mask) & ((tmpimg >> left) & mask))
	(*imgout) |= (((tmpimg >> pos) & mask) << pos);
    }
}

/** This function sets the label it is at to the current label and then
 *   calls itself on all its eight neighbors that are one it ends when
 *   it has called itself on all eight neighbors. 
 */
static void
label_blob (const int *image, int *image1, dim_struct **dims, int row, int column, int width, int label)
{
  image1[row * width + column] = label;
  /* Enregistrer les coordonnees des points de chaque blob */
  /* Allocation de memoire dynamique */
  ((*dims)[label - 1].numpts)++;
  (*dims)[label - 1].x =
    realloc ((*dims)[label - 1].x,
	     ((*dims)[label - 1].numpts) * sizeof (int));
  if ((*dims)[label - 1].x == NULL)
    alloc_error (__FILE__, __LINE__);
  (*dims)[label - 1].y =
    realloc ((*dims)[label - 1].y,
	     ((*dims)[label - 1].numpts) * sizeof (int));
  if ((*dims)[label - 1].y == NULL)
    alloc_error (__FILE__, __LINE__);
  /* On assigne a row-1 et column-1 car on doit utiliser en source une image */
  /* une dimension (width+2)*(height+2)  a cause de la fonction presente */
  /* qui necessite des points vide aux frontieres */
  /* Et on veut ensuite utiliser ces coordonnees pour creer une image de width*height */
  (*dims)[label - 1].x[((*dims)[label - 1].numpts) - 1] = row - 1;
  (*dims)[label - 1].y[((*dims)[label - 1].numpts) - 1] = column - 1;

  if (image[(row - 1) * width + column] == 1
      && image1[(row - 1) * width + column] == 0)
    {
      label_blob (image, image1, dims, (row - 1), column, width, label);
    }
  if (image[(row - 1) * width + (column + 1)] == 1 &&
      image1[(row - 1) * width + (column + 1)] == 0)
    {
      label_blob (image, image1, dims, (row - 1), (column + 1), width, label);
    }
  if (image[(row) * width + (column + 1)] == 1 &&
      image1[(row) * width + (column + 1)] == 0)
    {
      label_blob (image, image1, dims, (row), (column + 1), width, label);
    }
  if (image[(row + 1) * width + (column + 1)] == 1 &&
      image1[(row + 1) * width + (column + 1)] == 0)
    {
      label_blob (image, image1, dims, (row + 1), (column + 1), width, label);
    }
  if (image[(row + 1) * width + (column)] == 1 &&
      image1[(row + 1) * width + (column)] == 0)
    {
      label_blob (image, image1, dims, (row + 1), (column), width, label);
    }
  if (image[(row + 1) * width + (column - 1)] == 1 &&
      image1[(row + 1) * width + (column - 1)] == 0)
    {
      label_blob (image, image1, dims, (row + 1), (column - 1), width, label);
    }
  if (image[(row) * width + (column - 1)] == 1 &&
      image1[(row) * width + (column - 1)] == 0)
    {
      label_blob (image, image1, dims, (row), (column - 1), width, label);
    }
  if (image[(row - 1) * width + (column - 1)] == 1 &&
      image1[(row - 1) * width + (column - 1)] == 0)
    {
      label_blob (image, image1, dims, (row - 1), (column - 1), width, label);
    }

  return;
}

/** This function labels the image scanning the image until it hits a pixel that
 * is one and has not been labeled. It then recursively calls a function that 
 * finds all pixels associated with this function and labels then with the same
 * label
 */
static void
lbl_image (const int *image, int *image1,  dim_struct **dims, int height, int width, int *nlabel)
{
  int i, j;
  int Label = 1;

  for (i = 1; i < height - 1; i++)
    {
      for (j = 1; j < width - 1; j++)
	{
	  if (image[i * width + j] == 1 && image1[i * width + j] == 0)
	    {
	      (*dims) = realloc (*dims, Label * sizeof (dim_struct));
	      if ((*dims) == NULL)
		alloc_error (__FILE__, __LINE__);
	      (*dims)[Label - 1].numpts = 0;
	      (*dims)[Label - 1].x = NULL;
	      (*dims)[Label - 1].y = NULL;
	      /* call recursive function */
	      label_blob (image, image1, dims, i, j, width, Label);
	      *nlabel = Label;
	      Label++;
	    }
	}
    }
}

/*------------------------------------------------------
  Component labeling
--------------------------------------------------------*/
static void
label_image (int **image, int *image1, dim_struct ** dims, int dim_ima,
	     int *width, int *height, int *nlabel)
{
  int i, j, totdim;
  int *tmpima = NULL;
  unsigned long int mask = 0x80000000;
  unsigned long int m;

  *width = dim_ima + 2;
  *height = BYTES + 2;
  totdim = (*width) * (*height);
  *nlabel = 0;

  (*image) = calloc (totdim, sizeof (int));
  if ((*image) == NULL)
    alloc_error (__FILE__, __LINE__);
  tmpima = calloc (totdim, sizeof (int));
  if (tmpima == NULL)
    alloc_error (__FILE__, __LINE__);
  (*dims) = malloc (sizeof (dim_struct));
  if ((*dims) == NULL)
    alloc_error (__FILE__, __LINE__);

  (*dims)[0].x = NULL;
  (*dims)[0].y = NULL;
  (*dims)[0].numpts = 0;

  for (i = 0; i < dim_ima; i++)
    {
      j = 0;
      for (m = mask; m != 0; m >>= 1)
	{
	  if (m & image1[i])
	    tmpima[(i + 1) + (j + 1) * (*width)] = 1;
	  j++;
	}
    }

  lbl_image (tmpima, (*image), dims, *height, *width, nlabel);

  free (tmpima);
  tmpima = NULL;
}




/** Recupere les coordonnees des pixels d'une image */
static int
get_dims (int *array, dim_struct * dims, int npts)
{
  unsigned long int mask = 0x80000000;
  unsigned long int m;
  int i;
  int area = 0;
  int ndims = 0;
  int x;

  for (i = 0; i < npts; i++)
    {
      x = 0;
      for (m = mask; m != 0; m >>= 1)
	{
	  if (m & array[i])
	    {
	      area++;
	      (*dims).x = realloc ((*dims).x, (ndims + 1) * sizeof (int));
	      if ((*dims).x == NULL)
		alloc_error (__FILE__, __LINE__);
	      (*dims).y = realloc ((*dims).y, (ndims + 1) * sizeof (int));
	      if ((*dims).y == NULL)
		alloc_error (__FILE__, __LINE__);
	      (*dims).x[ndims] = x;
	      (*dims).y[ndims] = i;
	      ndims++;
	    }
	  x++;
	}
    }

  (*dims).numpts = ndims;
  return area;
}


/** Trouve l'indice de la valeur dans un histogramme */
int
find_bin (const float *bins, float val, int nbins)
{
  int i;
  int bin = 0;

  for (i = 0; i < (nbins - 1); i++)
    if (val >= bins[i] && val < bins[i + 1])
      bin = i;

  return bin;
}

int
Bill_Hall_DOF_2D (const unsigned long int Nloop_rg,
		  const double *time_rg,
		  const int *img2d,
		  const double *time_as,
		  const short int *tas2d,
		  const char *codei,
		  const char *maskds,
		  const short int tempsb,
		  const unsigned long int Nloop_as,
		  const long int tdebut,
		  const long int tfin,
		  const short int tronqdeb,
		  const short int tronqfin,
		  const short int DOF_ok,
		  const short int dof_pms,
		  const float xwid,
		  const float ywid,
		  float *spec2d, float *specm2d, float *specmt2d,
		  float *conc2d, float *conct2d, float *mvd2d, float *lwc2d)
{

#define NCOEFF 6
#define NIND 8
  /* DOF Polynomial coefficients, 50% threshold level */
  float DOFPC[NIND * NCOEFF] = {
    /* TAS = 20 m/s */ -3.1903e-9, 9.9836e-7, -1.2411e-4, 1.4332e-2, -0.26909,
      1.6357,
    /* TAS = 40 m/s */ 2.9412e-9, -9.6296e-7, 1.1017e-4, 2.4316e-3, -0.14014,
      1.4101,
    /* TAS = 60 m/s */ 7.3223e-9, -2.6309e-6, 3.6032e-4, -1.5199e-2, 0.29372,
      -2.0261,
    /* TAS = 80 m/s */ 1.0707e-8, -4.2674e-6, 6.5974e-4, -4.1064e-2, 1.2062,
      -13.340,
    /* TAS = 100 m/s */ 4.7395e-9, -2.4150e-6, 4.7391e-4, -3.6523e-2, 1.3219,
      -17.934,
    /* TAS = 120 m/s */ 0, -5.4557e-7, 2.1603e-4, -2.3048e-2, 1.1053, -19.326,
    /* TAS = 140 m/s */ -1.6605e-8, 7.2186e-6, -1.1651e-3, 9.2008e-2, -3.4065,
      46.943,
    /* TAS = 160 m/s */ -2.2128e-8, 1.0829e-5, -2.0087e-3, 0.18109, -7.7577,
      125.88,
  };

  /* Compteurs */
  long int j, ii, jj, k, pos_rg;
  /**** Masques ****/
  /* Masque pour recuperer l'info bit par bit */
  unsigned long int mask = 0x80000000;
  /* Masque de temps */
  unsigned long int maskt = 0xff000000;
  /* Masque inverse de temps */
  unsigned long int masktd = 0x00ffffff;
  /* Masque plein */
  unsigned long int maskd = 0xffffffff;
  /* Masque du code de fin de separateur */
  unsigned long int bite = 0x55000000;
  /* Compteur mask */
  unsigned long int i;
  /* Variable de temps */
  double cur_time, sum_time, int_time, somme_int, dtime, time_deb;
  long int tdeb, tfi;
  /* Compteurs */
  long int count, counter;
  /* Position de l'image dans les donnees */
  long int prev_i, posp, posc;
  /* Nombre de bits */
  int b;
  /* Frequence d'echantillonnage */
  double freq;
  /* Verification des conditions de tronquature, splash et perim. min. */
  short int condition, tronque /*, splash, p3*/ , imgvide;
  /* Variables qui contiennent l'image des particules en traitement */
  int dim_ima;
  int *ima = NULL;
  int *ima_l = NULL;
  int *timg = NULL;
  int *tim = NULL;
  /* Variable pour l'acceptation des particules */
  int *accepted = NULL;
  int vali, reason;
  /* Dimensions des particules et variables reliees */
  float area, *aread, xdim, ydim, maxlng2, diam, xbl, xbr, d2, val;
  float *arat2, *arat, *dia, *dia2, *xmax, *ymax, *diaf, *aratf, *xcent,
    *ycent;
  float area_in, xa, xb, thetaa, thetab, r22, h1, ar_min;
  int *xstart, *xfin, *ystart, *yfin, yarat;
  /* Position des points des perimetres des particules */
  dim_struct *dims = NULL;
  dim_struct tdims;
  int nlabel;
  /* Taille de l'image */
  int width, height;
  /* Bins du spectre */
  float end_bins[NBINS + 1];
  int ind;
  float dofc[NBINS];
  /* LWC et MVD */
  float lwci2d[NBINS], lwc2dpro[NBINS], lwc2dprot;
  /* Comptage des particules */
  int *cnt2d = NULL;
  /* Valeurs de DOF, vitesse TAS et largeur de la surface effective */
  float DOF, speed, sample_area_width;
  /* Fichier spectre et LWC moyen */
  FILE *outptr = NULL;
  FILE *outptrl = NULL;

  /* Initialisation */
  count = counter = tronque = 0;
  (*lwc2d) = lwc2dprot = (*mvd2d) = 0.0;
  tdims.x = tdims.y = NULL;
  aread = arat2 = arat = aratf = dia = dia2 = xmax = ymax = diaf = xcent =
    ycent = NULL;
  ystart = yfin = xstart = xfin = accepted = NULL;
  if (xwid == 25.0 && ywid == 25.0)
    {
      dofc[0] = 1.25;
      dofc[1] = 5.00;
      dofc[2] = 11.25;
      dofc[3] = 20.00;
      dofc[4] = 31.25;
      dofc[5] = 45.0;
      for (i = 6; i < NBINS; i++)
	dofc[i] = 48.0;
    }
  else if (xwid == 200.0 && ywid == 200.0)
    {
      dofc[0] = 640.0;
      for (i = 1; i < NBINS; i++)
	dofc[i] = 1708.8;
    }
  for (i = 0; i < NBINS; i++)
    {
      lwci2d[i] = 0.0;
      lwc2dpro[i] = 0.0;
    }
  /* Aspect-ratio minimum */
  ar_min = 0.25;
  /* Comptage des particules: alloc memoire */
  cnt2d = malloc (Nloop_rg * sizeof (int));
  if (cnt2d == NULL)
    alloc_error (__FILE__, __LINE__);
  /* Initialisation bins du spectre */
  end_bins[0] = xwid;
  for (i = 1; i <= NBINS; i++)
    end_bins[i] = end_bins[i - 1] + xwid;
  for (i = 0; i < Nloop_rg; i++)
    {
      spec2d[i] = 0.0;
      cnt2d[i] = 0;
      for (j = 0; j < NBINS; j++)
	{
	  conc2d[j + i * NBINS] = 0.0;
	  conct2d[j + i * NBINS] = 0.0;
	  specm2d[j + i * NBINS] = 0.0;
	  specmt2d[j + i * NBINS] = 0.0;
	}
    }
  /* Position dans le vecteur de temps regulier */
  pos_rg = 1;
  /* Position de la fin de l'image precedente */
  prev_i = -1;
  /* Code d'identification de la sonde */
  /* Reglage du masque de separateur */
  (void) sscanf (codei, "%lx", &bite);
  /* Reglage du masque des diodes */
  (void) sscanf (maskds, "%lx", &maskd);
  /* Verification de l'argument du nombre de bits de temps interne et reglage du masque de temps */
  if (tempsb == 24)
    masktd = 0x00ffffff;
  else if (tempsb == 32)
    masktd = 0xffffffff;
  else
    {
      fprintf (stderr,
	       "\nLe nombre de bits pour le temps interne n'est pas 24 ou 32: %hd.\nOn doit quitter.\n",
	       tempsb);
      return (1);
    }

  /* Reglage des arguments de temps d'analyse */
  /* Si -1 est specifie, utiliser le debut ou la fin, respectivement */
  /* du set de donnees */
  if (tdebut == -1)
    tdeb = time_as[0];
  else
    tdeb = tdebut;
  if (tfin == -1)
    tfi = time_as[Nloop_as - 1];
  else
    tfi = tfin;

  /* Boucle sur le temps irregulier */
  for (j = 0; j < Nloop_as; j++)
    {

      /* Restreindre a la periode specifiee */
      if (time_as[j] >= tdeb && time_as[j] <= tfi)
	{

	  /* Somme des temps internes pour chaque record separement */
	  sum_time = 0.0;

	  /* La vitesse de l'avion est (TAS/2)+1 */
	  /* La frequence est de 4 MHz pour 100 m/s */
	  /* Donc, regle de trois pour calculer la frequence selon la donnee TAS */
	  freq = ((double) tas2d[j] / 2.0 + 1.0) * 4.0e6 / 100.0;

	  /* Somme des temps internes pour le record courant */
	  somme_int =
	    decodage_tint (img2d, counter, mask, maskt, masktd, bite, tempsb,
			   freq);
#ifdef DEBUG
	  printf ("%d %lf\n", j, somme_int);
#endif
	  /* Calcul du deltat du temps d'acquisition */
	  if (j > 0)
	    dtime = time_as[j] - time_as[j - 1];
	  else
	    /* Premier deltat arbitraire */
	    dtime = 0.333;
	  /* Temps du debut du record */
	  time_deb = time_as[j] - dtime;

	  printf ("Record time_deb=%f\n", time_deb);

	  /* Boucle sur le record de 1024 elements */
	  for (k = 0; k < 1024; k++)
	    {
	      /* Compteur de l'element courant du vecteur d'image 2D */
	      counter++;

	      /* Compteur du nombre de bits dans un element integer de l'image */
	      b = 0;
	      /* Temps interne */
	      int_time = 0.0;

	      /* On debute l'analyse au deuxieme record seulement car nous avons besoin */
	      /* d'un separateur qui precede le bloc a analyser */
	      if (counter > 1)
		/* Test pour marqueur: fin d'imagette et marqueur de temps */
		/* On teste pour trouver le marqueur de 8 bits en debut des mots binaires de 32 bits */
		/* Pour MERLIN-IV c'etait 01010101, donc 55 en hexa */
		if (tempsb == 24)
		  condition = ((maskt & img2d[counter - 1]) == bite);
		else
		  condition = TRUE;
	      if (img2d[counter] == bite && condition)
		{
		  /* On a trouve une fin d'imagette, donc on en debute une nouvelle */
		  /* et on analyse la precedente */

		  /* Calcul du temps interne en utilisant les 24 premiers bits du mot de 32 bits */
		  /* du marqueur de temps inclut dans les donnees d'images */
		  /* Le temps est en unite de temps d'horloge TAS, donc on doit diviser */
		  /* par la frequence */
		  int_time = (double) (masktd & img2d[counter - 1]) / freq;
		  /* Somme des temps internes pour l'imagette courante */
		  sum_time += int_time;
		  if (j > 0)
		    /* Calculer le temps courant de l'imagette courante */
		    /* en utilisant le temps de debut de record, la somme des temps interne */
		    /* pour le record courant et la somme des temps interne jusqu'a */
		    /* l'imagette courante */
		    if (somme_int != 0.0)
		      cur_time = time_deb + dtime * sum_time / somme_int;
		    else
		      cur_time = time_deb;
		  /* Recherche du bin de temps regulier ou tombe l'imagette presente */
		  /* Ensuite, on comptabilise le compte */
		  while (!
			 (cur_time < time_rg[pos_rg]
			  && cur_time >= time_rg[pos_rg - 1])
			 && pos_rg < Nloop_rg)
		    pos_rg++;
		  /* Re-essayer une seconde fois au cas ou on aurait deja depasse la position... */
		  if (pos_rg == Nloop_rg)
		    {
		      pos_rg = 0;
		      while (!
			     (cur_time < time_rg[pos_rg]
			      && cur_time >= time_rg[pos_rg - 1])
			     && pos_rg < Nloop_rg)
			pos_rg++;
		    }
		  /* Si la condition est respectee, on analyse l'imagette */
		  if (cur_time < time_rg[pos_rg]
		      && cur_time >= time_rg[pos_rg - 1]
		      && img2d[counter - 1] != bite)
		    {

		      /* Compte des imagettes */
		      count++;

		      /* Position de l'imagette dans le record */
		      posp = prev_i + 1;
		      posc = counter - 2;
		      /* La dimension de l'image contient une colonne de plus */
		      /* Pour la reconstruction de la premiere colonne manquante */
		      /* dans la methode de Bill Hall */
		      dim_ima = posc - posp + 1 + 1;
		      if (prev_i != -1 && dim_ima > 0 && posc >= posp)
			{
			  /* L'image est d'au moins une colonne */
			  /* *** Analyse de l'image *** */
			  ima = realloc (ima, dim_ima * sizeof (int));
			  if (ima == NULL)
			    alloc_error (__FILE__, __LINE__);
			  /* Stockage de l'image dans un vecteur temporaire */
			  /* On utilise i-posp+1 (le +1) car on va reconstruire */
			  /* la premiere colonne manquante */
			  imgvide = TRUE;
			  ima[0] = 0;
			  for (i = posp; i <= posc; i++)
			    {
			      ima[i - posp + 1] = (~(img2d[i])) & maskd;
			      if ((masktd & ima[i - posp]) != ~maskd)
				imgvide = FALSE;
			    }
			  /* Reconstruction de la premiere colonne */
			  /* total : nombre total de pixels occultes dans la 2e colonne */
			  if (total (ima, mask, 1, 1) > 0)
			    erode_col (ima, &(ima[0]), 1);
			  /* Label image blobs et recuperer coordonnees x,y de chaque blob */
			  nlabel = 0;
			  label_image (&ima_l, ima, &dims, dim_ima, &width,
				       &height, &nlabel);
			  /* Calculer dimensions particules */
			  if (nlabel > 0)
			    {
			      /* Re-alloc memoire */
			      accepted =
				realloc (accepted, nlabel * sizeof (int));
			      if (accepted == NULL)
				alloc_error (__FILE__, __LINE__);
			      dia = realloc (dia, nlabel * sizeof (float));
			      if (dia == NULL)
				alloc_error (__FILE__, __LINE__);
			      dia2 = realloc (dia2, nlabel * sizeof (float));
			      if (dia2 == NULL)
				alloc_error (__FILE__, __LINE__);
			      xmax = realloc (xmax, nlabel * sizeof (float));
			      if (xmax == NULL)
				alloc_error (__FILE__, __LINE__);
			      ymax = realloc (ymax, nlabel * sizeof (float));
			      if (ymax == NULL)
				alloc_error (__FILE__, __LINE__);
			      arat = realloc (arat, nlabel * sizeof (float));
			      if (arat == NULL)
				alloc_error (__FILE__, __LINE__);
			      aratf =
				realloc (aratf, nlabel * sizeof (float));
			      if (aratf == NULL)
				alloc_error (__FILE__, __LINE__);
			      diaf = realloc (diaf, nlabel * sizeof (float));
			      if (diaf == NULL)
				alloc_error (__FILE__, __LINE__);
			      aread =
				realloc (aread, nlabel * sizeof (float));
			      if (aread == NULL)
				alloc_error (__FILE__, __LINE__);
			      arat2 =
				realloc (arat2, nlabel * sizeof (float));
			      if (arat2 == NULL)
				alloc_error (__FILE__, __LINE__);
			      ystart =
				realloc (ystart, nlabel * sizeof (int));
			      if (ystart == NULL)
				alloc_error (__FILE__, __LINE__);
			      yfin = realloc (yfin, nlabel * sizeof (int));
			      if (yfin == NULL)
				alloc_error (__FILE__, __LINE__);
			      xstart =
				realloc (xstart, nlabel * sizeof (int));
			      if (xstart == NULL)
				alloc_error (__FILE__, __LINE__);
			      xfin = realloc (xfin, nlabel * sizeof (int));
			      if (xfin == NULL)
				alloc_error (__FILE__, __LINE__);
			      xcent =
				realloc (xcent, nlabel * sizeof (float));
			      if (xcent == NULL)
				alloc_error (__FILE__, __LINE__);
			      ycent =
				realloc (ycent, nlabel * sizeof (float));
			      if (ycent == NULL)
				alloc_error (__FILE__, __LINE__);

			      /* Boucle sur les particules d'une imagette */
			      for (i = 0; i < nlabel; i++)
				{
				  if (dims != NULL)
				    if (dims[i].numpts > 0)
				      {
					/* Surface en pixels */
					area = (float) dims[i].numpts;
					/* Surface en microns */
					aread[i] = area * xwid * ywid;
					/* Boite qui circonscrit la particule en pixels */
					xstart[i] =
					  arrayi_min (dims[i].x,
						    dims[i].numpts);
					xfin[i] =
					  arrayi_max (dims[i].x,
						    dims[i].numpts);
					ystart[i] =
					  arrayi_min (dims[i].y,
						    dims[i].numpts);
					yfin[i] =
					  arrayi_max (dims[i].y,
						    dims[i].numpts);

					/* Initialisation a acceptee */
					accepted[i] = 1;

					/* Centre de masse en pixels */
					xcent[i] =
					  (float) total_arrayi (dims[i].x,
								dims[i].
								numpts) /
					  area;
					ycent[i] =
					  (float) total_arrayi (dims[i].y,
								dims[i].
								numpts) /
					  area;
					/* Dimension en microns */
					xdim =
					  (float) (xfin[i] - xstart[i] +
						   1) * xwid;
					ydim =
					  (float) (yfin[i] - ystart[i] +
						   1) * ywid;
					/* Dimension y en pixels */
					yarat = yfin[i] - ystart[i] + 1;
		      /**** Calcul du diametre maximal ****/
					timg =
					  realloc (timg,
						   yarat * sizeof (int));
					if (timg == NULL)
					  alloc_error (__FILE__, __LINE__);
					/* Initialisation de l'image */
					for (ii = 0; ii < yarat; ii++)
					  timg[ii] = 0x00000000;
					/* Remplissage de l'image selon les coordonnees */
					for (ii = 0; ii < dims[i].numpts;
					     ii++)
					  {
					    if (dims[i].x[ii] >= BYTES)
					      {
						fprintf (stderr,
							 "Erreur dims[].x!!\n");
						return (1);
					      }
					    else
					      timg[dims[i].y[ii] -
						   ystart[i]] |=
						(1 <<
						 (BYTES - dims[i].x[ii] - 1));
					  }
					/* Creation d'une image ne contenant que le perimetre */
					/* en utilisant la technique d'erodage */
					tim =
					  realloc (tim, yarat * sizeof (int));
					if (tim == NULL)
					  alloc_error (__FILE__, __LINE__);
					if (yarat > 2)
					  {
					    erode (timg, tim, yarat);
					    for (ii = 0; ii < yarat; ii++)
					      tim[ii] = tim[ii] ^ timg[ii];
					  }
					else
					  /* Particule trop petite : l'erodage n'est pas necessaire */
					  for (ii = 0; ii < yarat; ii++)
					    tim[ii] = timg[ii];
					/* Recuperation des coordonnees du perimetre */
					area = get_dims (tim, &tdims, yarat);
					if (tdims.numpts < 500)
					  {
					    /* Calcul du diametre maximal */
					    maxlng2 = 0.0;
					    for (ii = 0; ii < tdims.numpts;
						 ii++)
					      for (jj = ii; jj < tdims.numpts;
						   jj++)
						{
						  val =
						    powf ((fabsf
							   ((float)
							    (tdims.x[ii] -
							     tdims.x[jj])) +
							   1) * xwid,
							  2.0) +
						    powf ((fabsf
							   ((float)
							    (tdims.y[ii] -
							     tdims.y[jj])) +
							   1) * ywid, 2.0);
						  if (val > maxlng2)
						    maxlng2 = val;
						}
					    diam = sqrtf (maxlng2);
			/****** Algorithme de reconstruction d'images tronquees ******/
					    xbl = xbr = 0.0;
					    for (ii = 0; ii < tdims.numpts;
						 ii++)
					      {
						if (tdims.x[ii] <= tronqdeb)
						  xbl += xwid;
						if (tdims.x[ii] >= tronqfin)
						  xbr += xwid;
					      }
					    /* Initialisation */
					    d2 = -1.0;
					    arat2[i] = -1.0;
					    area_in =
					      M_PI * 0.25 * powf (diam, 2.0);
					    reason = 0;
					    tronque = 0;
					    if ((xbl + xbr) > 0.0)
					      {
						tronque = 1;
						/* Reconstruction */
						if (!
						    ((xdim <
						      ((tronqfin - tronqdeb +
							1) * ydim))
						     && (xdim <
							 (0.2 * ydim))))
						  {
						    xa = xbl < xbr;
						    xb = xbl > xbr;
						    d2 =
						      sqrtf (powf
							     (xdim +
							      0.25 *
							      (powf (xb, 2.0)
							       - powf (xa,
								       2.0)) /
							      xdim,
							      2.0) + powf (xa,
									   2.0));
						    /* Nouvel aspect-ratio */
						    if (xa == 0.0)
						      {
							/* Simplement tronque */
							thetab =
							  2.0 * asinf (xb /
								       d2);
							if (xdim > (0.5 * d2))
							  thetab =
							    2.0 * M_PI -
							    thetab;
							area_in =
							  0.125 * thetab *
							  powf (d2,
								2.0) -
							  0.5 * (xb *
								 ((0.5 * d2) -
								  xdim));
						      }
						    else
						      {
							/* Doublement tronque */
							thetab =
							  2.0 * asinf (xb /
								       d2);
							thetaa =
							  2.0 * asinf (xa /
								       d2);
							r22 =
							  0.25 * powf (d2,
								       2.0);
							h1 =
							  sqrtf (r22 -
								 0.25 *
								 powf (xa,
								       2.0));
							area_in =
							  (M_PI -
							   0.5 * (thetab +
								  thetaa)) *
							  r22 +
							  0.5 * (xb *
								 (xdim - h1) +
								 xa * h1);
						      }
						    arat2[i] =
						      aread[i] / area_in;
			    /** Fin de la reconstruction **/
						  }
						else
						  {
						    /* Reconstruction impossible */
						    accepted[i] = 0;
						    reason = 10;
						  }
					      }
					    /* Assignation des valeurs */
					    dia[i] = diam;
					    arat[i] =
					      aread[i] / (M_PI *
							  powf (diam * 0.5,
								2.0));
					    dia2[i] = d2;
					    xmax[i] = xdim;
					    ymax[i] = ydim;
					    diaf[i] = dia[i];
					    aratf[i] = arat[i];
					    /* Image tronquees */
					    if (dia2[i] >= dia[i])
					      {
						diaf[i] = dia2[i];
						aratf[i] = arat2[i];
					      }
					    /* Rejet des particules */
					    if (aratf[i] < ar_min)
					      {
						/* Aspect-ratio trop petit */
						accepted[i] = 0;
						reason = 1;
					      }
					    /* Dimension en X trop grande p/r a Y */
					    if ((ydim < (6 * xwid))
						&& (xdim >= (3 * ydim)))
					      {
						accepted[i] = 0;
						reason = 2;
					      }
					    /* Dimension en X trop grande p/r a Y */
					    else if ((ydim < (24 * xwid))
						     && (xdim >= (6 * ydim)))
					      {
						accepted[i] = 0;
						reason = 3;
					      }
					    /* Dimension X trop grande */
					    else if (xdim >= (200 * xwid))
					      {
						accepted[i] = 0;
						reason = 4;
					      }
			/**** Traitement final des particules acceptees non-tronquees ****/
					    if (accepted[i] == 1
						&& tronque == 0)
					      {
						/* Trouver le bin */
						vali =
						  find_bin (end_bins, dia[i],
							    NBINS);
						/* Image vides dans le premier bin */
						if (imgvide == TRUE)
						  vali = 0;
						if (vali < NBINS)
						  {
						    if (DOF_ok == TRUE)
						      {
							/* Vitesse de l'avion */
							speed =
							  (float) tas2d[j] /
							  2.0 + 1.0;
							/* Indice dans la matrice des DOFs selon la vitesse */
							ind =
							  ((int)
							   (speed / 20.0)) -
							  1;
							if (ind >= 8)
							  {
							    printf
							      ("Erreur! ind=%d\n",
							       ind);
							    return (1);
							  }
							/* Calcul du DOF selon la methode Korolev avec le polynome */
							DOF =
							  DOFPC[5 +
								ind *
								NCOEFF] +
							  DOFPC[4 +
								ind *
								NCOEFF] *
							  end_bins[vali] +
							  DOFPC[3 +
								ind *
								NCOEFF] *
							  powf (end_bins
								[vali],
								2.0) +
							  DOFPC[2 +
								ind *
								NCOEFF] *
							  powf (end_bins
								[vali],
								3.0) +
							  DOFPC[1 +
								ind *
								NCOEFF] *
							  powf (end_bins
								[vali],
								4.0) +
							  DOFPC[ind *
								NCOEFF] *
							  powf (end_bins
								[vali], 5.0);
							/* Limite DOF a 61 mm pour le 2D-C et 267 mm pour le 2D-P */
							if (DOF > 61.0
							    && xwid == 25.0
							    && ywid == 25.0)
							  DOF = 61.0;
							else if (DOF > 267.0
								 && xwid ==
								 200.0
								 && ywid ==
								 200.0)
							  DOF = 267.0;
							/* Calcul du sample_area_width selon la methode entire-in */
							/* sample_area_width = (NDIODES * xwid - end_bins[vali]) * 1.0e-3; */
							/*                              if (sample_area_width <= 0.0) */
							sample_area_width =
							  (NDIODES * xwid) *
							  1.0e-3 +
							  2.0 *
							  (end_bins[vali] /
							   2.0 -
							   end_bins[vali] /
							   7.25) * 1.0e-7;
							if (sample_area_width
							    <= 0.0
							    || DOF <= 0.0)
							  val = 0.0;
							else
							  {
							    if (dof_pms != 1)
							      val =
								1000.0 /
								(DOF * speed *
								 sample_area_width);
							    else
							      val =
								1.0 / (speed *
								       100.0 *
								       dofc
								       [vali]
								       *
								       1.0e-2);
							  }
						      }
						    else
						      /* Spectre en nombre */
						      val = 1.0;
						    spec2d[pos_rg] += val;
						    conc2d[vali +
							   pos_rg * NBINS] +=
						      val;
						    cnt2d[pos_rg]++;
						  }
					      }
			/**** Traitement final des particules acceptees tronquees ****/
					    if (accepted[i] == 1
						&& tronque == 1)
					      {
						/* Trouver le bin */
						vali =
						  find_bin (end_bins, diaf[i],
							    NBINS);
						if (vali < NBINS)
						  {
						    if (DOF_ok == TRUE)
						      {
							/* Vitesse de l'avion */
							speed =
							  (float) tas2d[j] /
							  2.0 + 1.0;
							/* Indice dans la matrice des DOFs selon la vitesse */
							ind =
							  ((int)
							   (speed / 20.0)) -
							  1;
							if (ind >= 8)
							  {
							    printf
							      ("Erreur! ind=%d\n",
							       ind);
							    return (1);
							  }
							/* Calcul du DOF selon la methode Korolev avec le polynome */
							DOF =
							  DOFPC[5 +
								ind *
								NCOEFF] +
							  DOFPC[4 +
								ind *
								NCOEFF] *
							  end_bins[vali] +
							  DOFPC[3 +
								ind *
								NCOEFF] *
							  powf (end_bins
								[vali],
								2.0) +
							  DOFPC[2 +
								ind *
								NCOEFF] *
							  powf (end_bins
								[vali],
								3.0) +
							  DOFPC[1 +
								ind *
								NCOEFF] *
							  powf (end_bins
								[vali],
								4.0) +
							  DOFPC[ind *
								NCOEFF] *
							  powf (end_bins
								[vali], 5.0);
							/* Limite DOF a 61 mm pour le 2D-C et 267 mm pour le 2D-P */
							if (DOF > 61.0
							    && xwid == 25.0
							    && ywid == 25.0)
							  DOF = 61.0;
							else if (DOF > 267.0
								 && xwid ==
								 200.0
								 && ywid ==
								 200.0)
							  DOF = 267.0;
							if (dof_pms == 1)
							  DOF = dofc[vali];
							/* Calcul du sample_area_width (a corriger) */
							sample_area_width =
							  (NDIODES * xwid) *
							  1.0e-3 +
							  2.0 *
							  (end_bins[vali] /
							   2.0 -
							   end_bins[vali] /
							   7.25) * 1.0e-7;
							if (sample_area_width
							    <= 0.0
							    || DOF <= 0.0)
							  val = 0.0;
							else
							  {
							    if (dof_pms == 1)
							      val =
								1.0 / (speed *
								       100.0 *
								       dofc
								       [vali]
								       *
								       1.0e-2);
							    else
							      val =
								1000.0 /
								(DOF * speed *
								 sample_area_width);
							  }
						      }
						    else
						      /* Spectre en nombre */
						      val = 1.0;
						    conct2d[vali +
							    pos_rg * NBINS] +=
						      val;
						  }
					      }
					  }
				      }
				}
			    }
			  /* Liberation de la memoire */
			  if (ima_l != NULL)
			    {
			      free (ima_l);
			      ima_l = NULL;
			    }
			  if (dims != NULL)
			    {
			      for (ii = 0; ii < nlabel; ii++)
				{
				  if (dims[ii].x != NULL)
				    {
				      free (dims[ii].x);
				      dims[ii].x = NULL;
				    }
				  if (dims[ii].y != NULL)
				    {
				      free (dims[ii].y);
				      dims[ii].y = NULL;
				    }
				}
			      free (dims);
			      dims = NULL;
			    }
			}
		    }
		  /* Compteur precedent stocke */
		  prev_i = counter;

		  /* Verification du nombre de bits */
		  for (i = mask; i != 0; i >>= 1)
		    b++;
		  if (b != 32)
		    {
		      printf
			("Nombre de bits pas egal a 32! Doit stopper...\n");
		      if (ima != NULL)
			{
			  free (ima);
			  ima = NULL;
			}
		      /* Liberation de la memoire */
		      if (timg != NULL)
			{
			  free (timg);
			  timg = NULL;
			}
		      if (tim != NULL)
			{
			  free (tim);
			  tim = NULL;
			}
		      if (ima_l != NULL)
			{
			  free (ima_l);
			  ima_l = NULL;
			}
		      if (tdims.x != NULL)
			{
			  free (tdims.x);
			  tdims.x = NULL;
			}
		      if (tdims.y != NULL)
			{
			  free (tdims.y);
			  tdims.y = NULL;
			}
		      return (1);
		    }
		}
	    }
	}
    }

  printf ("Nloop_as = %lu\n", Nloop_as);
  printf ("Images = %ld\n", count);

  /* Ecriture du spectre moyen sur la periode dans un format ASCII pour xmgrace */
  outptr = fopen ("Spec_moy_Hall_2d.dat", "w");
  outptrl = fopen ("LWC_moy_Hall_2d.dat", "w");
  /* Calcul du spectre moyen */
  for (i = 0; i < NBINS; i++)
    {
      for (j = 0; j < Nloop_rg; j++)
	{
	  specm2d[i] += conc2d[i + j * NBINS];
	  specmt2d[i] += conct2d[i + j * NBINS];
	}
      if (DOF_ok == TRUE)
	{
	  specm2d[i] = specm2d[i] / (float) Nloop_rg;
	  specmt2d[i] = specmt2d[i] / (float) Nloop_rg;
	}
      if (outptr != NULL)
	if (i != 0)
	  if (specm2d[i] != 0.0 || specmt2d[i] != 0.0)
	    (void) fprintf (outptr, "%f %e %e %e\n", end_bins[i],
			    specm2d[i] / (end_bins[i + 1] - end_bins[i]),
			    specmt2d[i] / (end_bins[i + 1] - end_bins[i]),
			    (specm2d[i] + specmt2d[i]) / (end_bins[i + 1] -
							  end_bins[i]));
	  else if (specm2d[i] != 0.0 || specmt2d[i] != 0.0)
	    (void) fprintf (outptr, "%f %e %e %e\n", end_bins[i],
			    specm2d[i] / (end_bins[i] - end_bins[i - 1]),
			    specmt2d[i] / (end_bins[i] - end_bins[i - 1]),
			    (specm2d[i] + specmt2d[i]) / (end_bins[i] -
							  end_bins[i - 1]));
      /* Calcul du LWC */
      lwci2d[i] = (specm2d[i] * 1.0e6 *
		   powf ((end_bins[i + 1] + end_bins[i]) / 2.0,
			 3.0) * M_PI / 6.0 * 1.0e-12);
      (*lwc2d) += lwci2d[i];
      if (outptrl != NULL)
	(void) fprintf (outptrl, "%f %e\n", end_bins[i], lwci2d[i]);
    }
  if (outptr != NULL)
    (void) fclose (outptr);
  if (outptrl != NULL)
    (void) fclose (outptrl);

  for (i = 0; i < NBINS; i++)
    {
      lwc2dprot += (lwci2d[i] / (*lwc2d));
      lwc2dpro[i] = lwc2dprot;
      if (lwc2dprot > 0.5)
	{
	  if ((*lwc2d) != 0.0 && lwci2d[i] != 0)
	    (*mvd2d) =
	      end_bins[i] +
	      ((0.5 -
		lwc2dpro[i - 1]) / (lwci2d[i] / (*lwc2d))) * (end_bins[i +
								       1] -
							      end_bins[i]);
	  else
	    (*mvd2d) = 0.0;
	  printf ("MVD moyen sur la periode = %e microns\n", *mvd2d);
	  printf ("LWC total moyen sur la periode = %e g/m3\n", *lwc2d);
	  i = NBINS;
	}
    }

  /* Ecriture du spectre moyen pour AIDA (le meme spectre sur toute la periode) */
  for (i = 0; i < Nloop_rg; i++)
    {
      if (i != 0)
	for (j = 0; j < NBINS; j++)
	  {
	    specm2d[j + i * NBINS] = specm2d[j];
	    specmt2d[j + i * NBINS] = specmt2d[j];
	  }
      if (cnt2d[i] != 0)
	spec2d[i] = spec2d[i] / (float) cnt2d[i];
    }

  /* Liberation de la memoire */
  if (ima != NULL)
    {
      free (ima);
      ima = NULL;
    }
  if (timg != NULL)
    {
      free (timg);
      timg = NULL;
    }
  if (tim != NULL)
    {
      free (tim);
      tim = NULL;
    }
  if (ima_l != NULL)
    {
      free (ima_l);
      ima_l = NULL;
    }
  if (tdims.x != NULL)
    {
      free (tdims.x);
      tdims.x = NULL;
    }
  if (tdims.y != NULL)
    {
      free (tdims.y);
      tdims.y = NULL;
    }
  if (dims != NULL)
    {
      for (ii = 0; ii < nlabel; ii++)
	{
	  if (dims[ii].x != NULL)
	    {
	      free (dims[ii].x);
	      dims[ii].x = NULL;
	    }
	  if (dims[ii].y != NULL)
	    {
	      free (dims[ii].y);
	      dims[ii].y = NULL;
	    }
	}
      free (dims);
      dims = NULL;
    }

  return 0;
}

/* fonction d'enrobage */

int
OP_Bill_Hall_DOF_2D (unsigned long int NbVal, void *ArgList[], char *DiagExec)
{
  float mvd2d, lwc2d;
  int NCar;

  NCar = sprintf (DiagExec, "Bill_Hall_DOF_2D : (%ld echant.) ", NbVal) ;
  if (NCar < 0)
    NCar = 0;
  DiagExec += NCar;

  Bill_Hall_DOF_2D (NbVal,
		    (double *) ArgList[0],
		    (int *) ArgList[1],
		    (double *) ArgList[2],
		    (short int *) ArgList[3],
		    (char *) ArgList[4],
		    (char *) ArgList[5],
		    *((short int *) ArgList[6]),
		    *((long int *) ArgList[7]),
		    *((long int *) ArgList[8]),
		    *((long int *) ArgList[9]),
		    *((short int *) ArgList[10]),
		    *((short int *) ArgList[11]),
		    *((short int *) ArgList[12]),
		    *((short int *) ArgList[13]),
		    *((float *) ArgList[14]),
		    *((float *) ArgList[15]),
		    (float *) ArgList[16],
		    (float *) ArgList[17],
		    (float *) ArgList[18],
		    (float *) ArgList[19],
		    (float *) ArgList[20], &mvd2d, &lwc2d);

  NCar =
    sprintf (DiagExec,
	     "Bill_Hall_DOF_2D:: Valeurs moyennes: MVD = %e microns  LWC total = %e g/m3\n",
	     mvd2d, lwc2d);
  DiagExec += NCar;

  return OP_OK;
}

void
ID_Bill_Hall_DOF_2D (oper * optr)
{
  int ind;

  strcpy (optr->Nom, "Bill_Hall_DOF_2D");
  optr->Version = "1.0";
  optr->Date = "20/03/01";
  optr->fctptr = OP_Bill_Hall_DOF_2D;
  optr->NbArg = 21;

  ind = 0;
  optr->Arg_Car[ind].direction = DIR_IN;
  optr->Arg_Car[ind].categorie = VECTOR;
  optr->Arg_Car[ind].typ = ATYC_IF64;
  optr->Arg_Car[ind].array_dim = "1";
  optr->Arg_Car[ind].type_sample = "any";
  optr->Arg_Car[ind].sample = "any";
  optr->Arg_Car[ind].unite = "second";

  ind++;
  optr->Arg_Car[ind].direction = DIR_IN;
  optr->Arg_Car[ind].categorie = VECTOR;
  optr->Arg_Car[ind].typ = ATYC_I32;
  optr->Arg_Car[ind].array_dim = "1024";
  optr->Arg_Car[ind].type_sample = "any";
  optr->Arg_Car[ind].sample = "any";
  optr->Arg_Car[ind].unite = "count";

  ind++;
  optr->Arg_Car[ind].direction = DIR_IN;
  optr->Arg_Car[ind].categorie = VECTOR;
  optr->Arg_Car[ind].typ = ATYC_IF64;
  optr->Arg_Car[ind].array_dim = "1";
  optr->Arg_Car[ind].type_sample = "any";
  optr->Arg_Car[ind].sample = "any";
  optr->Arg_Car[ind].unite = "second";

  ind++;
  optr->Arg_Car[ind].direction = DIR_IN;
  optr->Arg_Car[ind].categorie = VECTOR;
  optr->Arg_Car[ind].typ = ATYC_I16;
  optr->Arg_Car[ind].array_dim = "1";
  optr->Arg_Car[ind].type_sample = "any";
  optr->Arg_Car[ind].sample = "any";
  optr->Arg_Car[ind].unite = "second";

  ind++;
  optr->Arg_Car[ind].direction = DIR_IN;
  optr->Arg_Car[ind].categorie = COEFFICIENT;
  optr->Arg_Car[ind].typ = ATYC_STRING;
  optr->Arg_Car[ind].array_dim = "1";
  optr->Arg_Car[ind].type_sample = "any";
  optr->Arg_Car[ind].sample = "any";
  optr->Arg_Car[ind].unite = "";

  ind++;
  optr->Arg_Car[ind].direction = DIR_IN;
  optr->Arg_Car[ind].categorie = COEFFICIENT;
  optr->Arg_Car[ind].typ = ATYC_STRING;
  optr->Arg_Car[ind].array_dim = "1";
  optr->Arg_Car[ind].type_sample = "any";
  optr->Arg_Car[ind].sample = "any";
  optr->Arg_Car[ind].unite = "";

  ind++;
  optr->Arg_Car[ind].direction = DIR_IN;
  optr->Arg_Car[ind].categorie = COEFFICIENT;
  optr->Arg_Car[ind].typ = ATYC_I16;
  optr->Arg_Car[ind].array_dim = "1";
  optr->Arg_Car[ind].type_sample = "any";
  optr->Arg_Car[ind].sample = "any";
  optr->Arg_Car[ind].unite = "";

  ind++;
  optr->Arg_Car[ind].direction = DIR_IN;
  optr->Arg_Car[ind].categorie = COEFFICIENT;
  optr->Arg_Car[ind].typ = ATYC_I32;
  optr->Arg_Car[ind].array_dim = "1";
  optr->Arg_Car[ind].type_sample = "any";
  optr->Arg_Car[ind].sample = "any";
  optr->Arg_Car[ind].unite = "";

  ind++;
  optr->Arg_Car[ind].direction = DIR_IN;
  optr->Arg_Car[ind].categorie = COEFFICIENT;
  optr->Arg_Car[ind].typ = ATYC_I32;
  optr->Arg_Car[ind].array_dim = "1";
  optr->Arg_Car[ind].type_sample = "any";
  optr->Arg_Car[ind].sample = "any";
  optr->Arg_Car[ind].unite = "";

  ind++;
  optr->Arg_Car[ind].direction = DIR_IN;
  optr->Arg_Car[ind].categorie = COEFFICIENT;
  optr->Arg_Car[ind].typ = ATYC_I32;
  optr->Arg_Car[ind].array_dim = "1";
  optr->Arg_Car[ind].type_sample = "any";
  optr->Arg_Car[ind].sample = "any";
  optr->Arg_Car[ind].unite = "";

  ind++;
  optr->Arg_Car[ind].direction = DIR_IN;
  optr->Arg_Car[ind].categorie = COEFFICIENT;
  optr->Arg_Car[ind].typ = ATYC_I16;
  optr->Arg_Car[ind].array_dim = "1";
  optr->Arg_Car[ind].type_sample = "any";
  optr->Arg_Car[ind].sample = "any";
  optr->Arg_Car[ind].unite = "";

  ind++;
  optr->Arg_Car[ind].direction = DIR_IN;
  optr->Arg_Car[ind].categorie = COEFFICIENT;
  optr->Arg_Car[ind].typ = ATYC_I16;
  optr->Arg_Car[ind].array_dim = "1";
  optr->Arg_Car[ind].type_sample = "any";
  optr->Arg_Car[ind].sample = "any";
  optr->Arg_Car[ind].unite = "";

  ind++;
  optr->Arg_Car[ind].direction = DIR_IN;
  optr->Arg_Car[ind].categorie = COEFFICIENT;
  optr->Arg_Car[ind].typ = ATYC_I16;
  optr->Arg_Car[ind].array_dim = "1";
  optr->Arg_Car[ind].type_sample = "any";
  optr->Arg_Car[ind].sample = "any";
  optr->Arg_Car[ind].unite = "";

  ind++;
  optr->Arg_Car[ind].direction = DIR_IN;
  optr->Arg_Car[ind].categorie = COEFFICIENT;
  optr->Arg_Car[ind].typ = ATYC_I16;
  optr->Arg_Car[ind].array_dim = "1";
  optr->Arg_Car[ind].type_sample = "any";
  optr->Arg_Car[ind].sample = "any";
  optr->Arg_Car[ind].unite = "";

  ind++;
  optr->Arg_Car[ind].direction = DIR_IN;
  optr->Arg_Car[ind].categorie = COEFFICIENT;
  optr->Arg_Car[ind].typ = ATYC_IF32;
  optr->Arg_Car[ind].array_dim = "1";
  optr->Arg_Car[ind].type_sample = "any";
  optr->Arg_Car[ind].sample = "any";
  optr->Arg_Car[ind].unite = "";

  ind++;
  optr->Arg_Car[ind].direction = DIR_IN;
  optr->Arg_Car[ind].categorie = COEFFICIENT;
  optr->Arg_Car[ind].typ = ATYC_IF32;
  optr->Arg_Car[ind].array_dim = "1";
  optr->Arg_Car[ind].type_sample = "any";
  optr->Arg_Car[ind].sample = "any";
  optr->Arg_Car[ind].unite = "";

  ind++;
  optr->Arg_Car[ind].direction = DIR_OUT;
  optr->Arg_Car[ind].categorie = VECTOR;
  optr->Arg_Car[ind].typ = ATYC_IF32;
  optr->Arg_Car[ind].array_dim = "1";
  optr->Arg_Car[ind].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[ind].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[ind].sample = "$Arg1.sample";
  optr->Arg_Car[ind].ref_time = " $Arg1.nom ";
  optr->Arg_Car[ind].unite = "liter-1*micron-1";
  optr->Arg_Car[ind].famille = " \"microphysique\" ";
  optr->Arg_Car[ind].misval = "-1.0";

  ind++;
  optr->Arg_Car[ind].direction = DIR_OUT;
  optr->Arg_Car[ind].categorie = VECTOR;
  optr->Arg_Car[ind].typ = ATYC_IF32;
  optr->Arg_Car[ind].array_dim = "200";
  optr->Arg_Car[ind].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[ind].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[ind].sample = "$Arg1.sample";
  optr->Arg_Car[ind].ref_time = " $Arg1.nom ";
  optr->Arg_Car[ind].unite = "liter-1*micron-1";
  optr->Arg_Car[ind].famille = " \"microphysique\" ";
  optr->Arg_Car[ind].misval = "-1.0";

  ind++;
  optr->Arg_Car[ind].direction = DIR_OUT;
  optr->Arg_Car[ind].categorie = VECTOR;
  optr->Arg_Car[ind].typ = ATYC_IF32;
  optr->Arg_Car[ind].array_dim = "200";
  optr->Arg_Car[ind].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[ind].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[ind].sample = "$Arg1.sample";
  optr->Arg_Car[ind].ref_time = " $Arg1.nom ";
  optr->Arg_Car[ind].unite = "liter-1";
  optr->Arg_Car[ind].famille = " \"microphysique\" ";
  optr->Arg_Car[ind].misval = "-1.0";

  ind++;
  optr->Arg_Car[ind].direction = DIR_OUT;
  optr->Arg_Car[ind].categorie = VECTOR;
  optr->Arg_Car[ind].typ = ATYC_IF32;
  optr->Arg_Car[ind].array_dim = "200";
  optr->Arg_Car[ind].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[ind].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[ind].sample = "$Arg1.sample";
  optr->Arg_Car[ind].ref_time = " $Arg1.nom ";
  optr->Arg_Car[ind].unite = "liter-1";
  optr->Arg_Car[ind].famille = " \"microphysique\" ";
  optr->Arg_Car[ind].misval = "-1.0";

  ind++;
  optr->Arg_Car[ind].direction = DIR_OUT;
  optr->Arg_Car[ind].categorie = VECTOR;
  optr->Arg_Car[ind].typ = ATYC_IF32;
  optr->Arg_Car[ind].array_dim = "200";
  optr->Arg_Car[ind].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[ind].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[ind].sample = "$Arg1.sample";
  optr->Arg_Car[ind].ref_time = " $Arg1.nom ";
  optr->Arg_Car[ind].unite = "liter-1";
  optr->Arg_Car[ind].famille = " \"microphysique\" ";
  optr->Arg_Car[ind].misval = "-1.0";
}
