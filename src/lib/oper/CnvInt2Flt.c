/*******************************************************************
* OPERATOR      CnvInt2Flt.c FUNCTION ANSI-C
*
* PURPOSE       Conversion d'un vecteur "Int16" en vecteur "float"  
*
* DESCRIPTION   RAS 
*
* VERSION       1.0
*
*               IN      int16   vect_int	vecteur "int" 
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
*               GMEI/TRAMM
*               42, av. G. Coriolis
*               31057   TOULOUSE cedex
* modifie 05/12/2002 : CBerne ajout de misval dans les parametres
*                      transferes dans l'entete du nouveau vecteur
*              
*******************************************************************/

#define _POSIX_SOURCE 1
#define _XOPEN_SOURCE 600

#include <stdio.h>
#include <string.h>
#include <math.h>
#include "struct_oper.h"

long
CnvInt2Flt (unsigned long ndata,
	    const short *vect_int,
	    float *vect_flt)
{
  unsigned long i;

  for (i = 0; i < ndata; i++)
    {
      vect_flt[i] = (float) (vect_int[i]);
    }

  return i;
}

/* fonction d'enrobage */

int
OP_CnvInt2Flt (unsigned long Nbval, void *ArgList[], char *DiagExec)
{
  long CodRet;

  sprintf (DiagExec, "CnvInt2Flt (%lu ech); ", Nbval);

  CodRet = CnvInt2Flt (Nbval,
		       (ATYP_I16 *) ArgList[0],
		       (float *) ArgList[1]);

  sprintf (&(DiagExec[strlen (DiagExec)]), "%ld valeurs converties.", CodRet);

  return OP_OK;
}

void
ID_CnvInt2Flt (oper * optr)
{
  strcpy (optr->Nom, "CnvInt2Flt");
  optr->Version = "$Revision$";
  optr->Date = "$Date$";
  optr->fctptr = OP_CnvInt2Flt;
  optr->type = OPERTYP_FMT_TRANSFORM;
  optr->NbArg = 2;

  /* vect_int */
  optr->Arg_Car[0].direction = DIR_IN;
  optr->Arg_Car[0].categorie = VECTOR;
  optr->Arg_Car[0].typ = ATYC_I16;
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
  optr->Arg_Car[1].misval = "$Arg1.misval";
  optr->Arg_Car[1].name = "$Arg1.name";
  optr->Arg_Car[1].en_name = "$Arg1.english_name";
}
