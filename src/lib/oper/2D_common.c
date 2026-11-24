/* Ensemble de fonctions utilisées par les opérateurs travaillant sur
 * les données "2D"
 **/

#define _XOPEN_SOURCE 600

#include <stdio.h>
#include <stdlib.h>
#include <errno.h>
/* Les includes pour utiliser getpid() et kil() */
#include <sys/types.h>
#include <unistd.h>
#include <signal.h>

#ifndef TRUE
#define TRUE (1)
#endif
#ifndef FALSE
#define FALSE (0)
#endif

/** Arrêt brutal en cas d'erreur d'allocation mémoire
 *
 * TODO : faire qqchose de moins brutal, et laisser
 * l'appellant (souventfvb) terminer proprement.
 */
void
alloc_error (const char *file, int line)
{
  fprintf (stderr,
	   "Error : memory alloc error\nFile = %s Line = %d Error = %d\nDumping core...\n\n",
	   file, line, errno);
  (void) kill (getpid (), 5);
}


/** Calcule la valeur minimale d'un vecteur d'entiers */
int
arrayi_min (const int *array, int dim)
{
  int i, mini;

  mini = array[0];

  for (i = 1; i < dim; i++)
    if (array[i] < mini)
      mini = array[i];

  return mini;
}

/** Calcule la valeur maximale d'un vecteur d'entiers */
int
arrayi_max (const int *array, int dim)
{
  int i, maxi;

  maxi = array[0];

  for (i = 1; i < dim; i++)
    if (array[i] > maxi)
      maxi = array[i];

  return maxi;
}

/** Additionne toute les valeurs d'un vecteur d'entiers */
int
total_arrayi (const int *array, int dim)
{
  int i;
  int tot = 0;

  for (i = 0; i < dim; i++)
    tot += array[i];

  return tot;
}

/* Somme les elements de l'image binaire contenue dans array */
int
total (const int *array, unsigned long int mask, long int dima, long int dimb)
{
  unsigned long int i;
  int counti = 0;
  long int k;

  for (k = dima; k <= dimb; k++)
    for (i = mask; i != 0; i >>= 1)
      if (i & array[k])
	counti++;

  return counti;
}

/** Fonction de synchro des donnees 2D avec le temps interne
 *
 * Cette sous-routine calcule un temps de synchro qui utilise le temps externe
 * comme base (intervalle) et utilise la somme des temps interne comme etalonnage
 * pour le temps interne propre a chaque imagette.
 *
 * */
double
decodage_tint (const int *img2d, long int counter, unsigned long int mask,
	       unsigned long int maskt, unsigned long int masktd,
	       unsigned long int bite, short int tempsb, double freq)
{
  double sum_time = 0.0;
  short int condition, b, k;
  unsigned long int i;
  double int_time;

  /* Boucle sur le record de 1024 elements */
  for (k = 0; k < 1024; k++)
    {
      /* Compteur de l'element courant du vecteur d'image 2D */
      counter++;
      /* Compteur du nombre de bits dans un element integer de l'image */
      b = 0;
      /* Temps interne courant */
      int_time = 0.0;

      if (counter > 1)
	{
	  /* Test pour marqueur: fin d'imagette et marqueur de temps */
	  /* On teste pour trouver le marqueur de 8 bits en debut des mots binaires de 32 bits */
	  /* Pour MERLIN-IV c'etait 01010101, donc 55 en hexa */
	  if (tempsb == 24)
	    condition = ((maskt & img2d[counter - 1]) == bite);
	  else
	    condition = TRUE;
	}

      if (img2d[counter] == bite && condition)
	{
	  /* On a trouve une fin d'imagette, donc on en debute une nouvelle
	   * et on analyse la precedente */

	  /* Calcul du temps interne en utilisant les 24 premiers bits du mot de 32 bits
	   * du marqueur de temps inclut dans les donnees d'images
	   * Le temps est en unite de temps d'horloge TAS, donc on doit diviser
	   * par la frequence */
	  int_time = (double) (masktd & img2d[counter - 1]) / freq;
	  /* Somme des temps internes pour l'imagette courante */
	  sum_time += int_time;

	  /* Verification du nombre de bits */
	  for (i = mask; i != 0; i >>= 1)
	    b++;
	  if (b != 32)
	    {
	      printf
		("Nombre de bits pas egal a 32 -> %hd! Doit stopper...\n", b);
	      exit (1);
	    }
	}
    }
  return sum_time;
}

/* Comme partout ailleurs ....*/
#define BYTES 32
/* */

/** Operateur mathematique morphologique erode */
void
erode (const int *imgin, int *imgout, int nelem)
{
  int *tmpimg = NULL;
  unsigned long int mask = 0x00000001;
  int i, pos, up, down, left, right;

  tmpimg = malloc (nelem * sizeof (int));
  if (tmpimg == NULL)
    {
      printf ("Alloc error erode.\n");
      exit (1);
    }

  for (i = 0; i < nelem; i++)
    tmpimg[i] = imgin[i];

  imgout[0] = imgout[nelem - 1] = 0x00000000;
  for (i = 1; i < (nelem - 1); i++)
    {
      imgout[i] = 0x00000000;
      for (pos = 1; pos < (BYTES - 1); pos++)
	{
	  up = down = pos;
	  right = pos - 1;
	  left = pos + 1;
	  if (((tmpimg[i] >> right) & mask) & ((tmpimg[i] >> left) & mask) &
	      ((tmpimg[i - 1] >> up) & mask) & ((tmpimg[i + 1] >> down) &
						mask))
	    imgout[i] |= (((tmpimg[i] >> pos) & mask) << pos);
	}
    }

  free (tmpimg);
}

/* Calcul des dimensions de la boite minimale qui contient toute la particule */
void
box2d (const int *array, unsigned long int mask, long int dima, long int dimb,
       int *xmin, int *xmax, int *ymin, int *ymax)
{
  unsigned long int i;
  long int k;
  short int foundx = FALSE;
  short int foundy = FALSE;
  short int countx, county;
  int temp;

  /* Initialisation */
  *xmin = *xmax = *ymin = *ymax = -1;

  county = 0;
  /* Boucle sur les X */
  for (k = dima; k <= dimb; k++)
    {
      countx = 0;
      foundx = FALSE;
      foundy = FALSE;
      /* Boucle sur les Y */
      for (i = mask; i != 0; i >>= 1)
	{

	  if (i & array[k])
	    {
	      foundy = TRUE;
	      if ((foundx == FALSE && countx < *ymin) ||
		  (foundx == FALSE && *ymin == -1))
		{
		  *ymin = countx;
		  foundx = TRUE;
		}
	      if (countx > *ymax)
		*ymax = countx;

	    }
	  countx++;
	}

      if ((foundy == TRUE && county < *xmin) ||
	  (foundy == TRUE && *xmin == -1))
	*xmin = county;
      if (foundy == TRUE && county > *xmax)
	*xmax = county;

      county++;
    }

  /* Y doit etre inverse */
  temp = *ymin;
  *ymin = (BYTES - 1) - *ymax;
  *ymax = (BYTES - 1) - temp;
}
