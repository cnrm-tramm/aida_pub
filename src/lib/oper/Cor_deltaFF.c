/****************************************************************
* OPERATOR 	Cor_deltaFF  FUNCTION  ANSI-C
* 
* PURPOSE	Correction des valeurs ffbas, ffhaut et deltaFF
*               SAMER en fonction du "flag" de coherence (ctl_flag_deltaFF)
*               afin de permettre de calculer ensuite les flux methode aero
*               Pour le flag : voir Cor_deltaFF.c
*
* DESCRIPTION   Cette fonction detecte les valeurs
*	   	du flag et corrige ffbas ou ffhaut selon les cas.
*		Si flag = 0 : ffbas et ffhaut sont coherents entr'eux
*               Si flag > 0 : ffhaut trop "faible" --> on corrige empiriquement
*               Si flag < 0 : ffbas trop "faible" --> on corrige empiriquement
*
*
* VERSION         1.1
*
* ARGUMENTS 	IN 	float 	vent_bas    vent mesure au niveau bas
*           	IN 	float 	vent_haut   vent mesure au niveau haut
*           	IN 	float 	deltaFF     delta vent (haut - bas)
* 		IN 	float 	flag_deltaFF indicateur de validation du deltaFF
*                           --> 0 si OK
*                           --> -1 si ffbas = offset_bas et ffhaut trop fort (offset+0.5)
*                           --> -2 si ffhaut trop fort (incoherent : au-dessus de la droite empirique)
*                               2 droites : selon si ffbas < ou > a seuil_ffbas
*                           --> +1 si ffhaut = offset_haut et ffbas trop fort (offset+0.3)
*                           --> +2 si ffhaut trop faible (au-dessous de la droite empirique)
*                           --> -9999 si ffbas ou ffhaut manquant (ou les 2)
*		IN 	float 	offset_bas  valeur min du vent bas (en principe 0.)
*		IN 	float 	offset_haut valeur min du vent haut (en principe 0.)
*           	OUT	float 	vent_bas_cor  vent bas "qualifie" (OK ou cor)
*           	OUT	float 	vent_haut_cor vent haut "qualifie" (OK ou cor) 
*           	OUT	float 	deltaFF_cor   delta vent "qualifie"  
*           	OUT	float 	flag_cor   flag de qualification (0=ok , 1=interpol, 
*           	                              2=correction empirique)
*
* ENTRY		NONE
*
* SUBPROGRAMS 	NONE
* 
* REFERENCES	NONE
*
* CHANGES       1.2   
* 
* COPYRIGHT 	Meteo-France
*		Centre de Recherches Meteorologiques
*		GMEI/TRAMM
*		42, av. G. Coriolis
*		31057	TOULOUSE cedex
*
******************************************************************/

#define _POSIX_SOURCE 1
#define _XOPEN_SOURCE 600

/* Pour la fonction isfinite */
#define _HPUX_SOURCE 1


#include <stdio.h>
#include <string.h>
#include <limits.h>
#include <math.h>
#include "struct_oper.h"

