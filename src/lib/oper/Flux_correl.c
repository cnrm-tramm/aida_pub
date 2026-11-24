/****************************************************
*
* OPERATOR      Flux_correl.c   FUNCTION  ANSI-C
*
* PURPOSE      	Calcul des flux de chaleur et de quantité de
*		de mouvement par la méthode des corrélations 
*		a partir des covariances ; la base de temps doit etre commune.
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
*             IN   float  cov_wt    	mK/s	Covariance w't'	
*             IN   float  cov_wu    	m2/s2	Covariance w'u'	
*             IN   float  cov_wv    	m2/s2	Covariance w'v'	
*             IN   float  cov_wr    	m/s	Covariance w'r'	
*	      IN   float  Pamoy		hPa     Pression moyenne
*	      IN   float  Tamoy		C ou K	Temperature moyenne 
*	      IN   float  Rapmoy	g/kg	Rapport de mélange moyen
*             IN   float  Tint		s	Temps d'intégration pour le calcul du flux	
*	      IN   float  Ra		J.kg-1.K-1	Constante specifique de l'air sec 	
*	      IN   float  Cpa		J.kg-1.K-1	Capacité calorifique pour l'air sec
*             OUT  float  Flx_H		W/m2	Flux de chaleur sensible 
*             OUT  float  Flx_LE	W/m2	Flux de chaleur latente 
*             OUT  float  Flx_mouv	N/m2	Flux de quantité de mouvement 
*             OUT  float  ustar 	m/s	Vitesse de frottement 
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

#include "struct_oper.h"
#include "thermo.h"
#include "unit_def.h"

/* La vraie fonction... */
long
Flux_correl (unsigned long NLoop,
	 	float *cov_wt,
		float *cov_wu, 
		float *cov_wv,
		float *cov_wr,
		float *Pamoy,
   		float *Tamoy,
		float *Rapmoy,
		float Tint,
		double Ra,
		double Cpa,
		float *Flx_H,
		float *Flx_LE,
		float *Flx_mouv,
		float *ustar)
{
  int flag_info;
  unsigned long  k; 

  float Lv, Cph;

  float C_to_K_moy;

  double roa;
 

 
/* Calcul du nombre de points sur lequels on va calculer un flux */
/* vérification de la température  et initialisation
du coef de conversion */ 
 
  flag_info = auto_tempe_unit (NLoop, Tamoy, &C_to_K_moy);

  if (flag_info == MANQUANTES)
    return -1;

   for (k = 0; k < NLoop; k++)

   {
      
/* calcul des flux */

/* appel des fonctions de la la lib thermo */

      roa = ((double)Pamoy[k]*100.)/(Ra*(double)(Tamoy[k]+ C_to_K_moy)); 
      clw( (float)(Tamoy[k] + C_to_K_moy), &Lv);  
      cp_hum ( Cpa, (float)Rapmoy[k]/1000., &Cph);  

      Flx_H[k] = (float)(roa*Cph*cov_wt[k]);      
      Flx_LE[k] = (float)(roa*Lv*cov_wr[k]*0.001);
      Flx_mouv[k] = (float)(roa*sqrt( cov_wu[k]*cov_wu[k] + cov_wv[k]*cov_wv[k]));
       /* calcul de ustar */
      /* ustar=sqrt(Cov_wu_wv); */
      ustar[k]=(float)sqrt(sqrt( cov_wu[k]*cov_wu[k] + cov_wv[k]*cov_wv[k]));

/*      fprintf(stderr, "%d : Pamoy= %g, Tamoy= %g, Rapmoy=%g \n", k, Pamoy[k], Tamoy[k], Rapmoy[k]);*/
/*      fprintf(stderr, "C_to_K = %g \n", C_to_K_moy);*/
 /*     fprintf( stderr, "roa = %g\n", roa);*/
      /*
      fprintf (stderr, "Flx_H = %g\n", Flx_H[k] );
      fprintf (stderr, "Flx_LE = %g\n", Flx_LE[k]);
      fprintf (stderr, "Flx_mouv = %g\n",  Flx_mouv[k]);
      fprintf (stderr, "ustar = %g\n",  ustar[k]);
      */
 
    }
  return 0;
}

/* la fonction d'enrobage classique */

