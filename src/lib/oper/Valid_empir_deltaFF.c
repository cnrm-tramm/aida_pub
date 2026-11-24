/****************************************************************
* OPERATOR 	Valid_empir_deltaFF  FUNCTION  ANSI-C
* 
* PURPOSE	Validation empirique des valeurs de deltaFF (dispositif
*               SAMER pour calcul flux aerodynamiques) 
*
* DESCRIPTION   Cette fonction detecte les valeurs
*	   	hors de la zone determinee empiriquement (C.Berne + B.Piguet)
*		a partir des mesures Campagnes Escompte (Crau) et SMOS (Le-Fauga)
*               Cet operateur cree un nouveau vecteur "valid_deltaFF" qui permet
*               d'indiquer si le calcul de flux aerodynamique resultant est "valide"
*
*
* VERSION         1.1
*
* ARGUMENTS 	IN 	float 	vent_bas    vent mesure au niveau bas
*           	IN 	float 	vent_haut   vent mesure au niveau haut
*		IN 	float 	offset_bas  valeur min du vent bas (en principe 0.)
*		IN 	float 	offset_haut valeur min du vent haut (en principe 0.)
* 		OUT 	float 	flag_deltaFF indicateur de validation du deltaFF
*                           --> 0 si OK
*                           --> -1 si ffbas = offset_bas et ffhaut trop fort (offset+0.5)
*                           --> -2 si ffhaut trop fort (incoherent : au-dessus de la droite empirique)
*                               2 droites : selon si ffbas < ou > a seuil_ffbas
*                           --> +1 si ffhaut = offset_haut et ffbas trop fort (offset+0.3)
*                           --> +2 si ffhaut trop faible (au-dessous de la droite empirique)
*                           --> -9999 si ffbas ou ffhaut manquant (ou les 2)
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
Valid_empir_deltaFF (unsigned long Nloop,
		     const float *ffbas,
		     const float *ffhaut,
		     const float offset_bas,
		     const float offset_haut,
		     float *flag_deltaFF, unsigned long *Tab_diagno)
{
  unsigned long i;
  unsigned long nb_sup, nb_inf, nb_NaN, nbOK;
  float ffb, ffh, ffhaut_max1, ffhaut_max2, seuil_ffbas;
  float offset_ffb, offset_ffh, ffhaut_min;

  nb_sup = 0;
  nb_inf = 0;
  nb_NaN = 0;
  nbOK = 0;

  /* Empiriquement , deux droites ont ete determinees pour definir
     le ffhaut_max (donc 2 valeurs de ffhaut_max en fonction de la valeur
     de ffbas) - Le seuil_ffbas est la valeur de ffbas en m/s iau dela de
     de laquelle on prend ffhaut_max2 (si < alors ffhaut_max2) */
  seuil_ffbas = 4.;

 /* printf(" dans operateur : offset bas/haut = %f %f \n",offset_bas,offset_haut); */

  for (i = 0; i < Nloop; i++)
    {
      ffb = *ffbas;
      ffh = *ffhaut;
      *flag_deltaFF = 0.;
      /* Valeur correctement représentée par un float ?   */
      if ((!isfinite (ffb)) || (!isfinite (ffh)))
	{
	  nb_NaN = nb_NaN + 1;
	  *flag_deltaFF = -9999.;
	}
      else
	{
	  ffhaut_max1 = 1.225 * ffb + 0.7;
	  ffhaut_max2 = 1.6 * ffb - 0.8;
	  ffhaut_min = 1.08 * ffb - 0.5;
	  offset_ffb = offset_bas + 0.5;
	  offset_ffh = offset_haut + 0.3;

	  if ((ffb == offset_bas) && (ffh > offset_ffh))
	    /* ffbas = valeur_min et ffhaut incoherent --> trop fort */
	    {
	      *flag_deltaFF = -1.;
	      nb_sup = nb_sup + 1;
	    }
	  else if ((ffb <= seuil_ffbas) && (ffh > ffhaut_max1))
	    /* ffbas <= 4. et ffhaut incoherent (trop fort) */
	    {
	      *flag_deltaFF = -2.;
	      nb_sup = nb_sup + 1;
	    }
	  else if ((ffb > seuil_ffbas) && (ffh > ffhaut_max2))
	    /* ffbas > 4. et ffhaut incoherent (trop fort) */
	    {
	      *flag_deltaFF = -2.;
	      nb_sup = nb_sup + 1;
	    }
	  else if ((ffh == offset_haut) && (ffb > offset_ffb))
	    /* ffhaut = valeur_min et ffbas incoherent --> trop fort */
	    {
	      *flag_deltaFF = +1.;
	      nb_inf = nb_inf + 1;
	    }
	  else if (ffh < ffhaut_min)
	    /* ffhaut incoherent (trop faible) */
	    {
	      *flag_deltaFF = +2.;
	      nb_inf = nb_inf + 1;
	    }
	  else
	    {
	      /* Tout est coherent ...au niveau mesure mais on peut avoir
	         ffbas = ffhaut (ce sera filtre ensuite par le calcul de flux aero */
	      nbOK = nbOK + 1;
	      *flag_deltaFF = 0.;
	    }

	}
      flag_deltaFF++;
      ffbas++;
      ffhaut++;
    }
  /* La boucle est finie... */

  /* Test de validité interne */
  if (nb_sup + nb_inf + nb_NaN + nbOK != Nloop)
    {
      (void) fprintf (stderr, "internal error : \n");
    }
  /*  */

  Tab_diagno[0] = nbOK;
  Tab_diagno[1] = nb_sup;
  Tab_diagno[2] = nb_inf;
  Tab_diagno[3] = nb_NaN;
  return nb_sup + nb_inf + nb_NaN;
}

