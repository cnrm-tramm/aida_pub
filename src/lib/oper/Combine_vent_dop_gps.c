/****************************************************
*
* OPERATOR      Combine_vent_dop_gps.c   FUNCTION  ANSI-C
*
* PURPOSE       Create a pair of composite vectors
*
* DESCRIPTION   Selects one of two winds depending on the value of a flag vector.
*
* VERSION       $Revision$
*
* ARGUMENTS   IN   float  flag_vent    Any           wind flag value
* 						     (simple or detailled)
*             IN   float  input_u_1    Any             first u_value
*             IN   float  input_v_1    Any             first v_value
*             IN   float  input_u_2    Any             first u_value
*             IN   float  input_v_2    Any             first v_value
*             OUT  float  output_1                     composite u_value 
*             OUT  float  output_2                     composite v_value 
*
* ENTRY            
*                 
* SUBPROGRAMS   none
*
* FILES   
*
* REFERENCES   
*
* CHANGES       1.1   le 06 septembre 2005
*
* COPYRIGHT     Meteo-France
*
* AGREEMENT     The author wishes that .....
*#########################################################################*/

#define _POSIX_SOURCE 1
#define _XOPEN_SOURCE 600
/* Le #define _HPUX_SOURCE n'est la que pour "voir" strdup */
#define _HPUX_SOURCE 1

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "struct_oper.h"


unsigned long
Combine_vent_dop_gps (unsigned long NLoop, const float *flag_vent,	/* en ... any */
		      const float *input_u_1,	/* en ... any */
		      const float *input_v_1,	/* en ... any  */
		      const float *input_u_2,	/* en meme unité que input_u_1 */
		      const float *input_v_2,	/* en meme unité que input_v_1 */
		      float *output_u, float *output_v)
{
  unsigned long i;
  unsigned long nb_bad_flag = 0;
  const float misval = -9999;

  for (i = 0; i < NLoop; i++)
    {
      switch ((int) *flag_vent)
	{
	case 1:		/* Simple flags vector */
	  {
	  }
	case 210:		/* Detailled flags vector */
	  {
	  }
	case 221:
	  {
	  }
	case 222:
	  {
	  }
	case 410:
	  {
	  }
	case 421:
	  {
	  }
	case 422:
	  {
	  }
	case 424:
	  {
	    *output_u = *input_u_1;
	    *output_v = *input_v_1;
	    break;
	  }
	case 2:
	  {
	  }
	case 310:
	  {
	  }
	case 321:
	  {
	  }
	case 322:
	  {
	  }
	case 423:
	  {
	    *output_u = *input_u_2;
	    *output_v = *input_v_2;
	    break;
	  }
	case 0:
	  {
	  }
	case 110:
	  {
	    *output_u = misval;
	    *output_v = misval;
	    break;
	  }
	default:
	  {
	    nb_bad_flag++;
	  }
	}
      flag_vent++;
      input_u_1++;
      input_v_1++;
      input_u_2++;
      input_v_2++;
      output_u++;
      output_v++;
    }

  return nb_bad_flag;
}


/* la fonction d'enrobage classique */

int
OP_Combine_vent_dop_gps (unsigned long NbVal, void *ArgList[], char *DiagExec)
{
  unsigned long CodRet;

  (void) sprintf (DiagExec, "Combine_vent_dop_gps, NbVal=%lu", NbVal);

  CodRet = Combine_vent_dop_gps (NbVal,
				 (float *) ArgList[0],
				 (float *) ArgList[1],
				 (float *) ArgList[2],
				 (float *) ArgList[3],
				 (float *) ArgList[4],
				 (float *) ArgList[5], (float *) ArgList[6]);

  if (CodRet != 0)
    {
      fprintf (stderr,
	       "Dans Combine_vent_dop_gps : %lu flag_vent non reconnu(s)",
	       CodRet);
    }
  return OP_OK;
}

