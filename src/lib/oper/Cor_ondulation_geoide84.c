/*************************************************************************
*
* OPERATOR         Cor_ondulation_geoide84.c  FUNCTION ANSI-C
*
* PURPOSE          Correction de l'altitude gps par rapport au geoide
*
* DESCRIPTION      Conversion d'une fonction du NGA en fortran.
*
* VERSION          1.0
*
* ARGUMENTS
*            IN   float   lat       degree      latitude
*            IN   float   lon       degree      longitude
*            IN   float   alt       meters      altitude
*
*            OUT  float   alt_cor   meters      altitude corrigée
*
*
* ENTRY      NONE
*
* FILES      EGM180.NOR
*
* REFERENCES
*
* COPYRIGHT    Meteo-France
*	       Centre National de Recherches Meteorologiques
*	       GMEI/ TRAMM
*	       42, av G. Coriolis
*	       31057 TOULOUSE cedex 1
*
*
*############################################################################*/

#define _POSIX_SOURCE 1
#define _XOPEN_SOURCE 600

#include <math.h>
#include <stdio.h>
#include <string.h>
#include <stdlib.h>

#include "struct_oper.h"
#include "oper_util.h"


unsigned long
Cor_ondulation_geoide84 (unsigned long ndata,
			 const float *lat, const float *lon, float *alt,
			 float *alt_cor)
{
  const float ESQ = 0.00669437999013;
  const float C2 = 108262.9989050E-8;
  const float AE = 6378137.0;
  const float PI = 3.14159265358979323846;
  const float GRAVA = 9.7803267714;
  const float STAR = 0.001931851386;
  const float RKM = 3.9860015E14;


  int LL, LL2, LL3, N, M;
  unsigned long i;
  int j;
  int MP1, RM, RN;
  int IV[184];
  int CodRet;

  double CNM[16471], SNM[16471];
  double CBAR, SBAR;
  double C2N[6], CB2, CB4, CB6, CB8, CB10;
  double CR[180], SR[180];
  double AS[180], A[16836]={0.}, B[16836]={0.};
  double S11[180], S12[180], SHT[180];
  double T11[180], T12[180];
  double SUMHT;
  float PHID, RLAMD, HT, PHI;
  double RNF, T22, X2Y2, Z1, R, PSI;
  double GRAVN;
  double TH, Y, T, F1, F2, P11HT;
  double RLAM;
  double GA;

  char infile[100];
  char chaine_tempo[100];
  char *pt_char;

  FILE *fp_in;


/* Lecture du fichier des coefficients geopotentiel   */

  /*** Initialisation des differents chemins ***/
  CodRet = AidaGetEnv ("AIDA_HOME", &pt_char);
  if (CodRet != 0)
    {
      fprintf (stderr, "+++ ERREUR : Environnement AIDA non trouve ! \n");
      return -1;
    }

  sprintf (infile, "%s/extern/EGM_84/EGM180.NOR\0", pt_char);
  free (pt_char);

  if ((fp_in = fopen (infile, "r")) == NULL)
    {
      fprintf (stderr, "Pb ouverture fichier des coefficients  %s\n", infile);
    }

  i = 0;
  while ((i < 16471) && (fgets (chaine_tempo, 100, fp_in)) != NULL)
    {
      if (sscanf (chaine_tempo, "%5d%5d%15le%15le", &N, &M, &CBAR, &SBAR) !=
	  4)
	fprintf (stderr, "ERREUR\n");

      LL = N * (N + 1) / 2 + M + 1;
      CNM[LL] = CBAR;
      SNM[LL] = SBAR;

      i++;
    }

  fclose (fp_in);

/*  Elaboration tableau local             */

  for (i = 1; i <= 183; i++)
    IV[i] = i * (i - 1) / 2;

/*  Modification quelques coefficient CNM zonal     */

  for (i = 2; i <= 5; i++)
    C2N[i] =
      pow (-1.,
	   i +
	   1) * (3.0 * (pow (ESQ, i)) / ((2.0 * i + 1.0) * (2.0 * i + 3.0))) *
      (1.0 - i + 5.0 * i * C2 / ESQ);

/*  WGS84 VALUES ARE USED     */
  CB2 = -1.0 * C2 / sqrt (5.0);
  CB4 = -1.0 * C2N[2] / 3.0;
  CB6 = -1.0 * C2N[3] / sqrt (13.0);
  CB8 = -1.0 * C2N[4] / sqrt (17.0);
  CB10 = -1.0 * C2N[5] / sqrt (21.0);


  CNM[4] = CNM[4] - CB2;
  CNM[11] = CNM[11] - CB4;
  CNM[22] = CNM[22] - CB6;
  CNM[37] = CNM[37] - CB8;
  CNM[56] = CNM[56] - CB10;

/* BUILD ALL CLENSHAW COEFFICIENT ARRAYS.    */

  for (i = 1; i <= 180; i++)
    AS[i] = 0 - sqrt ((2. * i + 1.) / (2. * i));

  for (M = 0; M <= 180; M++)
    {
      MP1 = M + 1;
      RM = M;
      for (N = MP1; N <= 180; N++)
	{
	  RN = N;
	  LL = IV[N + 1] + M + 1;
	  A[LL] =
	    0 -
	    sqrt (((2. * RN + 1.) * (2. * RN - 1.)) / ((RN - RM) * (RN +
								    RM)));
	  B[LL] =
	    sqrt (((2. * RN + 1.) * (RN + RM - 1.) * (RN - RM -
						      1.)) / ((2. * RN -
							       3.) * (RN +
								      RM) *
							      (RN - RM)));
	}
    }

/*   Recuperation des valeur de latitude, longitude et altitude    */

  for (i = 0; i < ndata; i++)
    {
      PHID = lat[i];
      RLAMD = lon[i];
      HT = alt[i];
      if (!isfinite(PHID) || !isfinite(RLAMD) || !isfinite(HT)) {
        alt_cor[i] = K_NaN;
        continue;       
      }
      PHI = PHID * PI / 180;

      RNF = AE / sqrt (1.0 - ESQ * pow (sin (PHI), 2));
      T22 = (RNF + HT) * cos (PHI);
      X2Y2 = pow (T22, 2);
      Z1 = (RNF * (1.0 - ESQ) + HT) * sin (PHI);
      R = sqrt (X2Y2 + pow (Z1, 2));
      PSI = atan (Z1 / sqrt (X2Y2));

      GRAVN =
	GRAVA * (1.0 + STAR * pow (sin (PHI), 2)) / sqrt (1.0 -
							  ESQ *
							  pow (sin (PHI), 2));
      GRAVN = GRAVN - HT * 0.3086E-5;
      TH = (PI / 2.0) - PSI;
      Y = sin (TH);
      T = cos (TH);
      F1 = AE / R;
      F2 = pow ((AE / R), 2);
      P11HT = sqrt (3.) * Y * F2;

      SR[0] = 0.0;
      CR[0] = 1.0;
      RLAM = RLAMD * PI / 180.;
      SR[1] = sin (RLAM);
      CR[1] = cos (RLAM);

      for (j = 2; j <= 180; j++)
	{
	  SR[j] = 2. * CR[1] * SR[j - 1] - SR[j - 2];
	  CR[j] = 2. * CR[1] * CR[j - 1] - CR[j - 2];
	}


      GA = RKM / AE;

      for (M = 180; M >= 0; M--)
	{
	  for (N = 180; N >= M; N--)
	    {
	      LL = IV[N + 1] + M + 1;
	      LL2 = IV[N + 2] + M + 1;
	      LL3 = IV[N + 3] + M + 1;
	      S11[N] =
		-A[LL2] * T * F1 * S11[N + 1] - B[LL3] * F2 * S11[N + 2] +
		CNM[LL];
	      S12[N] =
		-A[LL2] * T * F1 * S12[N + 1] - B[LL3] * F2 * S12[N + 2] +
		SNM[LL];
	    }
	  T11[M] = S11[M];
	  T12[M] = S12[M];

	  SHT[M] =
	    -AS[M + 1] * Y * F1 * SHT[M + 1] + T11[M] * CR[M] +
	    T12[M] * SR[M];
	}

      SUMHT = (T11[0] + T12[0]) * F1 + SHT[1] * P11HT;
      SUMHT = SUMHT * GA / GRAVN;

      alt_cor[i] = HT - SUMHT;
    }

  return i;
}


