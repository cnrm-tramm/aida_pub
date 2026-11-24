/****************************************************
*
* OPERATOR     Rotat_2D_rep_vent_moy.c   FUNCTION  ANSI-C
*
* PURPOSE      	Double rotation par appel de Rotat_rep_vent_moy avec un flag  supplementaire,
*               ajoute en 4eme argument et valant 0.
*
* DESCRIPTION  	Ce opérateur effectuent les rotations dans le repere d'un vent moyen defini sur des périodes
*		de temps consécutives définies par l'utilisateur.   
*
* VERSION       $Revision$
*
* ARGUMENTS  IN    float   u   any         East component, from West
*            IN    float   v   same as u   North component, from South
*	     IN	   float   w   same as u   Vertical component, from ground
*            IN    float   Fe   s-1	fréquence d'échantillonnage des données	
*            IN    float   Tint	s	Temps d'intégration pour le calcul du flux	
*            OUT   float   u_r same as u   Component along mean vector
*                                            (Positif forward)
*            OUT   float   v_r same as u   Component transverse to mean
*                                            vector axe (mean(v) = 0)
*            OUT   float   w_r same as u   Component transverse to mean
*                                             vector axe (>0 up)
*
* REFERENCES
*
*
* COPYRIGHT     Meteo-France
*
*#########################################################################*/

#define _POSIX_SOURCE 1
#define _XOPEN_SOURCE 600

#include <stdio.h>
#include <math.h>
#include <string.h>
#include <limits.h>
#include <stdlib.h>

#include "thermo.h"

#include "struct_oper.h"
#include "Rotat_rep_vent_moy.h"

/* La vraie fonction... */

int
Rotat_2D_rep_vent_moy (unsigned long Ndata,
		    const float *u,
		    const float *v,
		    const float *w,
		    const float Fe, const float Tint,
		    float *u_r, float *v_r, float *w_r)

{
  long k, ntour, nbpt;
  double info_tab[11];

/* Calcul du nombre de points sur lequels on va calculer */

  /*nb de points sur la periode demandee */
  nbpt = floor ((Tint * Fe) + 0.5);
  /*fprintf (stderr, " nbpt= %ld \n", nbpt); */

  if (nbpt <= 0)
    return -1;

  /*******Calcul du nombre de tours***/
  ntour = Ndata / nbpt;
  /*reste = Ndata % nbpt;*/

  for (k = 0; k < ntour; k++)
    {
      /*Appel de la fonction avec le flag a 0 */
      Rotat_rep_vent_moy (nbpt , u, v, w, 0, u_r, v_r, w_r, info_tab);
      u += nbpt; v += nbpt; w += nbpt;
      u_r += nbpt; v_r += nbpt; w_r += nbpt;
    }

  return k;
}

/* la fonction d'enrobage classique */

int
OP_Rotat_2D_rep_vent_moy (unsigned long NbVal, void *ArgList[], char *DiagExec)
{
  long CodRet;
  int NCar;

  NCar = sprintf (DiagExec, "Rotat_2D_rep_vent_moy : (%ld echant.) ", NbVal) ;
  if (NCar < 0)
    NCar = 0;
  DiagExec += NCar;

  CodRet = Rotat_2D_rep_vent_moy (NbVal,
		     (float *) ArgList[0],
		     (float *) ArgList[1],
		     (float *) ArgList[2],
		     *((float *) ArgList[3]),
		     *((float *) ArgList[4]),
		     (float *) ArgList[5],
		     (float *) ArgList[6],
		     (float *) ArgList[7]);
  if (CodRet >= 0)
    {
      sprintf (DiagExec, "OK: %ld val. calculées.", CodRet);
      return OP_OK;
    }
  switch (CodRet)
    {
    case -1:
      strcat (DiagExec, "; Nb resultats <= 0");
      return OP_FAIL;
    default:
      strcat (DiagExec, "; Erreur inattendue");
      return OP_FAIL;
    }

}

