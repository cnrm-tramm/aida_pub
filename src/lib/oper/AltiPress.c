/*********************************************************
*
* OPERATOR       AltiPress.c  ANSI-C
*
* PURPOSE        Calculation of altitude from pressure and virtual temp.
*
* DESCRIPTION      
*
* 
* VERSION        $Revision$
*
* ARGUMENTS      IN   float   Tv      Kelvin          Virtual Temp.
*                IN   float   Ps      les 2 dans la   Static Pressure
*                IN   float   QNH     meme unite.     Ground pressure
*                IN   float   rsurg                   "constante" r/g
*
*                OUT  float   Alti_p  m               altitude
*
* FILES          NONE
*
* REFERENCES       
*              
* $Log: not supported by cvs2svn $
* Revision 1.7  2011/06/17 16:53:42  bruno_PIGUET
* Correction de syntaxe de formules utilisant le nom anglais d'un des vecteurs
* d'entree : $Arg<X>.english_name au lieu de $Arg<X>.en_name
*
* Revision 1.6  2010/12/02 10:24:22  bruno_PIGUET
* Adaptation Ã  la nouvelle version de struct oper (et arg_car).
*
* Revision 1.5  2009/06/18 15:12:50  william_MAUREL
* Ajout des informations de name, unit, english_name.
* Modification du nombre d argument de Poly_1_flt.c
*
* Revision 1.4  2009/03/12 15:48:46  bruno_PIGUET
* DÃ©finition gÃ©nÃ©rale et uniforme de "_XOPEN_SOURCE 600" pour pouvoir
* utiliser la fonction isfinite() (de math.h) tout en restant en C ANSI
* (isfinite() n'est officiellement dÃ©finie qu'en C99).
*
* Revision 1.3  2006/06/19 16:06:10  bruno_PIGUET
* Détection de l'unité de la température par appel à la fonction
* auto_tempe_unit de la bibliothèque "unit", au lieu de code local.
*
* Revision 1.2  2005/12/06 17:19:56  piguet
*
* Inclusion du bon fichier fil.h, amélioration reconnaissance température.
*
* Revision 1.2  2005/12/06 09:06:17  tramm
* Inclusion du bon fichier fil.h, amélioration reconnaissance température.
*
 * Revision 1.1  97/02/18  17:22:20  17:22:20  piguet (Bruno PIGUET)
 * Initial revision
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
AltiPress (unsigned long NLoop,
	   const float *Tv,
	   const float *Ps, const float QNH, const float rsurg, float *Alti_p)
{
  unsigned long i;
  int flag_info_tempe;
  float CtoK;

  /* Détermination automatique Kelvin/Celsius */
  flag_info_tempe = auto_tempe_unit (NLoop, Tv, &CtoK);

  for (i = 0; i < NLoop; i++)
    {
      *Alti_p = rsurg * (*Tv + CtoK) * log (QNH / *Ps);

      Tv++;
      Ps++;
      Alti_p++;
    }

  if (CtoK == 0.)
    return 0;
  else
    return +1;
}

/* la fonction d'enrobage classique */

int
OP_AltiPress (unsigned long NbVal, void *ArgList[], char *DiagExec)
{
  int CodRet;

  sprintf (DiagExec, "OP_AltiPress (%lu ech.), QNH=%f, R/g = %f", NbVal,
	   *((float *) ArgList[2]), *((float *) ArgList[3]));

  CodRet = AltiPress (NbVal,
		      (float *) ArgList[0],
		      (float *) ArgList[1],
		      *((float *) ArgList[2]),
		      *((float *) ArgList[3]), (float *) ArgList[4]);

  switch (CodRet)
    {
    case -1:
      strcat (DiagExec, "ERR : Tempé Ni Kelvin Ni Celsius");
      return OP_FAIL;
    case 0:
      strcat (DiagExec, "Unité Température reconnue : Kelvin;");
      return OP_OK;
    case 1:
      strcat (DiagExec, "Unité Température reconnue : Degrés Celsius");
      return OP_OK;
    default:
      strcat (DiagExec, "Erreur inattendue");
      return OP_FAIL;
    }
}

/* la fonction de description de l'operateur et ses arguments */

void
ID_AltiPress (oper * optr)
{
  strcpy (optr->Nom, "AltiPress");
  optr->Version = "$Revision$";
  optr->Date = "$Date$";
  optr->fctptr = OP_AltiPress;
  optr->NbArg = 5;

  /* Tv */
  optr->Arg_Car[0].direction = DIR_IN;
  optr->Arg_Car[0].categorie = VECTOR;
  optr->Arg_Car[0].typ = ATYC_IF32;
  optr->Arg_Car[0].array_dim = "1";
  optr->Arg_Car[0].type_sample = "any";
  optr->Arg_Car[0].sample = "any";
  optr->Arg_Car[0].unite = "Kelvin";

  /* Ps */
  optr->Arg_Car[1].direction = DIR_IN;
  optr->Arg_Car[1].categorie = VECTOR;
  optr->Arg_Car[1].typ = ATYC_IF32;
  optr->Arg_Car[1].array_dim = "1";
  optr->Arg_Car[1].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[1].type_sample = "any";
  optr->Arg_Car[1].sample = "any";
  optr->Arg_Car[1].unite = "hPa";

  /* QNH  */
  optr->Arg_Car[2].direction = DIR_IN;
  optr->Arg_Car[2].categorie = COEFFICIENT;
  optr->Arg_Car[2].typ = ATYC_IF32;
  optr->Arg_Car[2].array_dim = "1";
  optr->Arg_Car[2].type_sample = NULL;
  optr->Arg_Car[2].sample = NULL;
  optr->Arg_Car[2].unite = "hPa";

  /* rsurg */
  optr->Arg_Car[3].direction = DIR_IN;
  optr->Arg_Car[3].categorie = COEFFICIENT;
  optr->Arg_Car[3].typ = ATYC_IF32;
  optr->Arg_Car[3].array_dim = "1";
  optr->Arg_Car[3].type_sample = NULL;
  optr->Arg_Car[3].sample = NULL;
  optr->Arg_Car[3].unite = "any";

  /* Alti_p */
  optr->Arg_Car[4].direction = DIR_OUT;
  optr->Arg_Car[4].categorie = VECTOR;
  optr->Arg_Car[4].typ = ATYC_IF32;
  optr->Arg_Car[4].array_dim = "1";
  optr->Arg_Car[4].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[4].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[4].sample = "$Arg1.sample";
  optr->Arg_Car[4].ref_time = "$Arg1.ref_time";
  optr->Arg_Car[4].unite = "m";
  optr->Arg_Car[4].name = " \"Altitude pression issu de \" +$Arg2.name";
  optr->Arg_Car[4].en_name = " \"Pressure Altitude from \"+$Arg2.english_name";
  optr->Arg_Car[4].famille = " \"altitude\" ";
}
