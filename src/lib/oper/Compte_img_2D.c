/*******************************************************************
* OPERATOR      Compte_img_2D.c FUNCTION ANSI-C
*
* PURPOSE 	Compte le nombre d'imagettes dans les donnees PMS-2DC
*               selon la frequence definie dans les parametres.
*               Fait aussi la synchronisation du temps.
*		
* DESCRIPTION	
*		 
* VERSION       1.0
*
* ARGUMENTS     IN   double    time_rg  second  base de temps d'arrivee
*               IN   double    time_as  second  base de temps de depart
*               IN   int       img2d     any    donnees de la sonde PMS-2DC 
*               IN   short int tas2d     any    clock TAS
*               IN   short int ovld2d    any    overload
*               IN   char *    codei     any    code d'identification de la sonde en hexadecimal
*                                               encadre par des guillemets. Ex.: "0x55000000"
*               IN   char *    maskds    any    masque en hexadecimal qui indique quels bits
*                                               utiliser dans les donnees. Ceci afin de pouvoir
*                                               supprimer certaines diodes. Doit etre specifie
*                                               encadre par des guillemets. Ex.: "0xffffffff"
*               IN   short int tempsb    any    nombre de bits de l'info de temps interne, soit
*                                               24 ou 32.
*               IN   long  int Nloop_as  any    nombre d'elements asynchrones selon time_as
*
*               OUT  long  int count_img      compte total des imagettes sur la base de "time_rg"
*                                             sans les images artefacts
*               OUT  long  int count_img_vide compte des imagettes vides sur la base de "time_rg"
*               OUT  long  int count_img_art  compte des imagettes artefacts sur la base de "time_rg"
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

/* #define _POSIX_SOURCE 1 */
#define _XOPEN_SOURCE 600

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include <limits.h>
#include <errno.h>

#include "struct_oper.h"

#include "2D_common.h"

void
print_bin (const int val, const char *str)
{
  unsigned long int i;
  unsigned long int mask = 0x80000000;

  printf ("%s: ", str);
  for (i = mask; i != 0; i >>= 1)
    putchar ((i & val) ? '1' : '0');
  printf ("\n");
}


/* define pour debugging */
/*#define DEBUG*/
/*#define DEBUGG*/
#define BEGJ 7372800
#define BEGA BEGJ/1024
#define ENDJ 7377920
#define ENDA ENDJ/1024

