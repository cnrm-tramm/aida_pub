/*****************************************************
*
* OPERATOR         Rotat_uv.c   FUNCTION  ANSI-C
*
* PURPOSE          rotates GILL coordinates to geographic coordinates
*
* DESCRIPTION      Converts coordinates of a vector expressed in
*                  a GILL-anemometer referential to a Earth-related cartesian frame
*
* VERSION          1.1
*
* ARGUMENTS  IN   float   U        m/s      Component along GILL axe : u
*            IN   float   V        m/s      Component transverse to GILL axe : v
*            IN   float   offset   degree   Rotation angle between the two referentials, 
*            IN   float   flag     none     1.0 ou -1.0 ;  1.0 for direct referential (u,v,w)
*                                           -1.0 if not;  (-v,u,w) direct
* ARGUMENTS  OUT  float   UG       m/s      East component, from West
*            OUT  float   VG       m/s      North component, from South
*
* ENTRY            NONE
*               
* SUBPROGRAMS      NONE
*
* FILES            NONE
*
* REFERENCES       
*
*
* CHANGES          1.1  Initial version
*
* COPYRIGHT        Meteo-France/CNRM
*
* AGREEMENT        
*########################################################################*/

#define _POSIX_SOURCE 1
#define _XOPEN_SOURCE 600

#include <math.h>
#include <stdio.h>
#include <string.h>
#include "struct_oper.h"

int
Rotat_uv (unsigned long NLoop,
	  const float *U,
	  const float *V, float Offset, float flag, float *UG, float *VG)
{
  unsigned long i;
  register double coso, sino;
  register double Deg2Rad;
  register double Offset_rad;

  if (flag != 1.0 && flag != -1.0)
    return -1;

  /* entree de l'angle en degres, donc conversion en radians */
  Deg2Rad = M_PI / 180.0;

  /*il faut ajouter PI/2 a l'Offset qui est donne % au Nord et non % a l'Est */
  Offset_rad = Offset * Deg2Rad;
  coso = -sin (Offset_rad);
  sino = cos (Offset_rad);

  for (i = 0; i < NLoop; i++)
    {
      /*la formule classique :
         coso = cos (Offset_rad);
         sino = sin (Offset_rad);
         *UG  = flag * coso * *U - sino * *V;
         *VG  = flag * sino * *U + coso * *V; 
         devient : */

      *UG = flag * coso * *U - sino * *V;
      *VG = flag * sino * *U + coso * *V;

      UG++;
      VG++;
      U++;
      V++;
    }

  return 0;
}


/* la fonction d'enrobage classique */

int
OP_Rotat_uv (unsigned long NbVal, void *ArgList[], char *DiagExec)
{
  int CodRet;

  (void) sprintf (DiagExec, "Rotat_uv, NbVal=%lu, Angle=%g, flag=%g)",
		  NbVal, *(float *) ArgList[2], *(float *) ArgList[3]);

  CodRet = Rotat_uv (NbVal,
		     (float *) ArgList[0],
		     (float *) ArgList[1],
		     *(float *) ArgList[2],
		     *(float *) ArgList[3],
		     (float *) ArgList[4], (float *) ArgList[5]);
  if (CodRet == -1)
    {
      strcat (DiagExec, "flag (4eme arg) devrait être 1 ou -1");
      return OP_FAIL;
    }
  return OP_OK;
}

void
ID_Rotat_uv (oper * optr)
{
  strcpy (optr->Nom, "Rotat_uv");
  optr->Version = "$Revision$";
  optr->Date = "$Date$";
  optr->fctptr = OP_Rotat_uv;
  optr->NbArg = 6;

  /* U */
  optr->Arg_Car[0].direction = DIR_IN;
  optr->Arg_Car[0].categorie = VECTOR;
  optr->Arg_Car[0].typ = ATYC_IF32;
  optr->Arg_Car[0].array_dim = "1";
  optr->Arg_Car[0].type_sample = "any";
  optr->Arg_Car[0].sample = "any";
  optr->Arg_Car[0].unite = "any";
  optr->Arg_Car[0].famille = "any";

  /* V */
  optr->Arg_Car[1].direction = DIR_IN;
  optr->Arg_Car[1].categorie = VECTOR;
  optr->Arg_Car[1].typ = ATYC_IF32;
  optr->Arg_Car[1].array_dim = "1";
  optr->Arg_Car[1].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[1].type_sample = "any";
  optr->Arg_Car[1].sample = "any";
  optr->Arg_Car[1].unite = "$Arg1.unit";
  optr->Arg_Car[1].famille = "any";

  /* offset */
  optr->Arg_Car[2].direction = DIR_IN;
  optr->Arg_Car[2].categorie = COEFFICIENT;
  optr->Arg_Car[2].typ = ATYC_IF32;
  optr->Arg_Car[2].array_dim = "1";
  optr->Arg_Car[2].type_sample = NULL;
  optr->Arg_Car[2].sample = NULL;
  optr->Arg_Car[2].unite = "";

  /* flag */
  optr->Arg_Car[3].direction = DIR_IN;
  optr->Arg_Car[3].categorie = COEFFICIENT;
  optr->Arg_Car[3].typ = ATYC_IF32;
  optr->Arg_Car[3].array_dim = "1";
  optr->Arg_Car[3].type_sample = NULL;
  optr->Arg_Car[3].sample = NULL;
  optr->Arg_Car[3].unite = "";

  /* UG */
  optr->Arg_Car[4].direction = DIR_OUT;
  optr->Arg_Car[4].categorie = VECTOR;
  optr->Arg_Car[4].typ = ATYC_IF32;
  optr->Arg_Car[4].array_dim = "1";
  optr->Arg_Car[4].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[4].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[4].sample = "$Arg1.sample";
  optr->Arg_Car[4].ref_time = "$Arg1.ref_time";
  optr->Arg_Car[4].unite = "$Arg1.unit";
  optr->Arg_Car[4].famille = "$Arg1.famille";
  optr->Arg_Car[4].misval = "$Arg1.misval";

  /* VG */
  optr->Arg_Car[5].direction = DIR_OUT;
  optr->Arg_Car[5].categorie = VECTOR;
  optr->Arg_Car[5].typ = ATYC_IF32;
  optr->Arg_Car[5].array_dim = "1";
  optr->Arg_Car[5].NbVal = "$Arg1.NbVal";
  /* l'unite et le sample se deduisent de l'entree  */
  optr->Arg_Car[5].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[5].sample = "$Arg1.sample";
  optr->Arg_Car[5].ref_time = "$Arg1.ref_time";
  optr->Arg_Car[5].unite = "$Arg1.unit";
  optr->Arg_Car[5].famille = "$Arg1.famille";
  optr->Arg_Car[5].misval = "$Arg1.misval";
}
