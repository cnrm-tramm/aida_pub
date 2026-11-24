/****************************************************
*
* OPERATOR      Flux_correl_vect.c   FUNCTION  ANSI-C
*
* PURPOSE      	Calcul des flux de chaleur et de quantité de
*		de mouvement par la méthode des corrélations 
*
* DESCRIPTION  	Ce opérateur calcule les flux sur des périodes
*		de temps consécutives définies par l'utilisateur.   
*
*		Les parametres d'entrée dit "moyens" sont des vecteurs
*		à la meme fréquence que les vecteurs de sorties.
*
* VERSION       $Revision$
*
* ARGUMENTS   	
*             IN   float  Ta    	C ou K	Fluctuation de temperature de l'air	
*             IN   float  Rapm     	g/kg	Fluctuation de Rapport de mélange en vapeur d'eau
*             IN   float  Ua     	m/s 	Fluctuation 1ere composante horizontale du vent	
*             IN   float  Va     	m/s	Fluctuation 2eme composante horizontale du vent
*             IN   float  Wa     	m/s	Fluctuation composante verticale du vent
*	      IN   float  Pamoy		hPa     Pression moyenne
*	      IN   float  Tamoy		C ou K	Temperature moyenne 
*	      IN   float  Rapmoy	g/kg	Rapport de mélange moyen
*             IN   float  Fe    	/s	fréquence d'échantillonnage des données	
*             IN   float  Tint		s	Temps d'intégration pour le calcul du flux	
*	      IN   float  Ra		J.kg-1.K-1	Constante specifique de l'air sec 	
*	      IN   float  Cpa		J.kg-1.K-1	Capacité calorifique pour l'air sec
*             OUT  float  Flx_H		W/m2	Flux de chaleur sensible 
*             OUT  float  Flx_LE	W/m2	Flux de chaleur latente 
*             OUT  float  Flx_mouv	m2/s2	Flux de quantité de mouvement 
*#	      OUT  float  Cov_wu	m2/s2 	Covariance WU
*#	      OUT  float  Cov_wv	m2/s2 	Covariance WV
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
#include "unit_def.h"


/* La vraie fonction... */


long
Flux_correl_vect (unsigned long Ndata,
	 	float *Ta,
		float *Rapm, 
		float *Ua,
		float *Va,
		float *Wa,
		float *Pamoy,
   		float *Tamoy,
		float *Rapmoy,
		float Fe,
		float Tint,
		double Ra,
		double Cpa,
		float *Flx_H,
		float *Flx_LE,
		float *Flx_mouv)
/*		float *Cov_wu,
		float *Cov_wv )  */
		 

