/****************************************************
*
* OPERATOR      Correl_var.c   FUNCTION  ANSI-C
*
* PURPOSE      	Calcul des variances des paramètres rapides
*		par la méthode des corrélations 
*
* DESCRIPTION  	Ce opérateur calcule les variances sur des périodes
*		de temps consécutives définies par l'utilisateur.   
*               variance de u = fluct(u)*fluct(u) = u'**2
*               puis on fait une moyenne sur la période.
*
*		Les parametres d'entrée dit "moyens" sont des vecteurs
*		à la meme fréquence que les vecteurs de sorties.
*
* VERSION       $Revision$
*
* ARGUMENTS   	
*             IN   float  Ta    	C ou K	Temperature de l'air	
*             IN   float  Qa     	g/kg	Humidité absolue donnée par le krypton
*             IN   float  Ua     	m/s 	1ere composante horizontale du vent	
*             IN   float  Va     	m/s	2eme composante horizontale du vent
*             IN   float  Wa     	m/s	Composante verticale du vent
*             IN   float  Fe    	m/s	fréquence d'échantillonnage des données	
*             IN   float  Tint		m/s	Temps d'intégration pour le calcul du flux	
*             OUT  float  Var_U		m2/s2	Variance de U 
*             OUT  float  Var_V 	m2/s2   Variance de V	
*             OUT  float  Var_W         m2/s2	Variance de W 
* 	      OUT  float  Var_T 	Celsius2 Variance de T
* 	      OUT  float  Var_Q 	g2/m2  Variance de Q, humidite absolue
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
Correl_var (unsigned long Ndata,
	 	float *Ta,
		float *Qa, 
		float *Ua,
		float *Va,
		float *Wa,
		float Fe,
		float Tint,
		float *Var_U,
		float *Var_V,
		float *Var_W,
		float *Var_T,
		float *Var_Q)

{
  int flag_info;
  long i, j, k, ntour, reste, nbpt, nbval_out; 

  float C_to_K_moy;

  double fluct_u, fluct_v, fluct_w, fluct_q, fluct_t;

  double moy_w, moy_u, moy_v, moy_q, moy_t;
  double var_u, var_v, var_w ,var_t, var_q;
 

 
/* Calcul du nombre de points sur lequels on va calculer un flux */
/* on prend le meme principe d'arrondi que MoyEch car le fichier
temps sera calculé par MoyEch_dbl, ainsi on devrait éviter le
décalage */

  nbpt = floor( (Tint*Fe) + 0.5); 

  ntour = Ndata/nbpt;
  reste = Ndata % nbpt;

  fprintf (stderr, " ntour= %ld, reste=%ld \n", ntour, reste);


/* normalement le nombre de données des vecteurs moy est
égal à ntour le nombre de donnée */

/* vérification de la température  et initialisation
du coef de conversion */ 
 
  flag_info = auto_tempe_unit (ntour, Ta, &C_to_K_moy);

  if (flag_info == MANQUANTES)
    return (-1);

  k = 0;
  j = 0;
  
  for ( k=0; k < ntour; k++  )
     {
/* on calcule d'abord les moyennes */

      moy_w= 0.;
      moy_u= 0.;
      moy_v= 0.;
      moy_t= 0.;
      moy_q= 0.;

      for ( i = k*nbpt; i < (k+1)*nbpt; i++)
        {
         moy_u= moy_u + (double)Ua[i];
         moy_v= moy_v + (double)Va[i];
         moy_w= moy_w + (double)Wa[i];
         moy_t= moy_t + (double)Ta[i];
         moy_q= moy_q + (double)Qa[i];
        }
      
      moy_u=moy_u/((double)nbpt);
      moy_v=moy_v/((double)nbpt);
      moy_w=moy_w/((double)nbpt);
      moy_t=moy_t/((double)nbpt);
      moy_q=moy_q/((double)nbpt);

      fprintf (stderr, "moy_u = %g\n", moy_u);
      fprintf (stderr, "moy_v = %g\n", moy_v);
      fprintf (stderr, "moy_w = %g\n", moy_w);
      fprintf (stderr, "moy_t = %g\n", moy_t);
      fprintf (stderr, "moy_q = %g\n", moy_q);
      
/* on calcule les variances */

      var_u = 0.;
      var_v = 0.;
      var_w = 0.;
      var_t = 0.;
      var_q = 0.;

      for ( i = k*nbpt; i < (k+1)*nbpt; i++)
        {
         fluct_u= (double)Ua[i]-moy_u;
         fluct_v= (double)Va[i]-moy_v;
         fluct_w= (double)Wa[i]-moy_w;
         fluct_t= (double)Ta[i]-moy_t;
         fluct_q= (double)Qa[i]-moy_q;

	 var_u = var_u + fluct_u*fluct_u;
	 var_v = var_v + fluct_v*fluct_v;
	 var_w = var_w + fluct_w*fluct_w;
	 var_t = var_t + fluct_t*fluct_t;
	 var_q = var_q + fluct_q*fluct_q;
        }

      Var_U[j] = var_u/(double)nbpt; 
      Var_V[j] = var_v/(double)nbpt; 
      Var_W[j] = var_w/(double)nbpt; 
      Var_T[j] = var_t/(double)nbpt; 
      Var_Q[j] = var_q/(double)nbpt;

      fprintf (stderr, "Var_U = %g\n", Var_U[j]);
      fprintf (stderr, "Var_V = %g\n", Var_V[j]);
      fprintf (stderr, "Var_W = %g\n", Var_W[j]);
      fprintf (stderr, "Var_T = %g\n", Var_T[j]);
      fprintf (stderr, "Var_Q = %g\n", Var_Q[j]);


      j = j+1;

    }

  if (reste > 0)
    {
     Var_U[j] = 0./0.; 
     Var_V[j] = 0./0.; 
     Var_W[j] = 0./0.; 
     Var_T[j] = 0./0.; 
     Var_Q[j] = 0./0.; 

     j = j+1;
    }

  nbval_out = j;

  return (nbval_out);
}

