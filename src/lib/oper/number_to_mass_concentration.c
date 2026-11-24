/*************************************************
* OPERATOR 	number_to_mass_concentration.c 	FUNCTION ANSI-C
*
* PURPOSE	Calcul d'une concentration massique de particules (exprimés en µg/m3),
*               à partir d'un tableau de concentrations partielles en nombre (nb/cm3)
*               et d'un tableau des diamètres medians (typiquement, pour les
*               PCASP/SPP200, FSSP, OPC, ..).
*
* ARGUMENTS 	IN     float	Conc_tab 	Tableau des concentrations
*		IN     int      nb_classes      Nombre de classes.
*		IN     float 	midpoint_diam  	Tableau des "midpoint diameter"
*		IN     float 	Vol_mass  	Volumic mass of the aerosols (g/cm3)
*
*		OUT	float Conc	    rapport de melange en aerosols (µg/m3)
*		
* ENTRY		NONE
*
* SUBPROGRAMS 	NONE
*
* REFERENCE     
*
* COPYRIGHT	Meteo-France
*		Centre National de Recherches Meteorologiques
*		GMEI/TRAMM
*		42, av G. Coriolis 
*		31057	TOULOUSE cedex
*
*****************************************************************/

#define _POSIX_SOURCE 1
#define _XOPEN_SOURCE 600

#include <stdio.h>
#include <string.h>
#include <stdlib.h>

int
number_to_mass_concentration (unsigned long ndata,
			  float *Conc_tab,
			  int nb_classes,
			  float *midpoint_diam, float dens, float *conc)
{
  unsigned long i;
  int k;
  float dia;
  float *dia_cub;

  const float pi_sur_6 = 3.14159265358979323846 / 6.0;

  /* Petit pense-bête d'unité :
   *   les diamètres sont données en microns.
   *   La densite en g/cm3 (cm3 de matière)
   *   les concentrations en nb/cm3 (cm3 d'air).
   *
   *   1 g/cm3 = 1 mg/mm3 = 10-9 mg/µm3 = 10-6 µg/µm3
   *   
   *   Le calcul brut de volume a partir de µm donne des µm3.
   *   Il faut donc diviser par 10^6 le résultat de dens*volume
   *   pour avoir des µg. 
   *   Mais alors, ce sont des µg/cm3 (cm3 d'air).
   *   Il faut donc multiplier par un facteur 10^6 pour 
   *   arriver à des  µg/m3. 
   *   Ces deux facteurs se compensent donc exactement.
   *   */


  /* Prudence : vérification d'arguments. */
  if (nb_classes <= 0)
    return -1;

  if (nb_classes > 2048)
    return -2;

  dia_cub = malloc (sizeof (*dia_cub) * nb_classes);
  if (dia_cub == NULL)
    return -3;

  for (k = 0; k < nb_classes; k++)
    {
      dia = midpoint_diam[k];	/* microns */
      dia_cub[k] = dia * dia * dia;
    }

  for (i = 0; i < ndata; i++)
    {
      conc[i] = 0.0;
      for (k = 0; k < nb_classes; k++)
	{
	  conc[i] = conc[i] + dia_cub[k] * Conc_tab[i * nb_classes + k];
	}
      conc[i] = dens * pi_sur_6 * conc[i];	/* ug/m3 */
    }

  free (dia_cub);
  dia_cub = NULL;
  return 0;
}

/* fonction d'enrobage */
#include "struct_oper.h"

int
OP_number_to_mass_concentration (unsigned long NbVal, void *ArgList[],
			     char *DiagExec)
{
  int CodRet, nbchar;

  nbchar = sprintf (DiagExec,
		    "OP_number_to_mass_concentration, NbVal=%ld, Args=(%f, %d, [%g, ..], %g, ..)",
		    NbVal,
		    *((float *) ArgList[0]),
		    *((int *) ArgList[1]), *((float *) ArgList[2]),
		    *((float *) ArgList[3]));
  DiagExec += nbchar;

  CodRet = number_to_mass_concentration (NbVal,
				     (float *) ArgList[0],
				     *((int *) ArgList[1]),
				     (float *) ArgList[2],
				     *((float *) ArgList[3]),
				     (float *) ArgList[4]);

  switch (CodRet)
    {
    case 0:
      return OP_OK;
    case -1:
      sprintf (DiagExec, "Nb_classes (%d) <= 0 !", *((int *) ArgList[1]));
      return OP_FAIL;
    case -2:
      sprintf (DiagExec, "Nb_classes (%d) > 2048 !", *((int *) ArgList[1]));
      return OP_FAIL;
    case -3:
      sprintf (DiagExec, "probleme allocation memoire (%d classes)", *((int *) ArgList[1]));
      return OP_FAIL;
    default:
      sprintf (DiagExec, "Unexpected error");
      return OP_FAIL;
    }
}

void
ID_number_to_mass_concentration (oper * optr)
{
  strcpy (optr->Nom, "number_to_mass_concentration");
  optr->Version = "$Revision$";
  optr->Date = "$Date$";
  optr->fctptr = OP_number_to_mass_concentration;
  optr->NbArg = 5;

  /* Conc_tab */
  optr->Arg_Car[0].direction = DIR_IN;
  optr->Arg_Car[0].categorie = VECTOR;
  optr->Arg_Car[0].typ = ATYC_IF32;
  optr->Arg_Car[0].array_dim = "any";
  optr->Arg_Car[0].type_sample = "any";
  optr->Arg_Car[0].sample = "any";
  optr->Arg_Car[0].unite = "cm-3";

  /*  nb_classes  */
  optr->Arg_Car[1].direction = DIR_IN;
  optr->Arg_Car[1].categorie = COEFFICIENT;
  optr->Arg_Car[1].typ = ATYC_I32;
  optr->Arg_Car[1].array_dim = "1";
  optr->Arg_Car[1].type_sample = "";
  optr->Arg_Car[1].sample = "";
  optr->Arg_Car[1].unite = "";

  /* midpoint_diam */
  optr->Arg_Car[2].direction = DIR_IN;
  optr->Arg_Car[2].categorie = COEFFICIENT;
  optr->Arg_Car[2].typ = ATYC_IF32;
  optr->Arg_Car[2].array_dim = "$Arg1.array_dim";
  optr->Arg_Car[2].unite = "micron";

  /* dens */
  optr->Arg_Car[3].direction = DIR_IN;
  optr->Arg_Car[3].categorie = COEFFICIENT;
  optr->Arg_Car[3].typ = ATYC_IF32;
  optr->Arg_Car[3].array_dim = "1";
  optr->Arg_Car[3].unite = "gram/cm3";

  /* conc */
  optr->Arg_Car[4].direction = DIR_OUT;
  optr->Arg_Car[4].categorie = VECTOR;
  optr->Arg_Car[4].typ = ATYC_IF32;
  optr->Arg_Car[4].array_dim = "1";
  optr->Arg_Car[4].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[4].ref_time = "$Arg1.ref_time";
  optr->Arg_Car[4].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[4].sample = "$Arg1.sample";
  optr->Arg_Car[4].unite = "ugram/m3";
  optr->Arg_Car[4].famille = " \"microphysique\" ";
  optr->Arg_Car[4].name =
    " \"Concentration en masse a partir de \" + $Arg1.name";
  optr->Arg_Car[4].en_name = " \"Mass content from \" + $Arg1.name";
}
