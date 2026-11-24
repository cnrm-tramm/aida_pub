/*******************************************************************
* OPERATOR      CnvFlt2Dbl.c FUNCTION ANSI-C
*
* PURPOSE       Conversion d'un vecteur "float" en vecteur "double"  
*
* DESCRIPTION   RAS 
*
* VERSION       1.0
*
*               IN      float   vect_flt	vecteur "float" 
*
*               OUT     double   vect_dbl	vecteur "double"	
*
* ENTRY         NONE
*
* SUBPROGRAMS   NONE
*
* REFERENCES   	
*
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
#include <string.h>
#include <math.h>
#include "struct_oper.h"

long
CnvFlt2Dbl (unsigned long ndata,
	    const float *vect_flt,
	    double *vect_dbl)
{
  unsigned long i;

  for (i = 0; i < ndata; i++)
    {
      vect_dbl[i] = (double) (vect_flt[i]);
    }

  return i;
}

/* fonction d'enrobage */

int
OP_CnvFlt2Dbl (unsigned long Nbval, void *ArgList[], char *DiagExec)
{
  long CodRet;

  sprintf (DiagExec, "CnvFlt2Dbl (%lu ech); ", Nbval);

  CodRet = CnvFlt2Dbl (Nbval,
		       (float *) ArgList[0],
		       (double *) ArgList[1]);

  sprintf (&(DiagExec[strlen (DiagExec)]), "%ld valeurs converties.", CodRet);

  return OP_OK;
}

void
ID_CnvFlt2Dbl (oper * optr)
{
  strcpy (optr->Nom, "CnvFlt2Dbl");
  optr->Version = "$Revision$";
  optr->Date = "$Date$";
  optr->fctptr = OP_CnvFlt2Dbl;
  optr->type = OPERTYP_FMT_TRANSFORM;
  optr->NbArg = 2;

  /* vect_flt */
  optr->Arg_Car[0].direction = DIR_IN;
  optr->Arg_Car[0].categorie = VECTOR;
  optr->Arg_Car[0].typ = ATYC_IF32;
  optr->Arg_Car[0].array_dim = "1";
  optr->Arg_Car[0].type_sample = "any";
  optr->Arg_Car[0].sample = "any";
  optr->Arg_Car[0].unite = "any";

  /* vect_dbl */
  optr->Arg_Car[1].direction = DIR_OUT;
  optr->Arg_Car[1].categorie = VECTOR;
  optr->Arg_Car[1].typ = ATYC_IF64;
  optr->Arg_Car[1].array_dim = "1";
  optr->Arg_Car[1].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[1].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[1].sample = "$Arg1.sample";
  optr->Arg_Car[1].ref_time = "$Arg1.ref_time";
  optr->Arg_Car[1].unite = "$Arg1.unit";
  optr->Arg_Car[1].famille = "$Arg1.famille";
  optr->Arg_Car[1].name = "$Arg1.name";
  optr->Arg_Car[1].en_name = "$Arg1.english_name";
}
