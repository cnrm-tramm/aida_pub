/*******************************************************************
* OPERATOR      Cre_time_bnds_reg.c FUNCTION ANSI-C
*
* PURPOSE       Genere un temps regulier a partir 
*		d'une frequence et d'un decalage
*		de depart et positionne time_bnds.
*
* DESCRIPTION    
*
* VERSION       1.0
*
*               IN      double  durée	s	durée (en seconde) du vecteur désiré.
*               IN      double  decal	s	decalage initial
*               IN      double  freq    Hz      frequence d'"echantillonnage"
*               IN      string  time_bnds   bornes temps
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

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>

#include "struct_oper.h"
#include "Cre_time_reg.h"

int
OP_Cre_time_bnds_reg (unsigned long NbVal, void *ArgList[], char *DiagExec)
{
  long CodRet;
  int NCar;

  NCar = sprintf (DiagExec, "Cre_time_bnds_reg, duree %gs, depart : %g, freq :%g, time_bnds : %s ",
		  *((double *) ArgList[0]),
		  *((double *) ArgList[1]),
		  *((double *) ArgList[2]),
               (char *)ArgList[3] );
  if (NCar < 0)
    NCar = 0;
  DiagExec += NCar;

  CodRet = Cre_time_reg (*((double *) ArgList[0]),
			 *((double *) ArgList[1]),
			 *((double *) ArgList[2]), (double *) ArgList[4]);

  sprintf (DiagExec, "OK., le vecteur contient %ld echantillons", CodRet);


  Meta_Out[4].time_bnds = (char *) malloc((strlen((char *)ArgList[3]) + 1) * sizeof(char)) ;
  memset(Meta_Out[4].time_bnds, '\0', strlen((char *)ArgList[3]) + 1) ;
  memcpy(Meta_Out[4].time_bnds, (char *)ArgList[3], strlen((char *)ArgList[3])) ;

  return OP_OK;
}

void
ID_Cre_time_bnds_reg (oper * optr)
{
  strcpy (optr->Nom, "Cre_time_bnds_reg");
  optr->Version = "$Revision: 5097 $";
  optr->Date = "$Date: 2013-03-25 13:23:40 +0100 (lun. 25 mars 2013) $";
  optr->fctptr = OP_Cre_time_bnds_reg;
  optr->NbArg = 5;

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

  /* time_bnds      */
  optr->Arg_Car[3].direction = DIR_IN;
  optr->Arg_Car[3].categorie = COEFFICIENT;
  optr->Arg_Car[3].array_dim = "1";
  optr->Arg_Car[3].typ = ATYC_STRING;
  optr->Arg_Car[3].type_sample = NULL;	/* sans signification pour COEFFICIENT */
  optr->Arg_Car[3].sample = NULL;
  optr->Arg_Car[3].unite = "any";

  /* time_reg */
  optr->Arg_Car[4].direction = DIR_OUT;
  optr->Arg_Car[4].categorie = VECTOR;
  optr->Arg_Car[4].typ = ATYC_IF64;
  optr->Arg_Car[4].array_dim = "1";
  optr->Arg_Car[4].NbVal = " $Arg1 * $Arg3";
  optr->Arg_Car[4].type_sample = "\"regulier\"";
  optr->Arg_Car[4].sample = "$Arg3";
  optr->Arg_Car[4].ref_time = "";
  optr->Arg_Car[4].time_bnds = "";
  optr->Arg_Car[4].unite = "second";
  optr->Arg_Car[4].famille = " \"temps\" ";
  optr->Arg_Car[4].name = "\"temps regulier\" ";
  optr->Arg_Car[4].en_name = "\"regular time\" ";
}
