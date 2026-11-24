/*******************************************************************
* OPERATOR      Cre_time_reg.c FUNCTION ANSI-C
*
* PURPOSE       Genere un temps regulier a partir 
*		d'une frequence et d'un decalage
*		de depart
*
* DESCRIPTION    
*
* VERSION       1.0
*
*               IN      double  durée	s	durée (en seconde) du vecteur désiré.
*               IN      double  decal	s	decalage initial
*               IN      double  freq    Hz      frequence d'"echantillonnage"
*
*		OUT	double  time_reg 	temps regulier
*
* ENTRY         NONE
*
* SUBPROGRAMS   NONE
*
* REFERENCES     
*
* COPYRIGHT     Meteo-France
*               Centre National de Recherches Meteorologiques
*               GMEI/MMA
*               42, av. G. Coriolis
*               31057   TOULOUSE cedex
*
*******************************************************************/

#define _POSIX_SOURCE 1
#define _XOPEN_SOURCE 600
#define _XOPEN_SOURCE_EXTENDED 1

#include <math.h>
#include "struct_oper.h"

long
Cre_time_reg (const double duree,
	      const double decal, const double freq, double *time_reg)
{
  long nbi, i;
  double t;

  t = 1. / freq;
  /*nbi = duree * freq; */
  /* nbi = ceil(duree * freq); */
  /* modif. BP+OT 2004-11-05   */
  nbi = floor ((duree * freq) + 0.5);

  for (i = 0; i < nbi; i++)
    {
      time_reg[i] = i * t + decal;
    }

  /* modif. BP 2009-03-26 :
   * Le vecteur est créé avec une taille de 
   * ceil ($Arg1 * $Arg3), c'est à dire ceil(duree*freq)
   * alors que la boucle ci-dessus ne va que jusqu'à 
   * floor ((duree * freq) + 0.5)
   * Si les 2 calculs diffèrent, il est de bon ton
   * d'éviter d'avoir un dernier élément initialisé
   * aléatoirement
   */
  if (ceil (duree * freq) > nbi)
    {
      i = ceil (duree * freq) - 1;
      /* SB 2023-05-05 : pourquoi pas la valeur calculée ? (d'autant plus qu'un
	   * temps à Nan à peu de sens et de grande chance de faire planter les
	   * traitements qui l'utilise...)
	   * time_reg[i] = K_NaN;
	   */
      time_reg[i] = i * t + decal;
    }

  return nbi;
}

/* fonction d'enrobage */
#include <stdio.h>
#include <string.h>

int
OP_Cre_time_reg (unsigned long NbVal, void *ArgList[], char *DiagExec)
{
  long CodRet;
  int NCar;

  NCar = sprintf (DiagExec, "Cre_time_reg, duree %gs, depart : %g, freq :%g, ",
		  *((double *) ArgList[0]),
		  *((double *) ArgList[1]),
		  *((double *) ArgList[2]));
  if (NCar < 0)
    NCar = 0;
  DiagExec += NCar;

  CodRet = Cre_time_reg (*((double *) ArgList[0]),
			 *((double *) ArgList[1]),
			 *((double *) ArgList[2]), (double *) ArgList[3]);

  sprintf (DiagExec, "OK., le vecteur contient %ld échantillons", CodRet);
  return OP_OK;
}

void
ID_Cre_time_reg (oper * optr)
{
  strcpy (optr->Nom, "Cre_time_reg");
  optr->Version = "$Revision$";
  optr->Date = "$Date$";
  optr->fctptr = OP_Cre_time_reg;
  optr->NbArg = 4;

  /* duree */
  optr->Arg_Car[0].direction = DIR_IN;
  optr->Arg_Car[0].categorie = COEFFICIENT;
  optr->Arg_Car[0].typ = ATYC_IF64;
  optr->Arg_Car[0].array_dim = "1";
  optr->Arg_Car[0].type_sample = "";
  optr->Arg_Car[0].sample = "";
  optr->Arg_Car[0].unite = "second";

  /* decal */
  optr->Arg_Car[1].direction = DIR_IN;
  optr->Arg_Car[1].categorie = COEFFICIENT;
  optr->Arg_Car[1].typ = ATYC_IF64;
  optr->Arg_Car[1].array_dim = "1";
  optr->Arg_Car[1].type_sample = "";
  optr->Arg_Car[1].sample = "";
  optr->Arg_Car[1].unite = "second";

  /* freq */
  optr->Arg_Car[2].direction = DIR_IN;
  optr->Arg_Car[2].categorie = COEFFICIENT;
  optr->Arg_Car[2].typ = ATYC_IF64;
  optr->Arg_Car[2].array_dim = "1";
  optr->Arg_Car[2].type_sample = "";
  optr->Arg_Car[2].sample = "";
  optr->Arg_Car[2].unite = "Hz";

  /* time_reg */
  optr->Arg_Car[3].direction = DIR_OUT;
  optr->Arg_Car[3].categorie = VECTOR;
  optr->Arg_Car[3].typ = ATYC_IF64;
  optr->Arg_Car[3].array_dim = "1";
  optr->Arg_Car[3].NbVal = " $Arg1 * $Arg3";
  optr->Arg_Car[3].type_sample = "\"regulier\"";
  optr->Arg_Car[3].sample = "$Arg3";
  optr->Arg_Car[3].ref_time = "";
  optr->Arg_Car[3].unite = "second";
  optr->Arg_Car[3].famille = " \"temps\" ";
  optr->Arg_Car[3].name = "\"temps regulier\" ";
  optr->Arg_Car[3].en_name = "\"regular time\" ";
}
