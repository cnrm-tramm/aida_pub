/*******************************************************************
* OPERATOR      Habit_2D.c FUNCTION ANSI-C
*
* PURPOSE 	Utilise la methode developpee par Korolev et Sussman (2000) JAOT
*               pour determiner les classes de particules.
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
*               IN   short int freq_o    any    nombre de records a traiter ensemble
*
*               OUT  float *irreg        any    fraction de particules irregulieres
*               OUT  float *dentr        any    fraction de particules dentrites
*               OUT  float *needl        any    fraction de particules needles
*               OUT  float *spher        any    fraction de particules spheriques
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
#define _XOPEN_SOURCE_EXTENDED 1

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include <limits.h>
#include "struct_oper.h"

#include "2D_common.h"

#define BYTES 32
#define TRUE 1
#define FALSE 0
/* Dimension en microns d'une diode selon l'axe Y */
#define DIMY 25.0
/* Nombre total minimal de pixel pour traitement */
#define NTOTAL 20

void cnedge(const int *, unsigned long int, long int, long int, short int, short int, int *, int *);
void bin_to_array(int **, int *, int, int *, int *);
void inverse_mat(float **, float **, int);
void c_to_f(float **, float *, int);
void f_to_c(float **, float *, int);
void print_c(float **, int);
int find_cat(float *, float, int);

