/****************************************************
*
* OPERATOR      Remplace_mnq_angl_auto_unit.c   FUNCTION  ANSI-C
*
* PURPOSE       Replace missing values by linear interpolation.
*
* DESCRIPTION   Remplace dans un vecteur d'angles les valeurs manquantes dont 
*               le nombre est passé en argument.
*
* VERSION       1
*
* ARGUMENTS   IN   float  Var_in     degrés ou radians         vecteur origine
*             IN   char*  unit       "Radian" ou "Degre"       Unité de mesure des angles               
*             IN   int    nb_mnq     sans unité                nb maxi de valeurs manquantes pouvant être
*                                                              remplacées				     
*             OUT  float  Var_out    même unité que l'origine  vecteur interpolé
*
* REFERENCES
*
* CHANGES       
*               
*
* COPYRIGHT     Meteo-France
*
*#########################################################################*/

#define _POSIX_SOURCE 1
/* Le #define _XOPEN_SOURCE 600 necessaire pour isfinite() */
#define _XOPEN_SOURCE 600

#include <stdio.h>
#include <math.h>
#include <string.h>
#include <limits.h>
#include "struct_oper.h"
#include "unit_def.h"

/* La vraie fonction... */

long
Remplace_mnq_angl_auto_unit (unsigned long NbValIn,
			     float *Var_in,
			     const char *unit,
			     const int nb_mnq, float *Var_out)
{
  unsigned long i;
  int j;
  double D_to_R;
  int flag_ok;
  long duree_trou, nb_cor;
  float *last_val_ok;
  float Tmp_coeff;
  float X0, X1;

  switch (reconnait_deg_rad (unit))
    {
    case UNIT_IS_RADIAN:
      D_to_R = 1.0;
      break;
    case UNIT_IS_DEGREE:
      D_to_R = M_PI / 180.0;
      break;
    default:
      return -1;
    }
  /* Réglons immédiatement le cas ou y'a rien a faire : "NbValIn = 0" */
  if (NbValIn == 0)
    return 0;

  last_val_ok = NULL;
  duree_trou = 0;
  nb_cor = 0;
  for (i = 0; i < NbValIn; ++i)
    {
      if (!isfinite (*Var_in))
	{
	  flag_ok = 0;
	  ++duree_trou;
	}
      else
	{
	  flag_ok = 1;

	}
      if (flag_ok == 1)
	{
	  /*   Si cette valeur OK suit un "trou" (suite continue de */
	  /* valeurs invalides), il faut d'abord "boucher ce trou". */
	  if (duree_trou > nb_mnq)
	    {			/* Le trou entre last_val_ok et Var_in[i] est "long" */
	      /* on remplit par des "valeurs manquantes" */
	      for (j = 0; j < duree_trou; j++)
		{
		  *Var_out = K_NaN;
		  Var_out++;

		}
	    }
	  else if (duree_trou != 0)
	    {			/* Le trou entre last_val_ok et Var_in[i] est "court" */
	      if (last_val_ok == NULL)
		{		/* Que faire ? */
		  for (j = 0; j < duree_trou; j++)
		    {
		      *Var_out = *Var_in;
		      Var_out++;
		      nb_cor++;
		    }
		}
	      else
		{		/* Interpolation */
		  Tmp_coeff = 1.0 / (duree_trou + 1);
		  X0 = *last_val_ok;
		  X1 = *Var_in;
		  if (fabs (X0 - X1) > M_PI / D_to_R)
		    {
		      if (X1 < X0)
			X1 += 2.0 * M_PI / D_to_R;
		      else
			X1 -= 2.0 * M_PI / D_to_R;
		    }
		  for (j = 0; j < duree_trou; j++)
		    {
		      *Var_out =
			((duree_trou - j) * X0 + (j + 1) * X1) * Tmp_coeff;
		      Var_out++;
		      nb_cor++;
		    }
		}
	    }
	  *Var_out = *Var_in;
	  Var_out++;
	  last_val_ok = Var_in;
	  duree_trou = 0;
	}
      Var_in++;
    }
  /* La boucle est finie... */
  /* Mais toutes les corrections n'ont peut-être pas été faites */

  if (last_val_ok == NULL)
    {				/* Y'a pas une seule valeur bonne !! */
      for (j = 0; j < duree_trou; j++)
	{
	  *Var_out = K_NaN;
	  Var_out++;
	}
    }
  else if (duree_trou > nb_mnq)
    {				/* Il y a un GRAND trou avant la fin.  */
      for (j = 0; j < duree_trou; j++)
	{
	  *Var_out = K_NaN;
	  Var_out++;
	}

    }
  else if (duree_trou > 0)
    {				/* Il y a un petit trou avant la fin.  */
      for (j = 0; j < duree_trou; j++)
	{
	  *Var_out = *last_val_ok;
	  Var_out++;
	}
    }
  return nb_cor;
}

