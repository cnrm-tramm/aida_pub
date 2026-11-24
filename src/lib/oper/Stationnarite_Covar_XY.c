/****************************************************
*
* OPERATOR     Stationarite_Covar_XY.c   FUNCTION  ANSI-C
*
* PURPOSE      	Test de la stationnarite de la la covariance XY 
*
* DESCRIPTION  	Ce opérateur calcule le rapport  :
*
*                  Rapport = [ moyenne(cov(X,Y) sur T1) - cov(X,Y) sur T2 ]/ ( cov (X,Y) sur T2 ) 
*
*                Foken considère que si Rapport < 30 % on considère des conditions stationnaires 
*
* VERSION       $Revision: 5097 $
*
* ARGUMENTS   IN   float  x    			Any    		premier vecteur
*             IN   float  y    			Any    		second vecteur
*             IN   float  Fe   			s-1		fréquence d'échantillonnage des données	
*             IN   int    T1 	 		s		Temps d'intégration pour le calcul des covariances (T1 < T2 )
*             IN   int    T2 	 		s		Temps d'intégration pour le calcul des covariances (T2 multiple de T1) 	
*             IN   float  Rap_mini_valid  	without		Rapport minimum de données présentes pour le calcul des variances 
*
*             OUT  float  Rap_stat      	without         Rapport quantifiant la stationnarite 
*
* REFERENCES
* 	     T. Foken, Micrometeorology, 2008 
* 	     Ed Spinger, ISBN : 978-3-540-74665-2 
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
Stationnarite_Covar_XY (unsigned long Ndata,
	  const float *x,
	  const float *y, 
	  const float Fe, 
	  const int T1, 
	  const int T2, 
	  const float Rap_mini_valid,

	  float *Rap_stat)
{
  int rap_T2_T1; 
  long i, j, k, ntour_t1, ntour_t2, nbpt_t1, nbpt_t2;
  long kdeb, kfin, binf, bsup, n1, n2, nb_rap;

  double moy_cov_t1, cov_t2;
  double som_x_t2, som_y_t2, som_xy_t2;
  double d_n, d_n2;

  double *som_x, *som_y, *som_xy;
  long *nbpt_xy;

/* Calcul du nombre de points sur lequels on va calculer */

  if ( T1 > T2 )
    return -1;


  /*nb de points sur la periode demandee */
  nbpt_t1 = floor ((T1 * Fe) + 0.5);
  nbpt_t2 = floor ((T2 * Fe) + 0.5);

  if ( (nbpt_t1 <= 0) || (nbpt_t2 <=0) )
    return -3;

  if ( (T2%T1)  != 0 ) 
    return -2; 

  rap_T2_T1 = T2/T1; 

  /*******Calcul du nombre de tours***/
  ntour_t1 = Ndata / nbpt_t1;
  ntour_t2 = Ndata / nbpt_t2;

  /* Allocation d'un tableau pour stocker les covaraiances */

  som_x = malloc ( ntour_t1 * sizeof(double) );
  som_y = malloc ( ntour_t1 * sizeof(double) );
  som_xy = malloc ( ntour_t1 * sizeof(double) );
  nbpt_xy = malloc ( ntour_t1 * sizeof(long) );

/* on calcule les sommes sur la plus petite periode  T1 */
/* et on stocke les sommes dans un tableau de ntour_t1 elements */

  for (k = 0; k < ntour_t1; k++)
    {
      /*bornes sur chaque tour */
      binf = k * nbpt_t1;
      bsup = (k + 1)*nbpt_t1;

      som_x[k] = 0.;
      som_y[k] = 0.;
      som_xy[k] = 0.;
      nbpt_xy[k] = 0;

      for (j = binf; j < bsup; j++)
	{
	  if (isfinite (x[j]) && isfinite (y[j]))
	    {
	      som_x[k] = som_x[k] + (double) x[j];
	      som_y[k] = som_y[k] + (double) y[j];
	      som_xy[k] = som_xy[k] + ( (double) x[j] * (double) y[j] );
	      nbpt_xy[k] = nbpt_xy[k] + 1;
	    }
	}
    }

/* on itere sur le nombre le grande periode T2 */
   
   nb_rap = 0;
   
   for ( i = 0; i < ntour_t2; i++ ) 
      {
       kdeb = i*rap_T2_T1;
       kfin = (i+1)*rap_T2_T1;
       
       moy_cov_t1 = 0.;
       n1 = 0;

       som_xy_t2 = 0.; 
       som_x_t2 = 0.; 
       som_y_t2 = 0.; 
       n2 = 0;

       for ( k= kdeb; k< kfin; k++ )
	   {
            if (isfinite (som_xy[k]) && isfinite (som_x[k]) && isfinite (som_y[k]) && nbpt_xy[k] > Rap_mini_valid*nbpt_t1  )
               {
		/* somme pour moyenne des covariances */
                d_n =  (double)nbpt_xy[k]; 
                moy_cov_t1 = moy_cov_t1 + ( som_xy[k]/d_n - (som_x[k]/d_n)*(som_y[k]/d_n) ); 
   
		/* somme pour covariance sur T2 */
	        som_xy_t2 = som_xy_t2 + som_xy[k]; 
	        som_x_t2 = som_x_t2 + som_x[k]; 
	        som_y_t2 = som_y_t2 + som_y[k]; 

		n1 = n1 + 1 ;
		n2 = n2 + nbpt_xy[k];
	       }

           }
       if ( ( n1 >= rap_T2_T1*Rap_mini_valid ) && (n2 >= Rap_mini_valid*nbpt_t2 ) )  
	   {
            moy_cov_t1 = moy_cov_t1 / (double) n1;

            d_n2 = (double) n2; 
            cov_t2 =  (som_xy_t2 / d_n2) - (  som_x_t2 / d_n2  )*(som_y_t2 /d_n2);

            Rap_stat[i] = fabs( ( moy_cov_t1 -cov_t2 )/cov_t2 ) ; 
	    nb_rap = nb_rap +1 ;
	   }
       else
	   {
             Rap_stat[i] = K_NaN;
           }

      }

  free ( som_xy);
  free ( som_x );
  free ( som_y );
  free ( nbpt_xy );

  return nb_rap;
}

