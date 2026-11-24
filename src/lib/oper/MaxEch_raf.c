/****************************************************
*
* OPERATOR      MaxEch_raf.c   FUNCTION  ANSI-C
*
* PURPOSE       Calcul des valeurs maxi par echantillon dans une serie-temporelle
*               (ex : recherche des valeurs maxi toutes les nn minutes pour un vent
*               mesure toutes les secondes ... notion de "rafales")
*               Le time en sortie est le temps de la fin de l'echantillon : difference
*               avec MaxEch.c
*               Notion de "rafales" pour le vent
*
* DESCRIPTION   Routine de maxi-echantillon, pour variables "float".
*               Les valeurs absentes sont gérées par le mécanisme
*               automatique (système des NaN). 
*               Les valeurs manquantes (NaN) sont eliminees 
*               Attention, cette routine ne fonctionne bien que si RapFreq
*               est l'inverse d'un entier !
*               Dans les autres cas, on utilisera l'entier le plus proche,
*               ce qui risque de ne pas donner exactement le résultat
*               attendu.
*
* VERSION       $Revision$
*
* ARGUMENTS   IN   float  Var_in     any        Original data
*             IN   double Time_in    any        Original time data
*             IN   double RapFreq    whithout   frequency ratio
*             IN   int    Decal      sec/freq   delay between first values
*             OUT  double Time_Out              Temps corresp. a la FIN de l'echantillon
*             OUT  float  Var_out    same as 1  Valeurs maxi
*
* REFERENCES
*
* CHANGES       
*               Cette fonction est semblable a la fonction MoyEch.c
*               mais fournit en sortie les valeurs maxi par echantillon
*               (avec test des valeurs manquantes) C.Berne Mars 2004
*               Le time associe est le time de fin d'echantillon (difference avec MaxEch)
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

#include "struct_oper.h"

long
MaxEch_raf (unsigned long NbValIn,
	    const float *Var_in,
	    const double *Time_in,
	    const double RapFreq,
	    const int Decal,
	    double *Time_out, float *Var_out, long TabStat[4])
{
  long i, NbValOut;
  long Ntour, Reste;
  int j, NSom, NSomfin;
  register float loc_max, minfloat;
  const float misval_out = K_NaN;

  /* minfloat : valeur mini d'un flottant pour initialiser les loc_max */
  minfloat = -MAXFLOAT;

  if (RapFreq > 1.0)
    return -1;

  NSom = floor ((1.0 / RapFreq) + 0.5);
/* faudrait verifier que |Nsom - 1/RapFreq| < EPSILON */

  if ((Decal < -NSom) || (Decal > NSom))
    return -2;

/* Réglons immédiatement le cas ou y'a rien a faire : "NbValIn = 0" */
  if (NbValIn == 0)
    return 0;

/*
 * Normalement, il y a Ntour calculs "standards" à faire.
 *  Si on tient compte de Decal, le premier ou le dernier peut ne
 * plus être standard--> traitement des cas-particulier, et boucle sur
 * (Ntour - 1) cas.
 */

  Ntour = NbValIn / NSom;	/* division entière */
  Reste = NbValIn % NSom;

/* 
 * Le premier maxi se fait de Decal à Decal+Nsom-1, mais si 
 * Decal est negatif, on commence à zero.
 * Si Decal est positif, ce premier maxi se fait dans la boucle standard.
 * CBerne : minfloat : Mini Flottant pour initialiser loc_max
 */

  if (Decal < 0)
    {
      if (NSom + Decal > 0)
	{
	  loc_max = minfloat;
	  for (j = 0; j < NSom + Decal; j++)
	    {
	      if (!isfinite (*Var_in))
		{
		  Var_in++;
		  Time_in++;
		}
	      else
		{
		  if (*Var_in > loc_max)
		    {
		      loc_max = *Var_in;
		    }
		  Var_in++;
		  Time_in++;
		}
	    }
	  if (loc_max == minfloat)
	    {
	      /* que des valeurs mnq dans l'echantillon */
	      /* CBerne : on met le dernier time */
	      *Var_out = misval_out;
	      *Time_out = *Time_in;
	    }
	  else
	    {
	      *Var_out = loc_max;
	      *Time_out = *Time_in;
	      /* printf (" Maxi trouve (different de Nan) \n");  */
	    }
	}
      else
	{
	  *Var_out = *Var_in;	/* Plutôt que 0 ou misval... */
	  *Time_out = *Time_in;	/* Plutôt que 0 ou misval... */
	}

      Var_out++;
      Time_out++;
    }
  else				/* Cas ou Decal est positif */
    {
      Var_in += Decal;
      Time_in += Decal;
    }