/* la fonction d'enrobage classique */

int
OP_Correl_var (unsigned long NbVal, void *ArgList[], char *DiagExec)
{
  long CodRet;
  int NCar;

  NCar = sprintf (DiagExec, "Correl_var : (%ld echant.) ", NbVal) ;
  if (NCar < 0)
    NCar = 0;
  DiagExec += NCar;

  CodRet = Correl_var (NbVal,
		       (float *) ArgList[0],
		       (float *) ArgList[1],
		       (float *) ArgList[2],
		       (float *) ArgList[3],
		       (float *) ArgList[4],
		       *((float *) ArgList[5]),
		       *((float *) ArgList[6]),
		       (float *) ArgList[7],
		       (float *) ArgList[8],
		       (float *) ArgList[9],
		       (float *) ArgList[10],
		       (float *) ArgList[11]); 

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
ID_Correl_var (oper * optr)
{
  int i;

  strcpy (optr->Nom, "Correl_var");
  optr->Version = "$Revision$";
  optr->Date = "$Date$";
  optr->fctptr = OP_Correl_var;
  optr->NbArg = 12;
  optr->misval_auto = 1;

  for (i=0; i <=4; i++)  
    {
  optr->Arg_Car[i].direction = DIR_IN;
  optr->Arg_Car[i].categorie = VECTOR;
  optr->Arg_Car[i].typ = ATYC_IF32;
  optr->Arg_Car[i].array_dim = "1";
  optr->Arg_Car[i].type_sample = "any";
  optr->Arg_Car[i].sample = "any";
   }
  optr->Arg_Car[0].unite = "any"; /* en fait c'est C ou K */
  optr->Arg_Car[1].unite = "g/m3";
  optr->Arg_Car[2].unite = "m/s";
  optr->Arg_Car[3].unite = "m/s";
  optr->Arg_Car[4].unite = "m/s";

  for (i=5; i <=6; i++)
    {
  optr->Arg_Car[i].direction = DIR_IN;
  optr->Arg_Car[i].categorie = COEFFICIENT;
  optr->Arg_Car[i].array_dim = "1";
  optr->Arg_Car[i].typ = ATYC_IF32;
  optr->Arg_Car[i].unite = "any";
  optr->Arg_Car[i].type_sample = NULL;
  optr->Arg_Car[i].sample = NULL;
    }

  for (i = 7; i <=11; i++)
    { 

  optr->Arg_Car[i].direction = DIR_OUT;
  optr->Arg_Car[i].categorie = VECTOR;
  optr->Arg_Car[i].typ = ATYC_IF32;
  optr->Arg_Car[i].array_dim = "1";
  optr->Arg_Car[i].NbVal = "$Arg1.NbVal/($Arg6*$Arg7)";
  optr->Arg_Car[i].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[i].sample = "1./$Arg7";
  optr->Arg_Car[i].ref_time = "\"time_\"+$Arg8.sample";
    }

  optr->Arg_Car[7].unite = "m2/s2";
  optr->Arg_Car[7].famille = "flux";

  optr->Arg_Car[8].unite = "m2/s2";
  optr->Arg_Car[8].famille = "flux";

  optr->Arg_Car[9].unite = "m2/s2";
  optr->Arg_Car[9].famille = "flux";

  optr->Arg_Car[10].unite = "Celsius2";
  optr->Arg_Car[10].famille = "flux";
 
  optr->Arg_Car[11].unite = "g2/m6";
  optr->Arg_Car[11].famille = "flux";
 
}