int
Habit_2D (const unsigned long int Nloop_rg,
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
	  const short int freq_o,
	  float *irreg, float *dentr, float *needl, float *spher)
{

  /* Compteurs */
  long int j, ii, k, pos_rg, pos_rg_prev;
  /**** Masques ****/
  /* Masque pour recuperer l'info bit par bit */
  unsigned long int mask   = 0x80000000;
  /* Masque de temps */
  unsigned long int maskt  = 0xff000000;
  /* Masque inverse de temps */
  unsigned long int masktd = 0x00ffffff;
  /* Masque plein */
  unsigned long int maskd  = 0xffffffff;
  /* Masque du code de fin de separateur */
  unsigned long int bite   = 0x55000000;
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
  /* Dimensions en microns d'une diode */
  float dimx, dimy;
  /* Temps interne sur 24 ou 32 bits */
  short int condition;
  /* Dimension d'une image et nombre total de pixels d'une imagette */
  int dim_ima, ntotal;
  /* Variable temporaires pour une traitement des imagettes */
  int *ima, *ima_tmp, *ima_c, *ima_b, *ima_bi, *ima_ci, *ima_di, *ima_tmpi;
  int *ima_ei, *ima_fi;
  /* Nombre de pixels sur les bords et taille d'une imagette */
  int nedge1, nedge2, nedge, width, height;
  /* Coordonnees d'une imagette et dimensions X et Y */
  int xmi, xma, ymi, yma, nx, ny;
  /* Dimensions X et Y, surface en microns, et ratios */
  float dx, dy, surf, R1, R2;
  /* Compte des pixels valeur 2 et 3 dans la methode de determination du perimetre */
  int num2, num3;
  /* Calcul du perimetre equivalent a une particule circulaire */
  float perim, perimc;
  float x1, x2, y, z, r, theta1, theta2;
  /*** Matrices des ratios et distributions, et vecteur des fractions ***/
  /* Particules non-tronquees */
#define R1INUM 3
  float R1intrvl[R1INUM] = { 0.0, 1.07, 1.94 };
  float MR1[R1INUM];
  float fcatm1[R1INUM];
  float **B1, **B1inv, *B1invf;
  /* Particules tronquees */
#define R2INUM 4
  float R2intrvl[R2INUM] = { 0.0, 0.94, 1.16, 2.06 };
  float MR2[R2INUM];
  float fcatm2[R2INUM];
  float **B2, **B2inv, *B2invf;
  /* Categorie et normalisation */
  int cat, c1, c2, totp, totc, totcp;
  float totf;
  /* Pour calcul de l'inversion de matrice */
  char trans[2] = "T";
  float alpha, beta;
  /* int **MR1rg, **MR2rg; */
  /* Statistiques sur les rejets */
  int rejected_partials, rejected_tiny;
  /* Variable pour compter le nombre d'enregistrements, temps maximal pour inclure */
  /* les donnees afin d'obtenir le nombre d'enregistrements requis */
  /* Variables pour savoir si on peut calculer les fractions des particules completes */
  /* et partielles */
  int cur_f, max_dt, okc, okp;
  /* Regularisation */
  float negf;

  /* Alloc memoire */
  B1 = malloc(R1INUM * sizeof(float *));
  if (B1 == NULL) alloc_error(__FILE__, __LINE__);
  B1inv = malloc(R1INUM * sizeof(float *));
  if (B1inv == NULL) alloc_error(__FILE__, __LINE__);
  B1invf = malloc(R1INUM*R1INUM * sizeof(float));
  if (B1invf == NULL) alloc_error(__FILE__, __LINE__);
  for (i=0; i<R1INUM; i++) {
    B1[i] = malloc(R1INUM * sizeof(float));
    if (B1[i] == NULL) alloc_error(__FILE__, __LINE__);
    B1inv[i] = malloc(R1INUM * sizeof(float));
    if (B1inv[i] == NULL) alloc_error(__FILE__, __LINE__);
  }
  /* Initialisation matrice B1 des coefficients des distributions de base particules completes */
  B1[0][0] = 0.9803;
  B1[0][1] = 0.0197;
  B1[0][2] = 0.0;
  B1[1][0] = 0.2745;
  B1[1][1] = 0.7235;
  B1[1][2] = 0.0020;
  B1[2][0] = 0.0074;
  B1[2][1] = 0.3333;
  B1[2][2] = 0.6593;

  /* Alloc memoire */
  B2 = malloc(R2INUM * sizeof(float *));
  if (B2 == NULL) alloc_error(__FILE__, __LINE__);
  B2inv = malloc(R2INUM * sizeof(float *));
  if (B2inv == NULL) alloc_error(__FILE__, __LINE__);
  B2invf = malloc(R2INUM*R2INUM * sizeof(float));
  if (B2invf == NULL) alloc_error(__FILE__, __LINE__);
  for (i=0; i<R2INUM; i++) {
    B2[i] = malloc(R2INUM * sizeof(float));
    if (B2[i] == NULL) alloc_error(__FILE__, __LINE__);
    B2inv[i] = malloc(R2INUM * sizeof(float));
    if (B2inv[i] == NULL) alloc_error(__FILE__, __LINE__);
  }
  /* Initialisation matrice B2 des coefficients des distributions de base particules partielles */
  B2[0][0] = 0.0467;
  B2[0][1] = 0.9467;
  B2[0][2] = 0.0067;
  B2[0][3] = 0.0;
  B2[1][0] = 0.0117;
  B2[1][1] = 0.1780;
  B2[1][2] = 0.7869;
  B2[1][3] = 0.0234;
  B2[2][0] = 0.3493;
  B2[2][1] = 0.2059;
  B2[2][2] = 0.3346;
  B2[2][3] = 0.1103;
  B2[3][0] = 0.0;
  B2[3][1] = 0.0;
  B2[3][2] = 0.0591;
  B2[3][3] = 0.9409;

  /* Calcul des matrices B inverses */
  c1 = R1INUM;
  inverse_mat(B1inv, B1, c1);
  c_to_f(B1inv, B1invf, c1);
  c1 = R2INUM;
  inverse_mat(B2inv, B2, c1);
  c_to_f(B2inv, B2invf, c1);

  /* Initialisation */
  pos_rg_prev = 0;
  rejected_partials = 0;
  rejected_tiny = 0;
  cur_f = 0;
  max_dt = 180;
  for (i=0; i<R1INUM; i++)
    MR1[i] = 0.0;
  for (i=0; i<R2INUM; i++)
    MR2[i] = 0.0;
  ima = ima_tmp = ima_tmpi = ima_b = ima_bi = ima_c = ima_ci = ima_di = ima_ei = ima_fi = NULL;
  count = counter = 0;
  for (i=0; i<Nloop_rg; i++) {
    irreg[i] = 0.0;
    needl[i] = 0.0;
    spher[i] = 0.0;
    dentr[i] = 0.0;
  }
  /* Position dans le vecteur de temps regulier */
  pos_rg = 1;
  /* Position de la fin de l'image precedente */
  prev_i = -1;
  /* Code d'identification de la sonde */
  /* Reglage du masque de separateur */
  (void) sscanf(codei, "%lx", &bite);
  /* Reglage du masque des diodes */
  (void) sscanf(maskds, "%lx", &maskd);
  /* Verification de l'argument du nombre de bits de temps interne et reglage du masque de temps */
  if (tempsb == 24)
    masktd = 0x00ffffff;
  else if (tempsb == 32)
    masktd = 0xffffffff;
  else {
    fprintf(stderr, "\nLe nombre de bits pour le temps interne n'est pas 24 ou 32: %hd.\nOn doit quitter.\n", tempsb);
    return 1;
  }
  
  /* Reglage des arguments de temps d'analyse */
  /* Si -1 est specifie, utiliser le debut ou la fin, respectivement */
  /* du set de donnees */
  if (tdebut == -1)
    tdeb = time_as[0];
  else
    tdeb = tdebut;
  if (tfin == -1)
    tfi = time_as[Nloop_as-1];
  else
    tfi = tfin;

  /* Boucle sur le temps irregulier */
  for (j=0; j<Nloop_as; j++) {

    /* Restreindre sur le temps selectionne */
    if (time_as[j] >= tdeb && time_as[j] <= tfi) {
      
      /* Somme des temps internes pour chaque record separement */
      sum_time = 0.0;
      
      /* La vitesse de l'avion est (TAS/2)+1 */
      /* La frequence est de 4 MHz pour 100 m/s */
      /* Donc, regle de trois pour calculer la frequence selon la donnee TAS */
      freq = ( (double)tas2d[j] / 2.0 + 1.0 ) * 4.0e6 / 100.0;

      /* Calcul de la dimension que represente une diode en X selon le TAS */
      /* C'est egal a la dimension en Y si TAS=100 m/s */
      dimy = DIMY;
      dimx = ( (float)tas2d[j] / 2.0 + 1.0 ) * dimy / 100.0;

      /* Somme des temps internes pour le record courant */
      somme_int = decodage_tint(img2d, counter, mask, maskt, masktd, bite, tempsb, freq);
#ifdef DEBUG
      printf("%d %lf\n",j,somme_int);
#endif
      /* Calcul du deltat du temps d'acquisition */
      if (j > 0)
	dtime = time_as[j] - time_as[j-1];
      else
	/* deltat arbitraire pour le premier enregistrement */
	dtime = 0.333;
      /* Temps du debut du record */
      time_deb = time_as[j] - dtime;
    
      printf ("Record time_deb=%f\n", time_deb);

      /* Boucle sur le record de 1024 elements */
      for (k=0; k<1024; k++) {
      
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
	    condition = ((maskt & img2d[counter-1]) == bite);
	  else
	    condition = TRUE;
	if (img2d[counter] == bite && condition) {
	  /* On a trouve une fin d'imagette, donc on en debute une nouvelle */
	  /* et on analyse la precedente */

	  /* Calcul du temps interne en utilisant les 24 premiers bits du mot de 32 bits */
	  /* du marqueur de temps inclut dans les donnees d'images */
	  /* Le temps est en unite de temps d'horloge TAS, donc on doit diviser */
	  /* par la frequence */
	  int_time = (double) (masktd & img2d[counter-1]) / freq;
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
	  while ( !(cur_time < time_rg[pos_rg] && cur_time >= time_rg[pos_rg-1]) && pos_rg < Nloop_rg)
	    pos_rg++;	
	  /* Re-essayer une seconde fois au cas ou... car on pourrait avoir depasse la position */
	  if (pos_rg == Nloop_rg) {
	    pos_rg = 0;
	    while ( !(cur_time < time_rg[pos_rg] && cur_time >= time_rg[pos_rg-1]) && pos_rg < Nloop_rg)
	      pos_rg++;	
	  }
	  if (pos_rg_prev == 0)
	    pos_rg_prev = pos_rg;

	  /* Si la condition est respectee, on analyse l'imagette */
	  if (cur_time < time_rg[pos_rg] && cur_time >= time_rg[pos_rg-1] &&
	      img2d[counter-1] != bite) {

	    /* Compte des imagettes */
	    count++;
	    
	    /* Position de l'imagette dans le record */
	    posp = prev_i + 1;
	    posc = counter - 2;
	    dim_ima = posc - posp + 1;
	    if (prev_i != -1 && dim_ima > 0 && posc >= posp) {
	      /* L'image est d'au moins une colonne */
	      /* *** Analyse de l'image *** */
	      ima = realloc(ima, dim_ima * sizeof(int));
	      if (ima == NULL) alloc_error(__FILE__, __LINE__);
	      /* Stockage de l'image dans un vecteur temporaire */
	      for (i=posp; i<=posc; i++)
		ima[i-posp] = (~(img2d[i])) & maskd;
	      
	      /*** PREMIERE PARTIE ***/
	      /*** REJET DES MAUVAISES IMAGES ***/

	      /* 1- IMAGES TINY REJETEES */
	      /* Calcul du nombre total de pixels */
	      ntotal = total(ima, mask, 0, dim_ima-1);
	      if ( !(ntotal < NTOTAL) ) {
		/* 2- IMAGES PARTIELLES REJETEES */
		/* Calcul de nedge */
		cnedge(ima, mask, 0, dim_ima-1, tronqdeb, tronqfin, &nedge1, &nedge2);
		nedge = nedge1 + nedge2;
		/* Calcul de ny */
		box2d(ima, mask, 0, dim_ima-1, &xmi, &xma, &ymi, &yma);
		nx = xma - xmi + 1;
		ny = yma - ymi + 1;
		if ( !(ntotal <= 180 && nedge >= 4 && ny < (tronqfin-tronqdeb+1)) ) {
		  /* 3- IMAGES COMPLETES : TRAITEMENT */
		  if ( ntotal > NTOTAL && nedge < 4 ) {
		    /* Calcul de dx, dy et surf */
		    dx = dimx * nx;
		    dy = dimy * ny;
		    surf = (dimx*dimy) * ntotal;
		    /* Calcul de R1 */
		    R1 = M_PI * ( powf(dx, 2.0) + powf(dy, 2.0) ) /
		      ( 8.0 * surf );
		    cat = find_cat(R1intrvl, R1, R1INUM);
		    MR1[cat] += 1.0;
		    /* Recherche du bin de temps regulier ou tombe l'imagette presente */
		    /* Ensuite, on comptabilise le compte */
		    if (cur_time < time_rg[pos_rg])
		      pos_rg = 0;
		    while ( !(cur_time < time_rg[pos_rg] && cur_time >= time_rg[pos_rg-1]) )
		      pos_rg++;

		  }
		  else if ( ntotal > 180 && (nedge >= 4 || ny == (tronqfin-tronqdeb+1)) ) {
		    /* 4- IMAGES PARTIELLES ACCEPTEES : TRAITEMENT */
		    /*** Calcul du perimetre ***/
		    ima_tmp = realloc(ima_tmp, dim_ima * sizeof(unsigned long int));
		    if (ima_tmp == NULL) alloc_error(__FILE__, __LINE__);
		    ima_b = realloc(ima_b, dim_ima * sizeof(unsigned long int));
		    if (ima_b == NULL) alloc_error(__FILE__, __LINE__);
		    ima_c = realloc(ima_c, dim_ima * sizeof(unsigned long int));
		    if (ima_c == NULL) alloc_error(__FILE__, __LINE__);
		    ima_tmpi = realloc(ima_tmpi, dim_ima * BYTES * sizeof(int));
		    if (ima_tmpi == NULL) alloc_error(__FILE__, __LINE__);
		    ima_bi = realloc(ima_bi, dim_ima * BYTES * sizeof(int));
		    if (ima_bi == NULL) alloc_error(__FILE__, __LINE__);
		    ima_ci = realloc(ima_ci, dim_ima * BYTES * sizeof(int));
		    if (ima_ci == NULL) alloc_error(__FILE__, __LINE__);
		    ima_di = realloc(ima_di, dim_ima * BYTES * sizeof(int));
		    if (ima_di == NULL) alloc_error(__FILE__, __LINE__);
		    ima_ei = realloc(ima_ei, dim_ima * BYTES * sizeof(int));
		    if (ima_ei == NULL) alloc_error(__FILE__, __LINE__);
		    ima_fi = realloc(ima_fi, dim_ima * BYTES * sizeof(int));
		    if (ima_fi == NULL) alloc_error(__FILE__, __LINE__);
		    /* Calculer image B */
		    /* Shift image A up */
		    for (ii=0; ii<dim_ima; ii++)
		      ima_tmp[ii] = (ima[ii] << 1);
		    /* Sum result with original image A */
		    for (ii=0; ii<dim_ima; ii++)
		      ima_b[ii] = (ima_tmp[ii] ^ ima[ii]);
		    /* Calculer image C */
		    /* Shift image A left */
		    for (ii=0; ii<(dim_ima-1); ii++)
		      ima_tmp[ii] = ima[ii+1];
		    ima_tmp[dim_ima-1] = 0x00000000;
		    /* Sum result with original image A */
		    for (ii=0; ii<dim_ima; ii++)
		      ima_c[ii] = (ima_tmp[ii] ^ ima[ii]);		    
		    /* Calculer image D */
		    bin_to_array(&ima_bi, ima_b, dim_ima, &width, &height);
		    bin_to_array(&ima_ci, ima_c, dim_ima, &width, &height);
		    for (ii=0; ii<(dim_ima*BYTES); ii++)
		      ima_di[ii] = ima_bi[ii] + ima_ci[ii];
		    /* Calculer image E */
		    /* Shift image B right */
		    for (ii=0; ii<(dim_ima-1); ii++)
		      ima_tmp[ii+1] = ima_b[ii];
		    ima_tmp[0] = 0x00000000;
		    /* Sum result with original image C */
		    bin_to_array(&ima_tmpi, ima_tmp, dim_ima, &width, &height);
		    for (ii=0; ii<(dim_ima*BYTES); ii++)
		      ima_ei[ii] = ima_tmpi[ii] + ima_ci[ii];
		    /* Calculer image F et calculer N2 et N3 */
		    /* Sum E and D */
		    num2 = num3 = 0;
		    for (ii=0; ii<(dim_ima*BYTES); ii++) {
		      ima_fi[ii] = ima_ei[ii] + ima_di[ii];
		      if (ima_fi[ii] == 2)
			num2++;
		      else if (ima_fi[ii] == 3)
			num3++;
		    }
		    /* Calculer le perimetre */
		    /* Pour l'instant, dans le calcul du perimetre, on suppose */
		    /* que les pixels sont carres!!! */
		    perim = (float) dimy * ((float) num2 + sqrtf(2.0) * (float) num3);
		    /* Calcul du perimetre equivalent pour une particule circulaire */
		    /* On suppose les pixels carres !!! */
		    x1 = (float) (dimy * nedge1);
		    x2 = (float) (dimy * nedge2);
		    y = (float) dimy * ny;
		    r = sqrtf( powf(x1, 2.0)/4.0 +
			       powf( (y/2.0 + (powf(x2, 2.0) - powf(x1, 2.0))/(8.0*y)), 2.0 ) );
		    z = (powf(x1, 2.0) - powf(x2, 2.0)) / (8.0*y) - y/2.0 + r;
		    theta1 = M_PI - 2.0 * atanf(x1 / (2.0 * z));
		    theta2 = M_PI - 2.0 * atanf(x2 / (2.0 * (z+y)));
		    perimc = 2.0 * (theta2 - theta1) * r;
		    R2 = perim / perimc;
		    cat = find_cat(R2intrvl, R2, R2INUM);
		    MR2[cat] += 1.0;
		  }
		}
		else
		  /* Rejected partials */
		  rejected_partials++;
	      }
	      else
		/* Tiny images */
		rejected_tiny++;
            }
	  }
	  /* Compteur precedent stocke */
	  prev_i = counter;
	  
	  /* Verification du nombre de bits */
	  for ( i=mask; i != 0; i >>= 1 )
	    b++;
	  if (b != 32) {
	    printf("Nombre de bits pas egal a 32! Doit stopper...\n");
	    if (ima != NULL)
	      free(ima);
	    if (ima_tmp != NULL)
	      free(ima_tmp);
	    if (ima_b != NULL)
	      free(ima_b);
	    if (ima_c != NULL)
	      free(ima_c);
	    if (ima_bi != NULL)
	      free(ima_bi);
	    if (ima_ci != NULL)
	      free(ima_ci);
	    if (ima_di != NULL)
	      free(ima_di);
	    if (ima_ei != NULL)
	      free(ima_ei);
	    if (ima_fi != NULL)
	      free(ima_fi);
	    ima = ima_tmp = ima_b = ima_c = ima_bi = ima_ci = ima_di = ima_ei = ima_fi = NULL;
	    return 1;
	  }
	}
      }
      cur_f++;
      if (cur_f >= freq_o) {
	/*** On a assez d'enregistrements pour effectuer le calcul des fractions ***/
	if ((time_rg[pos_rg]-time_rg[pos_rg_prev+1]) > max_dt) {
	  /* Le temps maximal a ete depasse: nous avons trop peu de donnees s'etalant */
	  /* sur une trop grande periode: on met tout a zero  */
	  for (ii=(pos_rg_prev+1); ii<= pos_rg; ii++) {
	    spher[ii] = 0.0;
	    irreg[ii] = 0.0;
	    needl[ii] = 0.0;
	    dentr[ii] = 0.0;
	  }
	  pos_rg_prev = pos_rg;
	}
	else {
	  /* Normalisation */
	  totc = 0;
	  for (ii=0; ii<R1INUM; ii++)
	    totc += (int) MR1[ii];
	  if (totc != 0)
	    for (ii=0; ii<R1INUM; ii++)
	      MR1[ii] = MR1[ii] / (float) totc;
	
	  totp = 0;
	  for (ii=0; ii<R2INUM; ii++)
	    totp += (int) MR2[ii];
	  if (totp != 0)
	    for (ii=0; ii<R2INUM; ii++)
	      MR2[ii] = MR2[ii] / (float) totp;
	
	/* Calcul du vecteur des fractions */
	/* Particules completes */
	  c1 = R1INUM;
	  c2 = 1;
	  alpha = 1.0;
	  beta = 0.0;
	  sgemv(trans, &c1, &c1, &alpha, B1invf, &c1, MR1, &c2, &beta, fcatm1, &c2);
	  /*	printf("\nImages completes Spheres Irregulieres Needles\n");
		for (ii=0; ii<R1INUM; ii++)
		printf("%f ",MR1[ii]);
		printf("\n");
		for (ii=0; ii<R1INUM; ii++)
		printf("%f ",fcatm1[ii]);
		printf("\n\n");*/
	/* Particules partielles */
	  c1 = R2INUM;
	  sgemv(trans, &c1, &c1, &alpha, B2invf, &c1, MR2, &c2, &beta, fcatm2, &c2);
	  /*	printf("\nImages partielles Spheres Irregulieres Needles Dentrites/Aggregates\n");
		for (ii=0; ii<R2INUM; ii++)
		printf("%f ",MR2[ii]);
		printf("\n");
		for (ii=0; ii<R2INUM; ii++)
		printf("%f ",fcatm2[ii]);
		printf("\n\n");*/

	  /*** Particules completes ***/
	  /* Verification: calcul du total des fractions: doit etre egal a 1 */
	  okc = TRUE;
	  totf = 0.0;
	  for (ii=0; ii<R1INUM; ii++)
	    totf += fcatm1[ii];
	  if ( (totf > 1.0001 || totf < 0.999) && totf != 0.0) {
	    printf("TOTF=%f",totf);
	    printf("\nImages completes Spheres Irregulieres Needles\n");
	    for (ii=0; ii<R1INUM; ii++)
	      printf("%f ",MR1[ii]);
	    printf("\n");
	    for (ii=0; ii<R1INUM; ii++)
	      printf("%f ",fcatm1[ii]);
	    printf("\n\n");
	  }
	  if (totf > 1.0001 || totf < 0.999)
	    okc = FALSE;
	  /*** Regularization ***/
	  negf = 0.0;
	  /* Calculer somme des fractions negatives et les mettre a zero */
	  for (ii=0; ii<R1INUM; ii++)
	    if (fcatm1[ii] < 0.0) {
	      negf += fcatm1[ii];
	      fcatm1[ii] = 0.0;
	    }
	  /* Distribuer les valeurs negatives parmi les positives */
	  for (ii=0; ii<R1INUM; ii++)
	    if (fcatm1[ii] > 0.0)
	      fcatm1[ii] += (fcatm1[ii] * negf);
	  /* Nouveau total */
	  totf = 0.0;
	  for (ii=0; ii<R1INUM; ii++)
	    totf += fcatm1[ii];
	  /* Renormaliser a 1.0 */
	  if (totf != 0.0)
	    for (ii=0; ii<R1INUM; ii++)
	      fcatm1[ii] = fcatm1[ii] / totf;
	  /* Refaire la verification de la normalisation */
	  totf = 0.0;
	  for (ii=0; ii<R1INUM; ii++)
	    totf += fcatm1[ii];
	  for (ii=0; ii<R1INUM; ii++)
	    if (fcatm1[ii] < 0.0 || fcatm1[ii] > 1.0)
	      printf("fcatm1 %f\n",fcatm1[ii]);
	  /* Stockage des fractions selon le poids des particules completes */
	  if (okc == TRUE) 
	    for (ii=(pos_rg_prev+1); ii<= pos_rg; ii++) {
	      spher[ii] = (float)totc*fcatm1[0];
	      irreg[ii] = (float)totc*fcatm1[1];
	      needl[ii] = (float)totc*fcatm1[2];
	      dentr[ii] = 0.0;
	      /*	    printf("%d %d %f %f %f\n",pos_rg_prev+1,pos_rg,fcatm1[0],fcatm1[1],fcatm1[2]);*/
	    }
	  else
	    for (ii=(pos_rg_prev+1); ii<= pos_rg; ii++) {
	      spher[ii] = 0.0;
	      irreg[ii] = 0.0;
	      needl[ii] = 0.0;
	      dentr[ii] = 0.0;
	      /*	    printf("%d %d %f %f %f\n",pos_rg_prev+1,pos_rg,fcatm1[0],fcatm1[1],fcatm1[2]);*/
	    }
	  /*** Particules partielles */
	  /* Verification: calcul du total des fractions: doit etre egal a 1 */
	  okp = TRUE;
	  totf = 0.0;
	  for (ii=0; ii<R2INUM; ii++)
	    totf += fcatm2[ii];
	  if ( (totf > 1.0001 || totf < 0.999) && totf != 0.0) {
	    printf("TOTF=%f",totf);
	    printf("\nImages partielles Spheres Irregulieres Needles Dentrites\n");
	    for (ii=0; ii<R2INUM; ii++)
	      printf("%f ",MR2[ii]);
	    printf("\n");
	    for (ii=0; ii<R2INUM; ii++)
	      printf("%f ",fcatm2[ii]);
	    printf("\n\n");
	  }
	  if (totf > 1.0001 || totf < 0.999)
	    okp = FALSE;
	  /*** Regularization ***/
	  negf = 0.0;
	  /* Calculer somme des fractions negatives et les mettre a zero */
	  for (ii=0; ii<R2INUM; ii++)
	    if (fcatm2[ii] < 0.0) {
	      negf += fcatm2[ii];
	      fcatm2[ii] = 0.0;
	    }
	  /* Distribuer les valeurs negatives parmi les positives */
	  for (ii=0; ii<R2INUM; ii++)
	    if (fcatm2[ii] > 0.0)
	      fcatm2[ii] += (fcatm2[ii] * negf);
	  /* Nouveau total */
	  totf = 0.0;
	  for (ii=0; ii<R2INUM; ii++)
	    totf += fcatm2[ii];
	  /* Renormaliser a 1.0 */
	  if (totf != 0.0)
	    for (ii=0; ii<R2INUM; ii++)
	      fcatm2[ii] = fcatm2[ii] / totf;
	  for (ii=0; ii<R1INUM; ii++)
	    if (fcatm1[ii] < 0.0 || fcatm1[ii] > 1.0)
	      printf("fcatm1 %f\n",fcatm1[ii]);
	  /* Stockage des fractions selon le poids des particules partielles */
	  if (okp == TRUE) {
	    for (ii=(pos_rg_prev+1); ii<= pos_rg; ii++) {
	      spher[ii] += (float)totp*fcatm2[0];
	      irreg[ii] += (float)totp*fcatm2[1];
	      needl[ii] += (float)totp*fcatm2[2];
	      dentr[ii] += (float)totp*fcatm2[3];
	    }
	    /*	    printf("%d %d %f %f %f\n",pos_rg_prev+1,pos_rg,fcatm1[0],fcatm1[1],fcatm1[2]);*/
	  }

	  /* Combiner fractions completes et partielles selon leur poids */
	  totcp = 0;
	  if (okc == TRUE)
	    totcp += totc;
	  if (okp == TRUE)
	    totcp += totp;
	  if (totcp != 0)
	    for (ii=(pos_rg_prev+1); ii<= pos_rg; ii++) {
	      spher[ii] = spher[ii] / (float) totcp;
	      irreg[ii] = irreg[ii] / (float) totcp;
	      needl[ii] = needl[ii] / (float) totcp;
	      dentr[ii] = dentr[ii] / (float) totcp;
	    }  
	  pos_rg_prev = pos_rg;
	}

	/* Re-initialiser a zero pour une autre periode de calcul */
	for (ii=0; ii<R1INUM; ii++) {
	  MR1[ii] = 0.0;
	  fcatm1[ii] = 0.0;
	}
	for (ii=0; ii<R2INUM; ii++) {
	  MR2[ii] = 0.0;
	  fcatm2[ii] = 0.0;
	}
	
	cur_f = 0;
      }
    }
  }

  /* Mettre la valeur a 1.0 pour un pas de temps pour echelle graphique dans AIDA */
  spher[pos_rg] = 1.0;
  irreg[pos_rg] = 1.0;
  needl[pos_rg] = 1.0;
  dentr[pos_rg] = 1.0;

  /* Stats */
  printf("Echantillons images completes ");
  for (ii=0; ii<R1INUM; ii++)
    printf("%f ",MR1[ii]);
  printf("\n");
  printf("Echantillons images partielles ");
  for (ii=0; ii<R2INUM; ii++)
    printf("%f ",MR2[ii]);
  printf("\n\n");
  printf("Images rejetees:\n");
  printf("Tiny %d %f%%\n", rejected_tiny, (float)rejected_tiny/(float)count*100.0);
  printf("Partielles %d %f%%\n", rejected_partials, (float)rejected_partials/(float)count*100.0);
  printf("\n");
  
  printf("Nloop_as = %lu\n",Nloop_as);
  printf("Images = %ld\n",count);

  /* Liberation memoire */
  if (ima != NULL)
    free(ima);
  if (ima_tmp != NULL)
    free(ima_tmp);
  if (ima_b != NULL)
    free(ima_b);
  if (ima_c != NULL)
    free(ima_c);
  if (ima_bi != NULL)
    free(ima_bi);
  if (ima_ci != NULL)
    free(ima_ci);
  if (ima_di != NULL)
    free(ima_di);
  if (ima_ei != NULL)
    free(ima_ei);
  if (ima_fi != NULL)
    free(ima_fi);
  ima = ima_tmp = ima_b = ima_c = ima_bi = ima_ci = ima_di = ima_ei = ima_fi = NULL;
  
  return 0;
}

