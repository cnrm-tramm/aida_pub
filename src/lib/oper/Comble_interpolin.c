/*************************************************************************
*
* OPERATOR         Comble_interpolin  FUNCTION ANSI-C
*
* PURPOSE          Remplace les valeurs manquantes par une interpolation lineaire 
*
* DESCRIPTION      
*                1 - Calcul de Y = moyenne glissante de X sur Nbpt_moy points
*                2 - Calcul de Y_int = interpolation linéaire de Y 
*                3 - On remplace les valeurs manquantes de X par les valeurs de Y_int 
*
* VERSION          1.0 
*
* ARGUMENTS  
*            IN   float      X           Paramètre 
*            IN   float      Misval      Valeur désignant la valeur manquante 
*            IN	  float      Nbpt_moy   Nombre de point sur lequel on effectue la moyenne glissante
*
*            OUT  float      Xf       	Parametre X dont les valeurs manquantes sont remplacées par une interpolation linéaire.
*            OUT  float      Flag_Xf    Flag valant 1 pour les valeurs X qui ont été remplacées, 0 pour les valeurs   
*
* ENTRY        NONE
*        
* SUBPROGRAMS  NONE
*        
* REFERENCES   
*
* COPYRIGHT    Meteo-France
*	       Centre National de Recherches Meteorologiques 
*	       GMEI/ TRAMM
*	       42, av G. Coriolis
*	       31057 TOULOUSE cedex  
*
*
*############################################################################*/


#define _POSIX_SOURCE 1
#define _XOPEN_SOURCE 600

#include <math.h>
#include <stdio.h>
#include <string.h>
#include <stdlib.h>

#include "struct_oper.h"
#include "MoyEch_mnq.h"

float
moy_flt_mnq_2 (const float *data_p, long N, int tolerance_mnq)
{
  const float misval_out = K_NaN;
  long j;
  register double loc_som;
  long mnq_som;
  float moyenne;

  loc_som = 0.0;
  mnq_som = 0;
  for (j = 0; j < N; j++)
    {
      if (!isfinite (*data_p))
	{
	  mnq_som = mnq_som + 1;
	  data_p++;
	}
      else
	{
	  loc_som += *data_p;
	  data_p++;
	}
    }

  if (mnq_som <= tolerance_mnq)
    {
      moyenne = loc_som / (N - mnq_som);
    }
  else
    {
      moyenne = misval_out;
    }

  /*fprintf(stderr, "moyenne : %g \n", moyenne );*/
  return moyenne;
}


int
Comble_interpolin ( unsigned long ndata,
			float *X,
			int Nbpt_moy,
			float *Xf,
			float *Flag_Xf )

{
  unsigned long i, j, k, nbval;
  long ndatainter;
  int N_moy, codret;

  float *X_filtre, *X_inter;
  float moy_deb, moy_fin;

  double finter;
  X_filtre = malloc ( ndata*sizeof(float) );
  if ( X_filtre == NULL )
     {
      fprintf (stderr, " Allocation impossible de X_filtre \n");
      return -3;
     }

 /* Calcul de la moyenne glissante sur Nbpt_moy points */
 /* on fait notre propre moyenne glissante 
     car on veut une valeur même s'il ya 99% de valeurs manquantes
     sur la fenêtre */


  moy_deb = moy_flt_mnq (&X[0], Nbpt_moy, Nbpt_moy-1 );
  for ( i = 0; i < Nbpt_moy/2; i++) 
      X_filtre[i] = moy_deb;

  for ( i = 0 ; i < ndata - Nbpt_moy; i++)  
      X_filtre[i+Nbpt_moy/2] = moy_flt_mnq_2 (&X[i], Nbpt_moy, Nbpt_moy-1 );

  moy_fin = moy_flt_mnq (&X[ndata -Nbpt_moy], Nbpt_moy, Nbpt_moy-1 );
  for ( i = ndata-Nbpt_moy/2 ; i < ndata; i++) 
      X_filtre[i] = moy_fin;


 /* Interpolation lineaire */
  i = 0;
  nbval = 0;
  while (i < ndata)
     {
      if ( isfinite( X[i] ) ) 
         {
	  Xf[i] = X[i];
	  Flag_Xf[i] = 0;
	  i = i+1;
         }
      else 
	 {
          j = i;
	  while ( (!isfinite ( X[j])) && (j != ndata-1) )
	     j = j+1;

	  if ( (isfinite (X[j])) && ( i > 0 ) ) 
            {
	     /* on a 2 valeurs valides qui encadrent la periode manquante
	       -> interpolation lineaire */
             for ( k = i; k < j; k++)
	       {
                Xf[k] =  X_filtre [i-1] + (X_filtre [j] - X_filtre [i-1])* (float)(k-i+1) / (float)(j-i+1); 
                Flag_Xf[k] = 1;
		nbval = nbval +1;
	       }
	     i = j;
	    }
	  else 
	    /* cas ou la serie se termine ou debute par une valeur manquante */
	    {
	     if ( i== 0 )  /* 1ere valeur manquante */
	        {
	         for ( k = i; k < j; k++)
		   {	 
                    Xf[k] = X_filtre [j];  
                    Flag_Xf[k] = 1;
		    nbval = nbval + 1;
		   }
	         i = j;
		}
	     else  /*derniere valeur manquante */
		{
	         for ( k = i; k < ndata; k++)
	           {
                    Xf[k] = X_filtre [i-1];  
                    Flag_Xf[k] = 1;
		    nbval = nbval +1;
		   }
		 break; /* on a fini */
		}
	    }
	 }
     }
 
 
  free(X_filtre);

  return nbval;
}

