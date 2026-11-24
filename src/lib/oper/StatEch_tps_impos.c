/*******************************************************************
* OPERATOR      CalculEch_tps_impos.c FUNCTION ANSI-C
*
*
* PURPOSE 	Calcul et échantillonnage d'une variable sur une autre base
*               de temps. 
*
*		
* DESCRIPTION	Cette fonction échantillonne une variable "Var_in"
*		qui est daté par le vecteur temps "time_in" sur une 
*		autre base de temps "time_out".
*		La variable resultat est "Var_out"		
*               On ne fait aucune supposition sur la régularité de
*               l'échantillonnage des 2 variables. Cette fonction peut
*		donc servir, par exemple, à transformer une serie temporelle
*               asynchrone en une série réguliere.
*		On suppose que time_in est "à peu près" trié par ordre
*               croissant.
*		 
* VERSION       1.1  
*
* ARGUMENTS     IN  float   Var_in       any       variable de depart a échantillonner
*               IN  double  time_in    second      base de temps de depart
*               IN  double  Nb_Sec_ecart_avant second    Ecart AVANT sur lequel s'effectue le calcul
*               IN  double  Nb_Sec_ecart_apres second    Ecart max APRES sur lequel s'effectue le calcul
*               IN  int     tolerance_mnq   Nombre mini de valeur pour accepter de faire le calcul (mettre 0 pour faire
*                                           la calcul meme si un seul point !)
*               IN  double  time_out   second    base de temps d'arrivee
*               IN  int     size_out   any       Nb de valeurs dans la base de temps d'arrivee
*
*               OUT float   Var_out     same as "Var_in"  variable "Var_in" échantillonnée
*					             sur la base "time_out"	
*
* CHANGES 	NONE
*
* ENTRY         NONE
*
* SUBPROGRAMS   NONE
*
* REFERENCES     
*             
* COPYRIGHT     Meteo-France
*               Centre National de Recherches Meteorologiques
*               GMEI/TRAMM
*               42, av. G. Coriolis
*               31057   TOULOUSE cedex
*              
*******************************************************************/

#define _POSIX_SOURCE 1
#define _XOPEN_SOURCE 600

#include <stdio.h>
#include <string.h>
#include <math.h>
#include <limits.h>
#include <float.h>
#include <stdlib.h>

#include "struct_oper.h"
#include "oper_util.h"

result_1_t
calcule_min (const float *Var_in,
	     unsigned long j, unsigned long size_in, const double *time_in,
	     double time_inf, double time_sup)
{
  result_1_t result;
  register double loc_min = 0;

  result.Nb_OK = 0;
  result.Nb_mnq = 0;
  result.Nb_avant = 0;
  result.Nb_calc_KO = 0;


  while ((j < size_in) && (time_in[j] <= time_sup))
    {
      if (time_in[j] >= time_inf)
	{
	  if (!isfinite (Var_in[j]))
	    {
	      result.Nb_mnq++;
	    }
	  else
	    {
	      if ( result.Nb_OK == 0 )
	      {
	         loc_min = Var_in[j];
	      }
	      else if  (Var_in[j] < loc_min )
	      {
	         loc_min = Var_in[j];
	      }
	      result.Nb_OK++;
	    }
	}
      else
	{
	  result.Nb_avant++;
	}
      j = j + 1;
    }
  if (result.Nb_OK > 0)
    result.value = loc_min;
  /* si result.Nb_OK == 0, ne pas utiliser result.value. */
  return result;
}

result_1_t
calcule_max (const float *Var_in,
	     unsigned long j, unsigned long size_in, const double *time_in,
	     double time_inf, double time_sup)
{
  result_1_t result;
  register double loc_max = 0;

  result.Nb_OK = 0;
  result.Nb_mnq = 0;
  result.Nb_avant = 0;
  result.Nb_calc_KO = 0;

  while ((j < size_in) && (time_in[j] <= time_sup))
    {
      if (time_in[j] >= time_inf)
	{
	  if (!isfinite (Var_in[j]))
	    {
	      result.Nb_mnq++;
	    }
	  else
	    {
	      if ( result.Nb_OK == 0 )
	      {
	         loc_max = Var_in[j];
	      }
	      else if  (Var_in[j] > loc_max )
	      {
	         loc_max = Var_in[j];
	      }
	      result.Nb_OK++;
	    }
	}
      else
	{
	  result.Nb_avant++;
	}
      j = j + 1;
    }
  if (result.Nb_OK > 0)
    result.value = loc_max;
  /* si result.Nb_OK == 0, ne pas utiliser result.value. */
  return result;
}

result_1_t
calcule_moy (const float *Var_in,
	     unsigned long j, unsigned long size_in, const double *time_in,
	     double time_inf, double time_sup)
{
  result_1_t result;
  register double loc_som = 0.0;

  result.Nb_OK = 0;
  result.Nb_mnq = 0;
  result.Nb_avant = 0;
  result.Nb_calc_KO = 0;

  while ((j < size_in) && (time_in[j] <= time_sup))
    {
    if (time_in[j] - time_inf > 0)
	    {
	    if (!isfinite (Var_in[j]))
	    {
	      result.Nb_mnq++;
	    }
	    else
	    {
	      loc_som += Var_in[j];
	      result.Nb_OK++;
	    }
	  }
    else
	  {
	  result.Nb_avant++;
	  }
      j = j + 1;
  }
  if (result.Nb_OK > 0)
    {
    result.value = loc_som / result.Nb_OK;
    }
  /* si result.Nb_OK == 0, ne pas utiliser result.value. */
  return result;
}

/* calcul de l'écart type sur une période */
/* sigma= sqrt (1/N* som((xi-xmoy)²)*/
result_1_t
calcule_std_moy (const float *Var_in,
	     unsigned long j, unsigned long size_in, const double *time_in,
	     double time_inf, double time_sup)
{
  result_1_t result;
  register double loc_som = 0.0;
  register double loc_std = 0.0;
  register double ecart_moy_carre = 0.0; /* ecart à la moyenne au carré*/
  double loc_moy=0.0;
  unsigned long i;

  result.Nb_OK = 0;
  result.Nb_mnq = 0;
  result.Nb_avant = 0;
  result.Nb_calc_KO = 0;

  i=j;
  /* on recupère la moyenne par classe*/
  while ((i < size_in) && (time_in[i] <= time_sup))
    {
      if (time_in[i] - time_inf > 0)
	    {
	    if (!isfinite (Var_in[i]))
	      {
	      result.Nb_mnq++;
	      }
	    else
	      {
	      loc_som += Var_in[i];
	      result.Nb_OK++;
	      }
	    }
    else
	    {
	    result.Nb_avant++;
	    }
    i = i + 1;
    }
  if (result.Nb_OK > 0)
    {
    result.value = loc_som / result.Nb_OK;
    loc_moy=result.value;
    }

   /* on calcule (x-xmoy)² */
  result.Nb_OK = 0;
  result.Nb_mnq = 0;
  result.Nb_avant = 0;
  result.Nb_calc_KO = 0;

  i=j;
  ecart_moy_carre=0;
  while ((i < size_in) && (time_in[i] <= time_sup))
    {
    if (time_in[i] - time_inf > 0)
	    {
	    if (!isfinite (Var_in[i]))
	      {
	      result.Nb_mnq++;
	      }
	    else
	      {
        ecart_moy_carre= ecart_moy_carre + (Var_in[i]-loc_moy)*(Var_in[i]-loc_moy);
	      result.Nb_OK++;
	      }
	    }
    else
	    {
	    result.Nb_avant++;
	    }
    i = i + 1;
    }

  j=i;
  if (result.Nb_OK > 0)
    {
    result.value = sqrt( ecart_moy_carre / result.Nb_OK);
    }


  return result;
}

