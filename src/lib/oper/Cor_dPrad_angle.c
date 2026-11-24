/**********************************************************
*
* OPERATOR       Cor_dPrad_angle.c   FUNCTION   ANSI-C
*
* PURPOSE        Calcule une dP corrigee des erreurs sur Pt dues aux angles
*
* DESCRIPTION       La pression mesuree au point central d'un radome ne 
*                correspond pas tout a fait une pression totale lorsque
*                les angles (attaque/derapages) ne sont pas nuls.  Cette
*                fonction calcule un dP_vraie a partir d'un dP_mesure
*                (mais deja corrige de l'ErrStat), et des angles.
*                   On utilise une formule classique de repartition de        
*                la pression sur un hemisphere, telle que decrite par
*                P. Nacass dans la note NCAR nr385 de 1992. On a verifie
*                que cette formule est equivalent a celle proposee par
*                d'autres auteurs (Brown en 1998, ...)
*                   Naturellement, les angles doivent etres donnes
*                dans le repere du radome, qui peut differer legerement
*                de celui de l'avion (non-colineaires).
*
* VERSION        $Revision$
*
* ARGUMENTS    IN   float    dP  any  Pression dynamique calibree 
*              IN   float  alpha  rad  angle d'incidence
*              IN   float   beta  rad  angle de derapage.
*              OUT  float   dP_cor (idem dP) Pression dynamique corrigée des angles
*
* SUBPROGRAMS    
*
* FILES      
*
* REFERENCES      Nacass, P. "Theoretical Errors on Airborne Measurements
*                 of Static pressure, Impact Temperature, Air Flow Angle,
*                 Air Flow Speed", NCAT Tech. Note 385, November 1992.
*
* CHANGES       
*
* COPYRIGHT        Meteo-France
*
* AGREEMENT        The author wishes that .....
*#########################################################################*/

#define _POSIX_SOURCE 1
#define _XOPEN_SOURCE 600
/* Le #define _HPUX_SOURCE n'est la que pour "voir" strdup */
#define _HPUX_SOURCE 1
#define _XOPEN_SOURCE_EXTENDED 1

#include <stdio.h>
#include <string.h>
#include <math.h>

#include "struct_oper.h"

int
Cor_dPrad_angle (unsigned long NLoop,
		 const float *dP,
		 const float *alpha,
		 const float *beta,
		 float *dP_cor)
{
  unsigned long i;
  float coscos;

  for (i = 0; i < NLoop; i++)
    {
      coscos = cos (*alpha) * cos (*beta);
      *dP_cor = *dP / (0.25 * (9.0 * coscos * coscos - 5.0));

      alpha++;
      beta++;
      dP++;
      dP_cor++;
    }
  return 0;
}

int
OP_Cor_dPrad_angle (unsigned long NbVal, void *ArgList[], char *DiagExec)
{
  int CodRet;

  sprintf (DiagExec, "OP_Cor_dPrad_angle (%ld, ); ", NbVal);

  CodRet = Cor_dPrad_angle (NbVal,
			    (float *) ArgList[0],
			    (float *) ArgList[1],
			    (float *) ArgList[2],
			    (float *) ArgList[3]);
  return OP_OK;
}

void
ID_Cor_dPrad_angle (oper * optr)
{
  strcpy (optr->Nom, "Cor_dPrad_angle");
  optr->Version = "$Revision$";
  optr->Date = "$Date$";
  optr->fctptr = OP_Cor_dPrad_angle;
  optr->NbArg = 4;		/* doit rester inf. a FIL_MAX_ARG */

  /* dP */
  optr->Arg_Car[0].direction = DIR_IN;
  optr->Arg_Car[0].categorie = VECTOR;
  optr->Arg_Car[0].typ = ATYC_IF32;
  optr->Arg_Car[0].array_dim = "1";
  optr->Arg_Car[0].type_sample = "any";
  optr->Arg_Car[0].sample = "any";
  optr->Arg_Car[0].unite = "hPa";

  /* alpha */
  optr->Arg_Car[1].direction = DIR_IN;
  optr->Arg_Car[1].categorie = VECTOR;
  optr->Arg_Car[1].typ = ATYC_IF32;
  optr->Arg_Car[1].array_dim = "1";
  optr->Arg_Car[1].type_sample = "any";
  optr->Arg_Car[1].sample = "any";
  optr->Arg_Car[1].unite = "radian";

  /* beta */
  optr->Arg_Car[2].direction = DIR_IN;
  optr->Arg_Car[2].categorie = VECTOR;
  optr->Arg_Car[2].typ = ATYC_IF32;
  optr->Arg_Car[2].array_dim = "1";
  optr->Arg_Car[2].type_sample = "any";
  optr->Arg_Car[2].sample = "any";
  optr->Arg_Car[2].unite = "radian";

  optr->Arg_Car[3].direction = DIR_OUT;
  optr->Arg_Car[3].categorie = VECTOR;
  optr->Arg_Car[3].typ = ATYC_IF32;
  optr->Arg_Car[3].array_dim = "1";
  optr->Arg_Car[3].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[3].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[3].sample = "$Arg1.sample";
  optr->Arg_Car[3].ref_time = "$Arg1.ref_time";
  optr->Arg_Car[3].unite = "$Arg1.unit";
  optr->Arg_Car[3].famille = "$Arg1.famille";
}
