/*************************************************
* OPERATOR 	fssp_conc_part.c 	FUNCTION ANSI-C
*
* PURPOSE	Calcul de la concentration partielle
*		dans une classe de comptage d'une sonde FSSP. 
*
* ARGUMENTS 	IN 	float	jcl         comptage dans la classe 
*		IN	float   som_jcl     comptage total  	
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
* COPYRIGHT	Meteo-France
*		Centre National de Recherches Meteorologiques
*		GMEI/ MMA
*		42, av G. Coriolis 
*		31057	TOULOUSE cedex
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
fssp_conc_part (unsigned long ndata,
		float *jcl,
		float *som_jcl,
		float *conc_totale,
		float *conc_part)

{
  long i;

  for (i = 0; i < ndata; i++)
    {
      conc_part[i] = (jcl[i] * conc_totale[i]) / som_jcl[i];
    }

  return (0);
}

/* fonction d'enrobage */

int
OP_fssp_conc_part (unsigned long Nbval, void *ArgList[], char *DiagExec)
{
  int CodRet = fssp_conc_part (Nbval,
			       (float *) ArgList[0],
			       (float *) ArgList[1],
			       (float *) ArgList[2],
			       (float *) ArgList[3]);


  return OP_OK;
}

void
ID_fssp_conc_part (oper * optr)
{
  strcpy (optr->Nom, "fssp_conc_part");
  optr->Version = "1.0";
  optr->Date = "10/07/96";
  optr->fctptr = OP_fssp_conc_part;
  optr->NbArg = 4;

  optr->Arg_Car[0].direction = DIR_IN;
  optr->Arg_Car[0].categorie = VECTOR;
  optr->Arg_Car[0].typ = ATYC_IF32;
  optr->Arg_Car[0].array_dim = "1";
  optr->Arg_Car[0].type_sample = "any";
  optr->Arg_Car[0].sample = "any";
  optr->Arg_Car[0].unite = "";

  optr->Arg_Car[1].direction = DIR_IN;
  optr->Arg_Car[1].categorie = VECTOR;
  optr->Arg_Car[1].typ = ATYC_IF32;
  optr->Arg_Car[1].array_dim = "1";
  optr->Arg_Car[1].type_sample = "any";
  optr->Arg_Car[1].sample = "any";
  optr->Arg_Car[1].unite = "";

  optr->Arg_Car[2].direction = DIR_IN;
  optr->Arg_Car[2].categorie = VECTOR;
  optr->Arg_Car[2].typ = ATYC_IF32;
  optr->Arg_Car[2].array_dim = "1";
  optr->Arg_Car[2].type_sample = "any";
  optr->Arg_Car[2].sample = "any";
  optr->Arg_Car[2].unite = "cm-3";

  optr->Arg_Car[3].direction = DIR_OUT;
  optr->Arg_Car[3].categorie = VECTOR;
  optr->Arg_Car[3].typ = ATYC_IF32;
  optr->Arg_Car[3].array_dim = "1";
  optr->Arg_Car[3].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[3].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[3].sample = "$Arg1.sample";
  optr->Arg_Car[3].ref_time = "$Arg1.ref_time";
  optr->Arg_Car[3].unite = "$Arg3.unit";
  optr->Arg_Car[3].famille = " \"microphysique\" ";
}
