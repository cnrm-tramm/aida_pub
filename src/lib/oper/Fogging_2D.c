/*******************************************************************
* OPERATOR      Fogging_2D.c FUNCTION ANSI-C
*
* PURPOSE 	Indice de detection de Fogging presents dans les donnees 2D
*               et nettoyage des donnees images 2D
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
*               OUT  int *fogging        any    indice de fogging
*               OUT  int *img2d_clean    any    donnees de la sonde PMS-2DC nettoyees
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
#define RECL 1024
#define TRUE 1
#define FALSE 0
/* Dimensiosn en micron d'une diode selon l'axe des Y */
#define DIMY 25.0

int
Fogging_2D (const unsigned long int Nloop_rg,
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
	    int *fogging,
	    int *img2d_clean)
{

  /* Compteurs */
  long int j, ii, jj, im, k, pos_rg, pos_rg_prev, pos_as_prev;
  /**** Masques ****/
  /* Masque pour recuperer l'info bit par bit */
  unsigned long int mask   = 0x80000000;
  /* Masque de temps */
  unsigned long int maskt  = 0xff000000;
  /*** Masques pour le fogging ***/
  /* Masque pour ligne d'epaisseur 1 */
  unsigned long int maskfe  = 0xe0000000;
  /* Masque pour ligne d'epaisseur 2 */
  unsigned long int maskfed = 0xf0000000;
  /* Masque du critere de fogging ligne epaisseur 1 */
  unsigned long int maskfc  = 0x40000000;
  /* Masque du critere de fogging ligne epaisseur 2 */
  unsigned long int maskfcd = 0x60000000;
  /* Masque recuperation de bit ligne epaisseur 1 */
  unsigned long int masko   = 0x00000001;
  /* Masque recuperation de bit ligne epaisseur 2 */
  unsigned long int maskod  = 0x00000003;
  /* Masque vide */
  unsigned long int maskv   = 0x00000000;
  /* Masque inverse de temps */
  unsigned long int masktd = 0x00ffffff;
  /* Masque plein */
  unsigned long int maskd  = 0xffffffff;
  /* Masque du code de fin de separateur */
  unsigned long int bite   = 0x55000000;
  /* Compteur mask */
  unsigned long int i, m, ims;
  /* Variable de temps */
  double cur_time, sum_time, int_time, somme_int, dtime, time_deb;
  long int tdeb, tfi;
  /* Compteurs */
  long int count, counter;
  /* Position de l'image dans les donnees */
  long int prev_i, posp, posc, pos;
  /* Nombre de bits */
  int b;
  /* Frequence d'echantillonnage */
  double freq;
  /* Dimensions en microns d'une diode */
  float dimx, dimy;
  /* Temps interne sur 24 ou 32 bits */
  short int condition;
  /* Dimension d'une image et variable pour compter le nombre d'enregistrements */
  int dim_ima, cur_f;
  /* Variable temporaire pour une imagette */
  int *ima;
  /* Indice de fogging */
  int count_fogging = 0;
  /* Variable pour debugging pour imprimer temps */
  int hr, minutes;
  double sec;

  /* Initialisation */
  ima = NULL;
  count = counter = cur_f = 0;
  pos_rg_prev = pos_as_prev = 0;
  for (i=0; i<Nloop_rg; i++)
    fogging[i] = 0;
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

      /* Boucle sur le record de RECL elements */
      for (k=0; k<RECL; k++) {
      
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

	      /* Recherche de pixels noirs entoures de 2 blancs de chaque cote a la verticale */
	      for (i=0; i<dim_ima; i++) {
		m = maskfe;
		for ( ii=maskfc; ii != 0x00000001; ii >>= 1 ) {
		  if ( ( ima[i] & m ) == ii )
		    count_fogging++;
		  m >>= 1;
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
	    ima = NULL;
	    return 1;
	  }
	}
      }
      cur_f++;
      if (cur_f >= freq_o) {
	for (ii=(pos_rg_prev+1); ii<= pos_rg; ii++)
	  fogging[ii] = count_fogging;
	/* Test pour savoir si traitement image 2D */
	if (count_fogging >= 1000) {
	  /*	  printf("%d %d %f %f\n",pos_as_prev+1,j,time_as[pos_as_prev+1],time_as[j]);
	  hr = (int)time_as[pos_as_prev+1] / 3600;
	  minutes = (int) (time_as[pos_as_prev+1] - hr*3600.0) / 60;
	  sec = (double) (time_as[pos_as_prev+1] - hr*3600.0 - minutes*60.0);
	  printf("%02d:%02d:%06.3lf", hr, minutes, sec);
	  hr = (int)time_as[j] / 3600;
	  minutes = (int) (time_as[j] - hr*3600.0) / 60;
	  sec = (double) (time_as[j] - hr*3600.0 - minutes*60.0);
	  printf(" %02d:%02d:%06.3lf\n", hr, minutes, sec);*/
	  for (jj=(pos_as_prev+1); jj<=j; jj++) {
	    for (ii=1; ii<RECL; ii += 2) {
	      /* Test marqueur de fin */
	      if (img2d[ii+jj*RECL] == bite) {
		img2d_clean[(ii-1)+jj*RECL] = img2d[(ii-1)+jj*RECL];
		img2d_clean[ii+jj*RECL] = bite;
	      }
	      else {
		/* Nettoyer l'image */
		for (im=((ii-1)+jj*RECL); im<=(ii+jj*RECL); im++) {
		  img2d_clean[im] = maskv;
		  /* Fogging d'une ligne */
		  m = maskfe;
		  pos = BYTES-2;
		  for ( ims=maskfc; ims != 0; ims >>= 1 ) {
		    /*		      printf("%x %x %x %x %x %x\n",~(img2d[im]),maskd,((~(img2d[im])) & maskd),m,( ((~(img2d[im])) & maskd) & m ),ims);*/
		    if ( ( ((~(img2d[im])) & maskd) & m ) != ims ) {
		      /* Ne pas supprimer le pixel */
		      img2d_clean[im] |= ( (((~(img2d[im]))>>pos)&masko)<<pos );
		      /*						  printf("NO %d %x %x %x %x %x\n",pos,~img2d[im],img2d_clean[im],((~(img2d[im]))>>pos),( (((~(img2d[im]))>>pos)&masko)<<pos ),(((~(img2d[im]))>>pos)&masko));*/
		    }
		    m >>= 1;
		    pos--;
		  }
		  /* Fogging de deux lignes */
		  m = maskfed;
		  pos = BYTES-3;
		  for ( ims=maskfcd; ims != 0x00000001; ims >>= 1 ) {
		    /*		    printf("%x %x %x %x %x %x\n",img2d_clean[im],maskd,((img2d_clean[im]) & maskd),m,( ((img2d_clean[im]) & maskd) & m ),ims);*/
		    if ( ( (~(img2d[im])) & m ) == ims ) {
		      /* Supprimer le pixel de fogging */
		      img2d_clean[im] &= ~( ( (((~(img2d[im]))>>pos)&maskod)<<pos ) );
		      /*		      printf("YE %d %d %x %x %x %x %x %x\n",im,pos,~img2d[im],img2d_clean[im],((img2d_clean[im])>>pos),( (((img2d_clean[im])>>pos)&maskv)<<pos ),(((img2d_clean[im])>>pos)&maskod),maskod);*/
		    }
		    m >>= 1;
		    pos--;
		  }
		  /* Inverser les pixels car le standard du 2D est inverse p/r au standard habituel */
		  img2d_clean[im] = ~(img2d_clean[im]);
		}
	      }
	    }
	  }
	}
	else {
	  /* Pas de fogging a traiter, transferer les donnees originales */
	  for (jj=(pos_as_prev+1); jj<=j; jj++)
	    for (ii=0; ii<RECL; ii++)
	      img2d_clean[ii+jj*RECL] = img2d[ii+jj*RECL];
	}
	pos_as_prev = j;
	pos_rg_prev = pos_rg;
	count_fogging = 0;
	cur_f = 0;
      }
    }
  }

  printf("Nloop_as = %lu\n",Nloop_as);
  printf("Images = %ld\n",count);
  
  /* Liberation de memoire */
  if (ima != NULL)
    free(ima);
  ima = NULL;
  
  return 0;
}