/* Fin du if sur Decal < ou > 0 */


  /* Ensuite la boucle standard sur les Ntour 
     Si le nb de misval est >= tolerance_mnq :
     -pas de moyenne (misval)
     Sinon moyenne sur les (NSom - mnq_som) valeurs de Var_in */

  for (i = 0; i < Ntour - 1; i++)
    {
      loc_max = minfloat;
      for (j = 0; j < NSom; j++)
	{
	  if (!isfinite (*Var_in))
	    {
	      Var_in++;
	      Time_in++;
	      /* printf (" Vecteur en entree est a une valeur infinie... mnq ... \n");  */
	    }
	  else
	    {
	      if (*Var_in > loc_max)
		{
		  loc_max = *Var_in;
/*  	  printf (" Valeur maxi trouvee : loc_max = %6.2f \n", loc_max);     */
		}
	      Var_in++;
	      Time_in++;
	    }
	}
      /*printf (" Valeur maxi trouvee : loc_max = %6.2f \n", loc_max);    */
      if (loc_max == minfloat)
	{
	  /* que des valeurs mnq dans l'echantillon */
	  *Var_out = misval_out;
	  *Time_out = *Time_in;
	}
      else
	{
	  *Var_out = loc_max;
	  *Time_out = *Time_in;
	  /* printf (" Maxi trouve (different de Nan) \n"); */
	}
      Var_out++;
      Time_out++;
    }

/* 
 * La dernière boucle se doit pas dépasser NbValIn.
 * Si Decal est négatif, y'a pas de Pb, ça a été fait dans la boucle standard.
 * Si Decal est positif, le nombre normal de boucles peut être réduit
 * si (Nsom + Reste - Decal) est plus petit que Nsom.
 */

  if (Decal >= 0)
    {
      NSomfin = NSom + Reste - Decal;
      if (NSomfin > NSom)
	NSomfin = NSom;
      if (NSomfin > 0)
	{
	  loc_max = minfloat;
	  for (j = 0; j < NSomfin; j++)
	    {
	      if (!isfinite (*Var_in))
		{
		  Var_in++;
		  Time_in++;
		}
	      else
		{
		  if (*Var_in > loc_max)
		    {
		      loc_max = *Var_in;
		    }
		  Var_in++;
		  Time_in++;
		}
	    }
	  if (loc_max == minfloat)
	    {
	      /* que des valeurs mnq dans l'echantillon */
	      *Var_out = misval_out;
	      *Time_out = *Time_in;
	    }
	  else
	    {
	      *Var_out = loc_max;
	      *Time_out = *Time_in;
	    }
	}
      else			/* Cas ou NSomfin = 0 */
	{
	  *Var_out = *(Var_in - 1);
	  *Time_out = *(Time_in - 1);
	}

      Var_out++;
      Time_out++;
    }

  NbValOut = Ntour;

  /* Et si Reste > 0, Y'a encore une valeur a remplir, indépendament */
  /* de la valeur de Decal.             */
  /* Le nombre de valeurs qu'il reste à "boucler" est Reste - Decal,   */
  /* si ce terme est positif.           */

  if (Reste > 0)
    {
      NbValOut++;
      NSomfin = Reste - Decal;
      if (NSomfin < 0)
	{
	  *Var_out = *(Var_out - 1);	/* Duplication de la fin */
	  *Time_out = *(Time_out - 1);	/* Duplication de la fin */
	}
      else
	{
	  *Var_out = *(Var_in);	/* On ne fait pas de max.... */
	  *Time_out = *(Time_in);	/* On ne fait pas de max.... */
	}
    }

  TabStat[0] = NSom;
  TabStat[1] = Ntour;
  TabStat[2] = Reste;
  TabStat[3] = NSomfin;
  return NbValOut;
}

/* la fonction d'enrobage classique */

int
OP_MaxEch_raf (unsigned long NbVal, void *ArgList[], char *DiagExec)
{
  long CodRet;
  int NCar;
  long TabStat[4];

  NCar =
    sprintf (DiagExec, "MaxEch_raf (%ld ech), rapfreq = %f, decal = %d",
	     NbVal, *((double *) ArgList[2]), *((int *) ArgList[3]));
  if (NCar < 0)
    NCar = 0;
  DiagExec += NCar;

  CodRet = MaxEch_raf (NbVal,
		       (float *) ArgList[0],
		       (double *) ArgList[1],
		       *((double *) ArgList[2]),
		       *((int *) ArgList[3]),
		       (double *) ArgList[4], (float *) ArgList[5], TabStat);

  if (CodRet >= 0)
    {
      if (fabs (TabStat[0] - (1.0 / *((double *) ArgList[2]))) < 1.0e-6)
	{
	  sprintf (DiagExec,
		   "OK: %ld val. calculées,  (%ld = %ld * %ld + %ld).",
		   CodRet, NbVal, TabStat[1], TabStat[0], TabStat[2]);
	}
      else
	{
	  sprintf (DiagExec,
		   "WARN: %g arrondi en %g. %ld val. calculées (%ld*%ld+%ld).",
		   *((double *) ArgList[2]), 1.0 / TabStat[0], CodRet,
		   TabStat[1], TabStat[0], TabStat[2]);
	}
      return OP_OK;
    }
  switch (CodRet)
    {
    case -1:
      sprintf (DiagExec, "ERR: RapFreq > 1 !!!");
      break;
    case -2:
      sprintf (DiagExec, "ERR: Decal hors-bornes.");
      break;
    default:
      sprintf (DiagExec, "ERR: Erreur %ld.", CodRet);
    }
  return OP_FAIL;
}

