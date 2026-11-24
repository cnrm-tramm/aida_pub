/*******************************************************************
* OPERATOR      Duroure_2D.c FUNCTION ANSI-C
*
* PURPOSE 	Utilise la methode developpee par Christophe Duroure du LAMP
*               afin d'analyser les donnees d'une sonde PMS-2DC.
*               Modifiee afin de rajouter les imagettes vides dans le premier bin du spectre.
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
*               IN   char *    sonde     any    2DC ou 2DP encadre par des guillemets.
*
*               OUT  float *spec2d    any    spectre total 2D de chaque bloc selon la methode Duroure
*               OUT  float *specm2d   any    spectre moyen 2D selon la methode Duroure
*               OUT  float *conc2d    any    spectre 2D de chaque bloc selon la methode Duroure
*               OUT  float *dmoy      any    diametre moyen
*               OUT  float *rug       any    rugosite moyenne
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

#define BYTES 32
#define TRUE 1
#define FALSE 0


/* Calcul du perimetre d'une particule */
int perim(const int *array, unsigned long int mask, long int posp, long int posc, const int *surf)
{
  int *dumi = NULL;
  long int dima, per, i;

  dima = posc - posp + 1;

  dumi = malloc(dima * sizeof(int));
  if (dumi == NULL) alloc_error(__FILE__, __LINE__);

  /* Erode : operant morphologique */
  erode(array, dumi, dima);
  /* Soustraction de l'image obtenue moins l'image originale */
  /* On obtient alors un perimetre */
  for (i=0; i<dima; i++)
    dumi[i] = array[i] ^ dumi[i];

  /* Somme des points du perimetre */
  per = total(dumi, mask, 0, dima-1);

  if (dumi != NULL)
    free(dumi);

  return per;
}

