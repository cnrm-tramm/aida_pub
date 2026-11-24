/****************************************************
*
* OPERATOR     Stationnarite_Ustar.c   FUNCTION  ANSI-C
*
* PURPOSE      	Test de la stationnarite de  Ustar 
*
* DESCRIPTION  	Ce opérateur calcule le rapport  :
*
*                  Rapport = [ moyenne(Ustar sur T1) - Ustar sur T2 ]/ ( Ustar sur T2 ) 
*
*                Foken considère que si Rapport < 30 % on considère des conditions stationnaires 
*
* VERSION       $Revision: 5097 $
*
* ARGUMENTS   IN   float  U    		m/s    	        composante U du vent	
*             IN   float  V    		m/s    		composante V du vent 
*             IN   float  W    		m/s    		composante W du vent
*             IN   float  Fe   		s-1		fréquence d'échantillonnage des données	
*             IN   int  T1 	 	s		Temps d'intégration pour le calcul des covariances (T1 < T2 )
*             IN   int  T2 	 	s		Temps d'intégration pour le calcul des covariances (T2 multiple de T1) 	
*             IN   float Rap_mini_valid without		Rapport minimum de données présentes pour le calcul des variances 
*
*             OUT  float  Rap_stat      without         Rapport quantifiant la stationnarite de Ustar 
*
* REFERENCES
*            T. Foken, Micrometeorology, 2008 
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
Stationnarite_Ustar (unsigned long Ndata,
	  const float *u,
	  const float *v, 
	  const float *w, 
	  const float Fe, 
	  const int T1, 
	  const int T2, 
	  const float Rap_mini_valid, 
	  float *Rap_stat )
{
  int rap_T2_T1; 
  long i, j, k, ntour_t1, ntour_t2, nbpt_t1, nbpt_t2;
  long kdeb, kfin, binf, bsup, n1, n2, nb_rap;

  double moy_ustar_t1, ustar_t1, ustar_t2;
  double som_u_t2, som_v_t2, som_w_t2, som_wu_t2, som_wv_t2;
  double d_n, d_n2;

  double *som_u, *som_v, *som_w, *som_wu, *som_wv;
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

  /* Allocation d'un tableau pour stocker les covariances */

  som_u = malloc ( ntour_t1 * sizeof(double) );
  som_v = malloc ( ntour_t1 * sizeof(double) );
  som_w = malloc ( ntour_t1 * sizeof(double) );
  som_wu = malloc ( ntour_t1 * sizeof(double) );
  som_wv = malloc ( ntour_t1 * sizeof(double) );
  nbpt_xy = malloc ( ntour_t1 * sizeof(long) );

/* on calcule les sommes sur la plus petite periode  T1 */
/* et on stocke les sommes dans un tableau de ntour_t1 elements */

  for (k = 0; k < ntour_t1; k++)
    {
      /*bornes sur chaque tour */
      binf = k * nbpt_t1;
      bsup = (k + 1)*nbpt_t1;

      som_u[k] = 0.;
      som_v[k] = 0.;
      som_w[k] = 0.;
      som_wu[k] = 0.;
      som_wv[k] = 0.;
      nbpt_xy[k] = 0;

      for (j = binf; j < bsup; j++)
	{
	  if (isfinite (u[j]) && isfinite (v[j]) && isfinite (w[j]) )
	    {
	      som_u[k] = som_u[k] + (double) u[j];
	      som_v[k] = som_v[k] + (double) v[j];
	      som_w[k] = som_w[k] + (double) w[j];
	      som_wu[k] = som_wu[k] + ( (double) w[j] * (double) u[j] );
	      som_wv[k] = som_wv[k] + ( (double) w[j] * (double) v[j] );
	      nbpt_xy[k] = nbpt_xy[k] + 1;
	    }
	}
    }

/* on itere sur le nombre de grande periode T2 */
   
   nb_rap = 0;
   
   for ( i = 0; i < ntour_t2; i++ ) 
      {
       kdeb = i*rap_T2_T1;
       kfin = (i+1)*rap_T2_T1;
       
       moy_ustar_t1 = 0.;
       n1 = 0;

       som_wu_t2 = 0.; 
       som_wv_t2 = 0.; 
       som_u_t2 = 0.; 
       som_v_t2 = 0.; 
       som_w_t2 = 0.; 
       n2 = 0;

       for ( k= kdeb; k< kfin; k++ )
	   {
            if (isfinite (som_wu[k]) && isfinite (som_wv[k]) &&
	        isfinite (som_u[k]) && isfinite (som_v[k]) && 
	       	isfinite (som_w[k]) && nbpt_xy[k] >=  Rap_mini_valid*nbpt_t1  )
               {
		/* somme pour moyenne des ustar sur t1  */
                d_n =  (double)nbpt_xy[k]; 
		ustar_t1 = sqrt ( sqrt ( pow ( (som_wu[k]/d_n) - (som_w[k]/d_n)*(som_u[k]/d_n), 2.0 ) +
				         pow ( (som_wv[k]/d_n) - (som_w[k]/d_n)*(som_v[k]/d_n), 2.0 ) ) );
                moy_ustar_t1 = moy_ustar_t1 + ustar_t1;
   
		/* somme pour covariance sur T2 */
	        som_wu_t2 = som_wu_t2 + som_wu[k]; 
	        som_wv_t2 = som_wv_t2 + som_wv[k]; 
	        som_u_t2 = som_u_t2 + som_u[k]; 
	        som_v_t2 = som_v_t2 + som_v[k]; 
	        som_w_t2 = som_w_t2 + som_w[k]; 

		n1 = n1 + 1 ;
		n2 = n2 + nbpt_xy[k];
	       }

           }
       if ( ( n1 >= rap_T2_T1*Rap_mini_valid ) && (n2 >= Rap_mini_valid*nbpt_t2 ) ) 
	   {
            moy_ustar_t1 = moy_ustar_t1 / (double) n1;

            d_n2 = (double) n2; 
            ustar_t2 =  sqrt( sqrt ( pow((som_wu_t2 / d_n2) - (  som_u_t2 / d_n2  )*(som_w_t2 /d_n2), 2.0 ) +
			             pow((som_wv_t2 / d_n2) - (  som_v_t2 / d_n2  )*(som_w_t2 /d_n2), 2.0 ) ) );


            Rap_stat[i] = fabs( ( moy_ustar_t1 - ustar_t2 )/ustar_t2 ) ; 
	    nb_rap = nb_rap +1 ;
	   }
       else
	   {
             Rap_stat[i] = K_NaN;
           }

      }

  free ( som_wu);
  free ( som_wv);
  free ( som_u );
  free ( som_v );
  free ( som_w );
  free ( nbpt_xy );

  return nb_rap;
}

