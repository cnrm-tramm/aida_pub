/****************************************************
*
* OPERATOR      Decod_Top_CAM.c   FUNCTION  ANSI-C
*
* PURPOSE       Decode "TOP" markers produced by CAM acquisition system.
*
* DESCRIPTION   Décodage du mot "TOP" des systèmes d'acquisition du CAM.
*
* VERSION       $Revision$
*
* ARGUMENTS   IN   int32  TOP      unite     	
*             OUT  int16   topnum   count	Top number (sequencial)
*             OUT  int16   toptyp   none  	Top type ()
*
* REFERENCES
*
* CHANGES       
*
* COPYRIGHT     Meteo-France
*
*#########################################################################*/

#define _POSIX_SOURCE 1
#define _XOPEN_SOURCE 600
/* Le #define _HPUX_SOURCE n'est la que pour "voir" strdup */
#define _HPUX_SOURCE 1
#define _XOPEN_SOURCE_EXTENDED 1

#include <stdio.h>
#include <math.h>
#include <string.h>
#include <limits.h>
#include <sys/types.h>		/* we need int32_t... */

#include "struct_oper.h"

/* La vraie fonction... */

long
Decod_Top_CAM (long NbVal,
	       int32_t * TOPwrd, int16_t * topnum, int16_t * toptyp)
{
  unsigned long i;

  for (i = 0; i < NbVal; i++)
    {
      if ((TOPwrd[i] & 0x0000FFFF) == 0x0000FFFF)
	{
	  toptyp[i] = 0;
	  topnum[i] = 0;
	}
      else
	{
	  toptyp[i] = TOPwrd[i] & 0x0000FFFF;
	  topnum[i] = (TOPwrd[i] >> 16) & 0x0000FFFF;
	}
    }

  return i;
}

/* la fonction d'enrobage classique */

int
OP_Decod_Top_CAM (unsigned long NbVal, void *ArgList[], char *DiagExec)
{
  long CodRet;
  int NCar;

  NCar = sprintf (DiagExec, "Decod_Top_CAM : (%ld echant.) ", NbVal) ;
  if (NCar < 0)
    NCar = 0;
  DiagExec += NCar;

  CodRet = Decod_Top_CAM (NbVal,
			  (int32_t *) ArgList[0],
			  (int16_t *) ArgList[1], (int16_t *) ArgList[2]);

  if (CodRet > 0)
    return OP_OK;
  else
    return OP_FAIL;

}

void
ID_Decod_Top_CAM (oper * optr)
{
  strcpy (optr->Nom, "Decod_Top_CAM");
  optr->Version = "$Revision$";
  optr->Date = "$Date$";
  optr->fctptr = OP_Decod_Top_CAM;
  optr->NbArg = 3;
  optr->Arg_Car[0].direction = DIR_IN;
  optr->Arg_Car[0].categorie = VECTOR;
  optr->Arg_Car[0].typ = ATYC_I32;
  optr->Arg_Car[0].array_dim = "1";
  optr->Arg_Car[0].type_sample = "any";
  optr->Arg_Car[0].sample = "any";
  optr->Arg_Car[0].unite = "any";
  optr->Arg_Car[0].famille = "any";

  optr->Arg_Car[1].direction = DIR_OUT;
  optr->Arg_Car[1].categorie = VECTOR;
  optr->Arg_Car[1].typ = ATYC_I16;
  optr->Arg_Car[1].array_dim = "1";
  optr->Arg_Car[2].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[1].unite = "count";
  optr->Arg_Car[1].type_sample = NULL;
  optr->Arg_Car[1].sample = NULL;

  optr->Arg_Car[2].direction = DIR_OUT;
  optr->Arg_Car[2].categorie = VECTOR;
  optr->Arg_Car[2].typ = ATYC_I16;
  optr->Arg_Car[2].array_dim = "1";
  optr->Arg_Car[2].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[2].sample = "$Arg1.sample";
  optr->Arg_Car[2].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[2].ref_time = "$Arg1.ref_time";
  optr->Arg_Car[2].unite = "none";
  optr->Arg_Car[2].famille = " \"controle\" ";
}
