/******************************************************************
*
* OPERATOR      Cor_flow_dist.c   FUNCTION  ANSI-C
*
* PURPOSE       Application d'une correction de distortion d'ecoulement
*               aux composantes du vent mesurees par le sonique
*
* DESCRIPTION   calcul de l'angle de deformation en fonction de l'angle d'incidence 
*               mesure i_m et de l'azimuth, puis rotation du vent pour supprimer
*               l'effet spatial de la deformation, puis calcul d'un coefficient 
*               de correction par application d'un polynome de deux variables (i_m et
*               direction du vent / bateau) et application de ce coefficient
*               aux composantes du vent
*
* VERSION       2.2
*
* ARGUMENTS   IN   float  UU         Any          composante longitudinale.
*             IN   float  VV         Any          composante transversale.
*             IN   float  WW         Any          composante w verticale.
*             IN   float  DD         degree       Azimut
*             IN   float  A_min      Any          mini de la gamme d'application de DD
*             IN   float  A_max      Any          maxi de la gamme d'application de DD
*             IN   float  i_m       degree        angle d'incidence
*             IN   float  B_min      Any          mini de la gamme d'application de i_m
*             IN   float  B_max      Any          maxi de la gamme d'application de i_m
*             IN   float  Coef_z_DD_2     Any        coefficient of DD^2
*             IN   float  Coef_z_im_2     Any        coefficient of im^2
*             IN   float  Coef_z_im_1     Any        coefficient of im
*             IN   float  Coef_z_0_DD        Any        constant coefficient
*             IN   float  Coef_z_0_im        Any        constant coefficient
*             IN   float  Coef_ang_DD_6     Any          coefficient of DD^6
*             IN   float  Coef_ang_DD_4     Any          coefficient of DD^4
*             IN   float  Coef_ang_DD_2     Any          coefficient of DD^2
*             IN   float  Coef_ang_im_2     Any          coefficient of im^2
*             IN   float  Coef_ang_im_1     Any          coefficient of im
*             IN   float  Coef_ang_0_DD        Any          constant coefficient
*             IN   float  Coef_ang_0_im        Any          constant coefficient
*
*             OUT  float  UU_cor   same as 1      composante long. corrigee 
*             OUT  float  VV_cor   same as 1      composante trans. corrigee
*             OUT  float  WW_cor   same as 1      composante vert. corrigee
*
* ENTRY
*
* SUBPROGRAMS   none
*
* FILES
*
* REFERENCES
*
* CHANGES       3
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
unsigned long
Cor_flow_dist (unsigned long NLoop,
	      const float *UU,
	      const float *VV,
	      const float *WW,
	      const float *DD,
	      const float min_DD,
	      const float max_DD,
	      const float *i_m,
	      const float min_im,
	      const float max_im,
	      const float z2_DD,
	      const float z2_im,
	      const float z1_im,
	      const float z0_DD,
	      const float z0_im,
	      const float A6_DD,
	      const float A4_DD,
	      const float A2_DD,
	      const float A2_im,
	      const float A1_im,
	      const float A0_DD,
	      const float A0_im,
	      float *UU_cor,
	      float *VV_cor,
	      float *WW_cor)
{
  unsigned long i;
  double dir, inc, coef_cor_inc, coef_cor_mod, uu1, vv1, ww1, uu2, vv2, ww2;
  double a_phi, a_im, alfa_phi, alfa_im; 

    
  for ( i = 0; i < NLoop; i++ )
    {
      dir = DD[i];
      inc = i_m[i];
      if (dir > 180.0)
	dir -= 360.0;
      else if (dir < -180.0)
	dir += 360.0;

      if  ( ( dir < min_DD ) || ( dir > max_DD ) )  
	{
	a_phi = 1.0;
	alfa_phi = 2.0;
	}
      else
	{
/*	a_phi = z0_DD + dir * dir * z2_DD;  */
/*      alfa_phi = A0_DD + dir * dir * (A2_DD + dir * dir * A4_DD + dir * dir * dir * dir *A6_DD); */
	a_phi = 1.0;
        alfa_phi = 2.0;
	}

      if ( inc < min_im )
	{
	  a_im = 1.00;
	  alfa_im = 2.0;  
	}
      else if ( inc > max_im )
	{
	a_im = 1.0;  	 
	alfa_im = 2.0;
	}
      else
	{
/*	a_im = z0_im + inc * (z1_im + inc * z2_im); */
/*      alfa_im = A0_im + inc * ( A1_im + inc * A2_im); */
	a_im = 1.0;
        alfa_im = 2.0;
	}

      coef_cor_mod = a_phi * a_im / 1.00;
      coef_cor_inc = alfa_phi * alfa_im / 2.0;

      uu1 = cos( dir * 3.1415 /180.) * UU[i] - sin( dir * 3.1415/180.) * VV[i];
      vv1 = sin( dir * 3.1415 /180.) * UU[i] + cos( dir * 3.1415/180.) * VV[i];
      ww1 = WW[i];

      uu2 = (cos (coef_cor_inc * 3.1415 / 180.) * uu1 - sin (coef_cor_inc * 3.1415 / 180.) * ww1) * coef_cor_mod;
      vv2 = vv1 * coef_cor_mod;
      ww2 = (sin (coef_cor_inc * 3.1415 / 180.) * uu1 + cos (coef_cor_inc * 3.1415 / 180.) * ww1) * coef_cor_mod;

      UU_cor[i] = cos( dir * 3.1415 /180.) * uu2 + sin( dir * 3.1415/180.) * vv2;
      VV_cor[i] = -sin( dir * 3.1415 /180.) * uu2  + cos( dir * 3.1415/180.) * vv2;
      WW_cor[i] = ww2;
    }
  return i;
}


