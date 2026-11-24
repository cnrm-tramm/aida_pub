/****************************************************
*
* OPERATOR      Set_reftime.c   FUNCTION  ANSI-C
*
* PURPOSE       Change le champ ref_time du header
*
* DESCRIPTION   
*
* VERSION       $Revision: 4731 $
*
* ARGUMENTS   IN   float  X    	      any        Original data
*             IN   double time        second  	 new reftime 
*             IN   int    size_time   any        Nb de valeurs dans la base de temps time
*             OUT  float  Y    	      same as X 
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
#include "struct_oper.h"

/* La vraie fonction... */

long
Set_reftime (unsigned long NbVal,
     float *X,
     float *time_new ,
     unsigned long size_time,
     float *Y)
{
  long i;

  if ( NbVal != size_time )
  {
      (void) fprintf (stderr, "Taille Vecteur IN et vecteur temps de taille differente %d - %d)\n",
		      NbVal, size_time) ;
      return OP_FAIL;
  }

  for (i =0 ; i < NbVal; i++)
    {
     Y[i] = X[i];
    }
  return(0);
}

/* la fonction d'enrobage classique */

int
OP_Set_reftime (unsigned long NbVal, void *ArgList[], char *DiagExec)
{
  long CodRet;
  int NCar;

  CodRet = Set_reftime (NbVal,
		(float *) ArgList[0],
		(float *) ArgList[1],
		*((unsigned long *) ArgList[2]),
		(float *) ArgList[3]);

  return (CodRet);
}

void
ID_Set_reftime (oper * optr)
{
  strcpy (optr->Nom, "Set_reftime");
  optr->Version = "$Revision: 4731 $";
  optr->Date = "$Date: 2012-08-21 18:25:57 +0200 (mar. 21 août 2012) $";
  optr->fctptr = OP_Set_reftime;
  optr->NbArg = 4;
  optr->Arg_Car[0].direction = DIR_IN;
  optr->Arg_Car[0].categorie = VECTOR;
  optr->Arg_Car[0].typ = ATYC_IF32;
  optr->Arg_Car[0].array_dim = "1";
  optr->Arg_Car[0].type_sample = "any";
  optr->Arg_Car[0].sample = "any";
  optr->Arg_Car[0].unite = "any";
  optr->Arg_Car[0].famille = "any";

  optr->Arg_Car[1].direction = DIR_IN;
  optr->Arg_Car[1].categorie = VECTOR;
  optr->Arg_Car[1].array_dim = "1";
  optr->Arg_Car[1].typ = ATYC_IF64;
  optr->Arg_Car[1].unite = "any";
  optr->Arg_Car[1].type_sample = NULL;
  optr->Arg_Car[1].sample = NULL;

  optr->Arg_Car[2].direction = DIR_IN;
  optr->Arg_Car[2].categorie = COEFFICIENT;
  optr->Arg_Car[2].typ = ATYC_LOCAL_ULONG;
  optr->Arg_Car[2].array_dim = "1";
  optr->Arg_Car[2].type_sample = "any";
  optr->Arg_Car[2].sample = "any";
  optr->Arg_Car[2].unite = "";


  optr->Arg_Car[3].direction = DIR_OUT;
  optr->Arg_Car[3].categorie = VECTOR;
  optr->Arg_Car[3].typ = ATYC_IF32;
  optr->Arg_Car[3].array_dim = "1";
  optr->Arg_Car[3].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[3].sample = "$Arg1.sample";
  optr->Arg_Car[3].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[3].name = "$Arg1.name + \" corrige du decalage et derive dans le temps.\"";
  optr->Arg_Car[3].en_name = "$Arg1.english_name + \" corrected for offset and drift over time.\"";
  optr->Arg_Car[3].ref_time = "$Arg2.nom";
  optr->Arg_Car[3].unite = "$Arg1.unit";
  optr->Arg_Car[3].famille = "$Arg1.famille";
}
