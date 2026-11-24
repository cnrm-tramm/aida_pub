/*****************************************************
*
* OPERATOR         Module_tab_flt.c   FUNCTION  ANSI-C
*
* PURPOSE          Compute the module of a vector.
*
* DESCRIPTION      
*
* VERSION          $Revision: 4731 $
*
* ARGUMENTS  IN    float    X    any            
*   	     IN    int	    D                    Dimension of X
*            OUT   float    M    same as X       Module of the vector
*
*                                                
* ENTRY            NONE
*               
* SUBPROGRAMS      NONE
*
* FILES            NONE
*
* REFERENCES       
*
*
* CHANGES          None yet.
*
*
* COPYRIGHT        Meteo-France/CNRM
*
* AGREEMENT        
*########################################################################*/

#define _POSIX_SOURCE 1
#define _XOPEN_SOURCE 600
/* Le #define _HPUX_SOURCE est la pour utiliser la fonction isfinite */
#define _HPUX_SOURCE 1

#include <math.h>
#include <stdio.h>
#include <string.h>
#include "struct_oper.h"


int
Module_tab_flt (unsigned long NLoop, const float *X, int D, float *M)
{
  unsigned long i;
  int j;
  double loc_M;

  if (D <= 0)
    return -1;


  for (i = 0; i < NLoop; i++)
    {
      loc_M = 0.0;
      for (j = 0; j < D; j++)
	{
	  loc_M += (*X * *X);
	  X++;
	}
      *M = sqrt (loc_M);
      M++;
    }
  return 0;
}


/* la fonction d'enrobage classique */

int
OP_Module_tab_flt (unsigned long NbVal, void *ArgList[], char *DiagExec)
{
  int CodRet;

  (void) sprintf (DiagExec, "Module_tab_flt, NbVal=%lu, dim=%d", NbVal,
		  *((int *) ArgList[1]));

  CodRet = Module_tab_flt (NbVal,
			   (float *) ArgList[0],
			   *((int *) ArgList[1]), (float *) ArgList[2]);
  if (CodRet == 0)
    return OP_OK;
  else
    return OP_FAIL;
}

void
ID_Module_tab_flt (oper * optr)
{
  strcpy (optr->Nom, "Module_tab_flt");
  optr->Version = "$Revision: 4731 $";
  optr->Date = "$Date: 2012-08-21 18:25:57 +0200 (mar. 21 août 2012) $";
  optr->fctptr = OP_Module_tab_flt;
  optr->misval_auto = 1;	/* gestion auto des misval */
  optr->NbArg = 3;


  /* C1 */
  optr->Arg_Car[0].direction = DIR_IN;
  optr->Arg_Car[0].categorie = VECTOR;
  optr->Arg_Car[0].typ = ATYC_IF32;
  optr->Arg_Car[0].array_dim = "1";
  optr->Arg_Car[0].type_sample = "any";
  optr->Arg_Car[0].sample = "any";
  optr->Arg_Car[0].unite = "any";

  /* C2 */
  optr->Arg_Car[1].direction = DIR_IN;
  optr->Arg_Car[1].categorie = VECTOR;
  optr->Arg_Car[1].typ = ATYC_IF32;
  optr->Arg_Car[1].array_dim = "1";
  optr->Arg_Car[1].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[1].type_sample = "any";
  optr->Arg_Car[1].sample = "any";
  optr->Arg_Car[1].unite = "$Arg1.unit";

  /* M */
  optr->Arg_Car[2].direction = DIR_OUT;
  optr->Arg_Car[2].categorie = VECTOR;
  optr->Arg_Car[2].typ = ATYC_IF32;
  optr->Arg_Car[2].array_dim = "1";
  optr->Arg_Car[2].NbVal = "$Arg1.NbVal";
  /* l'unite et le sample se deduisent de l'entree  */
  optr->Arg_Car[2].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[2].sample = "$Arg1.sample";
  optr->Arg_Car[2].ref_time = "$Arg1.ref_time";
  optr->Arg_Car[2].misval = "$Arg1.misval";
  optr->Arg_Car[2].unite = "$Arg1.unit";
  optr->Arg_Car[2].famille = "$Arg1.famille";
  optr->Arg_Car[2].name = " \"Module de \" + $Arg1.name";
  optr->Arg_Car[2].en_name = " \"Module of \" + $Arg1.english_name";
}
