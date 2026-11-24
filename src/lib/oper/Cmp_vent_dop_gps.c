/****************************************************
*
* OPERATOR      Cmp_vent_dop_gps.c   FUNCTION  ANSI-C
*
* PURPOSE       Compute tests to determine the wind quality.
*
* DESCRIPTION   Checks plausible range for values, and compute a flag
*
* VERSION       $Revision$
*
* ARGUMENTS   IN   float  Ve		Composante est de la vitesse GPS
*             IN   float  Vn		Composante nord de la vitesse GPS
*             IN   float  Vx		Composante longitudinale de la vitesse GPS
*             IN   float  Vy		Composante ransversale de la vitesse GPS
*             IN   float  Vp		Vitesse propre
*             IN   float  V_sol_dop	Vitesse sol Doppler
*             IN   float  V_sol_gps	Vitesse sol gps
*             IN   float  maxVp		Vp max (coefficient)
*             IN   float  maxVent	Vent max (coefficient)
*             OUT  float  output_1      detailled wind quality flags
*             OUT  float  output_1      simple wind quality flags
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

#include <stdio.h>
#include <string.h>
#include <math.h>

#ifndef PI
#define PI        3.1415926535897932384
#endif
#define DEGRAD    (PI / 180.0)


#include "struct_oper.h"


int
Teste_Val_gps_dop (float Ve,
		   float Vn,
		   float Vx,
		   float Vy,
		   float maxModVit,
		   float minVx, float maxVx, float minVy, float maxVy)
/*------------------------------*/
{
  int Tgps, Tdop;
  float module_vit_gps;

  module_vit_gps = sqrt (Ve * Ve + Vn * Vn);

  if (module_vit_gps <= maxModVit)
    Tgps = 1;
  else
    Tgps = 0;
  if (((Vx > minVx) && (Vx < maxVx)) && ((Vy > minVy) && (Vy < maxVy)))
    Tdop = 1;
  else
    Tdop = 0;

  return Tgps * 2 + Tdop + 1;
}

int
Teste_Vp_Vsol (float Vp, float Vsol, float seuil_Vp_Vsol)
/*----------------------------------------------------------*/
{
  if (fabs (Vp - Vsol) < seuil_Vp_Vsol)
    return 1;
  else
    return 0;
}

int
Cmp_Vp_Vsol_dop_gps (float Vp, float Vsol_dop, float Vsol_gps,
		     float seuil_Vp_Vsol)
{
  int TVp_Vsol_dop, TVp_Vsol_gps;

  TVp_Vsol_dop = Teste_Vp_Vsol (Vp, Vsol_dop, seuil_Vp_Vsol);
  TVp_Vsol_gps = Teste_Vp_Vsol (Vp, Vsol_gps, seuil_Vp_Vsol);

  return 2 *  TVp_Vsol_gps + TVp_Vsol_dop + 1;
}


int
Teste_val_dans_gamme (float Val, float borne_min, float borne_max)
{
  if ((borne_min < Val) && (Val < borne_max))
    {
      return 1;
    }
  else
    {
      return 0;
    }
}

void
Cmp_vent_dop_gps (unsigned long NLoop, const float *Ve,	/* GPS ... any */
		  const float *Vn,	/* GPS ... any */
		  const float *Vx,	/* Dopp ... any */
		  const float *Vy,	/* Dopp ... any */
		  const float *Vp,	/* en ... any */
		  const float *Vsol_dop,	/* en ... any */
		  const float *Vsol_gps,	/* en ... any  */
		  const float maxVp,	/* en ... any  */
		  const float maxModVit,	/* en ... any  */
		  const float maxVy,	/* en ... any  */
		  float *output_1, float *output_2)
