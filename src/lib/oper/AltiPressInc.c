/*********************************************************
*
* OPERATOR       AltiPressInc.c  ANSI-C
*
* PURPOSE        Incremental calculation of altitude from pressure
*                and virtual temp.
*
* DESCRIPTION      
*
* 
* VERSION        $Revision$
*
* ARGUMENTS      IN   float   Tv       Kelvin      Virtual Temp.
*                IN   float   Ps       hPa         Static Pressure
*                IN   float   ref_time sec         Measurement datation.
*                IN   float   S0       sec         Initial time.
*                IN   float   Z0       m           Initial altitude
*                IN   float   rsurg                "constante" r/g
*
*                OUT  float   Alti_p   m           altitude
*
* FILES          NONE
*
* REFERENCES       
*              
* $Log: not supported by cvs2svn $
* Revision 1.7  2011/09/20 08:42:49  bruno_PIGUET
* Modernisation : message DiagExec moins inutilement bavard,
* ajout de la contrainte : les deux vecteurs d'entree doivent avoir le mÃªme nombre d'echantillon.
* amÃ©lioration des champs "name" produits.
*
* Revision 1.6  2010/12/02 10:24:22  bruno_PIGUET
* Adaptation Ã  la nouvelle version de struct oper (et arg_car).
*
* Revision 1.5  2009/03/12 15:48:46  bruno_PIGUET
* DÃ©finition gÃ©nÃ©rale et uniforme de "_XOPEN_SOURCE 600" pour pouvoir
* utiliser la fonction isfinite() (de math.h) tout en restant en C ANSI
* (isfinite() n'est officiellement dÃ©finie qu'en C99).
*
* Revision 1.4  2008/09/09 14:27:54  bruno_PIGUET
* Fonction ID_... : dÃ©calrartions avant le code, pour compilateurs C90.
*
* Revision 1.3  2007/11/14 12:23:37  henri-pierre_VERGE
* Correction commentaire en-tete et unite d'un argument.
*
* Revision 1.2  2007/11/14 11:57:31  henri-pierre_VERGE
* Traitement des valeurs manquantes.
*
* Revision 1.1  2007/10/16 16:35:49  henri-pierre_VERGE
* Creation, en modifiant AltiPress pour le rendre incremental.
*
 * 
*
* COPYRIGHT      Meteo-France
*
* AGREEMENT      Nothing special
*#########################################################################*/

#define _POSIX_SOURCE 1
#define _XOPEN_SOURCE 600

#include <string.h>
#include <stdio.h>
#include <math.h>
#include "struct_oper.h"
#include "unit.h"

#ifndef K_T0
#define K_T0 (273.15)
#endif

int
AltiPressInc (unsigned long NLoop,
	      const float *Tv,
	      const float *Ps,
	      const double *Sref,
	      double S0,
	      double ecart_max_avant,
	      float Z0, float rsurg, float *Alti_p, long *diagno)
{
  long i, j, i0;
  int flag_info_tempe;
  float CtoK;

  /* Détermination automatique Kelvin/Celsius. */
  flag_info_tempe = auto_tempe_unit (NLoop, Tv, &CtoK);

  /* Recherche i0 */
  /* On cherche le premier temps >= S0 */
  i0 = 0;
  while ((i0 < NLoop) && (Sref[i0] < S0))
    i0++;

  if (i0 >= NLoop)
    {
      for (i = 0; i < NLoop; i++)
	{
	  Alti_p[i] = K_NaN;
	}
      diagno[0] = -1;
    }
  else if (S0 < (Sref[0] - ecart_max_avant))
    {
      for (i = 0; i < NLoop; i++)
	{
	  Alti_p[i] = K_NaN;
	}
      diagno[0] = -2;
    }
  else
    {
      Alti_p[i0] = Z0;
      diagno[0] = i0;
      for (i = i0; i < NLoop - 1; i = j)
	{
	  j = i + 1;
	  while ((j < NLoop - 1) && ((!isfinite (Tv[j]))
				     || (!isfinite (Ps[j]))))
	    {
	      Alti_p[j] = K_NaN;
	      j++;
	    }
	  Alti_p[j] = Alti_p[i] +
	    rsurg * ((Tv[j] + Tv[i]) / 2. + CtoK) * log (Ps[i] / Ps[j]);
	}
      for (i = i0; i > 0; i = j)
	{
	  j = i - 1;
	  while ((j > 0) && ((!isfinite (Tv[j])) || (!isfinite (Ps[j]))))
	    {
	      Alti_p[j] = K_NaN;
	      j--;
	    }
	  Alti_p[j] = Alti_p[i] +
	    rsurg * ((Tv[j] + Tv[i]) / 2. + CtoK) * log (Ps[i] / Ps[j]);
	}
    }

  if (CtoK == 0.)
    return 0;
  else
    return +1;
}

/* la fonction d'enrobage classique */