/* la fonction d'enrobage classique */

int
OP_Stationnarite_Covar_XY (unsigned long NbVal, void *ArgList[], char *DiagExec)
{
  long CodRet;

  CodRet = Stationnarite_Covar_XY (NbVal,
		     (float *) ArgList[0],
		     (float *) ArgList[1],
		     *((float *) ArgList[2]),
		     *((int *) ArgList[3]),
		     *((int *) ArgList[4]),
		     *((float *) ArgList[5]),
		     (float *) ArgList[6] );
  if (CodRet >= 0)
    {
      sprintf (DiagExec, "OK: %ld val. calculées.", CodRet);
      return OP_OK;
    }
  switch (CodRet)
    {
    case -1:
      strcat (DiagExec, "; T1 doit etre inferieur a T2");
      return OP_FAIL;
    case -2:
      strcat (DiagExec, "; T2 doit etre multiple de T1");
      return OP_FAIL;
    case -3:
      strcat (DiagExec, "; Nombre points de la fenetre <=0");
      return OP_FAIL;
    default:
      strcat (DiagExec, "; Erreur inattendue");
      return OP_FAIL;
    }

}

void
ID_Stationnarite_Covar_XY (oper * optr)
{
  int i;

  strcpy (optr->Nom, "Stationnarite_Covar_XY");
  optr->Version = "$Revision: 5097 $";
  optr->Date = "$Date: 2013-03-25 13:23:40 +0100 (lun. 25 mars 2013) $";
  optr->fctptr = OP_Stationnarite_Covar_XY;
  optr->NbArg = 7;
  optr->misval_auto = 1;

  optr->Arg_Car[0].direction = DIR_IN;
  optr->Arg_Car[0].categorie = VECTOR;
  optr->Arg_Car[0].typ = ATYC_IF32;
  optr->Arg_Car[0].array_dim = "1";
  optr->Arg_Car[0].type_sample = "any";
  optr->Arg_Car[0].sample = "any";
  optr->Arg_Car[0].unite = "any";

  optr->Arg_Car[1].direction = DIR_IN;
  optr->Arg_Car[1].categorie = VECTOR;
  optr->Arg_Car[1].typ = ATYC_IF32;
  optr->Arg_Car[1].array_dim = "1";
  optr->Arg_Car[1].type_sample = "any";
  optr->Arg_Car[1].sample = "any";
  optr->Arg_Car[1].unite = "any";

  optr->Arg_Car[2].direction = DIR_IN;
  optr->Arg_Car[2].categorie = COEFFICIENT;
  optr->Arg_Car[2].array_dim = "1";
  optr->Arg_Car[2].typ = ATYC_IF32;
  optr->Arg_Car[2].unite = "any";
  optr->Arg_Car[2].type_sample = NULL;
  optr->Arg_Car[2].sample = NULL;

  for (i = 3; i <= 4; i++)
    {
      optr->Arg_Car[i].direction = DIR_IN;
      optr->Arg_Car[i].categorie = COEFFICIENT;
      optr->Arg_Car[i].array_dim = "1";
      optr->Arg_Car[i].typ = ATYC_I32;
      optr->Arg_Car[i].unite = "any";
      optr->Arg_Car[i].type_sample = NULL;
      optr->Arg_Car[i].sample = NULL;
    }

  optr->Arg_Car[5].direction = DIR_IN;
  optr->Arg_Car[5].categorie = COEFFICIENT;
  optr->Arg_Car[5].array_dim = "1";
  optr->Arg_Car[5].typ = ATYC_IF32;
  optr->Arg_Car[5].unite = "any";
  optr->Arg_Car[5].type_sample = NULL;
  optr->Arg_Car[5].sample = NULL;

  optr->Arg_Car[6].direction = DIR_OUT;
  optr->Arg_Car[6].categorie = VECTOR;
  optr->Arg_Car[6].typ = ATYC_IF32;
  optr->Arg_Car[6].array_dim = "1";
  optr->Arg_Car[6].NbVal = "$Arg1.NbVal/($Arg3*$Arg5)";
  optr->Arg_Car[6].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[6].sample = "1./$Arg5";
  optr->Arg_Car[6].ref_time = "$Arg1.ref_time+\"_Med_\"+$Arg7.sample";
  optr->Arg_Car[6].unite = "without";
  optr->Arg_Car[6].misval = "$Arg1.misval";
  optr->Arg_Car[6].famille = " \"controle\" ";
  optr->Arg_Car[6].name = "\"Stationnarite de la covariance \" + $Arg1.name + \".\" + $Arg2.name";
  optr->Arg_Car[6].en_name = "\"Stationnarity of :  \" + $Arg1.english_name + \".\" + $Arg2.english_name";

}