int
Compte_img_2D (const unsigned long int Nloop_rg,
	       const double *time_rg,
	       const int *img2d,
	       const double *time_as,
	       const short int *tas2d,
	       const short int *ovld2d,
	       const char *codei,
	       const char *maskds,
	       const short int tempsb,
	       const unsigned long int Nloop_as,
	       long int *count_img,
	       long int *count_img_vide,
	       long int *count_img_art)
{
#define BYTES 32
#define TRUE 1
#define FALSE 0

  /* Compteurs et variable de position dans le vecteur de temps regulier */
  long int j, k, pos_rg, pos_rg_p;
  /* Masque pour l'extraction bit par bit */
  unsigned long int mask = 0x80000000;
  /* Masque pour la recuperation du temps sur 8 bits */
  unsigned long int maskt = 0xff000000;
  /* Inverse du masque du temps */
  unsigned long int masktd = 0x00ffffff;
  /* Masque plein */
  unsigned long int maskd = 0xffffffff;
  /* Code de la sonde qui permet d'identifier une fin d'imagette */
  unsigned long int bite = 0x55000000;
  /* Compteur */
  unsigned long int i;
  /* Variable reliees au temps */
  double int_time, sum_time, difftime, cur_time, somme_int, dtime, time_deb;
  /* Vatiable de comptage pour les imagettes */
  long int count, counter, img_zero_cnt, img_vide_cnt, img_vide;
#ifdef DEBUGG
  char **buf = NULL;
#endif
  /* Compteur du nombre de bits dans une image et flag de debut d'imagette */
  int b, new;
  /* Frequence d'echantillonnage de la sonde */
  double freq;
  /* Variable booleenne qui permet de definir une condition pour le temps */
  /* code sur 24 ou 32 bits */
  short int condition;

#ifdef DEBUGG
  /* Allocate memory */
  buf = malloc (Nloop_as * sizeof (char *));
  if (buf == NULL)
    alloc_error (__FILE__, __LINE__);
  for (i = 0; i < Nloop_as; i++)
    {
      buf[i] = calloc (BYTES, sizeof (char));
      if (buf[i] == NULL)
	alloc_error (__FILE__, __LINE__);
    }
#endif

  /* Initialisation */
  count = counter = img_zero_cnt = img_vide_cnt = 0;
  img_vide = FALSE;
  /* Position dans le vecteur de temps regulier */
  pos_rg = pos_rg_p = 1;
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
      return 1;
    }
  /* Initialisation du comptage sur le temps regulier */
  for (i = 0; i < Nloop_rg; i++)
    {
      count_img[i] = 0;
      count_img_vide[i] = 0;
      count_img_art[i] = 0;
    }

  /* Boucle sur le temps irregulier */
  for (j = 0; j < Nloop_as; j++)
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
	dtime = 0.333;
      /* Temps du debut du record */
      time_deb = time_as[j] - dtime;

      /* Boucle sur le record de 1024 elements */
      for (k = 0; k < 1024; k++)
	{

	  /* Compteur de l'element courant du vecteur d'image 2D */
	  counter++;

#ifdef DEBUG
	  if (counter > BEGJ && counter < ENDJ)
	    {
#endif
	      /* Compteur du nombre de bits dans un element integer de l'image */
	      b = 0;
	      /* Temps interne */
	      int_time = 0.0;

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
		  new = TRUE;
		  if (img_vide == TRUE)
		    img_vide_cnt++;
#ifdef DEBUG
		  printf ("HEX %p %p\n", end, img2d[counter - 1]);
#endif
#ifdef DEBUG
		  print_bin (img2d[counter - 1], "Time");
#endif
		  /* Calcul du temps interne en utilisant les 24 premiers bits du mot de 32 bits
		   * du marqueur de temps inclut dans les donnees d'images
		   * Le temps est en unite de temps d'horloge TAS, donc on doit diviser
		   * par la frequence */
		  int_time = (double) (masktd & img2d[counter - 1]) / freq;
		  /* Somme des temps internes pour l'imagette courante */
		  sum_time += int_time;
		  if (j > 0)
		    {
		      /* Calculer le temps courant de l'imagette courante
		       * en utilisant le temps de debut de record, la somme des temps interne
		       * pour le record courant et la somme des temps interne jusqu'a
		       * l'imagette courante */
		      if (somme_int != 0.0)
			cur_time = time_deb + dtime * sum_time / somme_int;
		      else
			cur_time = time_deb;
		    }
		  if (img2d[counter - 1] == bite)
		    {
		      /* Le temps de l'imagette est zero: donc on comptabilise une imagette zero */
		      /* On ne comptabilise pas l'imagette car cela est un artifact */
		      img_zero_cnt++;
#ifdef DEBUG
		      print_bin (img2d[counter - 1], "Zero");
#endif
		    }
		  /* Recherche du bin de temps regulier ou tombe l'imagette presente */
		  /* Ensuite, on comptabilise le compte */
		  if (cur_time < time_rg[pos_rg])
		    pos_rg = 0;
		  while (!
			 (cur_time < time_rg[pos_rg]
			  && cur_time >= time_rg[pos_rg - 1])
			 && pos_rg < Nloop_rg)
		    pos_rg++;
		  /* Re-essayer une seconde fois au cas ou... */
		  if (pos_rg == Nloop_rg)
		    {
		      pos_rg = 0;
		      while (!
			     (cur_time < time_rg[pos_rg]
			      && cur_time >= time_rg[pos_rg - 1])
			     && pos_rg < Nloop_rg)
			pos_rg++;
		    }
		  /* Si la condition est respectee, on compte l'imagette */
		  if (cur_time < time_rg[pos_rg]
		      && cur_time >= time_rg[pos_rg - 1])
		    {
		      if (img2d[counter - 1] != bite)
			{
			  count_img[pos_rg - 1]++;
			  /* Compte des images vides */
			  if (img_vide == TRUE)
			    count_img_vide[pos_rg - 1]++;
			}
		      else
			/* Le temps de l'imagette est zero: donc on comptabilise une imagette zero */
			/* On ne comptabilise pas l'imagette car cela est un artifact */
			count_img_art[pos_rg - 1]++;
		    }
		  img_vide = TRUE;
		  count++;
#ifdef DEBUG
		  printf ("COUNT %d   time %lf int %lf\n", count, time_as[j],
			  int_time);
#endif
		}

	      /* Comptage des imagettes vides en excluant marqueurs de temps/fin */
	      if ((maskd & img2d[counter]) != maskd &&
		  ((maskt & img2d[counter]) != bite))
		img_vide = FALSE;

	      /* Verification du nombre de bits */
	      for (i = mask; i != 0; i >>= 1)
		{
#ifdef DEBUGG
		  (i & img2d[counter]) ? (buf[j][b] = 1) : (buf[j][b] = 0);
		  putchar ((buf[j][b]) ? '1' : '0');
#endif
		  b++;
		}
#ifdef DEBUGG
	      printf ("\n");
#endif

	      new = FALSE;

	      if (b != 32)
		{
		  printf ("Nombre de bits pas egal a 32! Doit stopper...\n");
#ifdef DEBUGG
		  /* Free memory */
		  for (i = 0; i < Nloop_as; i++)
		    free (buf[i]);
		  free (buf);
#endif
		  return 1;
		}
#ifdef DEBUG
	    }