int
OP_AltiPressInc (unsigned long NbVal, void *ArgList[], char *DiagExec)
{
  int CodRet;
  long diag_tab[3];
  const double ecart_max_avant = 15;

  sprintf (DiagExec,
	   "AltiPressInc : %lu ech.,  instant initial = %gs,  altitude initiale = %gm, R/g = %g; ",
	   NbVal, *((double *) ArgList[3]), *((float *) ArgList[4]),
	   *((float *) ArgList[5]));

  CodRet = AltiPressInc (NbVal,
			 (float *) ArgList[0],
			 (float *) ArgList[1],
			 (double *) ArgList[2],
			 *((double *) ArgList[3]),
			 ecart_max_avant,
			 *((float *) ArgList[4]),
			 *((float *) ArgList[5]), (float *) ArgList[6],
			 diag_tab);

  switch (CodRet)
    {
    case -1:
      strcat (DiagExec, "ERR : Tempé Ni Kelvin Ni Celsius");
      return OP_FAIL;
    case 0:
      strcat (DiagExec, "Unité T reconnue : Kelvin; ");
      break;
    case 1:
      strcat (DiagExec, "Unité T reconnue : Degrés Celsius");
      break;
    default:
      strcat (DiagExec, "Erreur inattendue");
      return OP_FAIL;
    }

  if (diag_tab[0] == -1)
    {
      sprintf (DiagExec + strlen (DiagExec), " Tous les temps <=%g",
	       *((double *) ArgList[3]));
    }
  else if (diag_tab[0] == -2)
    {
      sprintf (DiagExec + strlen (DiagExec), " premier temps %g > %g + %g",
	       *((double *) ArgList[2]), *((double *) ArgList[3]),
	       ecart_max_avant);
    }
  else
    {
      sprintf (DiagExec + strlen (DiagExec), " i0=%ld", diag_tab[0]);
    }
  return OP_OK;
}

/* la fonction de description de l'operateur et ses arguments */

void
ID_AltiPressInc (oper * optr)
{
  int idx = 0;
  strcpy (optr->Nom, "AltiPressInc");
  optr->Version = "$Revision$";
  optr->Date = "$Date$";
  optr->fctptr = OP_AltiPressInc;
  optr->NbArg = 7;

  /* Tv */
  optr->Arg_Car[idx].direction = DIR_IN;
  optr->Arg_Car[idx].categorie = VECTOR;
  optr->Arg_Car[idx].typ = ATYC_IF32;
  optr->Arg_Car[idx].array_dim = "1";
  optr->Arg_Car[idx].type_sample = "any";
  optr->Arg_Car[idx].sample = "any";
  optr->Arg_Car[idx].unite = "Kelvin";
  idx++;

  /* P */
  optr->Arg_Car[idx].direction = DIR_IN;
  optr->Arg_Car[idx].categorie = VECTOR;
  optr->Arg_Car[idx].typ = ATYC_IF32;
  optr->Arg_Car[idx].array_dim = "1";
  optr->Arg_Car[idx].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[idx].type_sample = "any";
  optr->Arg_Car[idx].sample = "any";
  optr->Arg_Car[idx].unite = "hPa";
  idx++;

  /* Sref */
  optr->Arg_Car[idx].direction = DIR_IN;
  optr->Arg_Car[idx].categorie = VECTOR;
  optr->Arg_Car[idx].typ = ATYC_IF64;
  optr->Arg_Car[idx].array_dim = "1";
  optr->Arg_Car[idx].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[idx].type_sample = "any";
  optr->Arg_Car[idx].sample = "any";
  optr->Arg_Car[idx].unite = "sec";
  idx++;

  /* S0 */
  optr->Arg_Car[idx].direction = DIR_IN;
  optr->Arg_Car[idx].categorie = COEFFICIENT;
  optr->Arg_Car[idx].typ = ATYC_IF64;
  optr->Arg_Car[idx].array_dim = "1";
  optr->Arg_Car[idx].type_sample = NULL;
  optr->Arg_Car[idx].sample = NULL;
  optr->Arg_Car[idx].unite = "sec";
  idx++;

  /* Z0 */
  optr->Arg_Car[idx].direction = DIR_IN;
  optr->Arg_Car[idx].categorie = COEFFICIENT;
  optr->Arg_Car[idx].typ = ATYC_IF32;
  optr->Arg_Car[idx].array_dim = "1";
  optr->Arg_Car[idx].type_sample = NULL;
  optr->Arg_Car[idx].sample = NULL;
  optr->Arg_Car[idx].unite = "m";
  idx++;

  /* Rsurg */
  optr->Arg_Car[idx].direction = DIR_IN;
  optr->Arg_Car[idx].categorie = COEFFICIENT;
  optr->Arg_Car[idx].typ = ATYC_IF32;
  optr->Arg_Car[idx].array_dim = "1";
  optr->Arg_Car[idx].type_sample = NULL;
  optr->Arg_Car[idx].sample = NULL;
  optr->Arg_Car[idx].unite = "any";
  idx++;

  /* AltiP */
  optr->Arg_Car[idx].direction = DIR_OUT;
  optr->Arg_Car[idx].categorie = VECTOR;
  optr->Arg_Car[idx].typ = ATYC_IF32;
  optr->Arg_Car[idx].array_dim = "1";
  optr->Arg_Car[idx].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[idx].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[idx].sample = "$Arg1.sample";
  optr->Arg_Car[idx].ref_time = "$Arg1.ref_time";
  optr->Arg_Car[idx].unite = "m";
  optr->Arg_Car[idx].famille = " \"altitude\" ";
  optr->Arg_Car[idx].name =
    " \"Altitude-pression par integration le long de la trajectoire\" ";
  optr->Arg_Car[idx].en_name = " \"Pressure-Altitude\" ";
  idx++;
}