result_1_t
calcule_moy_harmonique (const float *Var_in,
	     unsigned long j, unsigned long size_in, const double *time_in,
	     double time_inf, double time_sup)
{
  result_1_t result;
  register double loc_som = 0.0;

  result.Nb_OK = 0;
  result.Nb_mnq = 0;
  result.Nb_avant = 0;
  result.Nb_calc_KO = 0;

  while ((j < size_in) && (time_in[j] <= time_sup))
  {
    /* la moyenne harmonique ne se calcule que pour des données positives, une valeur negative intrdit le calcul*/
	  if (Var_in[j]< 0)
    {
      result.value=K_NaN;
      result.Nb_OK=0;
      result.Nb_calc_KO ++;
	  }
    else 
    {
      if (time_in[j] - time_inf > 0)
  	  {
	    if (!isfinite (Var_in[j]))
	      {
	        result.Nb_mnq++;
	      }
	    else
	      {
        if (fabs(Var_in[j])> 1.0e-8)
          {
	        loc_som += 1/Var_in[j];
	        result.Nb_OK++;
          }
        else
	        {
	        result.Nb_mnq++;
	        }
	      }
	    }
      else
	    {
	      result.Nb_avant++;
	    }
    }
      j = j + 1;
  }
  /* si result.Nb_OK == 0, ne pas utiliser result.value. */
  if ((result.Nb_OK > 0) && (loc_som>0 || loc_som <0))
  {
    result.value = result.Nb_OK/loc_som;
  }
  else
  {
    result.value=K_NaN;
  }
  return result;
}

/*tri par insertion, on ne traite pas les valeurs manquantes qui ne sont pas recopiées dans le tableau de tri*/
/*retourne le nombre de valeurs a traiter: size_tri-nbvalmanq*/
int tri_par_insertion(long size_tri,float * tri_tab)
{
    unsigned long k,/*n,*/rang;
    double xmin;
    long Nb_manq;


    rang=0;
    Nb_manq=0;

    xmin=tri_tab[0];
    for ( rang=1;rang<size_tri;rang++)
      {
      k=rang;
      while (k >0  )
        {
	      if (!isfinite ( tri_tab[k]) )
          {
          Nb_manq++;
          break;
          }
        else
          {
          if (tri_tab[k] >= tri_tab[k-1])
            {
            xmin=tri_tab[k-1];
            break;
            }
          else 
            {
            xmin=tri_tab[k] ;
            tri_tab[k]=tri_tab[k-1] ;
            tri_tab[k-1]=xmin;
            }
          }
        k--;
        }
          
      }
    return (size_tri-Nb_manq);
}

/* calcule mediane avec un tri par insertion*/
result_1_t calcule_med (const float *Var_in,
	     unsigned long j, unsigned long size_in, const double *time_in,
	     double time_inf, double time_sup)
{
result_1_t result;
float *tri_tab; /* tableau de tri de taille size_tri*/
unsigned long i;
long size_tri,size_tri_total;

result.Nb_OK = 0;
result.Nb_mnq = 0;
result.Nb_avant = 0;
result.Nb_calc_KO = 0;

/* calcul de la taille du tableau*/
size_tri=0;
i=j; /* j est le numéro de départ du balayage de Var_in */
while ((i < size_in) && (time_in[i] <= time_sup))
    {
    if (time_in[i] - time_inf >0)
	    {
	    size_tri++;
	    }
        
    i = i + 1;
    }


tri_tab=(float *)malloc( size_tri * sizeof(* tri_tab) );


while ((j < size_in) && (time_in[j] <= time_sup))
    {
    if (time_in[j] - time_inf >0)
	    {
        if (!isfinite (Var_in[j]))
	        {
	        result.Nb_mnq++;
	        }
	    else
	        {
            tri_tab[result.Nb_OK]=Var_in[j];
	        result.Nb_OK++;
	        }
	    }
        
    else
	    {
	    result.Nb_avant++;
	    }
    
    j = j + 1;
    }
       

/*tri par insertion*/
size_tri_total=tri_par_insertion(size_tri, tri_tab);

if (size_tri_total > 0)
{
    if ( ((size_tri_total) % 2) == 0)
    {
        result.value=(tri_tab[(size_tri_total/ 2 )-1]+tri_tab[(size_tri_total/ 2)])/2;
    }
    else
    {
        result.value=(tri_tab[(size_tri_total/ 2 )]);
    }
}
/* le resultat sera mis à misval_out si Nb_OK=0*/
free(tri_tab);
return result;
}

long
Fait_calcul_a_tps_impos (unsigned long size_in,
			 const float *Var_in,
			 const double *time_in,
			 double Nb_Sec_ecart_avant,
			 double Nb_Sec_ecart_apres,
			 int tolerance_mnq,
			 double *time_out,
			 unsigned long size_out,
			 calc_fct_ptr_t functionPtr, float *Var_out,
			 long TabStat[3])
{
  unsigned long i, j_inf;
  long Nb_moy,  Nb_zero, Nb_inf, Nb_calc_KO;
  long pre_diag;
  const float misval_out = K_NaN;
  long nb_neg; /* on vérifie l'absence de valeurs négatives pour les opérations sur les valeurs positives uniquement (ex moyh)*/
  result_1_t result;

  double time_inf, time_sup;

  Nb_moy = 0;
  Nb_zero = 0;
  Nb_inf = 0;
  Nb_calc_KO = 0;

  pre_diag = 0;
  if (time_in[size_in - 1] < (time_out[0] - Nb_Sec_ecart_avant))
  {
    pre_diag = -1;
    Nb_zero = size_out;
  }

  if ((time_out[size_out - 1] + Nb_Sec_ecart_apres) < time_in[0])
  {
    pre_diag = -2;
    Nb_zero = size_out;
  }

  if ((Nb_Sec_ecart_avant + Nb_Sec_ecart_apres) <= 0)
  {
    pre_diag = -3;
    Nb_zero = size_out;
  }

  /* l'instant c'est une information tant qu'on ne sait pas si le calcul est autorisé*/
  /*for (i = 0; i < size_in; i++)
  {
    nb_neg=0;
    if (Var_in[i] <0)
        nb_neg++;
    if (nb_neg > 0)
    {
      pre_diag = -4;
    }     
  }*/
 
  /*if ((pre_diag != 0) && (pre_diag != 4) )*/
  if ((pre_diag != 0)  )
  {
    for (i = 0; i < size_out; i++)
	  {
	    Var_out[i] = misval_out;
	  }
    TabStat[0] = Nb_moy;
    TabStat[1] = Nb_zero;
    TabStat[2] = Nb_inf;
      /*TabStat[3] = Nb_calc_KO;*/
    return pre_diag;
  }

  j_inf = 0;
  for (i = 0; i < size_out; i++)
  /*i=size_out;
  while (i<=size_out || pre_diag!=-4)*/
  {
    time_inf = time_out[i] - Nb_Sec_ecart_avant;
    time_sup = time_out[i] + Nb_Sec_ecart_apres;

    result = functionPtr (Var_in, j_inf, size_in, time_in, time_inf, time_sup);
    /* code d'erreur quand il existe des donnees negatives et que c'est interdit*/
    if (result.Nb_calc_KO > 0)
    {
	    Var_out[i] = misval_out;
      Nb_zero=size_out;
      TabStat[0] = Nb_moy;
      TabStat[1] = Nb_zero;
      TabStat[2] = Nb_inf;
      pre_diag= -4;
      /*i=size_out;*/
    }
    else if (result.Nb_OK == 0)
	  {
	    Var_out[i] = misval_out;
	    Nb_zero++;
	  }
    else if (result.Nb_OK <= tolerance_mnq)
	  {
	    Var_out[i] = misval_out;
	    Nb_inf++;
	  }
    else
	  {
	    Var_out[i] = result.value;
	    Nb_moy++;
	  }
      /* On repart du premier élément de var_in 
       * qui a passé le test (time_in[j] >= time_inf) */
    j_inf += result.Nb_avant;
  }

  TabStat[0] = Nb_moy;
  TabStat[1] = Nb_zero;
  TabStat[2] = Nb_inf;
  /*TabStat[3] = Nb_calc_KO;*/

  if (pre_diag==-4)
      return pre_diag;
  else
    return i;
}

