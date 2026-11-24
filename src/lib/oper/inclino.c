/*************************************************************************
*
* OPERATOR         inclino.c  FUNCTION ANSI-C
*
* PURPOSE          opérateur de calcul des inclino en x et en y à partir des vecteurs bruts
*
* DESCRIPTION      
*
* VERSION          1.0 
*
* ARGUMENTS  
*            IN   ATYP_UI8    StaA       vecteur de données attitude
*            IN   ATYP_UI8    StaD       vecteur de données attitude

*            OUT  float      inclinox    vecteur inclinox
*            OUT  float      inclinoy    vecteur inclinoy
*            OUT  double     time_5      vecteur time_5
*
* ENTRY        NONE
*        
* SUBPROGRAMS  NONE
*        
* REFERENCES   
*
* COPYRIGHT    Meteo-France
*	       Centre National de Recherches Meteorologiques 
*	       GMEI/ TRAMM
*	       42, av G. Coriolis
*	       31057 TOULOUSE cedex  
*
*
*############################################################################*/

#define _POSIX_SOURCE 1
#define _XOPEN_SOURCE 600
#define _HPUX_SOURCE 1

#include <math.h>
#include <stdio.h>
#include <string.h>
#include <math.h>
#include "struct_oper.h"


unsigned long
inclino (unsigned long ndata,
	 const ATYP_UI8 * StaA,
	 const ATYP_UI8 * StaD,
	 float *inclinox,
         float *inclinoy,
         double *time_5)
{
  unsigned long i;
  unsigned long j;
  unsigned long j_max = ndata / 10;
  unsigned long k;
  short int tempox, tempoy;
  k = 0;
  j = 0;

  for (i = 0; i < ndata - 3; i++)
    {
      if ((StaA[i] == 7) && (StaA[i + 1] == 8) && (StaA[i + 2] == 9)
	  && (StaA[i + 3] == 10))
	{
	  tempox = 0;
	  tempoy = 0;

	  /*inclinox */
	  tempox = StaD[i];
	  tempox = tempox << 8;
	  tempox = tempox | StaD[i + 1];
	  inclinox[j] = tempox * 0.01;

	  /*inclinoy */
	  tempoy = StaD[i + 2];
	  tempoy = tempoy << 8;
	  tempoy = tempoy | StaD[i + 3];
	  inclinoy[j] = tempoy * 0.01;

	  /*time_5 */
	  time_5[j] = (double) i / 50.;

	  if (j < j_max)
	    j++;
	  k = 0;
	}
      else
	++k;

      if (k == 10)
	{
	  time_5[j] = (double) i / 50.;
	  inclinox[j] = K_NaN;
	  inclinoy[j] = K_NaN;
	  if (j < j_max)
	    j++;
	  k = 0;
	}
    }
  return j;
}


/* la fonction d'enrobage classique */

int
OP_inclino (unsigned long NbVal, void *ArgList[], char *DiagExec)
{
  unsigned long CodRet;
 
  CodRet = inclino (NbVal,
		    (ATYP_UI8 *) ArgList[0],
		    (ATYP_UI8 *) ArgList[1],
		    (float *) ArgList[2],
		    (float *) ArgList[3],
                    (double *) ArgList[4]);

  sprintf (DiagExec, "inclino, NbVal_in=%ld,  NbVal_out=%ld", NbVal, CodRet);

  return OP_OK;
}

void
ID_inclino (oper * optr)
{
  strcpy (optr->Nom, "inclino");
  optr->Version = "Revision:$";
  optr->Date = "$Date:$";
  optr->fctptr = OP_inclino;
  optr->NbArg = 5;		/* doit rester inf. a FIL_MAX_ARG */

  /* StaA */
  optr->Arg_Car[0].direction = DIR_IN;
  optr->Arg_Car[0].categorie = VECTOR;
  optr->Arg_Car[0].typ = ATYC_UI8;
  optr->Arg_Car[0].array_dim = "1";
  optr->Arg_Car[0].type_sample = "any";
  optr->Arg_Car[0].sample = "any";
  optr->Arg_Car[0].unite = "";

  /* StaD */
  optr->Arg_Car[1].direction = DIR_IN;
  optr->Arg_Car[1].categorie = VECTOR;
  optr->Arg_Car[1].typ = ATYC_UI8;
  optr->Arg_Car[1].array_dim = "1";
  optr->Arg_Car[1].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[1].type_sample = "any";
  optr->Arg_Car[1].sample = "any";
  optr->Arg_Car[1].unite = "";

  /* inclinox */
  optr->Arg_Car[2].direction = DIR_OUT;
  optr->Arg_Car[2].categorie = VECTOR;
  optr->Arg_Car[2].typ = ATYC_IF32;
  optr->Arg_Car[2].array_dim = "1";
  optr->Arg_Car[2].NbVal = "$Arg1.NbVal * 0.1";
  optr->Arg_Car[2].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[2].sample = "5";
  optr->Arg_Car[2].ref_time = " \"time_\" + 5";
  optr->Arg_Car[2].unite = "degree";
  /* la valeur de misval n'est volontairement pas implémentée
     fvb la mettra automatiquement */

  /* inclinoy */
  optr->Arg_Car[3].direction = DIR_OUT;
  optr->Arg_Car[3].categorie = VECTOR;
  optr->Arg_Car[3].typ = ATYC_IF32;
  optr->Arg_Car[3].array_dim = "1";
  optr->Arg_Car[3].NbVal = "$Arg1.NbVal * 0.1";
  optr->Arg_Car[3].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[3].sample = "5";
  optr->Arg_Car[3].ref_time = " \"time_\" + 5";
  optr->Arg_Car[3].unite = "degree";
  /* la valeur de misval n'est volontairement pas implémentée
     fvb la mettra automatiquement */

  /* time_5 */
  optr->Arg_Car[4].direction = DIR_OUT;
  optr->Arg_Car[4].categorie = VECTOR;
  optr->Arg_Car[4].typ = ATYC_IF64;
  optr->Arg_Car[4].array_dim = "1";
  optr->Arg_Car[4].NbVal = "$Arg1.NbVal * 0.1";
  optr->Arg_Car[4].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[4].sample = "5";
  optr->Arg_Car[4].ref_time = " \"time_\" + 5";
  optr->Arg_Car[4].unite = "second";
}