/*-------------------------------------------------------------*/
{
  unsigned long i;
  float seuil_Vp_Vsol;
  float minVx, maxVx, minVy;
  int Flag_gps_dop, TestVp;
  int TVp_Vsol, TVp_Vsol_dop, TVp_Vsol_gps;
  float minVp;

  seuil_Vp_Vsol = 15.;		/* (Vp - Vsol) tolérée. */
  minVx = -2.;
  maxVx = maxVy;
  minVy = -1. * maxVy;
  Flag_gps_dop = -1;
  TestVp = -1;
  TVp_Vsol = -1;
  TVp_Vsol_dop = -1;
  TVp_Vsol_gps = -1;
  minVp = -2;

  for (i = 0; i < NLoop; i++)
    {
      /* Test de validité de la vitesse GPS et de la vitesse Doppler
         Si module de Vgps <= 125 m/s alors Tgps = 1 sinon Tgps = 0
         Si -2 < Vx < 47 et -47 < Vy < 47 alors Tdop = 1 sinon Tdop = 0

         Tgps = 0 et Tdop = 0 => Flag_gps_dop = 1
         Tgps = 0 et Tdop = 1 => Flag_gps_dop = 2
         Tgps = 1 et Tdop = 0 => Flag_gps_dop = 3
         Tgps = 1 et Tdop = 1 => Flag_gps_dop = 4 */


      Flag_gps_dop = Teste_Val_gps_dop (*Ve, *Vn, *Vx, *Vy,
					maxModVit,
					minVx, maxVx, minVy, maxVy);
      switch (Flag_gps_dop)
	{
	case 1:
	  *output_1 = 110;
	  *output_2 = 0;
	  break;
	case 2:
	  TestVp = Teste_val_dans_gamme (*Vp, minVp, maxVp);
	  if (TestVp)
	    {
	      TVp_Vsol_dop = Teste_Vp_Vsol (*Vp, *Vsol_dop, seuil_Vp_Vsol);
	      switch (TVp_Vsol_dop)
		{
		case 0:
		  *output_1 = 221;
		  *output_2 = 1;
		  break;
		case 1:
		  *output_1 = 222;
		  *output_2 = 1;
		  break;
		default:
		  fprintf (stderr,
			   "+++ Cmp_vent_dop_gps : problème retour de la fonction Teste_Vp_Vsol(..., dop ,%f)=%d\n", seuil_Vp_Vsol,TVp_Vsol_dop);
		  break;
		}
	    }
	  else
	    {
	      *output_1 = 210;
	      *output_2 = 1;
	    }
	  break;
	case 3:
	  TestVp = Teste_val_dans_gamme (*Vp, minVp, maxVp);
	  if (TestVp)
	    {
	      TVp_Vsol_gps = Teste_Vp_Vsol (*Vp, *Vsol_gps, seuil_Vp_Vsol);
	      switch (TVp_Vsol_gps)
		{
		case 0:
		  *output_1 = 321;
		  *output_2 = 2;
		  break;
		case 1:
		  *output_1 = 322;
		  *output_2 = 2;
		  break;
		default:
		  fprintf (stderr,
			   "+++ Cmp_vent_dop_gps : problème retour de la fonction Teste_Vp_Vsol(..., gps ,%f)=%d\n", seuil_Vp_Vsol,TVp_Vsol_gps);
		  break;
		}
	    }
	  else
	    {
	      *output_1 = 310;
	      *output_2 = 2;
	    }
	  break;
	case 4:
	  TestVp = Teste_val_dans_gamme (*Vp, minVp, maxVp);
	  if (TestVp)
	    {
	      TVp_Vsol =
		Cmp_Vp_Vsol_dop_gps (*Vp, *Vsol_dop, *Vsol_gps,
				     seuil_Vp_Vsol);
	      switch (TVp_Vsol)
		{
		case 1:
		  *output_1 = 421;
		  *output_2 = 1;
		  break;
		case 2:
		  *output_1 = 422;
		  *output_2 = 1;
		  break;
		case 3:
		  *output_1 = 423;
		  *output_2 = 2;
		  break;
		case 4:
		  *output_1 = 424;
		  *output_2 = 1;
		  break;
		default:
		  fprintf (stderr,
			   "+++ Cmp_vent_dop_gps : problème retour de la fonction Teste_Vp_Vsol_dop_gps(..., dop, gps , %f)=%d\n", seuil_Vp_Vsol,TVp_Vsol);
		  break;
		}
	    }
	  else
	    {
	      *output_1 = 410;
	      *output_2 = 1;
	    }
	  break;
	default:
	  fprintf (stderr,
		   "+++ %s : problème retour de la fonction Teste_Val_gps_dop()\n",
                   __FILE__);
	  break;
	}
      {
	/* Ecart par rapport à Vp */

	Ve++;
	Vn++;
	Vx++;
	Vy++;
	Vp++;
	Vsol_dop++;
	Vsol_gps++;
	output_1++;
	output_2++;
      }
    }
}



/* la fonction d'enrobage classique */

int
OP_Cmp_vent_dop_gps (unsigned long NbVal, void *ArgList[], char *DiagExec)
{
  float maxVp = *((float *) ArgList[7]);
  float maxVent = *((float *) ArgList[8]);
  float maxModVit = maxVp + maxVent;
  float maxVy = maxVent + sin (5 * DEGRAD) * maxVp;

  (void) sprintf (DiagExec,
		  "Cmp_vent_dop_gps, NbVal=%lu, Max Vp = %f , Max Vent = %f, Max module vitesse GPS = %f, Max Vy = %f\n",
		  NbVal,
		  *((float *) ArgList[7]),
		  *((float *) ArgList[8]), maxModVit, maxVy);

  Cmp_vent_dop_gps (NbVal,
		    (float *) ArgList[0],
		    (float *) ArgList[1],
		    (float *) ArgList[2],
		    (float *) ArgList[3],
		    (float *) ArgList[4],
		    (float *) ArgList[5],
		    (float *) ArgList[6],
		    maxVp,
		    maxModVit,
		    maxVy, (float *) ArgList[9], (float *) ArgList[10]);
  return OP_OK;
}