/* fonction d'enrobage */

int
OP_MinEch_tps_impos (unsigned long Nbval, void *ArgList[], char *DiagExec)
{
  int NCar;
  long CodRet;
  long TabStat[3];
  unsigned long nb_val_dest;

  nb_val_dest = *((unsigned long *) ArgList[6]);

  NCar = sprintf (DiagExec, "MinEch_tps_impos (%lu ech), ", Nbval);
  DiagExec += NCar;
  DiagExec = ecrit_bornes_temps (DiagExec, "time_orig", (double *) ArgList[1],
				 Nbval);
  NCar = sprintf (DiagExec, "ecart_av=%g, ecart_ap=%g, mini_ok=%d, ",
		  *((double *) ArgList[2]), *((double *) ArgList[3]),
		  *((int *) ArgList[4]));
  DiagExec += NCar;
  DiagExec = ecrit_bornes_temps (DiagExec, "time_dest", (double *) ArgList[5],
				 nb_val_dest);
  NCar = sprintf (DiagExec, " nb_resu=%lu", *((unsigned long *) ArgList[6]));
  DiagExec += NCar;

  CodRet =
    Fait_calcul_a_tps_impos (Nbval, (float *) ArgList[0],
			     (double *) ArgList[1],
			     *((double *) ArgList[2]),
			     *((double *) ArgList[3]),
			     *((int *) ArgList[4]),
			     (double *) ArgList[5],
			     *((unsigned long *) ArgList[6]),
			     calcule_min, (float *) ArgList[7], TabStat);

  if (CodRet == -1)
    {
      sprintf (DiagExec, "Les 2 periodes de temps ne se chevauchent pas, "
	       "Le dernier temps d'origine (%g) est avant le premier temps demandé (%g)",
	       ((double *) ArgList[1])[Nbval - 1],
	       ((double *) ArgList[5])[0] - *((double *) ArgList[2]));
    }
  else if (CodRet == -2)
    {
      sprintf (DiagExec, "Les 2 periodes de temps ne se chevauchent pas, "
	       "Le premier temps d'origine (%g) est apres le dernier temps demandé (%g)",
	       ((double *) ArgList[1])[0],
	       ((double *) ArgList[5])[nb_val_dest] +
	       *((double *) ArgList[3]));
    }
  else if (CodRet == -3)
    {
      sprintf (DiagExec,
	       "intervalle de temps trop petit : %g sec. avant, %g sec. apres",
	       *((double *) ArgList[2]), *((double *) ArgList[3]));
    }
  else
    {
      sprintf (DiagExec,
	       "OK: %ld val. en sortie,  (OK:%ld, 0:%ld, pas_assez:%ld).",
	       CodRet, TabStat[0], TabStat[1], TabStat[2]);
    }

  return OP_OK;
}

int
OP_MaxEch_tps_impos (unsigned long Nbval, void *ArgList[], char *DiagExec)
{
  int NCar;
  long CodRet;
  long TabStat[3];
  unsigned long nb_val_dest;

  nb_val_dest = *((unsigned long *) ArgList[6]);

  NCar = sprintf (DiagExec, "MaxEch_tps_impos (%lu ech), ", Nbval);
  DiagExec += NCar;
  DiagExec = ecrit_bornes_temps (DiagExec, "time_orig", (double *) ArgList[1],
				 Nbval);
  NCar = sprintf (DiagExec, "ecart_av=%g, ecart_ap=%g, mini_ok=%d, ",
		  *((double *) ArgList[2]), *((double *) ArgList[3]),
		  *((int *) ArgList[4]));
  DiagExec += NCar;
  DiagExec = ecrit_bornes_temps (DiagExec, "time_dest", (double *) ArgList[5],
				 nb_val_dest);
  NCar = sprintf (DiagExec, " nb_resu=%lu", *((unsigned long *) ArgList[6]));
  DiagExec += NCar;

  CodRet =
    Fait_calcul_a_tps_impos (Nbval, (float *) ArgList[0],
			     (double *) ArgList[1],
			     *((double *) ArgList[2]),
			     *((double *) ArgList[3]),
			     *((int *) ArgList[4]),
			     (double *) ArgList[5],
			     *((unsigned long *) ArgList[6]),
			     calcule_max, (float *) ArgList[7], TabStat);

  if (CodRet == -1)
    {
      sprintf (DiagExec, "Les 2 periodes de temps ne se chevauchent pas, "
	       "Le dernier temps d'origine (%g) est avant le premier temps demandé (%g)",
	       ((double *) ArgList[1])[Nbval - 1],
	       ((double *) ArgList[5])[0] - *((double *) ArgList[2]));
    }
  else if (CodRet == -2)
    {
      sprintf (DiagExec, "Les 2 periodes de temps ne se chevauchent pas, "
	       "Le premier temps d'origine (%g) est apres le dernier temps demandé (%g)",
	       ((double *) ArgList[1])[0],
	       ((double *) ArgList[5])[nb_val_dest] +
	       *((double *) ArgList[3]));
    }
  else if (CodRet == -3)
    {
      sprintf (DiagExec,
	       "intervalle de temps trop petit : %g sec. avant, %g sec. apres",
	       *((double *) ArgList[2]), *((double *) ArgList[3]));
    }
  else
    {
      sprintf (DiagExec,
	       "OK: %ld val. en sortie,  (OK:%ld, 0:%ld, pas_assez:%ld).",
	       CodRet, TabStat[0], TabStat[1], TabStat[2]);
    }

  return OP_OK;
}

