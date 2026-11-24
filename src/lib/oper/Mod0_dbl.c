/****************************************************
*
* OPERATOR       Mod0_dbl.c   FUNCTION  ANSI-C
*
* PURPOSE        Calcul de X - (X[0](modulo M))
*
* DESCRIPTION    Attention : pour convertir un temps GPS en UTC, utiliser GPS_to_UTC
*
* VERSION        1.0
*
* ARGUMENTS    IN   double  X    Any             first value
*              IN   double  M    Any             modulo value
*              OUT  double  Z    Any		Result
*
* ENTRY            
*                 
* SUBPROGRAMS    none
*
* FILES   
*
* REFERENCES   
*
* CHANGES              
*
* COPYRIGHT      Meteo-France
*
* AGREEMENT      The author wishes that .....
*#########################################################################*/

#define _POSIX_SOURCE 1
#define _XOPEN_SOURCE 600

#include <stdio.h>
#include <string.h>
#include <math.h>
#include "struct_oper.h"


double
Mod0_dbl (unsigned long NLoop,
	  const double *X,		/* en ... any */
	  double M,		/* en ... any  */
	  double *Z)
{
  unsigned long i;

  double offset;

  /* Calcul d'un offset sur le premier non-nul */
  i = 0;
  while ((X[i] == 0) && (i < NLoop))
    i++;
  offset = (double) (M * (floor (X[i] / M)));

  for (i = 0; i < NLoop; i++)
    {
      *Z = (*X) - offset;
      Z++;
      X++;
    }
  return offset;
}


/* la fonction d'enrobage classique */

int
OP_Mod0_dbl (unsigned long NbVal, void *ArgList[], char *DiagExec)
{
  double CodRet;
  int NCar;

  NCar = sprintf (DiagExec, "Mod0_dbl, NbVal=%lu", NbVal);
  if (NCar < 0)
    NCar = 0;
  DiagExec += NCar;

  CodRet = Mod0_dbl (NbVal, (double *) ArgList[0], *((double *) ArgList[1]), (double *) ArgList[2]);

  sprintf (DiagExec, "; Offset soustrait=%g", CodRet);

  return OP_OK;
}

void
ID_Mod0_dbl (oper * optr)
{
  strcpy (optr->Nom, "Mod0_dbl");
  optr->Version = "$Revision: 5568 $";
  optr->Date = "$Date: 2014-04-04 14:48:47 +0200 (ven. 04 avril 2014) $";
  optr->fctptr = OP_Mod0_dbl;
  optr->NbArg = 3;		/* doit rester inf. a FIL_MAX_ARG */

  optr->Arg_Car[0].direction = DIR_IN;
  optr->Arg_Car[0].categorie = VECTOR;
  optr->Arg_Car[0].typ = ATYC_IF64;
  optr->Arg_Car[0].array_dim = "1";
  optr->Arg_Car[0].type_sample = "any";
  optr->Arg_Car[0].sample = "any";
  optr->Arg_Car[0].unite = "any";

  optr->Arg_Car[1].direction = DIR_IN;
  optr->Arg_Car[1].categorie = COEFFICIENT;
  optr->Arg_Car[1].typ = ATYC_IF64;
  optr->Arg_Car[1].array_dim = "1";
  optr->Arg_Car[1].type_sample = "any";
  optr->Arg_Car[1].sample = "any";
  optr->Arg_Car[1].unite = "any";

  optr->Arg_Car[2].direction = DIR_OUT;
  optr->Arg_Car[2].categorie = VECTOR;
  optr->Arg_Car[2].typ = ATYC_IF64;
  optr->Arg_Car[2].array_dim = "1";
  optr->Arg_Car[2].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[2].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[2].sample = "$Arg1.sample";
  optr->Arg_Car[2].ref_time = "$Arg1.ref_time";
  optr->Arg_Car[2].unite = "$Arg1.unit";
  optr->Arg_Car[2].famille = "$Arg1.famille";

}