/* la fonction d'enrobage classique */

int
OP_Remplace_mnq_angl_auto_unit (unsigned long NbVal, void *ArgList[],
				char *DiagExec)
{
  long CodRet;

  CodRet = Remplace_mnq_angl_auto_unit (NbVal,
					(float *) ArgList[0],
					(char *) ArgList[1],
					*((int *) ArgList[2]),
					(float *) ArgList[3]);

  switch (CodRet)
    {
    case -1:
      sprintf (DiagExec, "ERR: Unité d'angle (%s) non reconnue.",
	       (char *) ArgList[1]);
      return OP_FAIL;
    case 0:
      sprintf (DiagExec, "Pas de valeur manquante ou pas de donnée");
    default:
      sprintf (DiagExec, "Nombre de valeurs corrigées: %ld.", CodRet);
    }
  return OP_OK;
}

void
ID_Remplace_mnq_angl_auto_unit (oper * optr)
{
  strcpy (optr->Nom, "Remplace_mnq_angl_auto_unit");
  optr->Version = "1";
  optr->Date = "$Date: 2015-08-17 13:59:12 +0200 (lun. 17 aout. 2015) $";
  optr->fctptr = OP_Remplace_mnq_angl_auto_unit;
  optr->NbArg = 4;

  /* Var_in */
  optr->Arg_Car[0].direction = DIR_IN;
  optr->Arg_Car[0].categorie = VECTOR;
  optr->Arg_Car[0].typ = ATYC_IF32;
  optr->Arg_Car[0].array_dim = "1";
  optr->Arg_Car[0].type_sample = "any";
  optr->Arg_Car[0].sample = "any";
  optr->Arg_Car[0].unite = "any";
  optr->Arg_Car[0].famille = "any";

  /* unit */
  optr->Arg_Car[1].direction = DIR_IN;
  optr->Arg_Car[1].categorie = COEFFICIENT;
  optr->Arg_Car[1].typ = ATYC_STRING;
  optr->Arg_Car[1].array_dim = "1";
  optr->Arg_Car[1].type_sample = NULL;
  optr->Arg_Car[1].sample = NULL;
  optr->Arg_Car[1].unite = "";

  /* nb_mnq */
  optr->Arg_Car[2].direction = DIR_IN;
  optr->Arg_Car[2].categorie = COEFFICIENT;
  optr->Arg_Car[2].array_dim = "1";
  optr->Arg_Car[2].typ = ATYC_I32;
  optr->Arg_Car[2].unite = "any";
  optr->Arg_Car[2].type_sample = NULL;
  optr->Arg_Car[2].sample = NULL;

  /* Var_out */
  optr->Arg_Car[3].direction = DIR_OUT;
  optr->Arg_Car[3].categorie = VECTOR;
  optr->Arg_Car[3].typ = ATYC_IF32;
  optr->Arg_Car[3].array_dim = "1";
  optr->Arg_Car[3].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[3].sample = "$Arg1.sample";
  optr->Arg_Car[3].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[3].ref_time = "$Arg1.ref_time";
  optr->Arg_Car[3].unite = "$Arg1.unit";
  optr->Arg_Car[3].famille = "$Arg1.famille";
}