/* la fonction d'enrobage classique */

int
OP_Cor_flow_dist (unsigned long NbVal, void *ArgList[], char *DiagExec)
{
  unsigned long CodRet;
  int NCar;

  NCar = sprintf (DiagExec, "Cor_flow_dist : (%ld echant.) ", NbVal) ;
  if (NCar < 0)
    NCar = 0;
  DiagExec += NCar;


/*
 * Le lecteur attentif aura remarqué que l'argument Nr 3
 * n'est pas passé à la routine de calcul. En fait, il ne sert
 * qu'à remplir le champ "unit" du vecteur de sortie.
 */
  CodRet = Cor_flow_dist (NbVal,
			 (float *) ArgList[0],
			 (float *) ArgList[1],
			 (float *) ArgList[2],
			 (float *) ArgList[3],
			 *((float *) ArgList[4]),
			 *((float *) ArgList[5]),
			 (float *) ArgList[6],
			 *((float *) ArgList[7]),
			 *((float *) ArgList[8]),
			 *((float *) ArgList[9]),
			 *((float *) ArgList[10]),
			 *((float *) ArgList[11]),
			 *((float *) ArgList[12]),
			 *((float *) ArgList[13]),
			 *((float *) ArgList[14]),
			 *((float *) ArgList[15]),
			 *((float *) ArgList[16]),
			 *((float *) ArgList[17]),
			 *((float *) ArgList[18]),
			 *((float *) ArgList[19]),
			 *((float *) ArgList[20]),
			 (float *) ArgList[21],
			 (float *) ArgList[22],
			 (float *) ArgList[23]);
  if (CodRet == NbVal)
    return OP_OK;
  else
    return OP_FAIL;
}

/* la fonction de description de l'operateur et ses arguments */