int
Duroure_2D (const unsigned long int Nloop_rg,
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
	    const char *sonde,
	    float *spec2d, float *specm2d, float *conc2d,
	    float *dmoy, float *rug)
{
  /* Nombre de bins pour le spectre */
#define NSE 30
#define NSET 50
  /* Espacement en microns de chaque bin */
#define SBIN 25
#define SBINT 100
#define SBINP 200
#define SBINTP 800

  /* Compteurs et compteur de position dans le vecteur de temps regulier */
  long int j, k, pos_rg;
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
  /* Compteur */
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
  /* Verification des conditions de tronquature, splash et perim. min., booleen pour imagettes vides */
  short int condition, tronq, tronq2, splash, p3, imgvide;
  /* Dimensions des particules */
  int xmi, xma, ymi, yma, dim_ima, lx, ly, nim, surf, su_i, dt;
  float su, val;  
  /* Nombre de particules comptees totale et de surface plus grande que 100 microns */
  float *nub, *nur;
  /* Vecteur des perimetre, surface, temps interne, dimensions X et Y et matrice d'image temporaire */
  int *per, *sur, *tima, *lxx, *lyy, *ima;
  /* Bins du spectre */
  /* effective sampling area 2DC mm-2 */
  float sech2dc[NSE] = { 1.17, 4.53, 9.84, 16.88, 25.39, 35.16, 36.6, 35.08, 33.55, 32.03, 30.5, 28.98,
			 27.45, 25.93, 24.4, 22.88, 21.35, 19.83, 18.30, 16.78, 15.25, 13.73, 12.2,
			 10.68, 9.15, 7.63, 6.1, 4.58, 3.05, 1.53 };
  /* effective sampling area 2DP mm-2 */
  float sech2dp[NSE] = { 620.0, 1602.0, 1548.6, 1495.2, 1441.8, 1388.4, 1335.0, 1281.6, 1228.2,
			 1174.8, 1121.4, 1068.0, 1014.6, 961.2, 907.8, 854.4, 801.0, 747.6, 694.2,
			 640.8, 587.4, 534.0, 480.6, 427.2, 373.8, 320.4, 267.0, 213.6, 160.2, 106.8 };
  /* Bins du spectre de particules tronquees */
  float secht2dc[NSET];
  float secht2dp[NSET];
  /* Fichier spectre moyen */
  FILE *outptr = NULL;
  /* Vecteurs des spectres moyen et de concentration */
  float specmt2d[NSET], *conct2d;
  
  /* Initialisation */
  count = counter = nim = 0;
  per = sur = tima = lxx = lyy = ima = NULL;
  /* Allocation de memoire */
  nub = malloc(Nloop_rg * sizeof(float));
  if (nub == NULL) alloc_error(__FILE__, __LINE__);
  nur = malloc(Nloop_rg * sizeof(float));
  if (nur == NULL) alloc_error(__FILE__, __LINE__);
  conct2d = malloc(Nloop_rg*NSET * sizeof(float));
  if (conct2d == NULL) alloc_error(__FILE__, __LINE__);
  /* Initialisation */
  for (i=0; i<Nloop_rg; i++) {
    for (j=0; j<NSE; j++) {
      conc2d[j+i*NSE] = 0.0;
      specm2d[j+i*NSE] = 0.0;
    }
    for (j=0; j<NSET; j++)
      conct2d[j+i*NSET] = 0.0;
    nub[i] = rug[i] = nur[i] = dmoy[i] = spec2d[i] = 0.0;
  }
  for (i=0; i<NSET; i++) {
    secht2dc[i] = fabsf(-48.8 + (((float)i)*48.8/8.0)) + 0.1;
    secht2dp[i] = fabsf(-1708.8 + (((float)i)*1708.8));
    specmt2d[i] = 0.0;
    for (j=0; j<Nloop_rg; j++)
      conct2d[i+j*NSET] = 0.0;
  }
  /* Intervalle de temps en secondes pour le calcul de la surface effective d'echantillonnage */
  dt = 1;
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

    /* Restreindre les calculs sur la periode de temps selectionnee */
    if (time_as[j] >= tdeb && time_as[j] <= tfi) {
    
      /* Somme des temps internes pour chaque record separement */
      sum_time = 0.0;
    
      /* La vitesse de l'avion est (TAS/2)+1 */
      /* La frequence est de 4 MHz pour 100 m/s */
      /* Donc, regle de trois pour calculer la frequence selon la donnee TAS */
      freq = ( (double)tas2d[j] / 2.0 + 1.0 ) * 4.0e6 / 100.0;

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
    
      printf("Record time_deb=%f\n",time_deb);

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
	  /* Re-essayer une seconde fois au cas ou... */
	  if (pos_rg == Nloop_rg) {
	    pos_rg = 0;
	    while ( !(cur_time < time_rg[pos_rg] && cur_time >= time_rg[pos_rg-1]) && pos_rg < Nloop_rg)
	      pos_rg++;	
	  }
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
	      imgvide = TRUE;
	      /* Stockage de l'image dans un vecteur temporaire */
	      for (i=posp; i<=posc; i++) {
		ima[i-posp] = ~(img2d[i]);
		if ( (masktd & ima[i-posp]) != ~maskd)
		  imgvide = FALSE;
	      }
	      if (imgvide == FALSE) {
		/* Imagette qui n'est pas vide */
		/* Calcul de la surface */
		surf = total(ima, mask, 0, dim_ima-1);
		/* Calcul de la boite qui encadre tous les pixels obscurcis */
		box2d(ima, mask, 0, dim_ima-1, &xmi, &xma, &ymi, &yma);
	      }
	      else {
		/* Imagette vide */
		surf = 1;
		xmi = xma = ymi = yma = 1;
	      }
	      if (xmi != -1 && xma != -1 && ymi != -1 && yma != -1) {
		/* Dimensions X et Y */
		lx = xma - xmi + 1;
		ly = yma - ymi + 1;
		/* Tests sur la tronquature, le splash ou le perimetre */
		tronq = (ymi != tronqdeb && yma <= tronqfin);
		splash = (lx < 4*ly);
		p3 = (lx >= 3 && ly >= 3);
		/* Doublement tronque */
		tronq2 = (ymi == tronqdeb && yma == tronqfin);
		if ( (tronq || tronq2) && splash) {
		  /* Nous n'avons pas une particule tronquee ou en splash */
		  /* ou bien nous avons une particule doublement tronquee mais pas en splash */
		  /* Allocation de memoire dynamique */
		  per = realloc(per, (nim+1) * sizeof(int));
		  if (per == NULL) alloc_error(__FILE__, __LINE__);
		  sur = realloc(sur, (nim+1) * sizeof(int));
		  if (sur == NULL) alloc_error(__FILE__, __LINE__);
		  tima = realloc(tima, (nim+1) * sizeof(int));
		  if (tima == NULL) alloc_error(__FILE__, __LINE__);
		  lxx = realloc(lxx, (nim+1) * sizeof(int));
		  if (lxx == NULL) alloc_error(__FILE__, __LINE__);
		  lyy = realloc(lyy, (nim+1) * sizeof(int));
		  if (lyy == NULL) alloc_error(__FILE__, __LINE__);
		  /* Calcul du perimetre si l'image est au moins contenue dans */
		  /* Une boite plus grande que 3x3 */
		  /* Sinon perimetre = surface */
		  if (p3)
		    per[nim] = perim(ima, mask, posp, posc, &surf);
		  else
		    /* Particule trop petite -> perimetre = surface */
		    per[nim] = surf;
		  /* Stockage de la surface */
		  sur[nim] = surf;
		  /* Stockage du temps interne */
		  tima[nim] = cur_time;
		  /* Stockage des dimensions X et Y */
		  lxx[nim] = lx;
		  lyy[nim] = ly;
		  /* Calcul des concentrations */
		  if (tronq && !tronq2) {
		    /* Non-tronquee */
		    su = sqrtf(4.0 * (float)sur[nim] / M_PI);
		    su_i = (int) su;
		  }
		  else if (tronq2) {
		    /* Doublement tronquee */
		    su = ((float) lx) / 4.0;
		    su_i = (int) su;
		  }
		  /* Imagette vide: premier bin du spectre */
		  if (imgvide == TRUE)
		    su_i = 0;
		  nub[pos_rg]++;
		  dmoy[pos_rg] += su;
		  if (sur[nim] > 100) {
		    /* Rugosite pour grosses particules */
		    rug[pos_rg] += (float) per[nim] / su;
		    nur[pos_rg]++;
		  }
		  if (tronq && !tronq2) {
		    /* Non-tronquee */
		    if (su <= (NSE-1)) {
		      if ( !strcmp(sonde, "2DC") )
			val = 1000.0 / (sech2dc[su_i] * ((float)tas2d[j] / 2.0 + 1.0) * (float)dt);
		      else
			val = 1000.0 / (sech2dp[su_i] * ((float)tas2d[j] / 2.0 + 1.0) * (float)dt);
		      conc2d[su_i+pos_rg*NSE] += val;
		      spec2d[pos_rg] += val;
		    }
		  }
		  else if (tronq2)
		    /* Doublement tronquee */
		    if (su <= (NSET-1))
		      if ( !strcmp(sonde, "2DC") ) {
			if (secht2dc[su_i] != 0.0 && su_i != 8)
			  conct2d[su_i+pos_rg*NSET] += 1000.0 /
			    (secht2dc[su_i] * ((float)tas2d[j] / 2.0 + 1.0) * (float)dt);
		      }
		      else {
			if (secht2dp[su_i] != 0.0)
			  conct2d[su_i+pos_rg*NSET] += 1000.0 /
			    (secht2dp[su_i] * ((float)tas2d[j] / 2.0 + 1.0) * (float)dt);
		      }
		  nim++;
		}
	      }
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
	    if (per != NULL)
	      free(per);
	    if (sur != NULL)
	      free(sur);
	    if (tima != NULL)
	      free(tima);
	    if (lxx != NULL)
	      free(lxx);
	    if (lyy != NULL)
	      free(lyy);
	    if (nub != NULL)
	      free(nub);
	    if (nur != NULL)
	      free(nur);
	    return 1;
	  }
	}
      }
    }
  }
  nim--;

  /* Ecriture du spectre moyen dans 2 fichiers en format ASCII pour xmgrace */
  /* Non-tronquees */
  outptr = fopen("Spec_moy_Duroure_2d.dat", "w");
  for (i=0; i<NSE; i++) {
    for (j=0; j<Nloop_rg; j++)
      specm2d[i] += conc2d[i+j*NSE];
    specm2d[i] = specm2d[i] / (float) Nloop_rg;
    if (outptr != NULL && specm2d[i] != 0.0)
      if ( !strcmp(sonde, "2DC") )
	(void) fprintf(outptr, "%lu %e\n", (i*SBIN)+SBIN, specm2d[i]/1000.0/(float)SBIN);
      else
	(void) fprintf(outptr, "%lu %e\n", (i*SBINP)+SBINP, specm2d[i]/1000.0/(float)SBINP);
  }
  if (outptr != NULL)
    (void) fclose(outptr);  

  /* Doublement tronquees */
  outptr = fopen("Spec_moyt_Duroure_2d.dat", "w");
  for (i=0; i<NSET; i++) {
    for (j=0; j<Nloop_rg; j++)
      specmt2d[i] += conct2d[i+j*NSET];
    specmt2d[i] = specmt2d[i] / (float) Nloop_rg;
    if (outptr != NULL && specmt2d[i] != 0.0)
      if ( !strcmp(sonde, "2DC") )
	(void) fprintf(outptr, "%lu %e\n", (i*SBINT)+SBINT, specmt2d[i]/1000.0/(float)SBINT);
      else
	(void) fprintf(outptr, "%lu %e\n", (i*SBINTP)+SBINTP, specmt2d[i]/1000.0/(float)SBINTP);
  }
  if (outptr != NULL)
    (void) fclose(outptr);
  
  /* Ecriture du spectre moyen pour AIDA (le meme spectre sur toute la periode) */
  for (i=0; i<Nloop_rg; i++) {
    if (i != 0)
      for (j=0; j<NSE; j++)
	specm2d[j+i*NSE] = specm2d[j];
    /* Calcul des diametres moyens et de la rugosite moyenne */
    if (nub[i] != 0.0)
      dmoy[i] = 25.0 * dmoy[i] / nub[i];
    if (nur[i] != 0.0)
      rug[i] = rug[i] / nur[i];
  }
  
  printf("Nloop_as = %lu\n",Nloop_as);
  printf("Images = %ld\n",count);

  /* Liberation de memoire */
  if (ima != NULL)
    free(ima);
  if (per != NULL)
    free(per);
  if (sur != NULL)
    free(sur);
  if (tima != NULL)
    free(tima);
  if (lxx != NULL)
    free(lxx);
  if (lyy != NULL)
    free(lyy);
  if (nub != NULL)
    free(nub);
  if (nur != NULL)
    free(nur);

  return 0;
}