/* fonction d'enrobage */

int
OP_Habit_2D (unsigned long int NbVal, void *ArgList[], char *DiagExec)
{
  int CodRet;
  int NCar;

  NCar = sprintf (DiagExec, "Habit_2D : (%ld echant.) ", NbVal) ;
  if (NCar < 0)
    NCar = 0;
  DiagExec += NCar;

  CodRet = Habit_2D (NbVal,
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
		     *((long int *) ArgList[10]),
		     *((short int *) ArgList[11]),
		     *((short int *) ArgList[12]),
		     (float *) ArgList[13],
		     (float *) ArgList[14],
		     (float *) ArgList[15],
		     (float *) ArgList[16]);
  
  return OP_OK;
}

void
ID_Habit_2D (oper * optr)
{
  int ind;

  strcpy (optr->Nom, "Habit_2D");
  optr->Version = "1.0";
  optr->Date = "20/03/01";
  optr->fctptr = OP_Habit_2D;
  optr->NbArg = 17;

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
  optr->Arg_Car[ind].direction = DIR_OUT;
  optr->Arg_Car[ind].categorie = VECTOR;
  optr->Arg_Car[ind].typ = ATYC_IF32;
  optr->Arg_Car[ind].array_dim = "1";
  optr->Arg_Car[ind].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[ind].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[ind].sample = "$Arg1.sample";
  optr->Arg_Car[ind].ref_time = " $Arg1.nom ";
  optr->Arg_Car[ind].unite = "percent";
  optr->Arg_Car[ind].famille = " \"microphysique\" ";
  optr->Arg_Car[ind].misval = "-1.0";

  ind++;
  optr->Arg_Car[ind].direction = DIR_OUT;
  optr->Arg_Car[ind].categorie = VECTOR;
  optr->Arg_Car[ind].typ = ATYC_IF32;
  optr->Arg_Car[ind].array_dim = "1";
  optr->Arg_Car[ind].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[ind].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[ind].sample = "$Arg1.sample";
  optr->Arg_Car[ind].ref_time = " $Arg1.nom ";
  optr->Arg_Car[ind].unite = "percent";
  optr->Arg_Car[ind].famille = " \"microphysique\" ";
  optr->Arg_Car[ind].misval = "-1.0";

  ind++;
  optr->Arg_Car[ind].direction = DIR_OUT;
  optr->Arg_Car[ind].categorie = VECTOR;
  optr->Arg_Car[ind].typ = ATYC_IF32;
  optr->Arg_Car[ind].array_dim = "1";
  optr->Arg_Car[ind].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[ind].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[ind].sample = "$Arg1.sample";
  optr->Arg_Car[ind].ref_time = " $Arg1.nom ";
  optr->Arg_Car[ind].unite = "percent";
  optr->Arg_Car[ind].famille = " \"microphysique\" ";
  optr->Arg_Car[ind].misval = "-1.0";

  ind++;
  optr->Arg_Car[ind].direction = DIR_OUT;
  optr->Arg_Car[ind].categorie = VECTOR;
  optr->Arg_Car[ind].typ = ATYC_IF32;
  optr->Arg_Car[ind].array_dim = "1";
  optr->Arg_Car[ind].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[ind].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[ind].sample = "$Arg1.sample";
  optr->Arg_Car[ind].ref_time = " $Arg1.nom ";
  optr->Arg_Car[ind].unite = "percent";
  optr->Arg_Car[ind].famille = " \"microphysique\" ";
  optr->Arg_Car[ind].misval = "-1.0";
}