{
  int flag_info;
  long i, j, k, ntour, reste, nbpt, nbval_out; 

  float Lv, Cph;

  float C_to_K_moy;

  double fluct_w;

  double moy_w, moy_u, moy_v, moy_r, moy_t, roa;
  double cov_wt, cov_wr, cov_wu, cov_wv;
 

 
/* Calcul du nombre de points sur lequels on va calculer un flux */
/* on prend le meme principe d'arrondi que MoyEch car le fichier
temps sera calculé par MoyEch_dbl, ainsi on devrait éviter le
décalage */

  nbpt = floor( (Tint*Fe) + 0.5); 
  /*nb de points par 1/2 heure ou 1/4 heure */

  ntour = Ndata/nbpt;
  /*nb de 1/2 heure ou 1/4 heure par jour */
  reste = Ndata % nbpt;

  fprintf (stderr, " ntour= %ld, reste=%ld \n", ntour, reste);


/* normalement le nombre de données des vecteurs moy est
égal à ntour le nombre de donnée */

/* vérification de la température  et initialisation
du coef de conversion */ 
 
  flag_info = auto_tempe_unit (ntour, Tamoy, &C_to_K_moy);

  if (flag_info == MANQUANTES)
    return (-1);

  k = 0;
  j = 0;
  
  for ( k=0; k < ntour; k++  )
     {
/* initialisation des moyennes */

      moy_w = 0.;
      moy_u= 0.;
      moy_v= 0.;
      moy_t= 0.;
      moy_r= 0.;
      for ( i = k*nbpt; i < (k+1)*nbpt; i++)
/* on calcule d'abord les moyennes pour chaque intervalle (1/2 ou 1/4 heure) */
        {
         moy_w= moy_w + (double)Wa[i];
         moy_u= moy_u + (double)Ua[i];
         moy_v= moy_v + (double)Va[i];
         moy_t= moy_t + (double)Ta[i];
         moy_r= moy_r + (double)Rapm[i];
        }
      
      moy_w=moy_w/((double)nbpt);
      moy_u=moy_u/((double)nbpt);
      moy_v=moy_v/((double)nbpt);
      moy_t=moy_t/((double)nbpt);
      moy_r=moy_r/((double)nbpt);

      fprintf (stderr, "moy_w = %g\n", moy_w);
      fprintf (stderr, "moy_u = %g\n", moy_u);
      fprintf (stderr, "moy_v = %g\n", moy_v);
      fprintf (stderr, "moy_t = %g\n", moy_t);
      fprintf (stderr, "moy_r = %g\n", moy_r);
      
/* initialisation des covariances */

      cov_wt = 0.;
      cov_wr = 0.;
      cov_wu = 0.;
      cov_wv = 0.;

/* on calcule ensuite les covariances moyennes pour chaque intervalle (1/2 ou 1/4 heure) */
      for ( i = k*nbpt; i < (k+1)*nbpt; i++)
        {
         fluct_w= (double)Wa[i]-moy_w;
	 cov_wt = cov_wt + ((double)Ta[i]-moy_t)*fluct_w;
	 cov_wr = cov_wr + ((double)Rapm[i]-moy_r)*fluct_w;
	 cov_wu = cov_wu + ((double)Ua[i]-moy_u)*fluct_w;
	 cov_wv = cov_wv + ((double)Va[i]-moy_v)*fluct_w;
        }

      cov_wt = cov_wt/(double)nbpt; 
      cov_wr = cov_wr/(double)nbpt; 
      cov_wu = cov_wu/(double)nbpt; 
      cov_wv = cov_wv/(double)nbpt;

      fprintf (stderr, "cov_wt = %g\n", cov_wt);
      fprintf (stderr, "cov_wr = %g\n", cov_wr);
      fprintf (stderr, "cov_wu = %g\n", cov_wu);
      fprintf (stderr, "cov_wv = %g\n", cov_wv);

/* calcul des flux */

/* appel des fonctions de la la lib thermo */

      roa = ((double)Pamoy[k]*100.)/(Ra*(double)(Tamoy[k]+ C_to_K_moy)); 
      clw( (float)(Tamoy[k] + C_to_K_moy), &Lv);  
      cp_hum ( Cpa, (float)Rapmoy[k]/1000., &Cph);  

      Flx_H[j] = (float)(roa*Cph*cov_wt);      
      Flx_LE[j] = (float)(roa*Lv*cov_wr*0.001);
      Flx_mouv[j] = (float)(roa*sqrt( cov_wu*cov_wu + cov_wv*cov_wv));
/*      Cov_wu[j] = (float)cov_wu;
      Cov_wv[j] = (float)cov_wv; */
/*    
      fprintf(stderr, "%d : Pamoy= %g, Tamoy= %g, Rapmoy=%g \n", k, Pamoy[k], Tamoy[k], Rapmoy[k]);
      fprintf(stderr, "C_to_K = %g \n", C_to_K_moy);
      fprintf( stderr, "roa = %g\n", roa);
      fprintf (stderr, "Flx_H = %g\n", Flx_H[j] );
      fprintf (stderr, "Flx_LE = %g\n", Flx_LE[j]);
      fprintf (stderr, "Flx_mouv = %g\n",  Flx_mouv[j]);
*/
 
      j = j+1;

    }

  if (reste > 0)
    {
     Flx_H[j] = 0./0.; 
     Flx_LE[j] = 0./0.;
     Flx_mouv[j] = 0./0.;
/*     Cov_wu[j] = 0./0.;
     Cov_wv[j] = 0./0.; */
     j = j+1;
    }

  nbval_out = j;

  return (nbval_out);
}

/* la fonction d'enrobage classique */