#endif
	}

      /* Verification du temps interne VS externe */
      if (j > 0)
	{
	  /*      if (j >= BEGA && j <= ENDA) { */
	  difftime = time_as[j] - time_as[j - 1];
	  /* Ajout du temps d'OVERLOAD au temps calcule */
	  sum_time += (double) ovld2d[j] / 1000.0;
	  if (((difftime - sum_time) >= 0.0
	       || (difftime - sum_time) <= (difftime * 0.1))
	      && sum_time != 0.0)
#ifdef DEBUG
	    printf
	      ("Comparaison des temps: EXTERNE/INTERNE: %lf %lf %lf %lf\n",
	       difftime, sum_time, (double) ovld2d[j] / 1000.0, freq);
#endif
	  ;
	  else
	  {
	    printf ("Temps rejete...: EXTERNE/INTERNE: %f %f %f %f\n",
		    difftime, sum_time, (double) ovld2d[j] / 1000.0, freq);
	    for (i = (pos_rg_p + 1); i <= pos_rg; i++)
	      {
		count_img[i - 1] = -1;
		count_img_vide[i - 1] = -1;
		count_img_art[i - 1] = -1;
	      }
	  }
	  /*  } */
	}
      /* On retient la position dans le vecteur de temps regulier */
      /* Pour le cas ou on doit rejeter la donnees a cause de la comparaison des temps */
      pos_rg_p = pos_rg;
    }

  printf ("Nloop_as = %lu\n", Nloop_as);

#ifdef DEBUGG
  /* Free memory */
  for (i = 0; i < Nloop_as; i++)
    free (buf[i]);
  free (buf);
  buf = NULL;
#endif

#ifdef DEBUG
  for (i = 0; i < Nloop_rg; i++)
    if (count_img[i] != 0)
      printf ("Images %lf %ld\n", time_rg[i], count_img[i]);
#endif

  printf
    ("Images = %ld Zero_temps_images = %ld Images_vides %ld Moyenne = %f\n",
     count, img_zero_cnt, img_vide_cnt, (float) count / (float) Nloop_rg);

  return 0;
}

/* fonction d'enrobage */

int
OP_Compte_img_2D (unsigned long int NbVal, void *ArgList[], char *DiagExec)
{
  int CodRet;
  int NCar;

  NCar = sprintf (DiagExec, "Compte_img_2D : (%ld echant.) ", NbVal) ;
  if (NCar < 0)
    NCar = 0;
  DiagExec += NCar;

  CodRet = Compte_img_2D (NbVal,
			  (double *) ArgList[0],
			  (int *) ArgList[1],
			  (double *) ArgList[2],
			  (short int *) ArgList[3],
			  (short int *) ArgList[4],
			  (char *) ArgList[5],
			  (char *) ArgList[6],
			  *((short int *) ArgList[7]),
			  *((unsigned long int *) ArgList[8]),
			  (long int *) ArgList[9],
			  (long int *) ArgList[10], 
			  (long int *) ArgList[11]);

  return OP_OK;
}