void
ID_Cor_flow_dist (oper * optr)
{
  strcpy (optr->Nom, "Cor_flow_dist");
  optr->Version = "2.3";
  optr->Date = "12/02/02";
  optr->fctptr = OP_Cor_flow_dist;
  optr->NbArg = 24;
  /* UU */
  optr->Arg_Car[0].direction = DIR_IN;
  optr->Arg_Car[0].categorie = VECTOR;
  optr->Arg_Car[0].typ = ATYC_IF32;
  optr->Arg_Car[0].array_dim = "1";
  optr->Arg_Car[0].type_sample = "any";
  optr->Arg_Car[0].sample = "any";
  optr->Arg_Car[0].unite = "any";

  /* VV */
  optr->Arg_Car[1].direction = DIR_IN;
  optr->Arg_Car[1].categorie = VECTOR;
  optr->Arg_Car[1].typ = ATYC_IF32;
  optr->Arg_Car[1].array_dim = "1";
  optr->Arg_Car[1].type_sample = "any";
  optr->Arg_Car[1].sample = "any";
  optr->Arg_Car[1].unite = "any";

  /* WW */
  optr->Arg_Car[2].direction = DIR_IN;
  optr->Arg_Car[2].categorie = VECTOR;
  optr->Arg_Car[2].typ = ATYC_IF32;
  optr->Arg_Car[2].array_dim = "1";
  optr->Arg_Car[2].type_sample = "any";
  optr->Arg_Car[2].sample = "any";
  optr->Arg_Car[2].unite = "any";

  /* DD */
  optr->Arg_Car[3].direction = DIR_IN;
  optr->Arg_Car[3].categorie = VECTOR;
  optr->Arg_Car[3].typ = ATYC_IF32;
  optr->Arg_Car[3].array_dim = "1";
  optr->Arg_Car[3].type_sample = "any";
  optr->Arg_Car[3].sample = "any";
  optr->Arg_Car[3].unite = "degree";

  /* MIN_DD */
  optr->Arg_Car[4].direction = DIR_IN;
  optr->Arg_Car[4].categorie = COEFFICIENT;
  optr->Arg_Car[4].array_dim = "1";
  optr->Arg_Car[4].typ = ATYC_IF32;
  optr->Arg_Car[4].type_sample = NULL;	/* sans signification pour COEFFICIENT */
  optr->Arg_Car[4].sample = NULL;
  optr->Arg_Car[4].unite = "any";

  /* MAX_DD */
  optr->Arg_Car[5].direction = DIR_IN;
  optr->Arg_Car[5].categorie = COEFFICIENT;
  optr->Arg_Car[5].array_dim = "1";
  optr->Arg_Car[5].typ = ATYC_IF32;
  optr->Arg_Car[5].type_sample = NULL;		/* sans signification pour COEFFICIENT */
  optr->Arg_Car[5].sample = NULL;
  optr->Arg_Car[5].unite = "any";

  /* i_m*/
  optr->Arg_Car[6].direction = DIR_IN;
  optr->Arg_Car[6].categorie = VECTOR;
  optr->Arg_Car[6].typ = ATYC_IF32;
  optr->Arg_Car[6].array_dim = "1";
  optr->Arg_Car[6].type_sample = "any";
  optr->Arg_Car[6].sample = "any";
  optr->Arg_Car[6].unite = "degree";

  /* MIN_im */
  optr->Arg_Car[7].direction = DIR_IN;
  optr->Arg_Car[7].categorie = COEFFICIENT;
  optr->Arg_Car[7].array_dim = "1";
  optr->Arg_Car[7].typ = ATYC_IF32;
  optr->Arg_Car[7].type_sample = NULL;	/* sans signification pour COEFFICIENT */
  optr->Arg_Car[7].sample = NULL;
  optr->Arg_Car[7].unite = "any";

  /* MAX_im */
  optr->Arg_Car[8].direction = DIR_IN;
  optr->Arg_Car[8].categorie = COEFFICIENT;
  optr->Arg_Car[8].array_dim = "1";
  optr->Arg_Car[8].typ = ATYC_IF32;
  optr->Arg_Car[8].type_sample = NULL;		/* sans signification pour COEFFICIENT */
  optr->Arg_Car[8].sample = NULL;
  optr->Arg_Car[8].unite = "any";

  /* z2_DD */
  optr->Arg_Car[9].direction = DIR_IN;
  optr->Arg_Car[9].categorie = COEFFICIENT;
  optr->Arg_Car[9].array_dim = "1";
  optr->Arg_Car[9].typ = ATYC_IF32;
  optr->Arg_Car[9].type_sample = NULL;	/* sans signification pour COEFFICIENT */
  optr->Arg_Car[9].sample = NULL;
  optr->Arg_Car[9].unite = "any";

  /* z2_im */
  optr->Arg_Car[10].direction = DIR_IN;
  optr->Arg_Car[10].categorie = COEFFICIENT;
  optr->Arg_Car[10].array_dim = "1";
  optr->Arg_Car[10].typ = ATYC_IF32;
  optr->Arg_Car[10].type_sample = NULL;	/* sans signification pour COEFFICIENT */
  optr->Arg_Car[10].sample = NULL;
  optr->Arg_Car[10].unite = "any";

  /* z1_im */
  optr->Arg_Car[11].direction = DIR_IN;
  optr->Arg_Car[11].categorie = COEFFICIENT;
  optr->Arg_Car[11].array_dim = "1";
  optr->Arg_Car[11].typ = ATYC_IF32;
  optr->Arg_Car[11].type_sample = NULL;	/* sans signification pour COEFFICIENT */
  optr->Arg_Car[11].sample = NULL;
  optr->Arg_Car[11].unite = "any";

  /* z0_DD */
  optr->Arg_Car[12].direction = DIR_IN;
  optr->Arg_Car[12].categorie = COEFFICIENT;
  optr->Arg_Car[12].array_dim = "1";
  optr->Arg_Car[12].typ = ATYC_IF32;
  optr->Arg_Car[12].type_sample = NULL;	/* sans signification pour COEFFICIENT */
  optr->Arg_Car[12].sample = NULL;
  optr->Arg_Car[12].unite = "any";

  /* z0_im */
  optr->Arg_Car[13].direction = DIR_IN;
  optr->Arg_Car[13].categorie = COEFFICIENT;
  optr->Arg_Car[13].array_dim = "1";
  optr->Arg_Car[13].typ = ATYC_IF32;
  optr->Arg_Car[13].type_sample = NULL;	/* sans signification pour COEFFICIENT */
  optr->Arg_Car[13].sample = NULL;
  optr->Arg_Car[13].unite = "any";

  /* A6_DD */
  optr->Arg_Car[14].direction = DIR_IN;
  optr->Arg_Car[14].categorie = COEFFICIENT;
  optr->Arg_Car[14].array_dim = "1";
  optr->Arg_Car[14].typ = ATYC_IF32;
  optr->Arg_Car[14].type_sample = NULL;  /* sans signification pour COEFFICIENT */
  optr->Arg_Car[14].sample = NULL;
  optr->Arg_Car[14].unite = "any";

  /* A4_DD */
  optr->Arg_Car[15].direction = DIR_IN;
  optr->Arg_Car[15].categorie = COEFFICIENT;
  optr->Arg_Car[15].array_dim = "1";
  optr->Arg_Car[15].typ = ATYC_IF32;
  optr->Arg_Car[15].type_sample = NULL;	/* sans signification pour COEFFICIENT */
  optr->Arg_Car[15].sample = NULL;
  optr->Arg_Car[15].unite = "any";

  /* A2_DD */
  optr->Arg_Car[16].direction = DIR_IN;
  optr->Arg_Car[16].categorie = COEFFICIENT;
  optr->Arg_Car[16].array_dim = "1";
  optr->Arg_Car[16].typ = ATYC_IF32;
  optr->Arg_Car[16].type_sample = NULL;		/* sans signification pour COEFFICIENT */
  optr->Arg_Car[16].sample = NULL;
  optr->Arg_Car[16].unite = "any";

  /* A2_im */
  optr->Arg_Car[17].direction = DIR_IN;
  optr->Arg_Car[17].categorie = COEFFICIENT;
  optr->Arg_Car[17].array_dim = "1";
  optr->Arg_Car[17].typ = ATYC_IF32;
  optr->Arg_Car[17].type_sample = NULL;		/* sans signification pour COEFFICIENT */
  optr->Arg_Car[17].sample = NULL;
  optr->Arg_Car[17].unite = "any";

  /* A1_im */
  optr->Arg_Car[18].direction = DIR_IN;
  optr->Arg_Car[18].categorie = COEFFICIENT;
  optr->Arg_Car[18].array_dim = "1";
  optr->Arg_Car[18].typ = ATYC_IF32;
  optr->Arg_Car[18].type_sample = NULL;		/* sans signification pour COEFFICIENT */
  optr->Arg_Car[18].sample = NULL;
  optr->Arg_Car[18].unite = "any";

  /* A0_DD */
  optr->Arg_Car[19].direction = DIR_IN;
  optr->Arg_Car[19].categorie = COEFFICIENT;
  optr->Arg_Car[19].array_dim = "1";
  optr->Arg_Car[19].typ = ATYC_IF32;
  optr->Arg_Car[19].type_sample = NULL;		/* sans signification pour COEFFICIENT */
  optr->Arg_Car[19].sample = NULL;
  optr->Arg_Car[19].unite = "any";

  /* A0_im */
  optr->Arg_Car[20].direction = DIR_IN;
  optr->Arg_Car[20].categorie = COEFFICIENT;
  optr->Arg_Car[20].array_dim = "1";
  optr->Arg_Car[20].typ = ATYC_IF32;
  optr->Arg_Car[20].type_sample = NULL;		/* sans signification pour COEFFICIENT */
  optr->Arg_Car[20].sample = NULL;
  optr->Arg_Car[20].unite = "any";

  /* UU_cor */
  optr->Arg_Car[21].direction = DIR_OUT;
  optr->Arg_Car[21].categorie = VECTOR;
  optr->Arg_Car[21].typ = ATYC_IF32;
  optr->Arg_Car[21].array_dim = "1";
  optr->Arg_Car[21].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[21].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[21].sample = "$Arg1.sample";
  optr->Arg_Car[21].ref_time = "$Arg1.ref_time";
  optr->Arg_Car[21].misval = "$Arg1.misval";
  optr->Arg_Car[21].unite = "$Arg1.unit";
  optr->Arg_Car[21].famille = "$Arg1.famille";

  /* VV_cor */
  optr->Arg_Car[22].direction = DIR_OUT;
  optr->Arg_Car[22].categorie = VECTOR;
  optr->Arg_Car[22].typ = ATYC_IF32;
  optr->Arg_Car[22].array_dim = "1";
  optr->Arg_Car[22].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[22].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[22].sample = "$Arg1.sample";
  optr->Arg_Car[22].ref_time = "$Arg1.ref_time";
  optr->Arg_Car[22].misval = "$Arg1.misval";
  optr->Arg_Car[22].unite = "$Arg1.unit";
  optr->Arg_Car[22].famille = "$Arg1.famille";

  /* WW_cor */
  optr->Arg_Car[23].direction = DIR_OUT;
  optr->Arg_Car[23].categorie = VECTOR;
  optr->Arg_Car[23].typ = ATYC_IF32;
  optr->Arg_Car[23].array_dim = "1";
  optr->Arg_Car[23].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[23].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[23].sample = "$Arg1.sample";
  optr->Arg_Car[23].ref_time = "$Arg1.ref_time";
  optr->Arg_Car[23].misval = "$Arg1.misval";
  optr->Arg_Car[23].unite = "$Arg1.unit";
  optr->Arg_Car[23].famille = "$Arg1.famille";

}