/* fonction d'enrobage */

int
OP_Duroure_2D (unsigned long int NbVal, void *ArgList[], char *DiagExec)
{
  int CodRet;
  int NCar;

  NCar = sprintf (DiagExec, "Duroure_2D : (%ld echant.) ", NbVal) ;
  if (NCar < 0)
    NCar = 0;
  DiagExec += NCar;

  CodRet = Duroure_2D (NbVal,
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
		       (char *) ArgList[12],
		       (float *) ArgList[13],
		       (float *) ArgList[14],
		       (float *) ArgList[15],
		       (float *) ArgList[16],
		       (float *) ArgList[17]);
  
  return OP_OK;
}

void
ID_Duroure_2D (oper * optr)
{
  int ind = 0;

  strcpy (optr->Nom, "Duroure_2D");
  optr->Version = "1.0";
  optr->Date = "20/03/01";
  optr->fctptr = OP_Duroure_2D;

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
  optr->Arg_Car[ind].unite = "count";

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
  optr->Arg_Car[ind].unite = "sec";

  ind++;
  optr->Arg_Car[ind].direction = DIR_IN;
  optr->Arg_Car[ind].categorie = COEFFICIENT;
  optr->Arg_Car[ind].typ = ATYC_I32;
  optr->Arg_Car[ind].array_dim = "1";
  optr->Arg_Car[ind].type_sample = "any";
  optr->Arg_Car[ind].sample = "any";
  optr->Arg_Car[ind].unite = "sec";

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
  optr->Arg_Car[ind].typ = ATYC_STRING;
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
  optr->Arg_Car[ind].array_dim = "30";
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
  optr->Arg_Car[ind].array_dim = "30";
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
  optr->Arg_Car[ind].array_dim = "1";
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
  optr->Arg_Car[ind].array_dim = "1";
  optr->Arg_Car[ind].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[ind].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[ind].sample = "$Arg1.sample";
  optr->Arg_Car[ind].ref_time = " $Arg1.nom ";
  optr->Arg_Car[ind].unite = "liter-1";
  optr->Arg_Car[ind].famille = " \"microphysique\" ";
  optr->Arg_Car[ind].misval = "-1.0";

  optr->NbArg = ++ind;
}