unsigned long
Cor_deltaFF (unsigned long Nloop,
	     const float *ffbas,
	     const float *ffhaut,
	     const float *delta_ff,
	     const float *flag,
	     const float offset_bas,
	     const float offset_haut,
	     float *ffbas_cor,
	     float *ffhaut_cor,
	     float *deltaff_cor, float *flag_cor, unsigned long *Tab_diagno)
{
  unsigned long i, j;
  unsigned long nb_sup, nb_inf, nb_NaN, nbOK;
  int Flag_OK;
  float ffb, ffh, deltaff;
  float offset_ffb, offset_ffh, coeff;

  nb_sup = 0;
  nb_inf = 0;
  nb_NaN = 0;
  nbOK = 0;

  /* Empiriquement , une droite a ete determinee , reliant ffhaut et ffbas (coherence, en m/s) 
     FFhaut = 1.1647 * FFbas + 0.1 
     FFbas = 0.8586 * FFhaut - 0.08586 */
  /* seuil_ffbas = 4.; */

  for (i = 0; i < Nloop; i++)
    {
      ffb = ffbas[i];
      ffh = ffhaut[i];
      deltaff = delta_ff[i];
      /* Test : si flag[i] est OK ?   */
      if (flag[i] == 0.)
	{
	  /* Si flag[i] OK : valeurs identiques en sortie (ffbas, ffhaut...) */
/*	  printf (" dans operateur : flag=0 i=  ffb et ffh = %d %f %f \n", i,
		  ffbas[i], ffhaut[i]);  */
	  flag_cor[i] = 0.;
	  ffbas_cor[i] = ffbas[i];
	  ffhaut_cor[i] = ffhaut[i];
	  deltaff_cor[i] = delta_ff[i];
	  nbOK = nbOK + 1;
	}
      else
	{

	  if ((i == 0) || (i == (Nloop - 1)))
	    {
	      /* 1er point ou dernier point de la boucle : cas particulier */
	      /* on corrige avec la formule de la droite empirique */
	      flag_cor[i] = 2.;
	      if (flag[i] > 0.)
		/* ffhaut trop faible --> on le corrige (ffbas inchange) */
		{
		  ffhaut_cor[i] = (1.1647 * ffb) + 0.1;
		  ffbas_cor[i] = ffb;
		  nb_sup = nb_sup + 1;
		}
	      else
		/* ffbas trop faible --> on le corrige (ffhaut inchange) */
		{
		  ffbas_cor[i] = (0.8586 * ffh) - 0.08586;
		  ffhaut_cor[i] = ffh;
		  nb_inf = nb_inf + 1;
		}
	    }
	  else
	    /* autre point : indice >0 et  < Nloop */
	    {
	      if ((flag[i - 1] == 0.) && (flag[i + 1] == 0.))
		{
		  /* valeurs I-1 et I+1 sont OK --> on "interpole" */
		  flag_cor[i] = 1.;
		  coeff =
		    ((ffhaut[i - 1] / ffbas[i - 1]) +
		     (ffhaut[i + 1] / ffbas[i + 1])) / 2.;
		  if (flag[i] > 0.)
		    /* ffhaut trop faible --> on le corrige (ffbas inchange) */
		    {
		      ffhaut_cor[i] = (1. / coeff) * ffhaut[i];
		      ffbas_cor[i] = ffbas[i];
		      nb_sup = nb_sup + 1;
		    }
		  else
		    /* ffbas trop faible --> on le corrige (ffhaut inchange) */
		    {
		      ffbas_cor[i] = coeff * ffbas[i];
		      ffhaut_cor[i] = ffhaut[i];
		      nb_inf = nb_inf + 1;
		    }
		}
	      else
		{
		  /* formules empiriques de remplacement */
		  if (flag[i] > 0.)
		    /* ffhaut trop faible --> on le corrige (ffbas inchange) */
		    {
		      ffhaut_cor[i] = (1.1647 * ffb) + 0.1;
		      ffbas_cor[i] = ffb;
	              flag_cor[i] = 2.;
		      nb_sup = nb_sup + 1;
		    }
		  else
		    /* ffbas trop faible --> on le corrige (ffhaut inchange) */
		    {
		      ffbas_cor[i] = (0.8586 * ffh) - 0.08586;
		      ffhaut_cor[i] = ffh;
	      	      flag_cor[i] = 2.;
		      nb_inf = nb_inf + 1;
		    }
		}
	    }

	}
      deltaff_cor[i] = ffhaut_cor[i] - ffbas_cor[i];
    }
  /* La boucle est finie... */

  Tab_diagno[0] = nbOK;
  Tab_diagno[1] = nb_sup;
  Tab_diagno[2] = nb_inf;
  Tab_diagno[3] = nb_NaN;
  return nb_sup + nb_inf + nb_NaN;
}

/* fonction d'enrobage */

int
OP_Cor_deltaFF (unsigned long Nbval, void *ArgList[], char *DiagExec)
{
  unsigned long CodRet;
  unsigned long toto[4];

  /* sprintf (DiagExec,""); */

  CodRet = Cor_deltaFF (Nbval,
			(float *) ArgList[0],
			(float *) ArgList[1],
			(float *) ArgList[2],
			(float *) ArgList[3],
			*((float *) ArgList[4]),
			*((float *) ArgList[5]),
			(float *) ArgList[6],
			(float *) ArgList[7],
			(float *) ArgList[8], (float *) ArgList[9], toto);

  sprintf (DiagExec,
	   "%lu valeurs (sur %lu) rejetée(s) [s:%lu, i:%lu, a:%lu, n:%lu]",
	   CodRet, Nbval, toto[0], toto[1]);
  return OP_OK;
}