/* la fonction d'enrobage classique */

int
OP_Stationnarite_Ustar (unsigned long NbVal, void *ArgList[], char *DiagExec)
{
  long CodRet;

  CodRet = Stationnarite_Ustar (NbVal,
		     (float *) ArgList[0],
		     (float *) ArgList[1],
		     (float *) ArgList[2],
		     *((float *) ArgList[3]),
		     *((int *) ArgList[4]),
		     *((int *) ArgList[5]),
		     *((float *) ArgList[6]),
		     (float *) ArgList[7] );
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
ID_Stationnarite_Ustar (oper * optr)
{
  int i;

  strcpy (optr->Nom, "Stationnarite_Ustar");
  optr->Version = "$Revision: 5097 $";
  optr->Date = "$Date: 2013-03-25 13:23:40 +0100 (lun. 25 mars 2013) $";
  optr->fctptr = OP_Stationnarite_Ustar;
  optr->NbArg = 8;
  optr->misval_auto = 1;

  optr->Arg_Car[0].direction = DIR_IN;
  optr->Arg_Car[0].categorie = VECTOR;
  optr->Arg_Car[0].typ = ATYC_IF32;
  optr->Arg_Car[0].array_dim = "1";
  optr->Arg_Car[0].type_sample = "any";
  optr->Arg_Car[0].sample = "any";
  optr->Arg_Car[0].unite = "m/s";

  optr->Arg_Car[1].direction = DIR_IN;
  optr->Arg_Car[1].categorie = VECTOR;
  optr->Arg_Car[1].typ = ATYC_IF32;
  optr->Arg_Car[1].array_dim = "1";
  optr->Arg_Car[1].type_sample = "any";
  optr->Arg_Car[1].sample = "any";
  optr->Arg_Car[1].unite = "m/s";

  optr->Arg_Car[2].direction = DIR_IN;
  optr->Arg_Car[2].categorie = VECTOR;
  optr->Arg_Car[2].array_dim = "1";
  optr->Arg_Car[2].typ = ATYC_IF32;
  optr->Arg_Car[2].unite = "m/s";
  optr->Arg_Car[2].type_sample = NULL;
  optr->Arg_Car[2].sample = NULL;

  optr->Arg_Car[3].direction = DIR_IN;
  optr->Arg_Car[3].categorie = COEFFICIENT;
  optr->Arg_Car[3].array_dim = "1";
  optr->Arg_Car[3].typ = ATYC_IF32;
  optr->Arg_Car[3].unite = "any";
  optr->Arg_Car[3].type_sample = NULL;
  optr->Arg_Car[3].sample = NULL;

  for (i = 4; i <= 5; i++)
    {
      optr->Arg_Car[i].direction = DIR_IN;
      optr->Arg_Car[i].categorie = COEFFICIENT;
      optr->Arg_Car[i].array_dim = "1";
      optr->Arg_Car[i].typ = ATYC_I32;
      optr->Arg_Car[i].unite = "any";
      optr->Arg_Car[i].type_sample = NULL;
      optr->Arg_Car[i].sample = NULL;
    }
  
  optr->Arg_Car[6].direction = DIR_IN;
  optr->Arg_Car[6].categorie = COEFFICIENT;
  optr->Arg_Car[6].array_dim = "1";
  optr->Arg_Car[6].typ = ATYC_IF32;
  optr->Arg_Car[6].unite = "any";
  optr->Arg_Car[6].type_sample = NULL;
  optr->Arg_Car[6].sample = NULL;

  optr->Arg_Car[7].direction = DIR_OUT;
  optr->Arg_Car[7].categorie = VECTOR;
  optr->Arg_Car[7].typ = ATYC_IF32;
  optr->Arg_Car[7].array_dim = "1";
  optr->Arg_Car[7].NbVal = "$Arg1.NbVal/($Arg4*$Arg6)";
  optr->Arg_Car[7].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[7].sample = "1./$Arg6";
  optr->Arg_Car[7].ref_time = "$Arg1.ref_time+\"_Med_\"+$Arg8.sample";
  optr->Arg_Car[7].unite = "without";
  optr->Arg_Car[7].misval = "$Arg1.misval";
  optr->Arg_Car[7].famille = " \"controle\" ";
  optr->Arg_Car[7].name = "\"Stationnarite de Ustar\"";
  optr->Arg_Car[7].en_name = "\"Stationnarity of Ustar\"";
}