/* Calcul du nombre de diodes obscurcies sur les bords dans une imagette */
void cnedge(const int *array, unsigned long int mask, long int dima, long int dimb,
	    short int tronqdeb, short int tronqfin, int *nedge1, int *nedge2)
{
  unsigned long int i;
  long int k;

  *nedge1 = 0;
  *nedge2 = 0;
  
  /* Compte sur les X */
  for (k=dima; k<=dimb; k++) {
    i = mask;
    if (tronqdeb > 0)
      i >>= tronqdeb;
    if (i & array[k])
      (*nedge1)++;
    i >>= tronqfin;
    if (i & array[k])
      (*nedge2)++;
  }
}

/* Transforme des donnees d'imagettes de format integer binaires en matrices integer */
void bin_to_array(int **image, int *image1, int dim_ima, int *width, int *height)
{
  int i, j, totdim;
  unsigned long int mask = 0x80000000;
  unsigned long int m;

  *width = dim_ima;
  *height = BYTES;
  totdim = (*width) * (*height);

  for (i=0; i<dim_ima; i++) {
    j = 0;
    for (m = mask; m != 0; m >>= 1 ) {
      if (m & image1[i])
	(*image)[i + j * (*width)] = 1;
      else
	(*image)[i + j * (*width)] = 0;
      j++;
    }
  }
}