int
OP_MoyEch_tps_impos (unsigned long Nbval, void *ArgList[], char *DiagExec)
{
  int NCar;
  long CodRet;
  long TabStat[3];
  unsigned long nb_val_dest;

  nb_val_dest = *((unsigned long *) ArgList[6]);

  NCar = sprintf (DiagExec, "MoyEch_tps_impos (%lu ech), ", Nbval);
  DiagExec += NCar;
  DiagExec = ecrit_bornes_temps (DiagExec, "time_orig", (double *) ArgList[1],
				 Nbval);
  NCar = sprintf (DiagExec, "ecart_av=%g, ecart_ap=%g, mini_ok=%d, ",
		  *((double *) ArgList[2]), *((double *) ArgList[3]),
		  *((int *) ArgList[4]));
  DiagExec += NCar;
  DiagExec = ecrit_bornes_temps (DiagExec, "time_dest", (double *) ArgList[5],
				 nb_val_dest);
  NCar = sprintf (DiagExec, " nb_resu=%lu", *((unsigned long *) ArgList[6]));
  DiagExec += NCar;

  CodRet =
    Fait_calcul_a_tps_impos (Nbval, (float *) ArgList[0],
			     (double *) ArgList[1],
			     *((double *) ArgList[2]),
			     *((double *) ArgList[3]),
			     *((int *) ArgList[4]),
			     (double *) ArgList[5],
			     *((unsigned long *) ArgList[6]),
			     calcule_moy, (float *) ArgList[7], TabStat);

  if (CodRet == -1)
    {
      sprintf (DiagExec, "Les 2 periodes de temps ne se chevauchent pas, "
	       "Le dernier temps d'origine (%g) est avant le premier temps demandé (%g)",
	       ((double *) ArgList[1])[Nbval - 1],
	       ((double *) ArgList[5])[0] - *((double *) ArgList[2]));
    }
  else if (CodRet == -2)
    {
      sprintf (DiagExec, "Les 2 periodes de temps ne se chevauchent pas, "
	       "Le premier temps d'origine (%g) est apres le dernier temps demandé (%g)",
	       ((double *) ArgList[1])[0],
	       ((double *) ArgList[5])[nb_val_dest] +
	       *((double *) ArgList[3]));
    }
  else if (CodRet == -3)
    {
      sprintf (DiagExec,
	       "intervalle de temps trop petit : %g sec. avant, %g sec. apres",
	       *((double *) ArgList[2]), *((double *) ArgList[3]));
    }
  else
    {
      sprintf (DiagExec,
	       "OK: %ld val. en sortie,  (OK:%ld, 0:%ld, pas_assez:%ld).",
	       CodRet, TabStat[0], TabStat[1], TabStat[2]);
    }

  return OP_OK;
}

int
OP_StdMoyEch_tps_impos (unsigned long Nbval, void *ArgList[], char *DiagExec)
{
  int NCar;
  long CodRet;
  long TabStat[3];
  unsigned long nb_val_dest;

  nb_val_dest = *((unsigned long *) ArgList[6]);

  NCar = sprintf (DiagExec, "StdMoyEch_tps_impos (%lu ech), ", Nbval);
  DiagExec += NCar;
  DiagExec = ecrit_bornes_temps (DiagExec, "time_orig", (double *) ArgList[1],
				 Nbval);
  NCar = sprintf (DiagExec, "ecart_av=%g, ecart_ap=%g, mini_ok=%d, ",
		  *((double *) ArgList[2]), *((double *) ArgList[3]),
		  *((int *) ArgList[4]));
  DiagExec += NCar;
  DiagExec = ecrit_bornes_temps (DiagExec, "time_dest", (double *) ArgList[5],
				 nb_val_dest);
  NCar = sprintf (DiagExec, " nb_resu=%lu", *((unsigned long *) ArgList[6]));
  DiagExec += NCar;

  CodRet =
    Fait_calcul_a_tps_impos (Nbval, (float *) ArgList[0],
			     (double *) ArgList[1],
			     *((double *) ArgList[2]),
			     *((double *) ArgList[3]),
			     *((int *) ArgList[4]),
			     (double *) ArgList[5],
			     *((unsigned long *) ArgList[6]),
			     calcule_std_moy, (float *) ArgList[7], TabStat);

  if (CodRet == -1)
    {
      sprintf (DiagExec, "Les 2 periodes de temps ne se chevauchent pas, "
	       "Le dernier temps d'origine (%g) est avant le premier temps demandé (%g)",
	       ((double *) ArgList[1])[Nbval - 1],
	       ((double *) ArgList[5])[0] - *((double *) ArgList[2]));
    }
  else if (CodRet == -2)
    {
      sprintf (DiagExec, "Les 2 periodes de temps ne se chevauchent pas, "
	       "Le premier temps d'origine (%g) est apres le dernier temps demandé (%g)",
	       ((double *) ArgList[1])[0],
	       ((double *) ArgList[5])[nb_val_dest] +
	       *((double *) ArgList[3]));
    }
  else if (CodRet == -3)
    {
      sprintf (DiagExec,
	       "intervalle de temps trop petit : %g sec. avant, %g sec. apres",
	       *((double *) ArgList[2]), *((double *) ArgList[3]));
    }
  else
    {
      sprintf (DiagExec,
	       "OK: %ld val. en sortie,  (OK:%ld, 0:%ld, pas_assez:%ld).",
	       CodRet, TabStat[0], TabStat[1], TabStat[2]);
    }

  return OP_OK;
}

int
OP_MoyHarmEch_tps_impos (unsigned long Nbval, void *ArgList[], char *DiagExec)
{
  int NCar;
  long CodRet,CodFin;
  long TabStat[3];
  unsigned long nb_val_dest;

  nb_val_dest = *((unsigned long *) ArgList[6]);

  NCar = sprintf (DiagExec, "MoyHarmEch_tps_impos (%lu ech), ", Nbval);
  DiagExec += NCar;
  DiagExec = ecrit_bornes_temps (DiagExec, "time_orig", (double *) ArgList[1],
				 Nbval);
  NCar = sprintf (DiagExec, "ecart_av=%g, ecart_ap=%g, mini_ok=%d, ",
		  *((double *) ArgList[2]), *((double *) ArgList[3]),
		  *((int *) ArgList[4]));
  DiagExec += NCar;
  DiagExec = ecrit_bornes_temps (DiagExec, "time_dest", (double *) ArgList[5],
				 nb_val_dest);
  NCar = sprintf (DiagExec, " nb_resu=%lu", *((unsigned long *) ArgList[6]));
  DiagExec += NCar;

  CodRet =
    Fait_calcul_a_tps_impos (Nbval, (float *) ArgList[0],
			     (double *) ArgList[1],
			     *((double *) ArgList[2]),
			     *((double *) ArgList[3]),
			     *((int *) ArgList[4]),
			     (double *) ArgList[5],
			     *((unsigned long *) ArgList[6]),
			     calcule_moy_harmonique, (float *) ArgList[7], TabStat);

  CodFin=OP_OK;
  if (CodRet == -1)
  {
    sprintf (DiagExec, "Les 2 periodes de temps ne se chevauchent pas, "
	       "Le dernier temps d'origine (%g) est avant le premier temps demandé (%g)",
	       ((double *) ArgList[1])[Nbval - 1],
	       ((double *) ArgList[5])[0] - *((double *) ArgList[2]));
  }
  else if (CodRet == -2)
  {
    sprintf (DiagExec, "Les 2 periodes de temps ne se chevauchent pas, "
	       "Le premier temps d'origine (%g) est apres le dernier temps demandé (%g)",
	       ((double *) ArgList[1])[0],
	       ((double *) ArgList[5])[nb_val_dest] +
	       *((double *) ArgList[3]));
  }
  else if (CodRet == -3)
  {
    sprintf (DiagExec,
	       "intervalle de temps trop petit : %g sec. avant, %g sec. apres",
	       *((double *) ArgList[2]), *((double *) ArgList[3]));
  }
  else if (CodRet == -4)
  {
    sprintf (DiagExec,
	       " Il existe des valeur négatives dans le vecteur. Impossible de calculer a moyenne harmonique.");
    CodFin=OP_FAIL;
  }
  else
    {
      sprintf (DiagExec,
	       "OK: %ld val. en sortie,  (OK:%ld, 0:%ld, pas_assez:%ld).",
	       CodRet, TabStat[0], TabStat[1], TabStat[2]);
    }

  return CodFin;
}

