/*************************************************************************
*
* OPERATOR         choix_vent_app.c  FUNCTION ANSI-C
*
* PURPOSE          Fabrication d'un vecteur vent apparent unique pour DD et FF à partir de deux
*		   capteurs anémo-girouette.
*
* DESCRIPTION      - on élimine la girouette 2 si la direction supérieure à 171° ou 
*		   inférieure à -178°(la correction des -180 degrés due à l'inversion du montage des
*		   girouettes ayant préalablement été faite ) (voir histogramme des zones mortes des
*                  girouettes)
*		   - on choisit l'ensemble anémo-girouette qui est au vent c'est à dire:
*                    dd1/ff1 étant à babord et dd2/ff2 étant à tribord,
*                    si dd1 > 0 on choisit la girouette 2
*                    si dd1 < 0 on choisit la girouette 1
*		   - par vent de face on choisit l'ensemble anémo-girouette qui mesure la force du
*		   vent la plus élevée
* 
*
*
* VERSION          1.0 
*
* ARGUMENTS  
*            IN   float   dd1     degrés  vecteur direction vent apparent babord
*            IN   float   ff1     kt      vecteur force vent apparent babord
*            IN   float   dd2     degrés  vecteur direction vent apparent tribord
*            IN   float   ff2     kt      vecteur force vent apparent tribord
*
*            OUT  float   dd_ap   degrés  vecteur final direction vent apparent
*            OUT  float   ff_ap   kt      vecteur final force vent apparent
*            
*
* ENTRY        NONE
*        
* SUBPROGRAMS  NONE
*        
* REFERENCES   campagne FETCH
*
* COPYRIGHT    Meteo-France
*	       Centre National de Recherches Meteorologiques 
*	       GMEI/ MMA
*	       42, av G. Coriolis
*	       31057 TOULOUSE cedex  
*
*
*############################################################################*/

#define _POSIX_SOURCE 1
#define _XOPEN_SOURCE 600
#define _HPUX_SOURCE 1
#define _XOPEN_SOURCE_EXTENDED 1

#include <math.h>
#include <stdio.h>
#include <string.h>
#include <math.h>
#include "struct_oper.h"

unsigned long
choix_vent_app (unsigned long ndata,
		const float *dd1,
		const float *ff1,
		const float *dd2,
		const float *ff2,
		float zone_morte_sup,
		float zone_morte_inf,
                float *dd_ap,
                float *ff_ap)
{
  unsigned long i;
  unsigned long nb_morte = 0;

  for (i = 0; i < ndata; i++)
    {
      if ((dd2[i] >= zone_morte_sup) || (dd2[i] <= zone_morte_inf)
	  || (!isfinite (dd2[i])))
	{
	  dd_ap[i] = dd1[i];
	  ff_ap[i] = ff1[i];
	  nb_morte += 1;
	}
      else
	{
	  if ((dd1[i] > 0) || (!isfinite (dd1[i])))
	    {
	      dd_ap[i] = dd2[i];
	      ff_ap[i] = ff2[i];
	    }
	  else if (dd1[i] < 0)
	    {
	      dd_ap[i] = dd1[i];
	      ff_ap[i] = ff1[i];
	    }
	  else if (dd1[i] == 0)
	    {
	      if (ff1[i] < ff2[i])
		{
		  dd_ap[i] = dd2[i];
		  ff_ap[i] = ff2[i];
		}
	      else
		{
		  dd_ap[i] = dd1[i];
		  ff_ap[i] = ff1[i];
		}
	    }
	}
    }
  return nb_morte;
}


/* la fonction d'enrobage classique */

int
OP_choix_vent_app (unsigned long NbVal, void *ArgList[], char *DiagExec)
{
  const float zone_morte_sup = 171;
  const float zone_morte_inf = -178;
  unsigned long CodRet;

  CodRet = choix_vent_app (NbVal,
			   (float *) ArgList[0],
			   (float *) ArgList[1],
			   (float *) ArgList[2],
			   (float *) ArgList[3],
			   zone_morte_sup,
			   zone_morte_inf,
			   (float *) ArgList[4],
                           (float *) ArgList[5]);

  sprintf (DiagExec, "%lu elimine (<%g ou >%g)", CodRet, zone_morte_inf,
	   zone_morte_sup);

  return OP_OK;
}

void
ID_choix_vent_app (oper * optr)
{
  strcpy (optr->Nom, "choix_vent_app");
  optr->Version = "1.0";
  optr->Date = "$Date: 2015-10-12 18:18:35 +0200 (lun. 12 oct. 2015) $";
  optr->fctptr = OP_choix_vent_app;
  optr->NbArg = 6;		/* doit rester inf. a FIL_MAX_ARG */

  /* dd1 */
  optr->Arg_Car[0].direction = DIR_IN;
  optr->Arg_Car[0].categorie = VECTOR;
  optr->Arg_Car[0].typ = ATYC_IF32;
  optr->Arg_Car[0].array_dim = "1";
  optr->Arg_Car[0].type_sample = "any";
  optr->Arg_Car[0].sample = "any";
  optr->Arg_Car[0].unite = "degre";

  /* ff1 */
  optr->Arg_Car[1].direction = DIR_IN;
  optr->Arg_Car[1].categorie = VECTOR;
  optr->Arg_Car[1].typ = ATYC_IF32;
  optr->Arg_Car[1].array_dim = "1";
  optr->Arg_Car[1].type_sample = "any";
  optr->Arg_Car[1].sample = "any";
  optr->Arg_Car[1].unite = "kt";

  /* dd2 */
  optr->Arg_Car[2].direction = DIR_IN;
  optr->Arg_Car[2].categorie = VECTOR;
  optr->Arg_Car[2].typ = ATYC_IF32;
  optr->Arg_Car[2].array_dim = "1";
  optr->Arg_Car[2].type_sample = "any";
  optr->Arg_Car[2].sample = "any";
  optr->Arg_Car[2].unite = "degre";

  /* ff2 */
  optr->Arg_Car[3].direction = DIR_IN;
  optr->Arg_Car[3].categorie = VECTOR;
  optr->Arg_Car[3].typ = ATYC_IF32;
  optr->Arg_Car[3].array_dim = "1";
  optr->Arg_Car[3].type_sample = "any";
  optr->Arg_Car[3].sample = "any";
  optr->Arg_Car[3].unite = "$Arg2.unit";

  optr->Arg_Car[4].direction = DIR_OUT;
  optr->Arg_Car[4].categorie = VECTOR;
  optr->Arg_Car[4].typ = ATYC_IF32;
  optr->Arg_Car[4].array_dim = "1";
  optr->Arg_Car[4].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[4].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[4].sample = "$Arg1.sample";
  optr->Arg_Car[4].ref_time = "$Arg1.ref_time";
  optr->Arg_Car[4].unite = "$Arg1.unit";
  optr->Arg_Car[4].famille = " \"vent\" ";

  optr->Arg_Car[5].direction = DIR_OUT;
  optr->Arg_Car[5].categorie = VECTOR;
  optr->Arg_Car[5].typ = ATYC_IF32;
  optr->Arg_Car[5].array_dim = "1";
  optr->Arg_Car[5].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[5].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[5].sample = "$Arg1.sample";
  optr->Arg_Car[5].ref_time = "$Arg1.ref_time";
  optr->Arg_Car[5].unite = "$Arg2.unit";
  optr->Arg_Car[5].famille = " \"vent\" ";
  optr->Arg_Car[5].misval = "$Arg1.misval";

}
