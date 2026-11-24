/****************************************************
*
* OPERATOR      Extract_param_profil.c   FUNCTION  ANSI-C
*
* PURPOSE       Vecteur suivant la trajectoire fabriqué selon le profil grib  
*
* DESCRIPTION   Routine d'extraction de valeur d'un parametre sur la trajectoire definie par le vecteur alti, pour variables 1D (float32) 
*
* VERSION       $Revision: 4731 $
*
* ARGUMENTS   IN   float  Var_in     any        Original data
*             IN   float  Var_z      any        Original data
*             IN   float  alti      any        Original data
*	          IN   int	  nbniv	   without      Number of levels
*             IN   string famille    without     famille de la mesure
*             IN   int    valManq    without     misval
*             IN   string unit    without     
*             OUT  float  Var_out   pseudo vecteur_traj same as 3  Interpolated data
*
* REFERENCES
*
* CHANGES     
*              
*
* COPYRIGHT     Meteo-France
*
*#########################################################################*/

#define _POSIX_SOURCE 1
#define _XOPEN_SOURCE 600
#define _XOPEN_SOURCE_EXTENDED 1

#include <stdio.h>
#include <math.h>
#include <string.h>
#include <stdlib.h>
#include <limits.h>
#include "struct_oper.h"


/* La vraie fonction... */

int Extract_param_profil (unsigned long NbValIn,
	float *Var_in,
    float *Var_z,
    float *Var_alti,
    int nbniv,
	float *Var_out)

{
    unsigned long j,k;
    float alti,z,var; /* vecteurs lus */
    float varf,zf;    /* valeurs finales*/
    float zprec,varprec; /* valeurs precedentes*/
    short int debut,premiere_alti;
    int compt_lig,compt_col;

    compt_lig=0;
    /*lecture selon le vecteur alti*/
    for (k = 0; k < NbValIn; k++)
        {
        debut=0;
        compt_col=0;
        premiere_alti=1;
        alti=Var_alti[k];

        /* on ne traite pas les valeurs manquantes de alti*/
        if ((isfinite(alti)) )  
            {
            /* balayage du profil*/
            for ( j=0;j<nbniv;j++ )
                {
                var=Var_in[k*nbniv+j];
                z=Var_z[k*nbniv+j];
                if (debut== 0 )
                    { 
                    zprec=z;
                    varprec=var;
                    debut=1;
                    varf=var;
                    zf=z;
                    }
                else
                    {
                    if ((z   <alti) )
                        {
                        if (!(premiere_alti))
                            {
                            /*  cas des valeurs alti manquantes */
                            }
                        else
                            {
                            varf=(alti-z)*(var-varprec)/(z-zprec)+var;
                            zf=alti;
                            premiere_alti=0;
                            }
                        }
                    else
                        {
                        zprec=z;
                        varprec=var;
                        var=0./0.;
                        z=alti;
                        varf=var;
                        zf=z;
                        }
                    }
                compt_col++;
                }
            }
        else
            {
            varf=0./0.;
            zf=0./0.;
            }

        
        Var_out[k]=varf;
        compt_lig++;
        }

  return 0;

}

/* la fonction d'enrobage classique */

int
OP_Extract_param_profil (unsigned long NbVal, void *ArgList[], char *DiagExec)
{
  int CodRet;
  int NCar;

  NCar = sprintf (DiagExec, "Extract_param_profil : (%ld echant.) ", NbVal) ;
  if (NCar < 0)
    NCar = 0;
  DiagExec += NCar;

  CodRet = Extract_param_profil (NbVal,
		   (float *) ArgList[0],
		   (float *) ArgList[1],
		   (float *) ArgList[2],
		   *((int *) ArgList[3]),
		   (float *) ArgList[4]);

  switch (CodRet)
    {
    case 0:
      sprintf (DiagExec, " OK.");
      return OP_OK;
    default:
      sprintf (DiagExec, "Erreur %d", CodRet);
      return OP_FAIL;
    }

}

void
ID_Extract_param_profil (oper * optr)
{
  strcpy (optr->Nom, "Extract_param_profil");
  optr->Version = "$Revision: 4731 $";
  optr->Date = "$Date: 2019-06-20 11:25:57 +0200 (6 juin 2019) $";
  optr->fctptr = OP_Extract_param_profil;
  optr->NbArg = 5;

  /* Var_in :xxx_profil_cal_yy*/
  optr->Arg_Car[0].direction = DIR_IN;
  optr->Arg_Car[0].categorie = VECTOR;
  optr->Arg_Car[0].typ = ATYC_IF32;
  optr->Arg_Car[0].array_dim = "*";
  optr->Arg_Car[0].type_sample = "any";
  optr->Arg_Car[0].sample = "any";
  optr->Arg_Car[0].unite = "any";
  optr->Arg_Car[0].famille = "any";

  /*alti_vol_profil_cal_yy*/
  optr->Arg_Car[1].direction = DIR_IN;
  optr->Arg_Car[1].categorie = VECTOR;
  optr->Arg_Car[1].typ = ATYC_IF32;
  optr->Arg_Car[1].array_dim = "*";
  optr->Arg_Car[1].type_sample = "any";
  optr->Arg_Car[1].sample = "any";
  optr->Arg_Car[1].unite = "m";

  /*alti_vol_cal_yy*/
  optr->Arg_Car[2].direction = DIR_IN;
  optr->Arg_Car[2].categorie = VECTOR;
  optr->Arg_Car[2].typ = ATYC_IF32;
  optr->Arg_Car[2].array_dim = "1";
  optr->Arg_Car[2].type_sample = "any";
  optr->Arg_Car[2].sample = "any";
  optr->Arg_Car[2].unite = "m";

  /*  NbNiv */
  optr->Arg_Car[3].direction = DIR_IN;
  optr->Arg_Car[3].categorie = COEFFICIENT;
  optr->Arg_Car[3].array_dim = "1";
  optr->Arg_Car[3].typ = ATYC_I32;
  optr->Arg_Car[3].unite = "without";

  /* Var_out */
  /* on rajoute 1 a Argx par rapport a optr->Arg_Car*/
  optr->Arg_Car[4].direction = DIR_OUT;
  optr->Arg_Car[4].categorie = VECTOR;
  optr->Arg_Car[4].typ = ATYC_IF32;
  optr->Arg_Car[4].array_dim = "1"; 
  optr->Arg_Car[4].NbVal = "$Arg3.NbVal";
  optr->Arg_Car[4].type_sample = "$Arg3.type_sample";
  optr->Arg_Car[4].sample = "$Arg3.sample ";
  optr->Arg_Car[4].ref_time = "$Arg3.ref_time";
  optr->Arg_Car[4].misval = "$Arg1.misval";
  optr->Arg_Car[4].unite = "$Arg1.unit";
  optr->Arg_Car[4].famille = "$Arg1.famille";
  optr->Arg_Car[4].name = "\"extraction de \"+ $Arg1.name +\" au niveau d'altitude \"+$Arg3.name";
  optr->Arg_Car[4].en_name = "\"extraction of \"+ $Arg1.name +\" at altitude level \"+ $Arg3.name";

}