/* Transforme des donnees d'imagettes de format matrices integer en format integer binaire */
void array_to_bin(int **image, int *image1, int dim_ima)
{
  int i, j, totdim;
  unsigned long int mask = 0x80000000;
  unsigned long int m;

  for (i=0; i<dim_ima; i++) {
    (*image)[i] = 0x00000000;
    for (j=0; j<BYTES; j++) {
      (*image)[i] |= ( image1[i+j*dim_ima] << (BYTES-j-1) );
      printf("IM1 %d\n",image1[i+j*dim_ima]);
      printf("%d %d %x\n",i,j,(*image)[i]);
    }
  }
}

/* Inversion de matrice LAPACK */
void inverse_mat(float **mat_inv, float **mat, int size)
{
  int i, c1, c2, ok;
  int *pivot = NULL;
  float *matf = NULL;
  float *matf_ori = NULL;
  float *work = NULL;
  float *identityf = NULL;
  float **identity = NULL;
  char trans[2] = "N";
  float alpha, beta;

  /* Allocation memoire */
  identityf = malloc((size*size) * sizeof(float));
  if (identityf == NULL) alloc_error(__FILE__, __LINE__);
  matf = malloc((size*size) * sizeof(float));
  if (matf == NULL) alloc_error(__FILE__, __LINE__);
  matf_ori = malloc((size*size) * sizeof(float));
  if (matf_ori == NULL) alloc_error(__FILE__, __LINE__);
  pivot = malloc((size*size) * sizeof(int));
  if (pivot == NULL) alloc_error(__FILE__, __LINE__);

  identity = malloc(size * sizeof(float *));
  if (identity == NULL) alloc_error(__FILE__, __LINE__);
  for (i=0; i<size; i++) {
    identity[i] = malloc(size * sizeof(float));
    if (identity[i] == NULL) alloc_error(__FILE__, __LINE__);
  }

  /* Conversion de la matrice c -> fortran */
  c_to_f(mat, matf, size);
  /*  printf("Matrice originale:\n");
      print_c(mat, size);
      printf("\n");*/
  
  /* Copier la matrice originale dans une autre matrice */
  for (i=0; i<(size*size); i++)
    matf_ori[i] = matf[i];

  /* Dimension de la matrice */
  c1 = size;
  
  /* Trouver la factorisation LU et determiner le pivot */
  sgetrf(&c1, &c1, matf, &c1, pivot, &ok);
  if (ok != 0) {
    printf("Erreur dans le calcul du pivot de la matrice = %d\n",ok);
    exit(1);
  }
  
  /* Calcul de la matrice inverse */
  c2 = c1*10;
  work = malloc(c2 * sizeof(float));
  if (work == NULL) alloc_error(__FILE__, __LINE__);
  sgetri(&c1, matf, &c1, pivot, work, &c2, &ok);
  if (ok != 0) {
    printf("Erreur dans le calcul de l'espace work = %d\n",ok);
    exit(1);
  }

  /* Conversion fortran -> c */
  f_to_c(mat_inv, matf, size);
  /* printf("Matrice inverse:\n");
     print_c(mat_inv, size);
     printf("\n");*/

  /* Multiplication de la matrice par son inverse pour verif */
  alpha = 1.0;
  beta = 0.0;
  sgemm(trans, trans, &c1, &c1, &c1, &alpha, matf_ori, &c1, matf, &c1, &beta,
	identityf, &c1);

  /* Conversion fortran -> c */
  f_to_c(identity, identityf, size);
  /*  printf("Matrice identite si l'inversion est correcte:\n");
      print_c(identity, size);
      printf("\n");*/

  /* Liberation memoire */
  free(work);
  free(matf);
  free(matf_ori);
  free(identity);
  for (i=0; i<size; i++)
    free(identity[i]);
}