void
ID_Cor_deltaFF (oper * optr)
{
  strcpy (optr->Nom, "Cor_deltaFF");
  optr->Version = "1.0";
  optr->Date = "07/10/05";
  optr->fctptr = OP_Cor_deltaFF;
  optr->NbArg = 10;
  optr->misval_auto = 0;	/*On traite explicitement misval */
  optr->Arg_Car[0].direction = DIR_IN;
  optr->Arg_Car[0].categorie = VECTOR;
  optr->Arg_Car[0].typ = ATYC_IF32;
  optr->Arg_Car[0].array_dim = "1";
  optr->Arg_Car[0].unite = "";
  optr->Arg_Car[0].type_sample = "any";
  optr->Arg_Car[0].sample = "any";

  optr->Arg_Car[1].direction = DIR_IN;
  optr->Arg_Car[1].categorie = VECTOR;
  optr->Arg_Car[1].typ = ATYC_IF32;
  optr->Arg_Car[1].array_dim = "1";
  optr->Arg_Car[1].unite = "";
  optr->Arg_Car[1].type_sample = "any";
  optr->Arg_Car[1].sample = "any";

  optr->Arg_Car[2].direction = DIR_IN;
  optr->Arg_Car[2].categorie = VECTOR;
  optr->Arg_Car[2].typ = ATYC_IF32;
  optr->Arg_Car[2].array_dim = "1";
  optr->Arg_Car[2].unite = "";
  optr->Arg_Car[2].type_sample = "any";
  optr->Arg_Car[2].sample = "any";

  optr->Arg_Car[3].direction = DIR_IN;
  optr->Arg_Car[3].categorie = VECTOR;
  optr->Arg_Car[3].typ = ATYC_IF32;
  optr->Arg_Car[3].array_dim = "1";
  optr->Arg_Car[3].unite = "";
  optr->Arg_Car[3].type_sample = "any";
  optr->Arg_Car[3].sample = "any";

  optr->Arg_Car[4].direction = DIR_IN;
  optr->Arg_Car[4].categorie = COEFFICIENT;
  optr->Arg_Car[4].typ = ATYC_IF32;
  optr->Arg_Car[4].array_dim = "1";
  optr->Arg_Car[4].unite = "";
  optr->Arg_Car[4].type_sample = NULL;
  optr->Arg_Car[4].sample = NULL;

  optr->Arg_Car[5].direction = DIR_IN;
  optr->Arg_Car[5].categorie = COEFFICIENT;
  optr->Arg_Car[5].typ = ATYC_IF32;
  optr->Arg_Car[5].array_dim = "1";
  optr->Arg_Car[5].unite = "";
  optr->Arg_Car[5].type_sample = NULL;
  optr->Arg_Car[5].sample = NULL;

  optr->Arg_Car[6].direction = DIR_OUT;
  optr->Arg_Car[6].categorie = VECTOR;
  optr->Arg_Car[6].typ = ATYC_IF32;
  optr->Arg_Car[6].array_dim = "1";
  optr->Arg_Car[6].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[6].sample = "$Arg1.sample";
  optr->Arg_Car[6].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[6].ref_time = "$Arg1.ref_time";
  optr->Arg_Car[6].unite = "$Arg1.unite";
  optr->Arg_Car[6].famille = "\"vent\"";
  optr->Arg_Car[6].misval = "";

  optr->Arg_Car[7].direction = DIR_OUT;
  optr->Arg_Car[7].categorie = VECTOR;
  optr->Arg_Car[7].typ = ATYC_IF32;
  optr->Arg_Car[7].array_dim = "1";
  optr->Arg_Car[7].NbVal = "$Arg2.NbVal";
  optr->Arg_Car[7].sample = "$Arg2.sample";
  optr->Arg_Car[7].type_sample = "$Arg2.type_sample";
  optr->Arg_Car[7].ref_time = "$Arg2.ref_time";
  optr->Arg_Car[7].unite = "$Arg2.unite";
  optr->Arg_Car[7].famille = "\"vent\"";
  optr->Arg_Car[7].misval = "";

  optr->Arg_Car[8].direction = DIR_OUT;
  optr->Arg_Car[8].categorie = VECTOR;
  optr->Arg_Car[8].typ = ATYC_IF32;
  optr->Arg_Car[8].array_dim = "1";
  optr->Arg_Car[8].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[8].sample = "$Arg1.sample";
  optr->Arg_Car[8].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[8].ref_time = "$Arg1.ref_time";
  optr->Arg_Car[8].unite = "";
  optr->Arg_Car[8].famille = "\"vent\"";
  optr->Arg_Car[8].misval = "";

  optr->Arg_Car[9].direction = DIR_OUT;
  optr->Arg_Car[9].categorie = VECTOR;
  optr->Arg_Car[9].typ = ATYC_IF32;
  optr->Arg_Car[9].array_dim = "1";
  optr->Arg_Car[9].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[9].sample = "$Arg1.sample";
  optr->Arg_Car[9].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[9].ref_time = "$Arg1.ref_time";
  optr->Arg_Car[9].unite = "";
  optr->Arg_Car[9].famille = "\"controle\"";
  optr->Arg_Car[9].misval = "";
}
