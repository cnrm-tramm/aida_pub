/******************************************************************
*
* OPERATOR      Cor_inv_dens.c   FUNCTION  ANSI-C
*
* PURPOSE       Corrects various measurements by a rho0/rho factor.
*               This is typically needed when the pump regulating
*               the air flow in some microphysics probe ensures
*               a constant mass flow when a constant volume flow
*               is needed.
*
* DESCRIPTION   
*
* VERSION       $Revision$
*
* ARGUMENTS   IN   float  Var_brut  any            Raw measurement
*             IN   int    Dim_Var                  Dimension of input var.
*             IN   float  rho       kg/m3          Ambiant air density
*             OUT  float  Var_cor   idem Var_brut  Result
*
* ENTRY
*
* SUBPROGRAMS   none
*
* FILES
*
* REFERENCES
*
* CHANGES       
*
* COPYRIGHT     Meteo-France
*
* AGREEMENT     The author wishes that .....
*#########################################################################*/

#define _POSIX_SOURCE 1
#define _XOPEN_SOURCE 600

#include <stdio.h>
#include <string.h>
#include "struct_oper.h"

/* La vraie fonction... */
int
Cor_inv_dens (unsigned long NLoop,
	      const float *Var_brut,
	      const int Dim_Var_brut, const float *rho, float *Var_cor)
{
  unsigned long i;
  int j;
  double X;

  /* Rho_0 est la densité de l'air sec standard à 1013.5 hPa et 15.0 °C
   * Le standard ISO-2533 (atmosphère type, publié en 1975)
   * indique la valeur suivante, en kg m-3.  */
  float rho_0 = 1.22500;

  if ((Dim_Var_brut <= 0) || (Dim_Var_brut > 90000))
    return -1;

  for (i = 0; i < NLoop; i++)
    {
      X = rho_0 / *rho;
      for (j = 0; j < Dim_Var_brut; j++)
	{
	  *Var_cor = *Var_brut * X;

	  Var_brut++;
	  Var_cor++;
	}
      rho++;
    }
  return 0;
}


/* la fonction d'enrobage classique */

int
OP_Cor_inv_dens (unsigned long NbVal, void *ArgList[], char *DiagExec)
{
  int CodRet;

  (void) sprintf (DiagExec, "Cor_inv_dens (%ld ech de dim %d);",
		  NbVal, *((int *) ArgList[1]));

  CodRet = Cor_inv_dens (NbVal,
			 (float *) ArgList[0],
			 *((int *) ArgList[1]),
			 (float *) ArgList[2], (float *) ArgList[3]);

  switch (CodRet)
    {
    case -1:
      strcat (DiagExec, "Strange value for Dimension !!");
      return OP_FAIL;
    case 0:
      strcat (DiagExec, "OK;");
      return OP_OK;
    default:
      strcat (DiagExec, "Unexpected error");
      return OP_FAIL;
    }
}

/* la fonction de description de l'operateur et ses arguments */

void
ID_Cor_inv_dens (oper * optr)
{
  strcpy (optr->Nom, "Cor_inv_dens");
  optr->Version = "$Revision$";
  optr->Date = "$Date$";
  optr->fctptr = OP_Cor_inv_dens;
  optr->NbArg = 4;

  /*  Var_brut */
  optr->Arg_Car[0].direction = DIR_IN;
  optr->Arg_Car[0].categorie = VECTOR;
  optr->Arg_Car[0].typ = ATYC_IF32;
  optr->Arg_Car[0].array_dim = "any";
  optr->Arg_Car[0].type_sample = "any";
  optr->Arg_Car[0].sample = "any";
  optr->Arg_Car[0].unite = "any";
  optr->Arg_Car[0].famille = "any";

  /* Dim_Var_brut */
  optr->Arg_Car[1].direction = DIR_IN;
  optr->Arg_Car[1].categorie = COEFFICIENT;
  optr->Arg_Car[1].typ = ATYC_I32;
  optr->Arg_Car[1].array_dim = "";
  optr->Arg_Car[1].unite = "";
  optr->Arg_Car[1].famille = "";

  /*  rho */
  optr->Arg_Car[2].direction = DIR_IN;
  optr->Arg_Car[2].categorie = VECTOR;
  optr->Arg_Car[2].typ = ATYC_IF32;
  optr->Arg_Car[2].array_dim = "1";
  optr->Arg_Car[2].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[2].type_sample = "any";
  optr->Arg_Car[2].sample = "any";
  optr->Arg_Car[2].unite = "kg m-3";
  optr->Arg_Car[2].famille = "";

  /* Var_cor */
  optr->Arg_Car[3].direction = DIR_OUT;
  optr->Arg_Car[3].categorie = VECTOR;
  optr->Arg_Car[3].typ = ATYC_IF32;
  optr->Arg_Car[3].array_dim = "$Arg1.array_dim";
  optr->Arg_Car[3].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[3].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[3].sample = "$Arg1.sample";
  optr->Arg_Car[3].ref_time = "$Arg1.ref_time";
  optr->Arg_Car[3].unite = "$Arg1.unit";
  optr->Arg_Car[3].famille = "$Arg1.famille";
  optr->Arg_Car[3].bornes = "$Arg1.bornes";
  optr->Arg_Car[3].unit_bornes = "$Arg1.unit_bornes";
}
