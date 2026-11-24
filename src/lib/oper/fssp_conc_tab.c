/*************************************************
* OPERATOR 	fssp_conc_tab.c 	FUNCTION ANSI-C
*
* PURPOSE	Transformation d'un tableau de comptage de FSSP
*               en tableau de concentrations partielles, par application
*               d'une simple proportionnalité Total_conc/Total_count.
*
* ARGUMENTS 	IN 	float  	Cnt_tab      Tableau des comptages
*		IN	int     nb_clases    Nombre de classes.
*		IN 	float	conc_totale  concentration totale (cm-3)
*
*		OUT 	float 	conc_part   concentration dans la classe  
*		
* ENTRY		NONE
*
* SUBPROGRAMS 	NONE
*
* REFERENCE	NONE
*
* "$Revision$"
*
* COPYRIGHT	Meteo-France
*		Centre National de Recherches Meteorologiques
*		GMEI/ TRAMM
*		42, av G. Coriolis 
*		31057	TOULOUSE cedex 1
*
*****************************************************************/

#define _POSIX_SOURCE 1
#define _XOPEN_SOURCE 600
/* Le #define _HPUX_SOURCE n'est la que pour "voir" strdup */
#define _HPUX_SOURCE 1

#include <stdio.h>
#include <string.h>
#include <math.h>
#include "struct_oper.h"

int
fssp_conc_tab (unsigned long ndata,
	       const float *Cnt_tab,
	       const int nb_classes,
	       const float *conc_totale,
	       float *conc_tab)

{
  unsigned long i;
  long indice_debut_ech, j;
  double somme_count, rapport;

  /* Prudence : vérification d'arguments. */
  if (nb_classes <= 0)
    return -1;

  if (nb_classes > 1024)
    return -2;

  for (i = 0; i < ndata; i++)
    {
      indice_debut_ech = i * nb_classes;

      somme_count = 0.0;
      for (j = indice_debut_ech; j < indice_debut_ech + nb_classes; j++)
	somme_count += Cnt_tab[j];

      if (somme_count == 0.0)
	{
	  for (j = indice_debut_ech; j < indice_debut_ech + nb_classes; j++)
	    conc_tab[j] = 0.0;
	}
      else
	{
	  rapport = conc_totale[i] / somme_count;

	  for (j = indice_debut_ech; j < indice_debut_ech + nb_classes; j++)
	    conc_tab[j] = Cnt_tab[j] * rapport;
	}
    }

  return 0;
}

/* fonction d'enrobage */

int
OP_fssp_conc_tab (unsigned long Nbval, void *ArgList[], char *DiagExec)
{
  int CodRet;

  CodRet = fssp_conc_tab (Nbval,
			  (float *) ArgList[0],
			  *((int *) ArgList[1]),
			  (float *) ArgList[2],
			  (float *) ArgList[3]);

  switch (CodRet)
    {
    case 0:
      return OP_OK;
    case -1:
      sprintf (DiagExec, "Nb_classes (%d) <= 0 !!!", *((int *) ArgList[1]) );
      return OP_FAIL;
    case -2:
      sprintf (DiagExec, "Nb_classes (%d) > 1024 !!!", *((int *) ArgList[1]) );
      return OP_FAIL;
    default:
      sprintf (DiagExec, "Unexpected error");
      return OP_FAIL;
    }
}

void
ID_fssp_conc_tab (oper * optr)
{
  strcpy (optr->Nom, "fssp_conc_tab");
  optr->Version = "$Revision$";
  optr->Date = "$Date$";
  optr->fctptr = OP_fssp_conc_tab;
  optr->NbArg = 4;

  /* Cnt_tab */
  optr->Arg_Car[0].direction = DIR_IN;
  optr->Arg_Car[0].categorie = VECTOR;
  optr->Arg_Car[0].typ = ATYC_IF32;
  optr->Arg_Car[0].array_dim = "any";
  optr->Arg_Car[0].type_sample = "any";
  optr->Arg_Car[0].sample = "any";
  optr->Arg_Car[0].unite = "";

  /* nb_classes */
  optr->Arg_Car[1].direction = DIR_IN;
  optr->Arg_Car[1].categorie = COEFFICIENT;
  optr->Arg_Car[1].typ = ATYC_I32;
  optr->Arg_Car[1].array_dim = "1";
  optr->Arg_Car[1].type_sample = "any";
  optr->Arg_Car[1].sample = "any";
  optr->Arg_Car[1].unite = "";

  /* conc_totale */
  optr->Arg_Car[2].direction = DIR_IN;
  optr->Arg_Car[2].categorie = VECTOR;
  optr->Arg_Car[2].typ = ATYC_IF32;
  optr->Arg_Car[2].array_dim = "1";
  optr->Arg_Car[2].type_sample = "any";
  optr->Arg_Car[2].sample = "any";
  optr->Arg_Car[2].unite = "cm-3";

  /* conc_tab */
  optr->Arg_Car[3].direction = DIR_OUT;
  optr->Arg_Car[3].categorie = VECTOR;
  optr->Arg_Car[3].typ = ATYC_IF32;
  optr->Arg_Car[3].array_dim = "$Arg1.array_dim";
  optr->Arg_Car[3].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[3].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[3].sample = "$Arg1.sample";
  optr->Arg_Car[3].ref_time = "$Arg1.ref_time";
  optr->Arg_Car[3].unite = "$Arg3.unit";
  optr->Arg_Car[3].famille = " \"microphysique\" ";
  optr->Arg_Car[3].name = " \"Concentrations\" ";
  optr->Arg_Car[3].en_name = " \"Concentrations\" ";
  optr->Arg_Car[3].bornes = "$Arg1.bornes";
  optr->Arg_Car[3].unit_bornes = "$Arg1.unit_bornes";
}
