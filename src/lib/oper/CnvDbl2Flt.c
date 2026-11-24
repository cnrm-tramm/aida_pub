/*******************************************************************
* OPERATOR      CnvDbl2Flt.c FUNCTION ANSI-C
*
* PURPOSE       Conversion d'un vecteur "double" en vecteur "float"  
*
* DESCRIPTION   RAS 
*
* VERSION       1.0
*
*               IN      double  vect_dbl	vecteur "double" 
*
*               OUT     float   vect_flt	vecteur "float"	
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
#include <float.h>

#include "struct_oper.h"

unsigned long
CnvDbl2Flt (unsigned long ndata,
	    double *vect_dbl,
	    float *vect_flt)
{
  unsigned long i;
  unsigned long nb_overflow = 0;

  for (i = 0; i < ndata; i++)
    {
      vect_flt[i] = (float) (vect_dbl[i]);
      if (vect_dbl[i] > FLT_MAX)
	nb_overflow++;
    }

  return nb_overflow;
}

/* fonction d'enrobage */

int
OP_CnvDbl2Flt (unsigned long Nbval, void *ArgList[], char *DiagExec)
{
  unsigned long CodRet;

  sprintf (DiagExec, "CnvDbl2Flt (%lu ech)", Nbval);

  CodRet = CnvDbl2Flt (Nbval, (double *) ArgList[0], (float *) ArgList[1]);

  sprintf (&(DiagExec[strlen (DiagExec)]), "%lu valeurs converties.",
           Nbval - CodRet);

  return OP_OK;
}

void
ID_CnvDbl2Flt (oper * optr)
{
  strcpy (optr->Nom, "CnvDbl2Flt");
  optr->Version = "$Revision$";
  optr->Date = "$Date$";
  optr->fctptr = OP_CnvDbl2Flt;
  optr->type = OPERTYP_FMT_TRANSFORM;
  optr->NbArg = 2;

  /* vect_dbl */
  optr->Arg_Car[0].direction = DIR_IN;
  optr->Arg_Car[0].categorie = VECTOR;
  optr->Arg_Car[0].typ = ATYC_IF64;
  optr->Arg_Car[0].array_dim = "1";
  optr->Arg_Car[0].type_sample = "any";
  optr->Arg_Car[0].sample = "any";
  optr->Arg_Car[0].unite = "any";

  /* vect_flt */
  optr->Arg_Car[1].direction = DIR_OUT;
  optr->Arg_Car[1].categorie = VECTOR;
  optr->Arg_Car[1].typ = ATYC_IF32;
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