int
OP_Flux_correl (unsigned long NbVal, void *ArgList[], char *DiagExec)
{
  long CodRet;
  int NCar;

  NCar = sprintf (DiagExec, "Flux_correl : (%ld echant.) ", NbVal) ;
  if (NCar < 0)
    NCar = 0;
  DiagExec += NCar;

  CodRet = Flux_correl (NbVal,
		       (float *) ArgList[0],
		       (float *) ArgList[1],
		       (float *) ArgList[2],
		       (float *) ArgList[3],
		       (float *) ArgList[4],
		       (float *) ArgList[5],
		       (float *) ArgList[6],
		       *((float *) ArgList[7]),
		       *((double *) ArgList[8]),
		       *((double *) ArgList[9]),
		       (float *) ArgList[10],
		       (float *) ArgList[11],
		       (float *) ArgList[12],
		       (float *) ArgList[13]);

  switch(CodRet)
   {
    case -1:
      strcat (DiagExec, "; Trop de valeurs manquantes : unité de température non reconnue.");
      return OP_FAIL;
   }


  
  return OP_OK;

}

void
ID_Flux_correl (oper * optr)
{
  int i;

  strcpy (optr->Nom, "Flux_correl");
  optr->Version = "$Revision$";
  optr->Date = "$Date$";
  optr->fctptr = OP_Flux_correl;
  optr->NbArg = 14;
  optr->misval_auto = 1;

  for (i=0; i <=6; i++)  
    {
  optr->Arg_Car[i].direction = DIR_IN;
  optr->Arg_Car[i].categorie = VECTOR;
  optr->Arg_Car[i].typ = ATYC_IF32;
  optr->Arg_Car[i].array_dim = "1";
  optr->Arg_Car[i].type_sample = "any";
  optr->Arg_Car[i].sample = "any";
   }
  optr->Arg_Car[0].unite = "m.K/s"; /* en fait c'est C ou K */
  optr->Arg_Car[1].unite = "m2/s2";
  optr->Arg_Car[2].unite = "m2/s2";
  optr->Arg_Car[3].unite = "m/s";
  optr->Arg_Car[4].unite = "hPa";
  optr->Arg_Car[5].sample = "any"; /* en fait c'est C ou K */ 
  optr->Arg_Car[6].sample = "gram/kg";  

  for (i=7; i <8; i++)
    {
  optr->Arg_Car[i].direction = DIR_IN;
  optr->Arg_Car[i].categorie = COEFFICIENT;
  optr->Arg_Car[i].array_dim = "1";
  optr->Arg_Car[i].typ = ATYC_IF32;
  optr->Arg_Car[i].unite = "any";
  optr->Arg_Car[i].type_sample = NULL;
  optr->Arg_Car[i].sample = NULL;
    }

  for (i=8; i <=9; i++)
    {
  optr->Arg_Car[i].direction = DIR_IN;
  optr->Arg_Car[i].categorie = COEFFICIENT;
  optr->Arg_Car[i].array_dim = "1";
  optr->Arg_Car[i].typ = ATYC_IF64;
  optr->Arg_Car[i].unite = "any";
  optr->Arg_Car[i].type_sample = NULL;
  optr->Arg_Car[i].sample = NULL;
    }

  for (i = 10; i <=13; i++)
    { 

  optr->Arg_Car[i].direction = DIR_OUT;
  optr->Arg_Car[i].categorie = VECTOR;
  optr->Arg_Car[i].typ = ATYC_IF32;
  optr->Arg_Car[i].array_dim = "1";
  optr->Arg_Car[i].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[i].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[i].sample = "1./$Arg8";
/*  optr->Arg_Car[i].ref_time = "$Arg1.ref_time";*/
  optr->Arg_Car[i].ref_time = "$Arg5.ref_time";
/*  optr->Arg_Car[i].ref_time = "$Arg1.ref_time+\"_Med_\"+$Arg13.sample";*/
  /*optr->Arg_Car[i].ref_time = "\"time_\"+$Arg13.sample";*/
    }

  optr->Arg_Car[10].unite = "W/m2";
  optr->Arg_Car[10].famille = "\"flux\"";

  optr->Arg_Car[11].unite = "W/m2";
  optr->Arg_Car[11].famille = "\"flux\"";

  optr->Arg_Car[12].unite = "N/m2";
  optr->Arg_Car[12].famille = "\"flux\"";

  optr->Arg_Car[13].unite = "m/s";
  optr->Arg_Car[13].famille = "\"flux\"";
}