int
OP_MedEch_tps_impos (unsigned long Nbval, void *ArgList[], char *DiagExec)
{
  int NCar;
  long CodRet;
  long TabStat[3];
  unsigned long nb_val_dest;

  nb_val_dest = *((unsigned long *) ArgList[6]);

  NCar = sprintf (DiagExec, "MedEch_tps_impos (%lu ech), ", Nbval);
  DiagExec += NCar;
  DiagExec = ecrit_bornes_temps (DiagExec, "time_orig", (double *) ArgList[1],
				 Nbval);
  NCar = sprintf (DiagExec, "ecart_av=%g, ecart_ap=%g, mini_ok=%d, ",
		  *((double *) ArgList[2]), *((double *) ArgList[3]),
		  *((int *) ArgList[4]));
  DiagExec += NCar;
  DiagExec = ecrit_bornes_temps (DiagExec, "time_dest", (double *) ArgList[5],
				 nb_val_dest);
  NCar = sprintf (DiagExec, " nb_resu=%lu", *((unsigned long *) ArgList[6]));
  DiagExec += NCar;

  CodRet =
    Fait_calcul_a_tps_impos (Nbval, (float *) ArgList[0],
			     (double *) ArgList[1],
			     *((double *) ArgList[2]),
			     *((double *) ArgList[3]),
			     *((int *) ArgList[4]),
			     (double *) ArgList[5],
			     *((unsigned long *) ArgList[6]),
			     calcule_med, (float *) ArgList[7], TabStat);

  if (CodRet == -1)
    {
      sprintf (DiagExec, "Les 2 periodes de temps ne se chevauchent pas, "
	       "Le dernier temps d'origine (%g) est avant le premier temps demandé (%g)",
	       ((double *) ArgList[1])[Nbval - 1],
	       ((double *) ArgList[5])[0] - *((double *) ArgList[2]));
    }
  else if (CodRet == -2)
    {
      sprintf (DiagExec, "Les 2 periodes de temps ne se chevauchent pas, "
	       "Le premier temps d'origine (%g) est apres le dernier temps demandé (%g)",
	       ((double *) ArgList[1])[0],
	       ((double *) ArgList[5])[nb_val_dest] +
	       *((double *) ArgList[3]));
    }
  else if (CodRet == -3)
    {
      sprintf (DiagExec,
	       "intervalle de temps trop petit : %g sec. avant, %g sec. apres",
	       *((double *) ArgList[2]), *((double *) ArgList[3]));
    }
  else
    {
      sprintf (DiagExec,
	       "OK: %ld val. en sortie,  (OK:%ld, 0:%ld, pas_assez:%ld).",
	       CodRet, TabStat[0], TabStat[1], TabStat[2]);
    }

  return OP_OK;
}

void
ID_MoyEch_tps_impos (oper * optr)
{
  strcpy (optr->Nom, "MoyEch_tps_impos");
  optr->Version = "$Revision: 5436 $";
  optr->Date = "$Date: 2013-10-18 18:27:26 +0200 (ven. 18 oct. 2013) $";
  optr->fctptr = OP_MoyEch_tps_impos;
  optr->NbArg = 8;

  /* 1: X_in */
  optr->Arg_Car[0].direction = DIR_IN;
  optr->Arg_Car[0].categorie = VECTOR;
  optr->Arg_Car[0].typ = ATYC_IF32;
  optr->Arg_Car[0].array_dim = "1";
  optr->Arg_Car[0].type_sample = "any";
  optr->Arg_Car[0].sample = "any";
  optr->Arg_Car[0].unite = "";

  /* 2: time_in */
  optr->Arg_Car[1].direction = DIR_IN;
  optr->Arg_Car[1].categorie = VECTOR;
  optr->Arg_Car[1].typ = ATYC_IF64;
  optr->Arg_Car[1].array_dim = "1";
  optr->Arg_Car[1].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[1].type_sample = "any";
  optr->Arg_Car[1].sample = "any";
  optr->Arg_Car[1].unite = "second";

  /* 3: Ecart avant */
  optr->Arg_Car[2].direction = DIR_IN;
  optr->Arg_Car[2].categorie = COEFFICIENT;
  optr->Arg_Car[2].typ = ATYC_IF64;
  optr->Arg_Car[2].array_dim = "1";
  optr->Arg_Car[2].type_sample = "any";
  optr->Arg_Car[2].sample = "any";
  optr->Arg_Car[2].unite = "";

  /* 4: Ecart apres */
  optr->Arg_Car[3].direction = DIR_IN;
  optr->Arg_Car[3].categorie = COEFFICIENT;
  optr->Arg_Car[3].typ = ATYC_IF64;
  optr->Arg_Car[3].array_dim = "1";
  optr->Arg_Car[3].type_sample = "any";
  optr->Arg_Car[3].sample = "any";
  optr->Arg_Car[3].unite = "";

  /* 5: Mini_OK acceptés */
  optr->Arg_Car[4].direction = DIR_IN;
  optr->Arg_Car[4].categorie = COEFFICIENT;
  optr->Arg_Car[4].typ = ATYC_I32;
  optr->Arg_Car[4].array_dim = "1";
  optr->Arg_Car[4].type_sample = "any";
  optr->Arg_Car[4].sample = "any";
  optr->Arg_Car[4].unite = "";

  /* 6: time_out */
  optr->Arg_Car[5].direction = DIR_IN;
  optr->Arg_Car[5].categorie = VECTOR;
  optr->Arg_Car[5].typ = ATYC_IF64;
  optr->Arg_Car[5].array_dim = "1";
  optr->Arg_Car[5].type_sample = "any";
  optr->Arg_Car[5].sample = "any";
  optr->Arg_Car[5].unite = "second";

  /* 7: size_out */
  optr->Arg_Car[6].direction = DIR_IN;
  optr->Arg_Car[6].categorie = COEFFICIENT;
  optr->Arg_Car[6].typ = ATYC_LOCAL_ULONG;
  optr->Arg_Car[6].array_dim = "1";
  optr->Arg_Car[6].type_sample = "any";
  optr->Arg_Car[6].sample = "any";
  optr->Arg_Car[6].unite = "";

  /* 8: X_out */
  optr->Arg_Car[7].direction = DIR_OUT;
  optr->Arg_Car[7].categorie = VECTOR;
  optr->Arg_Car[7].typ = ATYC_IF32;
  optr->Arg_Car[7].array_dim = "1";
  optr->Arg_Car[7].NbVal = "$Arg6.NbVal";	/* ou $Arg6.value */
  optr->Arg_Car[7].type_sample = "$Arg6.type_sample";
  optr->Arg_Car[7].sample = "$Arg6.sample";
  optr->Arg_Car[7].ref_time = " $Arg6.nom ";
  optr->Arg_Car[7].unite = "$Arg1.unit";
  optr->Arg_Car[7].famille = "$Arg1.famille";
  optr->Arg_Car[7].misval = "$Arg1.misval";
  optr->Arg_Car[7].name = "$Arg1.name + \" synchronise sur \" + $Arg6.name";
  optr->Arg_Car[7].en_name =
    "$Arg1.english_name + \" synchronised on \" + $Arg6.english_name";
}