/* la fonction d'enrobage classique */
int
OP_Cor_ondulation_geoide84 (unsigned long NbVal, void *ArgList[],
			    char *DiagExec)
{
  int NCar;

  NCar =
    sprintf (DiagExec, "Cor_ondulation_geoide84 (%ld ech)", NbVal);
  DiagExec += NCar;
  /*** SB : ArgList[1] n'est pas un temps !!! DiagExec = ecrit_bornes_temps (DiagExec, "temps", (double *) ArgList[1],
				 NbVal);
  ***/
  Cor_ondulation_geoide84 (NbVal,
			   (float *) ArgList[0],
			   (float *) ArgList[1],
			   (float *) ArgList[2], (float *) ArgList[3]);

  return OP_OK;
}


void
ID_Cor_ondulation_geoide84 (oper * optr)
{
  strcpy (optr->Nom, "Cor_ondulation_geoide84");
  optr->Version = "$Revision: 5415 $";
  optr->Date = "$Date: 2016-05-26 10:44:00 +0200 (jeu. 26 mai 2016) $";
  optr->fctptr = OP_Cor_ondulation_geoide84;
  optr->NbArg = 4;		/* doit rester inf. a FIL_MAX_ARG */

  /* lat */
  optr->Arg_Car[0].direction = DIR_IN;
  optr->Arg_Car[0].categorie = VECTOR;
  optr->Arg_Car[0].typ = ATYC_IF32;
  optr->Arg_Car[0].array_dim = "1";
  optr->Arg_Car[0].NbVal = "$Arg3.NbVal";
  optr->Arg_Car[0].type_sample = "any";
  optr->Arg_Car[0].sample = "any";
  optr->Arg_Car[0].unite = "degree";

  /* lon */
  optr->Arg_Car[1].direction = DIR_IN;
  optr->Arg_Car[1].categorie = VECTOR;
  optr->Arg_Car[1].typ = ATYC_IF32;
  optr->Arg_Car[1].array_dim = "1";
  optr->Arg_Car[1].NbVal = "$Arg3.NbVal";
  optr->Arg_Car[1].type_sample = "any";
  optr->Arg_Car[1].sample = "any";
  optr->Arg_Car[1].unite = "degree";

  /* alt */
  optr->Arg_Car[2].direction = DIR_IN;
  optr->Arg_Car[2].categorie = VECTOR;
  optr->Arg_Car[2].typ = ATYC_IF32;
  optr->Arg_Car[2].array_dim = "1";
  optr->Arg_Car[2].NbVal = "$Arg3.NbVal";
  optr->Arg_Car[2].type_sample = "any";
  optr->Arg_Car[2].sample = "any";
  optr->Arg_Car[2].unite = "meters";

  /* Alti_cor :  */
  optr->Arg_Car[3].direction = DIR_OUT;
  optr->Arg_Car[3].categorie = VECTOR;
  optr->Arg_Car[3].typ = ATYC_IF32;
  optr->Arg_Car[3].array_dim = "1";
  optr->Arg_Car[3].NbVal = "$Arg3.NbVal";
  optr->Arg_Car[3].type_sample = "any";
  optr->Arg_Car[3].sample = "$Arg3.sample";
  optr->Arg_Car[3].ref_time = "$Arg3.ref_time";
  optr->Arg_Car[3].unite = "meters";
  optr->Arg_Car[3].famille = " \"altitude\" ";
  optr->Arg_Car[3].name = "\"Altitude corrigee ondulation geoide\"";
  optr->Arg_Car[3].en_name =
    "\"Altitude corrected from the geoid undulation\"";

}