void
ID_Cmp_vent_dop_gps (oper * optr)
{
  strcpy (optr->Nom, "Cmp_vent_dop_gps");
  optr->Version = "$Revision$";
  optr->Date = "$Date$";
  optr->fctptr = OP_Cmp_vent_dop_gps;
  optr->NbArg = 11;		/* doit rester inf. a FIL_MAX_ARG */

  /* Ve	Composante est de la vitesse GPS */
  optr->Arg_Car[0].direction = DIR_IN;
  optr->Arg_Car[0].categorie = VECTOR;
  optr->Arg_Car[0].typ = ATYC_IF32;
  optr->Arg_Car[0].array_dim = "1";
  optr->Arg_Car[0].type_sample = "any";
  optr->Arg_Car[0].sample = "any";
  optr->Arg_Car[0].unite = "any";

  /* Vn	Composante nord de la vitesse GPS */
  optr->Arg_Car[1].direction = DIR_IN;
  optr->Arg_Car[1].categorie = VECTOR;
  optr->Arg_Car[1].typ = ATYC_IF32;
  optr->Arg_Car[1].array_dim = "1";
  optr->Arg_Car[1].type_sample = "any";
  optr->Arg_Car[1].sample = "any";
  optr->Arg_Car[1].unite = "any";
  /*  le mieux serait :
     optr->Arg_Car[1].unite = "$Arg1.unit"; */

  optr->Arg_Car[2].direction = DIR_IN;
  optr->Arg_Car[2].categorie = VECTOR;
  optr->Arg_Car[2].typ = ATYC_IF32;
  optr->Arg_Car[2].array_dim = "1";
  optr->Arg_Car[2].type_sample = "any";
  optr->Arg_Car[2].sample = "any";
  optr->Arg_Car[2].unite = "any";

  optr->Arg_Car[3].direction = DIR_IN;
  optr->Arg_Car[3].categorie = VECTOR;
  optr->Arg_Car[3].typ = ATYC_IF32;
  optr->Arg_Car[3].array_dim = "1";
  optr->Arg_Car[3].type_sample = "any";
  optr->Arg_Car[3].sample = "any";
  optr->Arg_Car[3].unite = "any";

  optr->Arg_Car[4].direction = DIR_IN;
  optr->Arg_Car[4].categorie = VECTOR;
  optr->Arg_Car[4].typ = ATYC_IF32;
  optr->Arg_Car[4].array_dim = "1";
  optr->Arg_Car[4].type_sample = "any";
  optr->Arg_Car[4].sample = "any";
  optr->Arg_Car[4].unite = "any";

  optr->Arg_Car[5].direction = DIR_IN;
  optr->Arg_Car[5].categorie = VECTOR;
  optr->Arg_Car[5].typ = ATYC_IF32;
  optr->Arg_Car[5].array_dim = "1";
  optr->Arg_Car[5].type_sample = "any";
  optr->Arg_Car[5].sample = "any";
  optr->Arg_Car[5].unite = "any";

  optr->Arg_Car[6].direction = DIR_IN;
  optr->Arg_Car[6].categorie = VECTOR;
  optr->Arg_Car[6].typ = ATYC_IF32;
  optr->Arg_Car[6].array_dim = "1";
  optr->Arg_Car[6].type_sample = "any";
  optr->Arg_Car[6].sample = "any";
  optr->Arg_Car[6].unite = "any";

  optr->Arg_Car[7].direction = DIR_IN;
  optr->Arg_Car[7].categorie = COEFFICIENT;
  optr->Arg_Car[7].typ = ATYC_IF32;
  optr->Arg_Car[7].array_dim = "1";
  optr->Arg_Car[7].type_sample = NULL;
  optr->Arg_Car[7].sample = NULL;
  optr->Arg_Car[7].unite = "m/s";

  optr->Arg_Car[8].direction = DIR_IN;
  optr->Arg_Car[8].categorie = COEFFICIENT;
  optr->Arg_Car[8].typ = ATYC_IF32;
  optr->Arg_Car[8].array_dim = "1";
  optr->Arg_Car[8].type_sample = NULL;
  optr->Arg_Car[8].sample = NULL;
  optr->Arg_Car[8].unite = "m/s";

  optr->Arg_Car[9].direction = DIR_OUT;
  optr->Arg_Car[9].categorie = VECTOR;
  optr->Arg_Car[9].typ = ATYC_IF32;
  optr->Arg_Car[9].array_dim = "1";
  optr->Arg_Car[9].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[9].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[9].sample = "$Arg1.sample";
  optr->Arg_Car[9].ref_time = "$Arg1.ref_time";
  optr->Arg_Car[9].unite = "nihil";
  optr->Arg_Car[9].famille = "\"vent\"";
  optr->Arg_Car[9].misval = "$Arg1.misval";

  optr->Arg_Car[10].direction = DIR_OUT;
  optr->Arg_Car[10].categorie = VECTOR;
  optr->Arg_Car[10].typ = ATYC_IF32;
  optr->Arg_Car[10].array_dim = "1";
  optr->Arg_Car[10].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[10].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[10].sample = "$Arg1.sample";
  optr->Arg_Car[10].ref_time = "$Arg1.ref_time";
  optr->Arg_Car[10].unite = "nihil";
  optr->Arg_Car[10].famille = "\"vent\"";
  optr->Arg_Car[10].misval = "$Arg1.misval";
}