void
ID_StdMoyEch_tps_impos (oper * optr)
{
  strcpy (optr->Nom, "StdMoyEch_tps_impos");
  optr->Version = "$Revision: 5436 $";
  optr->Date = "$Date: 2013-10-18 18:27:26 +0200 (ven. 18 oct. 2013) $";
  optr->fctptr = OP_StdMoyEch_tps_impos;
  optr->NbArg = 8;

  /* 1: X_in */
  optr->Arg_Car[0].direction = DIR_IN;
  optr->Arg_Car[0].categorie = VECTOR;
  optr->Arg_Car[0].typ = ATYC_IF32;
  optr->Arg_Car[0].array_dim = "1";
  optr->Arg_Car[0].type_sample = "any";
  optr->Arg_Car[0].sample = "any";
  optr->Arg_Car[0].unite = "";

  /* 2: time_in */
  optr->Arg_Car[1].direction = DIR_IN;
  optr->Arg_Car[1].categorie = VECTOR;
  optr->Arg_Car[1].typ = ATYC_IF64;
  optr->Arg_Car[1].array_dim = "1";
  optr->Arg_Car[1].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[1].type_sample = "any";
  optr->Arg_Car[1].sample = "any";
  optr->Arg_Car[1].unite = "second";

  /* 3: Ecart avant */
  optr->Arg_Car[2].direction = DIR_IN;
  optr->Arg_Car[2].categorie = COEFFICIENT;
  optr->Arg_Car[2].typ = ATYC_IF64;
  optr->Arg_Car[2].array_dim = "1";
  optr->Arg_Car[2].type_sample = "any";
  optr->Arg_Car[2].sample = "any";
  optr->Arg_Car[2].unite = "";

  /* 4: Ecart apres */
  optr->Arg_Car[3].direction = DIR_IN;
  optr->Arg_Car[3].categorie = COEFFICIENT;
  optr->Arg_Car[3].typ = ATYC_IF64;
  optr->Arg_Car[3].array_dim = "1";
  optr->Arg_Car[3].type_sample = "any";
  optr->Arg_Car[3].sample = "any";
  optr->Arg_Car[3].unite = "";

  /* 5: Mini_OK acceptés */
  optr->Arg_Car[4].direction = DIR_IN;
  optr->Arg_Car[4].categorie = COEFFICIENT;
  optr->Arg_Car[4].typ = ATYC_I32;
  optr->Arg_Car[4].array_dim = "1";
  optr->Arg_Car[4].type_sample = "any";
  optr->Arg_Car[4].sample = "any";
  optr->Arg_Car[4].unite = "";

  /* 6: time_out */
  optr->Arg_Car[5].direction = DIR_IN;
  optr->Arg_Car[5].categorie = VECTOR;
  optr->Arg_Car[5].typ = ATYC_IF64;
  optr->Arg_Car[5].array_dim = "1";
  optr->Arg_Car[5].type_sample = "any";
  optr->Arg_Car[5].sample = "any";
  optr->Arg_Car[5].unite = "second";

  /* 7: size_out */
  optr->Arg_Car[6].direction = DIR_IN;
  optr->Arg_Car[6].categorie = COEFFICIENT;
  optr->Arg_Car[6].typ = ATYC_LOCAL_ULONG;
  optr->Arg_Car[6].array_dim = "1";
  optr->Arg_Car[6].type_sample = "any";
  optr->Arg_Car[6].sample = "any";
  optr->Arg_Car[6].unite = "";

  /* 8: X_out */
  optr->Arg_Car[7].direction = DIR_OUT;
  optr->Arg_Car[7].categorie = VECTOR;
  optr->Arg_Car[7].typ = ATYC_IF32;
  optr->Arg_Car[7].array_dim = "1";
  optr->Arg_Car[7].NbVal = "$Arg6.NbVal";	/* ou $Arg6.value */
  optr->Arg_Car[7].type_sample = "$Arg6.type_sample";
  optr->Arg_Car[7].sample = "$Arg6.sample";
  optr->Arg_Car[7].ref_time = " $Arg6.nom ";
  optr->Arg_Car[7].unite = "$Arg1.unit";
  optr->Arg_Car[7].famille = "$Arg1.famille";
  optr->Arg_Car[7].misval = "$Arg1.misval";
  optr->Arg_Car[7].name = "$Arg1.name + \" synchronise sur \" + $Arg6.name";
  optr->Arg_Car[7].en_name =
    "$Arg1.english_name + \" synchronised on \" + $Arg6.english_name";
}

void
ID_MinEch_tps_impos (oper * optr)
{
  strcpy (optr->Nom, "MinEch_tps_impos");
  optr->Version = "$Revision: 5436 $";
  optr->Date = "$Date: 2013-10-18 18:27:26 +0200 (ven. 18 oct. 2013) $";
  optr->fctptr = OP_MinEch_tps_impos;
  optr->NbArg = 8;

  /* 1: X_in */
  optr->Arg_Car[0].direction = DIR_IN;
  optr->Arg_Car[0].categorie = VECTOR;
  optr->Arg_Car[0].typ = ATYC_IF32;
  optr->Arg_Car[0].array_dim = "1";
  optr->Arg_Car[0].type_sample = "any";
  optr->Arg_Car[0].sample = "any";
  optr->Arg_Car[0].unite = "";

  /* 2: time_in */
  optr->Arg_Car[1].direction = DIR_IN;
  optr->Arg_Car[1].categorie = VECTOR;
  optr->Arg_Car[1].typ = ATYC_IF64;
  optr->Arg_Car[1].array_dim = "1";
  optr->Arg_Car[1].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[1].type_sample = "any";
  optr->Arg_Car[1].sample = "any";
  optr->Arg_Car[1].unite = "second";

  /* 3: Ecart avant */
  optr->Arg_Car[2].direction = DIR_IN;
  optr->Arg_Car[2].categorie = COEFFICIENT;
  optr->Arg_Car[2].typ = ATYC_IF64;
  optr->Arg_Car[2].array_dim = "1";
  optr->Arg_Car[2].type_sample = "any";
  optr->Arg_Car[2].sample = "any";
  optr->Arg_Car[2].unite = "";

  /* 4: Ecart apres */
  optr->Arg_Car[3].direction = DIR_IN;
  optr->Arg_Car[3].categorie = COEFFICIENT;
  optr->Arg_Car[3].typ = ATYC_IF64;
  optr->Arg_Car[3].array_dim = "1";
  optr->Arg_Car[3].type_sample = "any";
  optr->Arg_Car[3].sample = "any";
  optr->Arg_Car[3].unite = "";

  /* 5: Mini_OK acceptés */
  optr->Arg_Car[4].direction = DIR_IN;
  optr->Arg_Car[4].categorie = COEFFICIENT;
  optr->Arg_Car[4].typ = ATYC_I32;
  optr->Arg_Car[4].array_dim = "1";
  optr->Arg_Car[4].type_sample = "any";
  optr->Arg_Car[4].sample = "any";
  optr->Arg_Car[4].unite = "";

  /* 6: time_out */
  optr->Arg_Car[5].direction = DIR_IN;
  optr->Arg_Car[5].categorie = VECTOR;
  optr->Arg_Car[5].typ = ATYC_IF64;
  optr->Arg_Car[5].array_dim = "1";
  optr->Arg_Car[5].type_sample = "any";
  optr->Arg_Car[5].sample = "any";
  optr->Arg_Car[5].unite = "second";

  /* 7: size_out */
  optr->Arg_Car[6].direction = DIR_IN;
  optr->Arg_Car[6].categorie = COEFFICIENT;
  optr->Arg_Car[6].typ = ATYC_LOCAL_ULONG;
  optr->Arg_Car[6].array_dim = "1";
  optr->Arg_Car[6].type_sample = "any";
  optr->Arg_Car[6].sample = "any";
  optr->Arg_Car[6].unite = "";

  /* 8: X_out */
  optr->Arg_Car[7].direction = DIR_OUT;
  optr->Arg_Car[7].categorie = VECTOR;
  optr->Arg_Car[7].typ = ATYC_IF32;
  optr->Arg_Car[7].array_dim = "1";
  optr->Arg_Car[7].NbVal = "$Arg6.NbVal";	/* ou $Arg6.value */
  optr->Arg_Car[7].type_sample = "$Arg6.type_sample";
  optr->Arg_Car[7].sample = "$Arg6.sample";
  optr->Arg_Car[7].ref_time = " $Arg6.nom ";
  optr->Arg_Car[7].unite = "$Arg1.unit";
  optr->Arg_Car[7].famille = "$Arg1.famille";
  optr->Arg_Car[7].misval = "$Arg1.misval";
  optr->Arg_Car[7].name = "$Arg1.name + \" synchronise sur \" + $Arg6.name";
  optr->Arg_Car[7].en_name =
    "$Arg1.english_name + \" synchronised on \" + $Arg6.english_name";
}