/* fonction d'enrobage */

int
OP_Fogging_2D (unsigned long int NbVal, void *ArgList[], char *DiagExec)
{
  int CodRet;
  int NCar;

  NCar = sprintf (DiagExec, "Fogging_2D : (%ld echant.) ", NbVal) ;
  if (NCar < 0)
    NCar = 0;
  DiagExec += NCar;

  CodRet = Fogging_2D (NbVal,
		       (double *) ArgList[0],
		       (int *) ArgList[1],
		       (double *) ArgList[2],
		       (short int *) ArgList[3],
		       (char *) ArgList[4],
		       (char *) ArgList[5],
		       *((short int *) ArgList[6]),
		       *((unsigned long int *) ArgList[7]),
		       *((long int *) ArgList[8]),
		       *((long int *) ArgList[9]),
		       *((short int *) ArgList[10]),
		       *((short int *) ArgList[11]),
		       *((short int *) ArgList[12]),
		       (int *) ArgList[13],
		       (int *) ArgList[14]);
  
  return OP_OK;
}

void
ID_Fogging_2D (oper * optr)
{
  int ind;

  strcpy (optr->Nom, "Fogging_2D");
  optr->Version = "1.0";
  optr->Date = "20/07/01";
  optr->fctptr = OP_Fogging_2D;
  optr->NbArg = 15;

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
  optr->Arg_Car[ind].typ = ATYC_I32;
  optr->Arg_Car[ind].array_dim = "1";
  optr->Arg_Car[ind].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[ind].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[ind].sample = "$Arg1.sample";
  optr->Arg_Car[ind].ref_time = " $Arg1.nom ";
  optr->Arg_Car[ind].unite = "without";
  optr->Arg_Car[ind].famille = " \"microphysique\" ";
  optr->Arg_Car[ind].misval = "-1.0";

  ind++;
  optr->Arg_Car[ind].direction = DIR_OUT;
  optr->Arg_Car[ind].categorie = VECTOR;
  optr->Arg_Car[ind].typ = ATYC_I32;
  optr->Arg_Car[ind].array_dim = "1024";
  optr->Arg_Car[ind].NbVal = "$Arg2.NbVal";
  optr->Arg_Car[ind].type_sample = "$Arg2.type_sample";
  optr->Arg_Car[ind].sample = "$Arg2.sample";
  optr->Arg_Car[ind].ref_time = " $Arg2.ref_time ";
  optr->Arg_Car[ind].unite = " $Arg2.nom ";
  optr->Arg_Car[ind].misval = "-1.0";
}
