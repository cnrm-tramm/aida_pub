/****************************************************
*
* OPERATOR      Filtre_Gen.c   FUNCTION  ANSI-C
*
* PURPOSE       Filtre numerique avec type de fenetre en argument 
* 		et fonction de poids
*
* DESCRIPTION   Réalise numériquement un filtrage
*               avec le type de fenetre et une fonction de poids en argument 
*
* VERSION       $Revision$
*
* ARGUMENTS   IN   float  data      any        	Original data
*             IN   float  fe	     Hz   		Original data frequency
*             IN   int  pas        seconds            Intervale de temps autour de la valeur centrée          
*	      IN   int  type	     any		Type of filter (0 = simple, 1= Gauss, 2=Blackman etc..)
*             OUT  float  meandata      same as data	Averaged data
*             OUT  float  datafil      same as data	Filtered data
*
* REFERENCES
*
*	  	Octobre 2005
*
* COPYRIGHT     Meteo-France
*
*#########################################################################*/

#define _POSIX_SOURCE 1
#define _XOPEN_SOURCE 600

/* pour pouvoir utiliser la fonction isfinite */
#define _HPUX_SOURCE 1


#include <stdio.h>
#include <math.h>
#include <string.h>
#include <limits.h>
#include "struct_oper.h"

/* La vraie fonction... */


#include <stdlib.h>
#include <stdio.h>
#include <math.h>


int
calc_gauss (unsigned long fenetre, float *gauss)
{
  float sig = (float) fenetre / 6.;
  float mu = (float) fenetre / 2.;
  float pi = 4. * atan (1.);
  int j;
  for (j = 0; j <= fenetre; ++j)
    {
      float x_norm = (j - mu) / sig;
      gauss[j] = 1. / (sqrt (2. * pi) * sig) * exp (-x_norm * x_norm / 2.);
    }
  return 0;
}

float
convol (float *poids, const float *data, int n)
{
  int i;
  float pdt = 0, pds = 0;
  for (i = 0; i < n; i++)
    {
      pdt += poids[i] * data[i];
      pds += poids[i];
    }
  return pdt / pds;
}

int
Filtre_Gen (const unsigned long Ndata, const float *data, const float fe,
	    const unsigned long pas, const int type, float *meandata,
	    float *datafil)
{
  unsigned long i;
  unsigned long fenetre = floor ((pas * fe) + 0.5);
  unsigned long demifen = floor ((fenetre / 2.) + 0.5);
  unsigned long borne = Ndata - demifen;
  float *gauss;
  unsigned long binf;
  unsigned long bsup;
  unsigned long binfgauss;
  unsigned long bsupgauss;
  int len;
  /*fprintf (stderr, "fe=%f , pas= %ld ", fe, pas);

     fprintf (stderr, "fenetre=%ld , demifen= %ld ", fenetre, demifen); */
  /* gauss = (float*)malloc (( fenetre + 1) * sizeof (float)); */
  gauss = malloc ((fenetre + 1) * sizeof (*gauss));

  calc_gauss (fenetre, gauss);

  for (i = 0; i < demifen; i++)
    {
      binf = 0;
      binfgauss = demifen - i;
      bsup = i + demifen;
      bsupgauss = fenetre;
      len = (bsup - binf) + 1;
      if (isfinite (data[i]))
	{
	  meandata[i] = convol (&gauss[binfgauss], &data[binf], len);
	  /*fprintf (stderr, "i, meandata = %ld, %f\n", i, meandata[i]); */
	  datafil[i] = data[i] - meandata[i];
	}
    }
  for (i = demifen; i < borne; i++)
    {
      binf = i - demifen;
      binfgauss = 0;
      bsup = i + demifen;
      bsupgauss = fenetre;
      len = (bsup - binf) + 1;
      if (isfinite (data[i]))
	{
	  meandata[i] = convol (&gauss[binfgauss], &data[binf], len);
	  datafil[i] = data[i] - meandata[i];
	}
    }

  for (i = borne; i < Ndata; i++)
    {
      binf = i - demifen;
      binfgauss = 0;
      bsup = Ndata - 1;
      bsupgauss = demifen + (Ndata - 1) - i;
      len = (bsup - binf) + 1;
      if (isfinite (data[i]))
	{
	  meandata[i] = convol (&gauss[binfgauss], &data[binf], len);
	  datafil[i] = data[i] - meandata[i];
	}
    }
  free (gauss);
  return 0;
}