void
ID_MaxEch_tps_impos (oper * optr)
{
  strcpy (optr->Nom, "MaxEch_tps_impos");
  optr->Version = "$Revision: 5436 $";
  optr->Date = "$Date: 2013-10-18 18:27:26 +0200 (ven. 18 oct. 2013) $";
  optr->fctptr = OP_MaxEch_tps_impos;
  optr->NbArg = 8;

  /* 1: X_in */
  optr->Arg_Car[0].direction = DIR_IN;
  optr->Arg_Car[0].categorie = VECTOR;
  optr->Arg_Car[0].typ = ATYC_IF32;
  optr->Arg_Car[0].array_dim = "1";
  optr->Arg_Car[0].type_sample = "any";
  optr->Arg_Car[0].sample = "any";
  optr->Arg_Car[0].unite = "";

  /* 2: time_in */
  optr->Arg_Car[1].direction = DIR_IN;
  optr->Arg_Car[1].categorie = VECTOR;
  optr->Arg_Car[1].typ = ATYC_IF64;
  optr->Arg_Car[1].array_dim = "1";
  optr->Arg_Car[1].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[1].type_sample = "any";
  optr->Arg_Car[1].sample = "any";
  optr->Arg_Car[1].unite = "second";

  /* 3: Ecart avant */
  optr->Arg_Car[2].direction = DIR_IN;
  optr->Arg_Car[2].categorie = COEFFICIENT;
  optr->Arg_Car[2].typ = ATYC_IF64;
  optr->Arg_Car[2].array_dim = "1";
  optr->Arg_Car[2].type_sample = "any";
  optr->Arg_Car[2].sample = "any";
  optr->Arg_Car[2].unite = "";

  /* 4: Ecart apres */
  optr->Arg_Car[3].direction = DIR_IN;
  optr->Arg_Car[3].categorie = COEFFICIENT;
  optr->Arg_Car[3].typ = ATYC_IF64;
  optr->Arg_Car[3].array_dim = "1";
  optr->Arg_Car[3].type_sample = "any";
  optr->Arg_Car[3].sample = "any";
  optr->Arg_Car[3].unite = "";

  /* 5: Mini_OK acceptés */
  optr->Arg_Car[4].direction = DIR_IN;
  optr->Arg_Car[4].categorie = COEFFICIENT;
  optr->Arg_Car[4].typ = ATYC_I32;
  optr->Arg_Car[4].array_dim = "1";
  optr->Arg_Car[4].type_sample = "any";
  optr->Arg_Car[4].sample = "any";
  optr->Arg_Car[4].unite = "";

  /* 6: time_out */
  optr->Arg_Car[5].direction = DIR_IN;
  optr->Arg_Car[5].categorie = VECTOR;
  optr->Arg_Car[5].typ = ATYC_IF64;
  optr->Arg_Car[5].array_dim = "1";
  optr->Arg_Car[5].type_sample = "any";
  optr->Arg_Car[5].sample = "any";
  optr->Arg_Car[5].unite = "second";

  /* 7: size_out */
  optr->Arg_Car[6].direction = DIR_IN;
  optr->Arg_Car[6].categorie = COEFFICIENT;
  optr->Arg_Car[6].typ = ATYC_LOCAL_ULONG;
  optr->Arg_Car[6].array_dim = "1";
  optr->Arg_Car[6].type_sample = "any";
  optr->Arg_Car[6].sample = "any";
  optr->Arg_Car[6].unite = "";

  /* 8: X_out */
  optr->Arg_Car[7].direction = DIR_OUT;
  optr->Arg_Car[7].categorie = VECTOR;
  optr->Arg_Car[7].typ = ATYC_IF32;
  optr->Arg_Car[7].array_dim = "1";
  optr->Arg_Car[7].NbVal = "$Arg6.NbVal";	/* ou $Arg6.value */
  optr->Arg_Car[7].type_sample = "$Arg6.type_sample";
  optr->Arg_Car[7].sample = "$Arg6.sample";
  optr->Arg_Car[7].ref_time = " $Arg6.nom ";
  optr->Arg_Car[7].unite = "$Arg1.unit";
  optr->Arg_Car[7].famille = "$Arg1.famille";
  optr->Arg_Car[7].misval = "$Arg1.misval";
  optr->Arg_Car[7].name = "$Arg1.name + \" synchronise sur \" + $Arg6.name";
  optr->Arg_Car[7].en_name =
    "$Arg1.english_name + \" synchronised on \" + $Arg6.english_name";
}
void
ID_MoyHarmEch_tps_impos (oper * optr)
{
  strcpy (optr->Nom, "MoyHarmEch_tps_impos");
  optr->Version = "$Revision: 5436 $";
  optr->Date = "$Date: 2013-10-18 18:27:26 +0200 (ven. 18 oct. 2013) $";
  optr->fctptr = OP_MoyHarmEch_tps_impos;
  optr->NbArg = 8;

  /* 1: X_in */
  optr->Arg_Car[0].direction = DIR_IN;
  optr->Arg_Car[0].categorie = VECTOR;
  optr->Arg_Car[0].typ = ATYC_IF32;
  optr->Arg_Car[0].array_dim = "1";
  optr->Arg_Car[0].type_sample = "any";
  optr->Arg_Car[0].sample = "any";
  optr->Arg_Car[0].unite = "";

  /* 2: time_in */
  optr->Arg_Car[1].direction = DIR_IN;
  optr->Arg_Car[1].categorie = VECTOR;
  optr->Arg_Car[1].typ = ATYC_IF64;
  optr->Arg_Car[1].array_dim = "1";
  optr->Arg_Car[1].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[1].type_sample = "any";
  optr->Arg_Car[1].sample = "any";
  optr->Arg_Car[1].unite = "second";

  /* 3: Ecart avant */
  optr->Arg_Car[2].direction = DIR_IN;
  optr->Arg_Car[2].categorie = COEFFICIENT;
  optr->Arg_Car[2].typ = ATYC_IF64;
  optr->Arg_Car[2].array_dim = "1";
  optr->Arg_Car[2].type_sample = "any";
  optr->Arg_Car[2].sample = "any";
  optr->Arg_Car[2].unite = "";

  /* 4: Ecart apres */
  optr->Arg_Car[3].direction = DIR_IN;
  optr->Arg_Car[3].categorie = COEFFICIENT;
  optr->Arg_Car[3].typ = ATYC_IF64;
  optr->Arg_Car[3].array_dim = "1";
  optr->Arg_Car[3].type_sample = "any";
  optr->Arg_Car[3].sample = "any";
  optr->Arg_Car[3].unite = "";

  /* 5: Mini_OK acceptés */
  optr->Arg_Car[4].direction = DIR_IN;
  optr->Arg_Car[4].categorie = COEFFICIENT;
  optr->Arg_Car[4].typ = ATYC_I32;
  optr->Arg_Car[4].array_dim = "1";
  optr->Arg_Car[4].type_sample = "any";
  optr->Arg_Car[4].sample = "any";
  optr->Arg_Car[4].unite = "";

  /* 6: time_out */
  optr->Arg_Car[5].direction = DIR_IN;
  optr->Arg_Car[5].categorie = VECTOR;
  optr->Arg_Car[5].typ = ATYC_IF64;
  optr->Arg_Car[5].array_dim = "1";
  optr->Arg_Car[5].type_sample = "any";
  optr->Arg_Car[5].sample = "any";
  optr->Arg_Car[5].unite = "second";

  /* 7: size_out */
  optr->Arg_Car[6].direction = DIR_IN;
  optr->Arg_Car[6].categorie = COEFFICIENT;
  optr->Arg_Car[6].typ = ATYC_LOCAL_ULONG;
  optr->Arg_Car[6].array_dim = "1";
  optr->Arg_Car[6].type_sample = "any";
  optr->Arg_Car[6].sample = "any";
  optr->Arg_Car[6].unite = "";

  /* 8: X_out */
  optr->Arg_Car[7].direction = DIR_OUT;
  optr->Arg_Car[7].categorie = VECTOR;
  optr->Arg_Car[7].typ = ATYC_IF32;
  optr->Arg_Car[7].array_dim = "1";
  optr->Arg_Car[7].NbVal = "$Arg6.NbVal";	/* ou $Arg6.value */
  optr->Arg_Car[7].type_sample = "$Arg6.type_sample";
  optr->Arg_Car[7].sample = "$Arg6.sample";
  optr->Arg_Car[7].ref_time = " $Arg6.nom ";
  optr->Arg_Car[7].unite = "$Arg1.unit";
  optr->Arg_Car[7].famille = "$Arg1.famille";
  optr->Arg_Car[7].misval = "$Arg1.misval";
  optr->Arg_Car[7].name = "$Arg1.name + \" synchronise sur \" + $Arg6.name";
  optr->Arg_Car[7].en_name =
    "$Arg1.english_name + \" synchronised on \" + $Arg6.english_name";
}

