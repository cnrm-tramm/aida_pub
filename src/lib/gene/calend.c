/*
 * Référence sur les calendriers :
 * http://www.imcce.fr/fr/grandpublic/temps/calendriers.php
 */

#include <math.h>

/** Indique si une année est bissextile, selon la règle du
 * calendrier grégorien.
 *
 * @param annee
 * @return 1 si l'année est bissextile, 0 sinon.
 */
int
gregor_bissextile (int annee)
{
  if (annee % 4 == 0)
    {
      if (annee % 100 == 0)
	{
	  if (annee % 400 == 0)
	    return 1;
	  else
	    return 0;
	}
      else
	return 1;
    }
  else
    return 0;
  /* ça peut aussi se coder : 
     return  ((annee % 4 == 0 && annee % 100) || annee % 400 == 0)
     Mais ça ne coûte pas cher d'être explicite.
   */
}

/** Indique le nombre de jours d'une année.
 *
 * @param annee
 * @return 365 pour une année "normale", 366 pour une année bissextile.
 */
int
nb_jour_annee (int annee)
{
  if (gregor_bissextile (annee))
    return 366;
  else
    return 365;
}

/* Position dans l'année du dernier jour du mois précédent */
static int jda_preced[] = { -31, 0, 31, 59, 90, 120, 151,
  181, 212, 243, 273, 304, 334, 365
};

/** Calcule le JDA à partir d'une date calendaire grégorienne.
 *
 * @param annee : le numéro de l'année
 * @param mois : le numero du mois, gamme [1, 12]
 * @param jour : le numéro du jour dans le mois.
 * @return Le numéro du jour dans l'année, -1 en cas d'arguments hors-gamme,
 *       -2 si l'année est avant la mise en place du calendrier grégorien.
 * */
int
date_to_JDA (int annee, int mois, int jour)
{
  /* Arguments hors gamme. */
  if (annee < 0 || mois <= 0 || mois > 12 || jour <= 0 || jour > 31)
    return -1;

  /* On ne souhaite pas traiter une époque où le
   * calendrier n'était pas grégorien (julien, ...). */
  if (annee < 1583)
    return -2;

  if (gregor_bissextile (annee))
    {
      if (mois > 2)		/* 1 jour de plus après février */
	jour++;
    }

  return jda_preced[mois] + jour;
}


/** Calcul du jour dans l'année selon la formule de N. Derhowitz et
 * E. M. Reingold, Calendrical calculations, third edition, eq. 2.1 p 46.
 *
 * @param annee : le numéro de l'année
 * @param mois : le numero du mois, gamme [1, 12]
 * @param jour : le numéro du jour dans le mois.
 * @return Le numéro du jour dans l'année, -1 en cas d'arguments hors-gamme,
 *
 */
int
date_to_JDA_DnR (int annee, int mois, int jour)
{
  int corr = 0;
  /* Arguments hors gamme. */
  if (annee < 0 || mois <= 0 || mois > 12 || jour <= 0 || jour > 31)
    return -1;

  /* */
  if (mois > 2)
    {
      if (gregor_bissextile (annee))
	{
	  corr = -1;
	}
      else
	{
	  corr = -2;
	}
    }

  return floor ((367 * mois - 362) / 12.) + corr + jour;
}



/** Calcule une date calendaire (mois, jour) à partir de JDA et année.
 *
 * @param JDA : le numéro du jour dans l'année. Doit être positif, 
 *                 peut être sup à 366
 * @param  annee_p : pointeur vers l'année. Sera modifié si JDA > Nb_Jour(année)
 * @param  mois_p : pointeur vers le numéro du mois. Gamme [1:12], 0 si erreur.
 * @param  jour_p : pointeur vers le numéro du jour dans le mois. Gamme [1:31], 0 si erreur.
 */
void
JDA_to_date (int JDA, int *annee_p, int *mois_p, int *jour_p)
{
  int nb_j_an;
  int decal_bissext;

  /* Argument hors gamme. */
  if (JDA <= 0)
    {
      *mois_p = 0;
      *jour_p = 0;
    }

  decal_bissext = 0;
  if (gregor_bissextile (*annee_p))
    {
      decal_bissext = 1;
    }
  nb_j_an = 365 + decal_bissext;

  /* "Cadeau" facile à l'appelant : si JDA est trop grand, on va
   * chercher dans les années suivantes. */
  if (JDA > nb_j_an)
    {
      JDA -= nb_j_an;
      (*annee_p)++;
      JDA_to_date (JDA, annee_p, mois_p, jour_p);
      return;
    }

  /* Le cas de janvier est simple, et ne dépend pas de la bissextilité. */
  if (JDA <= 31)
    {
      *mois_p = 1;
      *jour_p = JDA;
      return;
    }
  if (JDA <= 31 + 28 + decal_bissext)
    {
      *mois_p = 2;
      *jour_p = JDA - 31;
      return;
    }

  *mois_p = 3;
  while (JDA > (jda_preced[*mois_p + 1] + decal_bissext))
    (*mois_p)++;
  *jour_p = JDA - (jda_preced[*mois_p] + decal_bissext);
}