void
ID_Compte_img_2D (oper * optr)
{
  strcpy (optr->Nom, "Compte_img_2D");
  optr->Version = "1.0";
  optr->Date = "20/03/01";
  optr->fctptr = OP_Compte_img_2D;
  optr->NbArg = 12;

  optr->Arg_Car[0].direction = DIR_IN;
  optr->Arg_Car[0].categorie = VECTOR;
  optr->Arg_Car[0].typ = ATYC_IF64;
  optr->Arg_Car[0].array_dim = "1";
  optr->Arg_Car[0].type_sample = "any";
  optr->Arg_Car[0].sample = "any";
  optr->Arg_Car[0].unite = "second";

  optr->Arg_Car[1].direction = DIR_IN;
  optr->Arg_Car[1].categorie = VECTOR;
  optr->Arg_Car[1].typ = ATYC_I32;
  optr->Arg_Car[1].array_dim = "1024";
  optr->Arg_Car[1].type_sample = "any";
  optr->Arg_Car[1].sample = "any";
  optr->Arg_Car[1].unite = "count";

  optr->Arg_Car[2].direction = DIR_IN;
  optr->Arg_Car[2].categorie = VECTOR;
  optr->Arg_Car[2].typ = ATYC_IF64;
  optr->Arg_Car[2].array_dim = "1";
  optr->Arg_Car[2].type_sample = "any";
  optr->Arg_Car[2].sample = "any";
  optr->Arg_Car[2].unite = "second";

  optr->Arg_Car[3].direction = DIR_IN;
  optr->Arg_Car[3].categorie = VECTOR;
  optr->Arg_Car[3].typ = ATYC_I16;
  optr->Arg_Car[3].array_dim = "1";
  optr->Arg_Car[3].type_sample = "any";
  optr->Arg_Car[3].sample = "any";
  optr->Arg_Car[3].unite = "second";

  optr->Arg_Car[4].direction = DIR_IN;
  optr->Arg_Car[4].categorie = VECTOR;
  optr->Arg_Car[4].typ = ATYC_I16;
  optr->Arg_Car[4].array_dim = "1";
  optr->Arg_Car[4].type_sample = "any";
  optr->Arg_Car[4].sample = "any";
  optr->Arg_Car[4].unite = "msec";

  optr->Arg_Car[5].direction = DIR_IN;
  optr->Arg_Car[5].categorie = COEFFICIENT;
  optr->Arg_Car[5].typ = ATYC_STRING;
  optr->Arg_Car[5].array_dim = "1";
  optr->Arg_Car[5].type_sample = "any";
  optr->Arg_Car[5].sample = "any";
  optr->Arg_Car[5].unite = "";

  optr->Arg_Car[6].direction = DIR_IN;
  optr->Arg_Car[6].categorie = COEFFICIENT;
  optr->Arg_Car[6].typ = ATYC_STRING;
  optr->Arg_Car[6].array_dim = "1";
  optr->Arg_Car[6].type_sample = "any";
  optr->Arg_Car[6].sample = "any";
  optr->Arg_Car[6].unite = "";

  optr->Arg_Car[7].direction = DIR_IN;
  optr->Arg_Car[7].categorie = COEFFICIENT;
  optr->Arg_Car[7].typ = ATYC_I16;
  optr->Arg_Car[7].array_dim = "1";
  optr->Arg_Car[7].type_sample = "any";
  optr->Arg_Car[7].sample = "any";
  optr->Arg_Car[7].unite = "";

  optr->Arg_Car[8].direction = DIR_IN;
  optr->Arg_Car[8].categorie = COEFFICIENT;
  optr->Arg_Car[8].typ = ATYC_I32;
  optr->Arg_Car[8].array_dim = "1";
  optr->Arg_Car[8].type_sample = "any";
  optr->Arg_Car[8].sample = "any";
  optr->Arg_Car[8].unite = "";

  optr->Arg_Car[9].direction = DIR_OUT;
  optr->Arg_Car[9].categorie = VECTOR;
  optr->Arg_Car[9].typ = ATYC_I32;
  optr->Arg_Car[9].array_dim = "1";
  optr->Arg_Car[9].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[9].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[9].sample = "$Arg1.sample";
  optr->Arg_Car[9].ref_time = " $Arg1.nom ";
  optr->Arg_Car[9].unite = "count";
  optr->Arg_Car[9].famille = " \"microphysique\" ";
  optr->Arg_Car[9].misval = "-1";

  optr->Arg_Car[10].direction = DIR_OUT;
  optr->Arg_Car[10].categorie = VECTOR;
  optr->Arg_Car[10].typ = ATYC_I32;
  optr->Arg_Car[10].array_dim = "1";
  optr->Arg_Car[10].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[10].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[10].sample = "$Arg1.sample";
  optr->Arg_Car[10].ref_time = " $Arg1.nom ";
  optr->Arg_Car[10].unite = "count";
  optr->Arg_Car[10].famille = " \"microphysique\" ";
  optr->Arg_Car[10].misval = "-1";

  optr->Arg_Car[11].direction = DIR_OUT;
  optr->Arg_Car[11].categorie = VECTOR;
  optr->Arg_Car[11].typ = ATYC_I32;
  optr->Arg_Car[11].array_dim = "1";
  optr->Arg_Car[11].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[11].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[11].sample = "$Arg1.sample";
  optr->Arg_Car[11].ref_time = " $Arg1.nom ";
  optr->Arg_Car[11].unite = "count";
  optr->Arg_Car[11].famille = " \"microphysique\" ";
  optr->Arg_Car[11].misval = "-1";
}