void
ID_Rotat_2D_rep_vent_moy (oper * optr)
{
  int i;

  strcpy (optr->Nom, "Rotat_2D_rep_vent_moy");
  optr->Version = "$Revision$";
  optr->Date = "$Date$";
  optr->fctptr = OP_Rotat_2D_rep_vent_moy;
  optr->NbArg = 8;
  optr->misval_auto = 1;

 /* u */
  optr->Arg_Car[0].direction = DIR_IN;
  optr->Arg_Car[0].categorie = VECTOR;
  optr->Arg_Car[0].typ = ATYC_IF32;
  optr->Arg_Car[0].array_dim = "1";
  optr->Arg_Car[0].type_sample = "any";
  optr->Arg_Car[0].sample = "any";
  optr->Arg_Car[0].unite = "any";
  optr->Arg_Car[0].famille = "any";

  /* v */
  optr->Arg_Car[1].direction = DIR_IN;
  optr->Arg_Car[1].categorie = VECTOR;
  optr->Arg_Car[1].typ = ATYC_IF32;
  optr->Arg_Car[1].array_dim = "1";
  optr->Arg_Car[1].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[1].type_sample = "any";
  optr->Arg_Car[1].sample = "any";
  optr->Arg_Car[1].unite = "$Arg1.unit";
  optr->Arg_Car[1].famille = "any";

  /* w */
  optr->Arg_Car[2].direction = DIR_IN;
  optr->Arg_Car[2].categorie = VECTOR;
  optr->Arg_Car[2].typ = ATYC_IF32;
  optr->Arg_Car[2].array_dim = "1";
  optr->Arg_Car[2].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[2].type_sample = "any";
  optr->Arg_Car[2].sample = "any";
  optr->Arg_Car[2].unite = "$Arg1.unit";
  optr->Arg_Car[2].famille = "any";

  /*Fe et Tint*/
  for (i = 3; i <= 4; i++)
    {
      optr->Arg_Car[i].direction = DIR_IN;
      optr->Arg_Car[i].categorie = COEFFICIENT;
      optr->Arg_Car[i].array_dim = "1";
      optr->Arg_Car[i].typ = ATYC_IF32;
      optr->Arg_Car[i].unite = "any";
      optr->Arg_Car[i].type_sample = NULL;
      optr->Arg_Car[i].sample = NULL;
    }

  /* u_r */
  optr->Arg_Car[5].direction = DIR_OUT;
  optr->Arg_Car[5].categorie = VECTOR;
  optr->Arg_Car[5].typ = ATYC_IF32;
  optr->Arg_Car[5].array_dim = "1";
  optr->Arg_Car[5].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[5].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[5].sample = "$Arg1.sample";
  optr->Arg_Car[5].ref_time = "$Arg1.ref_time";
  optr->Arg_Car[5].unite = "$Arg1.unit";
  optr->Arg_Car[5].famille = "$Arg1.famille";
  optr->Arg_Car[5].misval = "$Arg1.misval";
  optr->Arg_Car[7].name = "$Arg1.name +\" projete sur le vent moyen\"";

  /* v_r */
  optr->Arg_Car[6].direction = DIR_OUT;
  optr->Arg_Car[6].categorie = VECTOR;
  optr->Arg_Car[6].typ = ATYC_IF32;
  optr->Arg_Car[6].array_dim = "1";
  optr->Arg_Car[6].NbVal = "$Arg1.NbVal";
  /* l'unite et le sample se deduisent de l'entree  */
  optr->Arg_Car[6].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[6].sample = "$Arg1.sample";
  optr->Arg_Car[6].ref_time = "$Arg1.ref_time";
  optr->Arg_Car[6].unite = "$Arg1.unit";
  optr->Arg_Car[6].famille = "$Arg1.famille";
  optr->Arg_Car[6].misval = "$Arg1.misval";
  optr->Arg_Car[7].name = "$Arg2.name +\" projete transversalement au vent moyen\"";

  /* w_r */
  optr->Arg_Car[7].direction = DIR_OUT;
  optr->Arg_Car[7].categorie = VECTOR;
  optr->Arg_Car[7].typ = ATYC_IF32;
  optr->Arg_Car[7].array_dim = "1";
  optr->Arg_Car[7].NbVal = "$Arg1.NbVal";
  /* l'unite et le sample se deduisent de l'entree  */
  optr->Arg_Car[7].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[7].sample = "$Arg1.sample";
  optr->Arg_Car[7].ref_time = "$Arg1.ref_time";
  optr->Arg_Car[7].unite = "$Arg1.unit";
  optr->Arg_Car[7].famille = "$Arg1.famille";
  optr->Arg_Car[7].misval = "$Arg1.misval";

}
