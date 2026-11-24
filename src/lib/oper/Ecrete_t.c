/*********************************************************
* OPERATOR 	Ecrete_t.c FUNCTION ANSI-C
*
* PURPOSE       Detects period where the dew-point is 
*		greater than the static temperature.
*		It replace these values by temperature values
*               (todo :if the plane flies in cloud (LWC content ...) else these
*               values are replaced by invalids values..).
*
*	        Detecte les passages ou la valeur du Td est superieure a celle
*               de la temperature statique, remplace ces valeurs par celles de 
*               la temperature.
*		Un flag par defaut a 0 est initialise a 1 en cas d'ecretage.
*               (A faire : si la mesure est faite en nuage (contenu en eau 
*               liquide...) remplace ces valeurs par celles de la temperature 
*               sinon invalide-les).
*
* VERSION       $Revision$
*
* ARGUMENTS 	IN	float	td	dew-point temperature 
*		IN 	float 	ts 	static temperature
*
*		OUT 	int 	flag_t  state flag
*		OUT 	float 	td_cor  valid dewpoint  
*
* ENTRY		NONE
*
* SUBPROGRAMS 	NONE
* 
* REFERENCES	
*
* COPYRIGHT 	Meteo-France
*		Centre National de Recherches Meteorologiques
*		GMEI/TRAMM
*		42, av. G. Coriolis
* 		31057 	TOULOUSE cedex
*
************************************************************/

#define _POSIX_SOURCE 1
#define _XOPEN_SOURCE 600

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>

#include "struct_oper.h"

#include "thermo.h"

size_t
Ecrete_t (unsigned long Nloop,
	  const float *td, const float *ts, int *flag_t, float *td_cor)
{
  unsigned long i;
  size_t nb_ecrete = 0;

  float degK_td, degK_ts;

/*** conversion Celsius -> kelvin ***/

  degK_td = 0.;
  degK_ts = 0.;
  if (td[0] < 100.)
    degK_td = 273.15;
  if (ts[0] < 100.)
    degK_ts = 273.15;

  for (i = 0; i < Nloop; i++)
    {
      if ((td[i] + degK_td) > (ts[i] + degK_ts))
	{
	  td_cor[i] = ts[i];
	  flag_t[i] = 1;
          nb_ecrete++;
	}
      else
	{
	  td_cor[i] = td[i];
	  flag_t[i] = 0;
	}
    }

  return nb_ecrete;
}

/* fonction d'enrobage */

int
OP_Ecrete_t (unsigned long Nbval, void *ArgList[], char *DiagExec)
{
  size_t CodRet;
  int NCar;

  NCar = sprintf (DiagExec, "Ecrete_t, NbVal=%lu", Nbval);
  DiagExec += NCar;

  CodRet = Ecrete_t (Nbval,
		     (float *) ArgList[0],
		     (float *) ArgList[1],
		     (int *) ArgList[2],
                     (float *) ArgList[3]);

  (void) sprintf (DiagExec, " %lu échantillons ecretes", (unsigned long) CodRet);

  return OP_OK;
}

void
ID_Ecrete_t (oper * optr)
{
  strcpy (optr->Nom, "Ecrete_t");
  optr->Version = "$Revision$";
  optr->Date = "$Date$";
  optr->fctptr = OP_Ecrete_t;
  optr->NbArg = 4;

  /* td */
  optr->Arg_Car[0].direction = DIR_IN;
  optr->Arg_Car[0].categorie = VECTOR;
  optr->Arg_Car[0].typ = ATYC_IF32;
  optr->Arg_Car[0].array_dim = "1";
  optr->Arg_Car[0].type_sample = "any";
  optr->Arg_Car[0].sample = "any";
  optr->Arg_Car[0].unite = "K";

  /* ts */
  optr->Arg_Car[1].direction = DIR_IN;
  optr->Arg_Car[1].categorie = VECTOR;
  optr->Arg_Car[1].typ = ATYC_IF32;
  optr->Arg_Car[1].array_dim = "1";
  optr->Arg_Car[3].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[1].type_sample = "any";
  optr->Arg_Car[1].sample = "K";
  optr->Arg_Car[1].unite = "volt";

  /* flag_t */
  optr->Arg_Car[2].direction = DIR_OUT;
  optr->Arg_Car[2].categorie = VECTOR;
  optr->Arg_Car[2].typ = ATYC_I32;
  optr->Arg_Car[2].array_dim = "1";
  optr->Arg_Car[2].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[2].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[2].sample = "$Arg1.sample";
  optr->Arg_Car[2].ref_time = "$Arg1.ref_time";
  optr->Arg_Car[2].unite = "without";
  optr->Arg_Car[2].famille = "\"controle\"";
  optr->Arg_Car[2].misval = "$Arg1.misval";

  /* td_val */
  optr->Arg_Car[3].direction = DIR_OUT;
  optr->Arg_Car[3].categorie = VECTOR;
  optr->Arg_Car[3].typ = ATYC_IF32;
  optr->Arg_Car[3].array_dim = "1";
  optr->Arg_Car[3].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[3].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[3].sample = "$Arg1.sample";
  optr->Arg_Car[3].ref_time = " $Arg1.ref_time";
  optr->Arg_Car[3].unite = "$Arg1.unit";
  optr->Arg_Car[3].famille = "$Arg1.famille";
  optr->Arg_Car[3].misval = "$Arg1.misval";
}