/* Transfert des indices d'une matrice du langage C vers Fortran */
void c_to_f (float **c, float *f, int size) {
/* Transforms a row-major 2d matrix array in C to a 1d column major array to be
used lapack subroutines  */

  int i, j;
  
  for (i = 0; i < size; i++) {
    for (j = 0 ; j < size; j++) {
      f[j + size*i] = c[j][i];
    }
  }
}

/* Transfert des indices d'une matrice du langage Fortran vers le C */
void f_to_c (float **c, float *f, int size) {
/* Transforms a  1d column major array submitted by lapack to a row-major 2d 
matrix array which can be displayd easily.  */

  int i, j;
  
  for (i = 0; i < size; i++) {
    for (j = 0 ; j < size; j++) {
      c[j][i] = f[j + size*i];
    }
  }
}

/* Imprime une matrice langage C */
void print_c (float **c, int size) {
  int i, j;
  
  printf("\n\n\n");
  for (i=0; i<size ; i++) {
    for (j=0; j<size; j++) {
      printf("%f\t", c[i][j]);
    }
    printf("\n");
  }
  printf("\n\n\n");
}  

/* Trouve la categorie d'une valeur dans un vecteur et retourne l'indice */
int find_cat(float *vect, float val, int num)
{
  int i;

  for (i=1; i<num; i++) {
    if (val > vect[i-1] && val <= vect[i])
      return (i-1);
  }
  if (val > vect[num-1])
    return (num-1);
  else
    return -1;
}

/*
 * mis en commentaire le 09/08/2002 par BP
 * Car provoque une boucle infinie avec la
 * macro définie dans "struct_oper.h"
 */
 
/*
int finite(double value)
{
  return isfinite(value);
}
*/
