/*************************************************
* OPERATOR 	cdp_conc.c 	FUNCTION ANSI-C
*
* PURPOSE	Calcul de la concentration dans les classes
*		de mesure d'un CDP (OAP-200X).
*		On divise le comptage par un sampling volume
*               qui est le produit de la "real sampling area"
*		par la distance échantillonnée (vitesse/freq_ech).
*
* ARGUMENTS 	IN     float	Cnt_tab 	Tableau des comptages
*		IN     int      nb_classes    Nombre de classes.
*		IN     float*   SA      Tableau des "Sampling Areas"
*		IN     float 	vp	vitesse propre (m/s)
*		IN     int 	fr	frequence d'echantillonnage (Hz)
*
*		OUT    float 	conc	Tableau des concentration (cm-3)
*		
* ENTRY		NONE
*
* SUBPROGRAMS 	NONE
*
* REFERENCE     
*
* COPYRIGHT	Meteo-France
*		Centre National de Recherches Meteorologiques
*		GMEI/TRAMM+MNPCA
*		42, av G. Coriolis 
*		31057	TOULOUSE cedex
*
*****************************************************************/

#define _POSIX_SOURCE 1
#define _XOPEN_SOURCE 600
#define _HPUX_SOURCE 1
#define _XOPEN_SOURCE_EXTENDED 1

#include <stdio.h>
#include <string.h>
#include <math.h>

int
cdp_conc (unsigned long ndata,
	  float *Cnt_tab,
	  const int nb_classes,
	  float *SA, float *vp, float fr, float *Conc_tab)
{
  unsigned long i;
  int k;
  double sv;			/* Pour éviter les erreurs d'arrondi */

  /* Prudence : vérification d'arguments. */
  if (nb_classes <= 0)
    return -1;

  if (nb_classes > 1024)
    return -2;

  for (i = 0; i < ndata; i++)
    {
      if (vp[i] < 25.)
	{
	  for (k = 0; k < nb_classes; k++)
	    Conc_tab[i * nb_classes + k] = 0.;
	  continue;
	}
      for (k = 0; k < nb_classes; k++)
	{
	  sv = SA[k] * (vp[i] / fr);	/* mm2*m = cm3 */

	  if (sv > 0)
	    Conc_tab[i * nb_classes + k] = Cnt_tab[i * nb_classes + k] / sv;
	  else
	    Conc_tab[i * nb_classes + k] = 0.;
	}
    }
  return 0;
}

/* fonction d'enrobage */
#include "struct_oper.h"

int
OP_cdp_conc (unsigned long NbVal, void *ArgList[], char *DiagExec)
{
  int CodRet, k;
  int NCar;

  NCar = sprintf (DiagExec, "cdp_conc : (%ld echant.) ", NbVal) ;
  if (NCar < 0)
    NCar = 0;
  DiagExec += NCar;

  CodRet = cdp_conc (NbVal,
		     (float *) ArgList[0],
		     *((int *) ArgList[1]),
		     (float *) ArgList[2],
		     (float *) ArgList[3],
		     *((float *) ArgList[4]), (float *) ArgList[5]);

  switch (CodRet)
    {
    case 0:
      return OP_OK;
    case -1:
      sprintf (DiagExec, "Nb_classes (%d) <= 0 !!!", *((int *) ArgList[1]));
      return OP_FAIL;
    case -2:
      sprintf (DiagExec, "Nb_classes (%d) > 1024 !!!", *((int *) ArgList[1]));
      return OP_FAIL;
    default:
      sprintf (DiagExec, "Unexpected error");
      return OP_FAIL;
    }
}

void
ID_cdp_conc (oper * optr)
{
  strcpy (optr->Nom, "cdp_conc");
  optr->Version = "1.0";
  optr->Date = "03/19/04";
  optr->fctptr = OP_cdp_conc;
  optr->NbArg = 6;

  /* Cnt_tab */
  optr->Arg_Car[0].direction = DIR_IN;
  optr->Arg_Car[0].categorie = VECTOR;
  optr->Arg_Car[0].typ = ATYC_IF32;
  optr->Arg_Car[0].array_dim = "any";
  optr->Arg_Car[0].type_sample = "any";
  optr->Arg_Car[0].sample = "any";
  optr->Arg_Car[0].unite = "";

  /*  nb_classes  */
  optr->Arg_Car[1].direction = DIR_IN;
  optr->Arg_Car[1].categorie = COEFFICIENT;
  optr->Arg_Car[1].typ = ATYC_I32;
  optr->Arg_Car[1].array_dim = "1";
  optr->Arg_Car[1].type_sample = "";
  optr->Arg_Car[1].sample = "";
  optr->Arg_Car[1].unite = "";

  /* Sampling Area */
  optr->Arg_Car[2].direction = DIR_IN;
  optr->Arg_Car[2].categorie = COEFFICIENT;
  optr->Arg_Car[2].typ = ATYC_IF32;
  optr->Arg_Car[2].array_dim = "15";
  /* TODO : $Arg1.array_dim, ou $Arg2, ....*/
  optr->Arg_Car[2].unite = "";

  /*  vp  */
  optr->Arg_Car[3].direction = DIR_IN;
  optr->Arg_Car[3].categorie = VECTOR;
  optr->Arg_Car[3].typ = ATYC_IF32;
  optr->Arg_Car[3].array_dim = "1";
  optr->Arg_Car[3].type_sample = "";
  optr->Arg_Car[3].sample = "";
  optr->Arg_Car[3].unite = "m/s";

  /* fr : frequence échantillonnage */
  optr->Arg_Car[4].direction = DIR_IN;
  optr->Arg_Car[4].categorie = COEFFICIENT;
  optr->Arg_Car[4].typ = ATYC_IF32;
  optr->Arg_Car[4].array_dim = "1";
  optr->Arg_Car[4].direction = DIR_IN;
  optr->Arg_Car[4].array_dim = "1";
  optr->Arg_Car[4].type_sample = NULL;
  optr->Arg_Car[4].sample = NULL;
  optr->Arg_Car[4].unite = "Hz";

  /* Conc_tab */
  optr->Arg_Car[5].direction = DIR_OUT;
  optr->Arg_Car[5].categorie = VECTOR;
  optr->Arg_Car[5].typ = ATYC_IF32;
  optr->Arg_Car[5].array_dim = "$Arg1.array_dim";
  optr->Arg_Car[5].bornes = "$Arg1.bornes";
  optr->Arg_Car[5].unit_bornes = "$Arg1.unit_bornes";
  optr->Arg_Car[5].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[5].ref_time = "$Arg1.ref_time";
  optr->Arg_Car[5].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[5].sample = "$Arg1.sample";
  optr->Arg_Car[5].unite = "cm-3";
  optr->Arg_Car[5].famille = " \"microphysique\" ";
  optr->Arg_Car[5].name = "\"Concentration a partir de \"+ $Arg1.name";
  optr->Arg_Car[5].en_name = "\"Concentration from \"+ $Arg1.english_name";
}