void
ID_MaxEch_raf (oper * optr)
{
  strcpy (optr->Nom, "MaxEch_raf");
  optr->Version = "$Revision$";
  optr->Date = "$Date$";
  optr->fctptr = OP_MaxEch_raf;
  optr->NbArg = 6;
  optr->misval_auto = 1;	/* On s'en remet au mécanisme automatique.  */
  optr->Arg_Car[0].direction = DIR_IN;
  optr->Arg_Car[0].categorie = VECTOR;
  optr->Arg_Car[0].typ = ATYC_IF32;
  optr->Arg_Car[0].array_dim = "1";
  optr->Arg_Car[0].type_sample = "any";
  optr->Arg_Car[0].sample = "any";
  optr->Arg_Car[0].unite = "any";
  optr->Arg_Car[0].famille = "any";

  optr->Arg_Car[1].direction = DIR_IN;
  optr->Arg_Car[1].categorie = VECTOR;
  optr->Arg_Car[1].typ = ATYC_IF64;
  optr->Arg_Car[1].array_dim = "1";
  optr->Arg_Car[1].type_sample = "any";
  optr->Arg_Car[1].sample = "any";
  optr->Arg_Car[1].unite = "any";
  optr->Arg_Car[1].famille = "any";

  optr->Arg_Car[2].direction = DIR_IN;
  optr->Arg_Car[2].categorie = COEFFICIENT;
  optr->Arg_Car[2].array_dim = "1";
  optr->Arg_Car[2].typ = ATYC_IF64;
  optr->Arg_Car[2].unite = "any";
  optr->Arg_Car[2].type_sample = NULL;
  optr->Arg_Car[2].sample = NULL;

  optr->Arg_Car[3].direction = DIR_IN;
  optr->Arg_Car[3].categorie = COEFFICIENT;
  optr->Arg_Car[3].array_dim = "1";
  optr->Arg_Car[3].typ = ATYC_I32;
  optr->Arg_Car[3].unite = "any";
  optr->Arg_Car[3].type_sample = NULL;
  optr->Arg_Car[3].sample = NULL;

  optr->Arg_Car[4].direction = DIR_OUT;
  optr->Arg_Car[4].categorie = VECTOR;
  optr->Arg_Car[4].typ = ATYC_IF64;
  optr->Arg_Car[4].array_dim = "1";
  optr->Arg_Car[4].name = "$Arg2.name";
  optr->Arg_Car[4].NbVal = "$Arg1.NbVal * $Arg3";
  optr->Arg_Car[4].sample = "$Arg1.sample * $Arg3";
  optr->Arg_Car[4].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[4].ref_time = "$Arg5.nom";
  optr->Arg_Car[4].unite = "$Arg2.unit";
  optr->Arg_Car[4].famille = "$Arg2.famille";

  optr->Arg_Car[5].direction = DIR_OUT;
  optr->Arg_Car[5].categorie = VECTOR;
  optr->Arg_Car[5].typ = ATYC_IF32;
  optr->Arg_Car[5].array_dim = "1";
  optr->Arg_Car[5].name = "$Arg1.name";
  /* Les routines d'interpolations "universelles" obligent à utiliser */
  /* une  formule pour calculer le nombre d'elements du vecteur de sortie. */
  optr->Arg_Car[5].NbVal = "$Arg1.NbVal * $Arg3";
  optr->Arg_Car[5].sample = "$Arg1.sample * $Arg3";
  /* Par contre, l'unite est simple... */
  optr->Arg_Car[5].type_sample = "$Arg1.type_sample";
/*  optr->Arg_Car[5].ref_time = " \"time_\" + $Arg5.sample";  */
  optr->Arg_Car[5].ref_time = "$Arg5.nom";
  optr->Arg_Car[5].misval = "$Arg1.misval";
  optr->Arg_Car[5].unite = "$Arg1.unit";
  optr->Arg_Car[5].famille = "$Arg1.famille";
}
