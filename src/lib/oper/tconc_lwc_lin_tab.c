/*************************************************
* OPERATOR 	tconc_lwc_lin_tab.c 	FUNCTION ANSI-C
*
* PURPOSE	Calcul de la concentration totale et du contenu
*		en eau liquide à partir d'un tableau de 
*		concentrations partielles dont les diamètres 
*		sont répartis linéairement (typiquement, pour les OAP).
*
* ARGUMENTS 	IN     float	Conc_tab 	Tableau des concentrations
*		IN     int      nb_classes    Nombre de classes.
*		IN 	float 	a  	terme proportionnel à la classe pour le calcul du diamètre

*		IN 	float 	b  	terme constant pour le calcul du diamètre
*
*		OUT	float 	tcon 	concentration totale (cm-3)
*		OUT	float 	lwc	rapport de melange en eau liquide (g/m3)
*		
* ENTRY		NONE
*
* SUBPROGRAMS 	NONE
*
* REFERENCE     
*
* COPYRIGHT	Meteo-France
*		Centre National de Recherches Meteorologiques
*		GMEI/TRAMM+MNPCA
*		42, av G. Coriolis 
*		31057	TOULOUSE cedex
*
*****************************************************************/

#define _POSIX_SOURCE 1
#define _XOPEN_SOURCE 600

#include <stdio.h>
#include <string.h>
#include <stdlib.h>

int
tconc_lwc_lin_tab (unsigned long ndata,
		   float *Conc_tab,
		   int nb_classes, float a, float b, float *tconc, float *lwc)
{
  unsigned long i;
  int k;
  float dia;
  float *dia_cub;

  const float pi_sur_6 = 3.14159265358979323846 / 6.0;
  const float dens = 1.0;		/* densite de l'eau */

  /* Prudence : vérification d'arguments. */
  if (nb_classes <= 0)
    return -1;

  if (nb_classes > 1024)
    return -2;

  dia_cub = malloc (sizeof (*dia_cub) * nb_classes);
  for (k = 0; k < nb_classes; k++)
    {
      dia = a * (k + 1) + b;	/* microns */
      dia_cub[k] = dia * dia * dia;
    }

  for (i = 0; i < ndata; i++)
    {
      tconc[i] = 0;
      lwc[i] = 0;
      for (k = 0; k < nb_classes; k++)
	{
	  tconc[i] = tconc[i] + Conc_tab[i * nb_classes + k];
	  lwc[i] = lwc[i] + dia_cub[k] * Conc_tab[i * nb_classes + k];
	}
      lwc[i] =  dens * pi_sur_6 * lwc[i] * 1.e-6;	/* g/m3 */
    }

  free (dia_cub);
  dia_cub = NULL;
  return 0;
}

/* fonction d'enrobage */
#include "struct_oper.h"

int
OP_tconc_lwc_lin_tab (unsigned long NbVal, void *ArgList[], char *DiagExec)
{
  int CodRet;
  int NCar;

  NCar = sprintf (DiagExec, "tconc_lwc_lin_tab : (%ld echant.) ", NbVal) ;
  if (NCar < 0)
    NCar = 0;
  DiagExec += NCar;

  CodRet = tconc_lwc_lin_tab (NbVal,
			      (float *) ArgList[0],
			      *((int *) ArgList[1]),
			      *((float *) ArgList[2]),
			      *((float *) ArgList[3]),
			      (float *) ArgList[4], (float *) ArgList[5]);

  switch (CodRet)
    {
    case 0:
      return OP_OK;
    case -1:
      sprintf (DiagExec, "Nb_classes (%d) <= 0 !!!", *((int *) ArgList[1]));
      return OP_FAIL;
    case -2:
      sprintf (DiagExec, "Nb_classes (%d) > 1024 !!!", *((int *) ArgList[1]));
      return OP_FAIL;
    default:
      sprintf (DiagExec, "Unexpected error");
      return OP_FAIL;
    }
}

void
ID_tconc_lwc_lin_tab (oper * optr)
{
  strcpy (optr->Nom, "tconc_lwc_lin_tab");
  optr->Version = "$Revision$";
  optr->Date = "$Date$";
  optr->fctptr = OP_tconc_lwc_lin_tab;
  optr->NbArg = 6;

  /* Conc_tab */
  optr->Arg_Car[0].direction = DIR_IN;
  optr->Arg_Car[0].categorie = VECTOR;
  optr->Arg_Car[0].typ = ATYC_IF32;
  optr->Arg_Car[0].array_dim = "any";
  optr->Arg_Car[0].type_sample = "any";
  optr->Arg_Car[0].sample = "any";
  optr->Arg_Car[0].unite = "cm-3";

  /*  nb_classes  */
  optr->Arg_Car[1].direction = DIR_IN;
  optr->Arg_Car[1].categorie = COEFFICIENT;
  optr->Arg_Car[1].typ = ATYC_I32;
  optr->Arg_Car[1].array_dim = "1";
  optr->Arg_Car[1].type_sample = "";
  optr->Arg_Car[1].sample = "";
  optr->Arg_Car[1].unite = "";

  /* a */
  optr->Arg_Car[2].direction = DIR_IN;
  optr->Arg_Car[2].categorie = COEFFICIENT;
  optr->Arg_Car[2].typ = ATYC_IF32;
  optr->Arg_Car[2].array_dim = "1";
  optr->Arg_Car[2].unite = "micron";

  /* b */
  optr->Arg_Car[3].direction = DIR_IN;
  optr->Arg_Car[3].categorie = COEFFICIENT;
  optr->Arg_Car[3].typ = ATYC_IF32;
  optr->Arg_Car[3].array_dim = "1";
  optr->Arg_Car[3].unite = "micron";

  /*  tconc  */
  optr->Arg_Car[4].direction = DIR_OUT;
  optr->Arg_Car[4].categorie = VECTOR;
  optr->Arg_Car[4].typ = ATYC_IF32;
  optr->Arg_Car[4].array_dim = "1";
  optr->Arg_Car[4].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[4].ref_time = "$Arg1.ref_time";
  optr->Arg_Car[4].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[4].sample = "$Arg1.sample";
  optr->Arg_Car[4].unite = "cm-3";
  optr->Arg_Car[4].famille = " \"microphysique\" ";
  optr->Arg_Car[4].name = " \"Total concentration from \" + $Arg1.name";

  /* lwc */
  optr->Arg_Car[5].direction = DIR_OUT;
  optr->Arg_Car[5].categorie = VECTOR;
  optr->Arg_Car[5].typ = ATYC_IF32;
  optr->Arg_Car[5].array_dim = "1";
  optr->Arg_Car[5].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[5].ref_time = "$Arg1.ref_time";
  optr->Arg_Car[5].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[5].sample = "$Arg1.sample";
  optr->Arg_Car[5].unite = "gram/m3";
  optr->Arg_Car[5].famille = " \"microphysique\" ";
  optr->Arg_Car[5].name = " \"Liquid water content from \" + $Arg1.name";
}
