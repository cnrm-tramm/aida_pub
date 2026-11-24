/*********************************************************
* OPERATOR 	valid_td.c FUNCTION ANSI-C
*
* PURPOSE       Detect period where the dew-point sensor 
*		searchs the balance.
*		It replace these values by invalids values. 
*
*	        Detecte les passages ou le capteur a point
*		de rosee est en phase de recherche d'equilibre
*		Remplace ces valeurs par des valeurs invalides.
*
* VERSION       $Revision$
*
* ARGUMENTS 	IN	float	td	dew-point temperature 
*		IN 	float	vpel	dew-point Peltier voltage
*		IN 	float 	ts 	static temperature
*		IN	float 	vpel_inf Peltier voltage minimum value   
*		IN 	float 	vpel_sup Peltier voltage maximum value
*		IN 	float 	inv_val	 invalid value 	
*
*		OUT 	float 	td_valid valid dewpoint  
*
* ENTRY		NONE
*
* SUBPROGRAMS 	NONE
* 
* REFERENCES	
*
* COPYRIGHT 	Meteo-France
*		Centre National de Recherches Meteorologiques
*		GMEI/MMA
*		42, av. G. Coriolis
* 		31057 	TOULOUSE cedex
*
************************************************************/

#define _POSIX_SOURCE 1
#define _XOPEN_SOURCE 600
/* Le #define _HPUX_SOURCE n'est la que pour "voir" strdup */
#define _HPUX_SOURCE 1

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>

#include "struct_oper.h"


int
valid_td (unsigned long Nloop,
	  const float *td,
	  const float *vpel,
	  const float *ts,
	  const float vpel_inf,
	  const float vpel_sup,
	  const float inv_val,
	  float *td_valid)
{
  unsigned long i;

/***********************************************************
   Td est considere bon si ces criteres sont verifies :
   	1) vpel_inf < Tension Peltier < vpel_sup
   	2) Td+eps_td < Td  (actuellement ignoré)
************************************************************/

  for (i = 0; i < Nloop; i++)
    {

      if ((vpel[i] > vpel_sup) || (vpel[i] < vpel_inf))
/*
   || ((td[i] + degK_td + eps_td) > (ts[i] + degK_ts)) )
 */
	{
	  td_valid[i] = inv_val;
	}
      else
	{
	  td_valid[i] = td[i];
	}
    }

  return 0;
}

/* fonction d'enrobage */

int
OP_valid_td (unsigned long Nbval, void *ArgList[], char *DiagExec)
{
  int CodRet;

  (void) sprintf (DiagExec, "valid_td, %lu echant.;", Nbval);

  CodRet = valid_td (Nbval,
		     (float *) ArgList[0],
		     (float *) ArgList[1],
		     (float *) ArgList[2],
		     *((float *) ArgList[3]),
		     *((float *) ArgList[4]),
		     *((float *) ArgList[5]),
		     (float *) ArgList[6]);

  return OP_OK;
}
void
ID_valid_td (oper * optr)
{
  strcpy (optr->Nom, "valid_td");
  optr->Version = "$Revision$";
  optr->Date = "$Date$";
  optr->fctptr = OP_valid_td;
  optr->repl_oper = "select_X_selon_Y";
  optr->repl_cause = "";
  optr->NbArg = 7;

  /* td */
  optr->Arg_Car[0].direction = DIR_IN;
  optr->Arg_Car[0].categorie = VECTOR;
  optr->Arg_Car[0].typ = ATYC_IF32;
  optr->Arg_Car[0].array_dim = "1";
  optr->Arg_Car[0].type_sample = "any";
  optr->Arg_Car[0].sample = "any";
  optr->Arg_Car[0].unite = "K";

  /* vpel */
  optr->Arg_Car[1].direction = DIR_IN;
  optr->Arg_Car[1].categorie = VECTOR;
  optr->Arg_Car[1].typ = ATYC_IF32;
  optr->Arg_Car[1].array_dim = "1";
  optr->Arg_Car[1].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[1].type_sample = "any";
  optr->Arg_Car[1].sample = "any";
  optr->Arg_Car[1].unite = "any";

  /* Actuellement inutilisé...*/
  optr->Arg_Car[2].direction = DIR_IN;
  optr->Arg_Car[2].categorie = VECTOR;
  optr->Arg_Car[2].typ = ATYC_IF32;
  optr->Arg_Car[2].array_dim = "1";
  optr->Arg_Car[2].type_sample = "any";
  optr->Arg_Car[2].sample = "any";
  optr->Arg_Car[2].unite = "K";

  /* vpel_inf */
  optr->Arg_Car[3].direction = DIR_IN;
  optr->Arg_Car[3].categorie = COEFFICIENT;
  optr->Arg_Car[3].typ = ATYC_IF32;
  optr->Arg_Car[3].array_dim = "1";
  optr->Arg_Car[3].unite = "$Arg2.unit";

  /* vpel_sup */
  optr->Arg_Car[4].direction = DIR_IN;
  optr->Arg_Car[4].categorie = COEFFICIENT;
  optr->Arg_Car[4].typ = ATYC_IF32;
  optr->Arg_Car[4].array_dim = "1";
  optr->Arg_Car[4].unite = "$Arg2.unit";

  /* inv_val */
  optr->Arg_Car[5].direction = DIR_IN;
  optr->Arg_Car[5].categorie = COEFFICIENT;
  optr->Arg_Car[5].typ = ATYC_IF32;
  optr->Arg_Car[5].array_dim = "1";
  optr->Arg_Car[5].type_sample = NULL;
  optr->Arg_Car[5].sample = NULL;
  optr->Arg_Car[5].unite = "without";

  /* td_valid */
  optr->Arg_Car[6].direction = DIR_OUT;
  optr->Arg_Car[6].categorie = VECTOR;
  optr->Arg_Car[6].typ = ATYC_IF32;
  optr->Arg_Car[6].array_dim = "1";
  optr->Arg_Car[6].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[6].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[6].sample = "$Arg1.sample";
  optr->Arg_Car[6].ref_time = " $Arg1.ref_time";
  optr->Arg_Car[6].unite = "$Arg1.unit";
  optr->Arg_Car[6].famille = "$Arg1.famille";
  optr->Arg_Car[6].misval = "$Arg6";
  optr->Arg_Car[6].name = "$Arg1.name + \"valide\"";
  optr->Arg_Car[6].en_name = "\"Validated\" $Arg1.english_name";
}
