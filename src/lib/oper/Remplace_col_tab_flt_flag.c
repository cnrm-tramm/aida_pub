/*************************************************
* OPERATOR 	 Remplace_col_tab_flt_flag.c 	FUNCTION ANSI-C
*
* PURPOSE	Crée une copie d'un vecteur tableau, en remplaçant les
*               valeurs des colonnes données par un vecteur "scalaire"
*               lorsque le flag est différent de 0.
* 
* DESCRIPTION
*
* ARGUMENTS 	IN 	float[]	tabin 	        Vecteur-tableau d'entree
*               IN 	float[]	tabin 	        Vecteur-flag d'entree
*               IN 	int	Nb_Col_Tab_in   Taille du vecteur d'entree
*               IN 	char *	col_rempla      Numéro des "Colonnes" à remplacer
*                                                 (convention "C", début à zéro)
*               IN 	float	val_rempla      Valeurs de remplacement.
*
*               OUT	float[]	tabout		Vecteur-tableau produit
*		
* ENTRY		NONE
*
* SUBPROGRAMS 	NONE
*
* REFERENCE	NONE
*
* AUTHOR 	Bruno Piguet
*
* COPYRIGHT	CNRM-GAME,
*               URA Meteo-France & CNRS
*		Centre National de Recherches Meteorologiques
*		GMEI/TRAMM
*		42, av G. Coriolis 
*		31057	TOULOUSE cedex
*
*****************************************************************/

#define _POSIX_SOURCE 1
#define _XOPEN_SOURCE 600

#include <stdio.h>
#include <string.h>
#include "struct_oper.h"
#include <limits.h>

long
Remplace_col_tab_flt_flag (unsigned long ndata,
                      const float *tabin,	/* tabin est en fait un tableau 2D */
                      const float *flag,	
		              int Nb_Col_Tab_in,
                      char *col_rempla,
                      float val_rempla,
                      float *tabout)	/* tabout est en fait un tableau 2D */
{
  unsigned long i, k;
  int j;
  int int_col;
  char *str_col;

/*  if (col_rempla < 0)
    return -1;

  if (col_rempla > Nb_Col_Tab_in)
    return -2;
*/
  /* Première boucle de copie systématique. */
  for (i = 0; i < ndata; i++)
    {
      k = i * Nb_Col_Tab_in;
      for (j = 0; j < Nb_Col_Tab_in; j++)
	{
	  tabout[k] = tabin[k];
	  k++;
	}
    }

  /* Seconde boucle de remplacement */

  str_col = strtok (col_rempla, "-");
  while (str_col != NULL)
    {
      int_col = atoi(str_col);
      for (i = 0; i < ndata; i++)
        {
          if ( flag[i] != 0 )
          {     
            k = i * Nb_Col_Tab_in + int_col;
/*	    tabout[k] = val_rempla;*/
	    tabout[k] = K_NaN;
	  }
        }
      str_col = strtok (NULL, "-");
    }

  return i;
}

/* fonction d'enrobage */

int 
OP_Remplace_col_tab_flt_flag (unsigned long Nbval, void *ArgList[], char *DiagExec)
{
  long CodRet;

  CodRet = Remplace_col_tab_flt_flag (Nbval,
				 (float *) ArgList[0],
				 (float *) ArgList[1],
				 *((int *) ArgList[2]),
				 (char *)  ArgList[3],
				 *((float *) ArgList[4]), (float *) ArgList[5]);

  if (CodRet > 0)
    {
      sprintf (DiagExec, "OK, %ld instants traités", CodRet);
      return OP_OK;
    }
  switch (CodRet)
    {
    case 0:
      strcpy (DiagExec, "WARN : 0 instants traités !");
      return OP_OK;
    case -1:
      strcpy (DiagExec,
	      "Valeur négative de l'indice de colonne à remplacer !");
      return OP_FAIL;
    case -2:
      strcpy (DiagExec,
	      "Indice de colonne à remplacer plus grand que taille du tableau d'entree !");
      return OP_FAIL;
    default:
      strcpy (DiagExec, "Unexpected error !!");
      return OP_FAIL;
    }
}

void
ID_Remplace_col_tab_flt_flag (oper * optr)
{
  strcpy (optr->Nom, "Remplace_col_tab_flt_flag");
  optr->Version = "$Revision: 4731 $";
  optr->Date = "$Date: 2012-08-21 18:25:57 +0200 (mar. 21 aoÃ»t 2012) $";
  optr->fctptr = OP_Remplace_col_tab_flt_flag;
  optr->NbArg = 6;

  /* tabin */
  optr->Arg_Car[0].direction = DIR_IN;
  optr->Arg_Car[0].categorie = VECTOR;
  optr->Arg_Car[0].typ = ATYC_IF32;
  optr->Arg_Car[0].array_dim = "any";
  optr->Arg_Car[0].type_sample = "any";
  optr->Arg_Car[0].sample = "any";
  optr->Arg_Car[0].unite = "";

  /* flag */
  optr->Arg_Car[1].direction = DIR_IN;
  optr->Arg_Car[1].categorie = VECTOR;
  optr->Arg_Car[1].typ = ATYC_I32;
  optr->Arg_Car[1].array_dim = "any";
  optr->Arg_Car[1].type_sample = "any";
  optr->Arg_Car[1].sample = "any";
  optr->Arg_Car[1].unite = "";

  /* Nb_Col_Tab_in  */
  optr->Arg_Car[2].direction = DIR_IN;
  optr->Arg_Car[2].categorie = COEFFICIENT;
  optr->Arg_Car[2].typ = ATYC_I32;
  optr->Arg_Car[2].array_dim = "1";
  optr->Arg_Car[2].unite = "";

  /* col_rempla  */
  optr->Arg_Car[3].direction = DIR_IN;
  optr->Arg_Car[3].categorie = COEFFICIENT;
  optr->Arg_Car[3].typ = ATYC_STRING;
  optr->Arg_Car[3].array_dim = "1";
  optr->Arg_Car[3].unite = "";

  /* val_rempla  */
  optr->Arg_Car[4].direction = DIR_IN;
  optr->Arg_Car[4].categorie = COEFFICIENT;
  optr->Arg_Car[4].typ = ATYC_IF32;
  optr->Arg_Car[4].array_dim = "1";
  optr->Arg_Car[4].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[4].unite = "$Arg1.unit";

  /* tabout */
  optr->Arg_Car[5].direction = DIR_OUT;
  optr->Arg_Car[5].categorie = VECTOR;
  optr->Arg_Car[5].typ = ATYC_IF32;
  optr->Arg_Car[5].array_dim = "$Arg1.array_dim";
  optr->Arg_Car[5].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[5].ref_time = "$Arg1.ref_time";
  optr->Arg_Car[5].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[5].sample = "$Arg1.sample";
  optr->Arg_Car[5].unite = "$Arg1.unit";
  optr->Arg_Car[5].famille = "$Arg1.famille";
  optr->Arg_Car[5].misval = "$Arg1.misval";
  optr->Arg_Car[5].name = "$Arg1.name modifie par $Arg4.name";
  optr->Arg_Car[5].bornes = "$Arg1.bornes";
  optr->Arg_Car[5].unit_bornes = "$Arg1.unit_bornes";
}