void
ID_Combine_vent_dop_gps (oper * optr)
{
  strcpy (optr->Nom, "Combine_vent_dop_gps");
  optr->Version = "$Revision$";
  optr->Date = "$Date$";
  optr->fctptr = OP_Combine_vent_dop_gps;
  optr->NbArg = 7;		/* doit rester inf. a FIL_MAX_ARG */

  /* flag_vent */
  optr->Arg_Car[0].direction = DIR_IN;
  optr->Arg_Car[0].categorie = VECTOR;
  optr->Arg_Car[0].typ = ATYC_IF32;
  optr->Arg_Car[0].array_dim = "1";
  optr->Arg_Car[0].type_sample = "any";
  optr->Arg_Car[0].sample = "any";
  optr->Arg_Car[0].unite = "any";

  /* input_u_1 */
  optr->Arg_Car[1].direction = DIR_IN;
  optr->Arg_Car[1].categorie = VECTOR;
  optr->Arg_Car[1].typ = ATYC_IF32;
  optr->Arg_Car[1].array_dim = "1";
  optr->Arg_Car[1].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[1].type_sample = "any";
  optr->Arg_Car[1].sample = "any";
  optr->Arg_Car[1].unite = "any";

  /* input_v_1 */
  optr->Arg_Car[2].direction = DIR_IN;
  optr->Arg_Car[2].categorie = VECTOR;
  optr->Arg_Car[2].typ = ATYC_IF32;
  optr->Arg_Car[2].array_dim = "1";
  optr->Arg_Car[2].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[2].type_sample = "any";
  optr->Arg_Car[2].sample = "any";
  optr->Arg_Car[2].unite = "any";

  /* input_u_2 */
  optr->Arg_Car[3].direction = DIR_IN;
  optr->Arg_Car[3].categorie = VECTOR;
  optr->Arg_Car[3].typ = ATYC_IF32;
  optr->Arg_Car[3].array_dim = "1";
  optr->Arg_Car[3].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[3].type_sample = "any";
  optr->Arg_Car[3].sample = "any";
  optr->Arg_Car[3].unite = "any";

  /* input_v_2 */
  optr->Arg_Car[4].direction = DIR_IN;
  optr->Arg_Car[4].categorie = VECTOR;
  optr->Arg_Car[4].typ = ATYC_IF32;
  optr->Arg_Car[4].array_dim = "1";
  optr->Arg_Car[4].type_sample = "any";
  optr->Arg_Car[4].sample = "any";
  optr->Arg_Car[4].unite = "any";

  optr->Arg_Car[5].direction = DIR_OUT;
  optr->Arg_Car[5].categorie = VECTOR;
  optr->Arg_Car[5].typ = ATYC_IF32;
  optr->Arg_Car[5].array_dim = "1";
  optr->Arg_Car[5].NbVal = "$Arg2.NbVal";
  optr->Arg_Car[5].type_sample = "$Arg2.type_sample";
  optr->Arg_Car[5].sample = "$Arg2.sample";
  optr->Arg_Car[5].ref_time = "$Arg2.ref_time";
  optr->Arg_Car[5].unite = "$Arg2.unit";
  optr->Arg_Car[5].famille = "\"vent\"";
  optr->Arg_Car[5].misval = "$Arg2.misval";

  optr->Arg_Car[6].direction = DIR_OUT;
  optr->Arg_Car[6].categorie = VECTOR;
  optr->Arg_Car[6].typ = ATYC_IF32;
  optr->Arg_Car[6].array_dim = "1";
  optr->Arg_Car[6].NbVal = "$Arg3.NbVal";
  optr->Arg_Car[6].type_sample = "$Arg3.type_sample";
  optr->Arg_Car[6].sample = "$Arg3.sample";
  optr->Arg_Car[6].ref_time = "$Arg3.ref_time";
  optr->Arg_Car[5].unite = "$Arg3.unit";
  optr->Arg_Car[6].famille = "\"vent\"";
  optr->Arg_Car[6].misval = "$Arg3.misval";
}