int
OP_Flux_correl_vect (unsigned long NbVal, void *ArgList[], char *DiagExec)
{
  long CodRet;
  int NCar;

  NCar = sprintf (DiagExec, "Flux_correl_vect : (%ld echant.) ", NbVal) ;
  if (NCar < 0)
    NCar = 0;
  DiagExec += NCar;

  CodRet = Flux_correl_vect (NbVal,
		       (float *) ArgList[0],
		       (float *) ArgList[1],
		       (float *) ArgList[2],
		       (float *) ArgList[3],
		       (float *) ArgList[4],
		       (float *) ArgList[5],
		       (float *) ArgList[6],
		       (float *) ArgList[7],
		       *((float *) ArgList[8]),
		       *((float *) ArgList[9]),
		       *((double *) ArgList[10]),
		       *((double *) ArgList[11]),
		       (float *) ArgList[12],
		       (float *) ArgList[13],
		       (float *) ArgList[14]);
/*		       (float *) ArgList[15],
		       (float *) ArgList[16]); */

  sprintf (DiagExec, "OK: %ld val. calculées.",
                   CodRet);

  switch(CodRet)
   {
    case -1:
      strcat (DiagExec, "; Trop de valeurs manquantes : unité de température non reconnue.");
      return OP_FAIL;
   }


  
  return OP_OK;

}

void
ID_Flux_correl_vect (oper * optr)
{
  int i;

  strcpy (optr->Nom, "Flux_correl_vect");
  optr->Version = "$Revision$";
  optr->Date = "$Date$";
  optr->fctptr = OP_Flux_correl_vect;
  optr->NbArg = 15;
  optr->misval_auto = 1;

  for (i=0; i <=7; i++)  
    {
  optr->Arg_Car[i].direction = DIR_IN;
  optr->Arg_Car[i].categorie = VECTOR;
  optr->Arg_Car[i].typ = ATYC_IF32;
  optr->Arg_Car[i].array_dim = "1";
  optr->Arg_Car[i].type_sample = "any";
  optr->Arg_Car[i].sample = "any";
   }
  optr->Arg_Car[0].unite = "any"; /* en fait c'est C ou K */
  optr->Arg_Car[1].unite = "gram/kg";
  optr->Arg_Car[2].unite = "m/s";
  optr->Arg_Car[3].unite = "m/s";
  optr->Arg_Car[4].unite = "m/s";
  optr->Arg_Car[5].unite = "hPa";
  optr->Arg_Car[6].sample = "any"; /* en fait c'est C ou K */ 
  optr->Arg_Car[7].sample = "gram/kg";  

  for (i=8; i <=9; i++)
    {
  optr->Arg_Car[i].direction = DIR_IN;
  optr->Arg_Car[i].categorie = COEFFICIENT;
  optr->Arg_Car[i].array_dim = "1";
  optr->Arg_Car[i].typ = ATYC_IF32;
  optr->Arg_Car[i].unite = "any";
  optr->Arg_Car[i].type_sample = NULL;
  optr->Arg_Car[i].sample = NULL;
    }

  for (i=10; i <=11; i++)
    {
  optr->Arg_Car[i].direction = DIR_IN;
  optr->Arg_Car[i].categorie = COEFFICIENT;
  optr->Arg_Car[i].array_dim = "1";
  optr->Arg_Car[i].typ = ATYC_IF64;
  optr->Arg_Car[i].unite = "any";
  optr->Arg_Car[i].type_sample = NULL;
  optr->Arg_Car[i].sample = NULL;
    }

  for (i = 12; i <=16; i++)
    { 

  optr->Arg_Car[i].direction = DIR_OUT;
  optr->Arg_Car[i].categorie = VECTOR;
  optr->Arg_Car[i].typ = ATYC_IF32;
  optr->Arg_Car[i].array_dim = "1";
  optr->Arg_Car[i].NbVal = "$Arg1.NbVal/($Arg10*$Arg9)";
  optr->Arg_Car[i].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[i].sample = "1./$Arg10";
  optr->Arg_Car[i].ref_time = "$Arg1.ref_time+\"_Med_\"+$Arg13.sample";
  /*optr->Arg_Car[i].ref_time = "\"time_\"+$Arg13.sample";*/
    }

  optr->Arg_Car[12].unite = "W/m2";
  optr->Arg_Car[12].famille = "flux";

  optr->Arg_Car[13].unite = "W/m2";
  optr->Arg_Car[13].famille = "flux";

  optr->Arg_Car[14].unite = "N/m2";
  optr->Arg_Car[14].famille = "flux";

/*  optr->Arg_Car[15].unite = "m2/s2";
  optr->Arg_Car[15].famille = "statistique";
 
  optr->Arg_Car[16].unite = "m2/s2";
  optr->Arg_Car[16].famille = "statistique"; */
 
}