void
ID_MedEch_tps_impos (oper * optr)
{
  strcpy (optr->Nom, "MedEch_tps_impos");
  optr->Version = "$Revision: 5436 $";
  optr->Date = "$Date: 2013-10-18 18:27:26 +0200 (ven. 18 oct. 2013) $";
  optr->fctptr = OP_MedEch_tps_impos;
  optr->NbArg = 8;

  /* 1: X_in */
  optr->Arg_Car[0].direction = DIR_IN;
  optr->Arg_Car[0].categorie = VECTOR;
  optr->Arg_Car[0].typ = ATYC_IF32;
  optr->Arg_Car[0].array_dim = "1";
  optr->Arg_Car[0].type_sample = "any";
  optr->Arg_Car[0].sample = "any";
  optr->Arg_Car[0].unite = "";

  /* 2: time_in */
  optr->Arg_Car[1].direction = DIR_IN;
  optr->Arg_Car[1].categorie = VECTOR;
  optr->Arg_Car[1].typ = ATYC_IF64;
  optr->Arg_Car[1].array_dim = "1";
  optr->Arg_Car[1].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[1].type_sample = "any";
  optr->Arg_Car[1].sample = "any";
  optr->Arg_Car[1].unite = "second";

  /* 3: Ecart avant */
  optr->Arg_Car[2].direction = DIR_IN;
  optr->Arg_Car[2].categorie = COEFFICIENT;
  optr->Arg_Car[2].typ = ATYC_IF64;
  optr->Arg_Car[2].array_dim = "1";
  optr->Arg_Car[2].type_sample = "any";
  optr->Arg_Car[2].sample = "any";
  optr->Arg_Car[2].unite = "";

  /* 4: Ecart apres */
  optr->Arg_Car[3].direction = DIR_IN;
  optr->Arg_Car[3].categorie = COEFFICIENT;
  optr->Arg_Car[3].typ = ATYC_IF64;
  optr->Arg_Car[3].array_dim = "1";
  optr->Arg_Car[3].type_sample = "any";
  optr->Arg_Car[3].sample = "any";
  optr->Arg_Car[3].unite = "";

  /* 5: Mini_OK acceptés */
  optr->Arg_Car[4].direction = DIR_IN;
  optr->Arg_Car[4].categorie = COEFFICIENT;
  optr->Arg_Car[4].typ = ATYC_I32;
  optr->Arg_Car[4].array_dim = "1";
  optr->Arg_Car[4].type_sample = "any";
  optr->Arg_Car[4].sample = "any";
  optr->Arg_Car[4].unite = "";

  /* 6: time_out */
  optr->Arg_Car[5].direction = DIR_IN;
  optr->Arg_Car[5].categorie = VECTOR;
  optr->Arg_Car[5].typ = ATYC_IF64;
  optr->Arg_Car[5].array_dim = "1";
  optr->Arg_Car[5].type_sample = "any";
  optr->Arg_Car[5].sample = "any";
  optr->Arg_Car[5].unite = "second";

  /* 7: size_out */
  optr->Arg_Car[6].direction = DIR_IN;
  optr->Arg_Car[6].categorie = COEFFICIENT;
  optr->Arg_Car[6].typ = ATYC_LOCAL_ULONG;
  optr->Arg_Car[6].array_dim = "1";
  optr->Arg_Car[6].type_sample = "any";
  optr->Arg_Car[6].sample = "any";
  optr->Arg_Car[6].unite = "";

  /* 8: X_out */
  optr->Arg_Car[7].direction = DIR_OUT;
  optr->Arg_Car[7].categorie = VECTOR;
  optr->Arg_Car[7].typ = ATYC_IF32;
  optr->Arg_Car[7].array_dim = "1";
  optr->Arg_Car[7].NbVal = "$Arg6.NbVal";	/* ou $Arg6.value */
  optr->Arg_Car[7].type_sample = "$Arg6.type_sample";
  optr->Arg_Car[7].sample = "$Arg6.sample";
  optr->Arg_Car[7].ref_time = " $Arg6.nom ";
  optr->Arg_Car[7].unite = "$Arg1.unit";
  optr->Arg_Car[7].famille = "$Arg1.famille";
  optr->Arg_Car[7].misval = "$Arg1.misval";
  optr->Arg_Car[7].name = "$Arg1.name + \" synchronise sur \" + $Arg6.name";
  optr->Arg_Car[7].en_name =
    "$Arg1.english_name + \" synchronised on \" + $Arg6.english_name";
}