/* fonction d'enrobage */

int
OP_Valid_empir_deltaFF (unsigned long Nbval, void *ArgList[], char *DiagExec)
{
  unsigned long CodRet;
  unsigned long toto[4];

  /* sprintf (DiagExec,""); */

  CodRet = Valid_empir_deltaFF (Nbval,
				(float *) ArgList[0],
				(float *) ArgList[1],
				*((float *) ArgList[2]),
				*((float *) ArgList[3]),
				(float *) ArgList[4], toto);

  sprintf (DiagExec,
	   "%lu valeurs (sur %lu) rejetée(s) [s:%lu, i:%lu, a:%lu, n:%lu]",
	   CodRet, Nbval, toto[0], toto[1], toto[2], toto[3]);
  return OP_OK;
}

void
ID_Valid_empir_deltaFF (oper * optr)
{
  strcpy (optr->Nom, "Valid_empir_deltaFF");
  optr->Version = "1.0";
  optr->Date = "09/02/05";
  optr->fctptr = OP_Valid_empir_deltaFF;
  optr->NbArg = 5;
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
  optr->Arg_Car[2].categorie = COEFFICIENT;
  optr->Arg_Car[2].typ = ATYC_IF32;
  optr->Arg_Car[2].array_dim = "1";
  optr->Arg_Car[2].unite = "";

  optr->Arg_Car[3].direction = DIR_IN;
  optr->Arg_Car[3].categorie = COEFFICIENT;
  optr->Arg_Car[3].typ = ATYC_IF32;
  optr->Arg_Car[3].array_dim = "1";
  optr->Arg_Car[3].unite = "";

  /*  flag_deltaFF  */
  optr->Arg_Car[4].direction = DIR_OUT;
  optr->Arg_Car[4].categorie = VECTOR;
  optr->Arg_Car[4].typ = ATYC_IF32;
  optr->Arg_Car[4].array_dim = "1";
  optr->Arg_Car[4].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[4].sample = "$Arg1.sample";
  optr->Arg_Car[4].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[4].ref_time = "$Arg1.ref_time";
  optr->Arg_Car[4].unite = "";
  optr->Arg_Car[4].famille = "\"controle\"";
  optr->Arg_Car[4].misval = "";
}