/* la fonction d'enrobage classique */

int
OP_Filtre_Gen (unsigned long NbVal, void *ArgList[], char *DiagExec)
{
  int CodRet;
  int NCar;

  NCar = sprintf (DiagExec, "Filtre_Gen : (%ld echant.) ", NbVal) ;
  if (NCar < 0)
    NCar = 0;
  DiagExec += NCar;

  CodRet = Filtre_Gen (NbVal,
		       (float *) ArgList[0],
		       *((float *) ArgList[1]),
		       *((unsigned long *) ArgList[2]),
		       *((int *) ArgList[3]),
		       (float *) ArgList[4], (float *) ArgList[5]);

}

void
ID_Filtre_Gen (oper * optr)
{
  strcpy (optr->Nom, "Filtre_Gen");
  optr->Version = "$Revision$";
  optr->Date = "$Date$";

  optr->fctptr = OP_Filtre_Gen;
  optr->NbArg = 6;
  optr->misval_auto = 1;	/* On s'en remet au mécanisme automatique, =0 si traitement specifique.  */

  /* data */
  optr->Arg_Car[0].direction = DIR_IN;
  optr->Arg_Car[0].categorie = VECTOR;
  optr->Arg_Car[0].typ = ATYC_IF32;
  optr->Arg_Car[0].array_dim = "1";
  optr->Arg_Car[0].type_sample = "any";
  optr->Arg_Car[0].sample = "any";
  optr->Arg_Car[0].unite = "any";

  /* fe */
  optr->Arg_Car[1].direction = DIR_IN;
  optr->Arg_Car[1].categorie = COEFFICIENT;
  optr->Arg_Car[1].array_dim = "1";
  optr->Arg_Car[1].typ = ATYC_IF32;
  optr->Arg_Car[1].unite = "Hz";
  optr->Arg_Car[1].type_sample = NULL;
  optr->Arg_Car[1].sample = NULL;

  /* pas */
  optr->Arg_Car[2].direction = DIR_IN;
  optr->Arg_Car[2].categorie = COEFFICIENT;
  optr->Arg_Car[2].array_dim = "1";
  optr->Arg_Car[2].typ = ATYC_LOCAL_ULONG;
  optr->Arg_Car[2].unite = "second";
  optr->Arg_Car[2].type_sample = NULL;
  optr->Arg_Car[2].sample = NULL;

  optr->Arg_Car[3].direction = DIR_IN;
  optr->Arg_Car[3].categorie = COEFFICIENT;
  optr->Arg_Car[3].array_dim = "1";
  optr->Arg_Car[3].typ = ATYC_I32;
  optr->Arg_Car[3].unite = "without";
  optr->Arg_Car[3].type_sample = NULL;
  optr->Arg_Car[3].sample = NULL;


  optr->Arg_Car[4].direction = DIR_OUT;
  optr->Arg_Car[4].categorie = VECTOR;
  optr->Arg_Car[4].typ = ATYC_IF32;
  optr->Arg_Car[4].array_dim = "1";
  optr->Arg_Car[4].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[4].misval = "$Arg1.misval";
  optr->Arg_Car[4].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[4].sample = "$Arg1.sample";
  optr->Arg_Car[4].ref_time = "$Arg1.ref_time";
  optr->Arg_Car[4].unite = "$Arg1.unit";
  optr->Arg_Car[4].famille = "$Arg1.famille";

  optr->Arg_Car[5].direction = DIR_OUT;
  optr->Arg_Car[5].categorie = VECTOR;
  optr->Arg_Car[5].typ = ATYC_IF32;
  optr->Arg_Car[5].array_dim = "1";
  optr->Arg_Car[5].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[5].misval = "$Arg1.misval";
  optr->Arg_Car[5].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[5].sample = "$Arg1.sample";
  optr->Arg_Car[5].ref_time = "$Arg1.ref_time";
  optr->Arg_Car[5].unite = "$Arg1.unit";
  optr->Arg_Car[5].famille = "$Arg1.famille";

}
