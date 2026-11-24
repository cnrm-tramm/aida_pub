/****************************************************
*
* OPERATOR      Correl_wq.c   FUNCTION  ANSI-C
*
* PURPOSE      	Calcul de la covariance de la quantité d'eau WQ
*
* DESCRIPTION  	Cet opérateur calcule la covariance sur des périodes
*		de temps consécutives définies par l'utilisateur.   
*
*		Les parametres d'entrée dit "moyens" sont des vecteurs
*		à la meme fréquence que les vecteurs de sorties.
*
* VERSION       $Revision$
*
* ARGUMENTS   	
*             IN   float  Wa     	m/s	Fluctuation Composante verticale du vent filtrée RC
*	      IN   float  Humabs        g/m3	Fluctuation Humidité absolue krypton filtrée RC
*             IN   float  Fe    	Hz	fréquence d'échantillonnage des données	
*             IN   float  Tint		s	Temps d'intégration pour le calcul du flux	
*
*             OUT  float  Cov_wq	m2/s2	Covariance WQ
*
* REFERENCES
*
*
* COPYRIGHT     Meteo-France
*
*#########################################################################*/

#define _POSIX_SOURCE 1
#define _XOPEN_SOURCE 600

#include <stdio.h>
#include <math.h>
#include <string.h>
#include <limits.h>
#include <stdlib.h>

#include "thermo.h"

#include "struct_oper.h"

/* La vraie fonction... */


long
Correl_wq (unsigned long Ndata,
		float *Wa,
		float *Humabs,
                float Fe,
                float Tint,
		float *Cov_wq )
		 

{
  long i, j, k, ntour, reste, nbpt, nbval_out; 

  double fluct_w;

  double moy_w, moy_q;
  double cov_wq;
 

 
/* Calcul du nombre de points sur lequels on va calculer un flux */
/* on prend le meme principe d'arrondi que MoyEch car le fichier
temps sera calculé par MoyEch_dbl, ainsi on devrait éviter le
décalage */

  nbpt = floor( (Tint*Fe) + 0.5); 
  fprintf (stderr, " nbpt= %ld \n", nbpt);
  if ( nbpt <=0)
    return -1;

  ntour = Ndata/nbpt;
  reste = Ndata % nbpt;

  fprintf (stderr, " ntour= %ld, reste=%ld \n", ntour, reste);


/* normalement le nombre de données des vecteurs moy est
égal à ntour le nombre de données */

  for ( k=0,j=0; k < ntour; k++,j++  )
     {
/* on calcule d'abord les moyennes */

      moy_w = 0.;
      moy_q= 0.;
      for ( i = k*nbpt; i < (k+1)*nbpt; i++)
        {
         moy_w= moy_w + (double)Wa[i];
         moy_q= moy_q + (double)Humabs[i];
        }
      
      moy_w=moy_w/((double)nbpt);
      moy_q=moy_q/((double)nbpt);

      fprintf (stderr, "moy_w = %g\n", moy_w);
      fprintf (stderr, "moy_q = %g\n", moy_q);
      
/* calcul de la covariance */

      cov_wq = 0.;

      for ( i = k*nbpt; i < (k+1)*nbpt; i++)
        {
         fluct_w= (double)Wa[i]-moy_w;
	 cov_wq = cov_wq + ((double)Humabs[i]-moy_q)*fluct_w;
        }

      cov_wq = cov_wq/(double)nbpt; 

      Cov_wq[j] = (float)cov_wq;

      fprintf (stderr, "Cov_wq = %g\n", Cov_wq[j]);


    }

  if (reste > 0)
    {
     Cov_wq[j] = 0./0.;
     j = j+1;
    }

  nbval_out = j;
  return (nbval_out);
}

/* la fonction d'enrobage classique */

int
OP_Correl_wq (unsigned long NbVal, void *ArgList[], char *DiagExec)
{
  long CodRet; 
  int NCar;

  NCar = sprintf (DiagExec, "Correl_wq : (%ld echant.) ", NbVal) ;
  if (NCar < 0)
    NCar = 0;
  DiagExec += NCar;

  CodRet = Correl_wq (NbVal,
		       (float *) ArgList[0],
		       (float *) ArgList[1],
		       *((float *) ArgList[2]),
		       *((float *) ArgList[3]),
		       (float *) ArgList[4]);

  if (CodRet > 0)
    {
     sprintf (DiagExec, "OK: %ld val. calculées.",
                   CodRet);
     return OP_OK;
    }
  switch(CodRet)
   {
    case -1:
      strcat (DiagExec, "; Nb resultats <= 0");
      return OP_FAIL;
    case -2:
      strcat (DiagExec, "; Trop de valeurs manquantes ");
      return OP_FAIL;
    default:
      strcat (DiagExec, "; Erreur inattendue");
      return OP_FAIL;
   }

}

void
ID_Correl_wq (oper * optr)
{
  int i;

  strcpy (optr->Nom, "Correl_wq");
  optr->Version = "$Revision$";
  optr->Date = "$Date$";
  optr->fctptr = OP_Correl_wq;
  optr->NbArg = 5;
  optr->misval_auto = 1;

  for (i=0; i <=1; i++)  
    {
  optr->Arg_Car[i].direction = DIR_IN;
  optr->Arg_Car[i].categorie = VECTOR;
  optr->Arg_Car[i].typ = ATYC_IF32;
  optr->Arg_Car[i].array_dim = "1";
  optr->Arg_Car[i].type_sample = "any";
  optr->Arg_Car[i].sample = "any";
    }
  optr->Arg_Car[0].unite = "m/s"; 
  optr->Arg_Car[1].unite = "g/m3";

  for (i=2; i <=3; i++)
    {
  optr->Arg_Car[i].direction = DIR_IN;
  optr->Arg_Car[i].categorie = COEFFICIENT;
  optr->Arg_Car[i].array_dim = "1";
  optr->Arg_Car[i].typ = ATYC_IF32;
  optr->Arg_Car[i].unite = "any";
  optr->Arg_Car[i].type_sample = NULL;
  optr->Arg_Car[i].sample = NULL;
    }
  for (i = 4; i < 5; i++)
    { 
  optr->Arg_Car[i].direction = DIR_OUT;
  optr->Arg_Car[i].categorie = VECTOR;
  optr->Arg_Car[i].typ = ATYC_IF32;
  optr->Arg_Car[i].array_dim = "1";
  optr->Arg_Car[i].NbVal = "$Arg1.NbVal/($Arg3*$Arg4)";
  optr->Arg_Car[i].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[i].sample = "1./$Arg4";
  optr->Arg_Car[i].ref_time = "$Arg1.ref_time+\"_Med_\"+$Arg5.sample";
  /*optr->Arg_Car[i].ref_time = " \"time_\"+$Arg5.sample";*/
    }

  optr->Arg_Car[4].unite = "$Arg1.unit $Arg2.unit";
  /*optr->Arg_Car[4].unite = "any";*/
  optr->Arg_Car[4].famille = " \"flux\" ";

}