int 
OP_Comble_interpolin( unsigned long NbVal, void *ArgList[], char *DiagExec)
{
  unsigned long Codret;
		
  Codret = Comble_interpolin ( NbVal,
		      (float *) ArgList[0],
		      *(int *)ArgList[1],
		      (float *) ArgList[2],
		      (float *) ArgList[3] );
  if (Codret < 0 )
     return OP_FAIL;
  else 
    {
     sprintf (DiagExec,
	   "Nb val comblees :%lu",
	   Codret );
     return OP_OK;
    }
}



void
ID_Comble_interpolin (oper *optr)
{
  int idx;
  strcpy (optr->Nom, "Comble_interpolin");
  optr->Version = "Revision:$";
  optr->Date = "$Date:$";
  optr->fctptr = OP_Comble_interpolin;
  optr->NbArg = 4;		/* doit rester inf. a FIL_MAX_ARG */


  idx = 0;
  optr->Arg_Car[idx].direction = DIR_IN;
  optr->Arg_Car[idx].categorie = VECTOR;
  optr->Arg_Car[idx].typ = ATYC_IF32;
  optr->Arg_Car[idx].array_dim = "1";
  optr->Arg_Car[idx].type_sample = "any";
  optr->Arg_Car[idx].sample = "any";
  optr->Arg_Car[idx].unite = "";
  idx++;

  optr->Arg_Car[idx].direction = DIR_IN;
  optr->Arg_Car[idx].categorie = COEFFICIENT;
  optr->Arg_Car[idx].typ = ATYC_I32;
  optr->Arg_Car[idx].array_dim = "1";
  optr->Arg_Car[idx].type_sample = "any";
  optr->Arg_Car[idx].sample = "any";
  optr->Arg_Car[idx].unite = "";
  idx++;

  optr->Arg_Car[idx].direction = DIR_OUT;
  optr->Arg_Car[idx].categorie = VECTOR;
  optr->Arg_Car[idx].array_dim = "1";
  optr->Arg_Car[idx].sample = "$Arg1.sample";
  optr->Arg_Car[idx].typ = ATYC_IF32;
  optr->Arg_Car[idx].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[idx].ref_time = "$Arg1.ref_time";
  optr->Arg_Car[idx].unite = "$Arg1.unit";
  optr->Arg_Car[idx].famille = "$Arg1.famille";
  optr->Arg_Car[idx].name = "$Arg1.name + \" avec valeurs manquantes comblees par interpolation lineaire\" ";
  optr->Arg_Car[idx].en_name = "$Arg1.english_name + \" with gap filled by linear interpolation\" ";
  idx++;

  optr->Arg_Car[idx].direction = DIR_OUT;
  optr->Arg_Car[idx].categorie = VECTOR;
  optr->Arg_Car[idx].array_dim = "1";
  optr->Arg_Car[idx].sample = "$Arg1.sample";
  optr->Arg_Car[idx].typ = ATYC_IF32;
  optr->Arg_Car[idx].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[idx].ref_time = "$Arg1.ref_time";
  optr->Arg_Car[idx].unite = "without";
  optr->Arg_Car[idx].famille = "\"controle\"";
  optr->Arg_Car[idx].name = "\"Flag indiquant les valeurs manquantes comblees dans \"+ $Arg1.name";
  optr->Arg_Car[idx].en_name = "\"Flag giving filled value in  \"+ $Arg1.english_name";
  idx++;

}




