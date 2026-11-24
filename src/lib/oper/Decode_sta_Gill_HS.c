/*************************************************************************
*
* OPERATOR         Decode_sta_Gill_HS  FUNCTION ANSI-C
*
* PURPOSE          Décodage des status (A et D) des anémomètres Gill_HS
*
* DESCRIPTION      
*
* VERSION          1.0 
*
* ARGUMENTS  
*            IN   ATYP_UI8   StaA        "Status Address"
*            IN   ATYP_UI8   StaD        "Status Data"
*            IN   double     time_sta    Datation des status
*
*            OUT  float      Err          Error codes de l'instrument
*            OUT  double     time_err     datation du vecteur Errr
*            OUT  float      Conf         Anemometer Configuration
*            OUT  double     time_cnf     datation du vecteur Conf
*            OUT  float      Data_conf    Data Output Configuration
*            OUT  double     time_dcnf    datation du vecteur Data_conf
*            OUT  float      Pair1_gain   Gain of pair 1
*            OUT  float      Pair2_gain   Gain of pair 2
*            OUT  float      Pair3_gain   Gain of pair 3
*            OUT  double     time_gain    datation des vecteur gain
*            OUT  float      Type         Anemometer Type
*            OUT  double     time_typ     datation du vecteur Type
*            OUT  float      Incl_X       X axis inclinometer
*            OUT  double     time_InclX   datation du vecteur Incl_X
*            OUT  float      Incl_Y       Y axis inclinometer
*            OUT  double     time_InclY   datation du vecteur Incl_Y
*
* ENTRY        NONE
*        
* SUBPROGRAMS  NONE
*        
* REFERENCES   
*
* COPYRIGHT    Meteo-France
*	       Centre National de Recherches Meteorologiques 
*	       GMEI/ TRAMM
*	       42, av G. Coriolis
*	       31057 TOULOUSE cedex  
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

typedef struct
{
  unsigned long nb_err;
  unsigned long nb_cnf;
  unsigned long nb_dcnf;
  unsigned long nb_gain;
  unsigned long nb_type;
  unsigned long nb_inclX;
  unsigned long nb_inclY;
  unsigned long nb_bad;
}
cr_exec_t;


static void
Decode_sta_Gill_HS (unsigned long ndata,
		    const ATYP_UI8 * StaA,
		    const ATYP_UI8 * StaD,
		    const double *time_sta,
		    float *Err,
		    double *time_err,
		    float *Conf,
		    double *time_cnf,
		    float *Data_conf,
		    double *time_dcnf,
		    float *Pair1_gain,
		    float *Pair2_gain,
		    float *Pair3_gain,
		    double *time_gain,
		    float *Type,
		    double *time_typ,
		    float *Incl_X,
		    double *time_InclX, float *Incl_Y, double *time_InclY,
		    cr_exec_t * CR)
{
  unsigned long i;
  short int tempo;
  int memoire_sta, memoire_val;

  CR->nb_err = 0;
  CR->nb_cnf = 0;
  CR->nb_dcnf = 0;
  CR->nb_gain = 0;
  CR->nb_type = 0;
  CR->nb_inclX = 0;
  CR->nb_inclY = 0;
  CR->nb_bad = 0;

  for (i = 0; i < ndata; i++)
    {
      switch (StaA[i])
	{
	case 0:
	  Err[CR->nb_err] = StaD[i];
	  time_err[CR->nb_err] = time_sta[i];
	  CR->nb_err++;
	  break;
	case 1:
	  Conf[CR->nb_cnf] = StaD[i];
	  time_cnf[CR->nb_cnf] = time_sta[i];
	  CR->nb_cnf++;
	  break;
	case 2:
	  Data_conf[CR->nb_dcnf] = StaD[i];
	  time_dcnf[CR->nb_dcnf] = time_sta[i];
	  CR->nb_dcnf++;
	  break;
	case 3:
	  break;
	case 4:
	  break;
	case 5:
	  Pair1_gain[CR->nb_gain] = StaD[i] & 0x03;
	  Pair2_gain[CR->nb_gain] = (StaD[i] & 0x0C) >> 2;
	  Pair3_gain[CR->nb_gain] = (StaD[i] & 0x30) >> 4;
	  time_gain[CR->nb_gain] = time_sta[i];
	  CR->nb_gain++;
	  break;
	case 6:
	  Type[CR->nb_type] = StaD[i];
	  time_typ[CR->nb_type] = time_sta[i];
	  CR->nb_type++;
	  break;
	case 7:
	  break;
	case 8:
	  if (memoire_sta == 7)
	    {
	      tempo = memoire_val;
	      tempo = tempo << 8;
	      tempo = tempo | StaD[i];
	      Incl_X[CR->nb_inclX] = tempo * 0.01;
	      time_InclX[CR->nb_inclX] = time_sta[i];
	      CR->nb_inclX++;
	    }
	  break;
	case 9:
	  break;
	case 10:
	  if (memoire_sta == 9)
	    {
	      tempo = memoire_val;
	      tempo = tempo << 8;
	      tempo = tempo | StaD[i];
	      Incl_Y[CR->nb_inclY] = tempo * 0.01;
	      time_InclY[CR->nb_inclY] = time_sta[i];
	      CR->nb_inclY++;
	    }
	  break;
	default:
	  CR->nb_bad++;
	}
      memoire_sta = StaA[i];
      memoire_val = StaD[i];
    }

  return;
}

/* la fonction d'enrobage classique */
int
OP_Decode_sta_Gill_HS (unsigned long NbVal, void *ArgList[], char *DiagExec)
{
  cr_exec_t CR;
  int NCar;

  NCar = sprintf (DiagExec, "Decode_sta_Gill_HS, NbVal=%ld", NbVal);
  if (NCar > 0)
    DiagExec += NCar;


  Decode_sta_Gill_HS (NbVal, (ATYP_UI8 *) ArgList[0], (ATYP_UI8 *) ArgList[1], (double *) ArgList[2], (float *) ArgList[3],	/* Err */
		      (double *) ArgList[4],	/* time_err */
		      (float *) ArgList[5],	/* Conf */
		      (double *) ArgList[6],	/* time_cnf */
		      (float *) ArgList[7],	/* Data_conf */
		      (double *) ArgList[8],	/* time_dcnf */
		      (float *) ArgList[9],	/* Pair1 gain */
		      (float *) ArgList[10],	/* Pair2 gain */
		      (float *) ArgList[11],	/* Pair3 gain */
		      (double *) ArgList[12],	/* time_gain */
		      (float *) ArgList[13],	/* Type */
		      (double *) ArgList[14],	/* time_Type */
		      (float *) ArgList[15],	/* Incl_X */
		      (double *) ArgList[16],	/* time_InclX */
		      (float *) ArgList[17],	/* Incl_Y */
		      (double *) ArgList[18],	/* time_InclY */
		      &CR);

  sprintf (DiagExec,
	   ", nb_err:%lu, nb_cnf:%lu, nb_dcnf:%lu, nb_gain:%lu, nb_type:%lu, nb_bad:%lu",
	   CR.nb_err, CR.nb_cnf, CR.nb_dcnf, CR.nb_gain, CR.nb_type,
	   CR.nb_bad);

  return OP_OK;
}

/* La même, mais avec des entrees de type différent */
int
OP_Decode_sta_Gill_HS_flt (unsigned long NbVal, void *ArgList[],
			   char *DiagExec)
{
  unsigned long i;
  int NCar;
  cr_exec_t CR;
  ATYP_UI8 *StaA = NULL;
  ATYP_UI8 *StaD = NULL;
  float *StaA_flt;
  float *StaD_flt;

  NCar = sprintf (DiagExec, "Decode_sta_Gill_HS_flt, NbVal=%ld", NbVal);
  if (NCar > 0)
    DiagExec += NCar;

  StaA = malloc (NbVal);
  if (StaA == NULL)
    return OP_FAIL;
  StaA_flt = (float *) ArgList[0];
  StaD = malloc (NbVal);
  if (StaD == NULL)
    {
      free (StaA);
      return OP_FAIL;
    }
  StaD_flt = (float *) ArgList[1];
  for (i = 0; i < NbVal; i++)
    {
      StaA[i] = StaA_flt[i];
      StaD[i] = StaD_flt[i];
    }

  Decode_sta_Gill_HS (NbVal, StaA, StaD, (double *) ArgList[2], (float *) ArgList[3],	/* Err */
		      (double *) ArgList[4],	/* time_err */
		      (float *) ArgList[5],	/* Conf */
		      (double *) ArgList[6],	/* time_cnf */
		      (float *) ArgList[7],	/* Data_conf */
		      (double *) ArgList[8],	/* time_dcnf */
		      (float *) ArgList[9],	/* Pair1 gain */
		      (float *) ArgList[10],	/* Pair2 gain */
		      (float *) ArgList[11],	/* Pair3 gain */
		      (double *) ArgList[12],	/* time_gain */
		      (float *) ArgList[13],	/* Type */
		      (double *) ArgList[14],	/* time_Type */
		      (float *) ArgList[15],	/* Incl_X */
		      (double *) ArgList[16],	/* time_InclX */
		      (float *) ArgList[17],	/* Incl_Y */
		      (double *) ArgList[18],	/* time_InclY */
		      &CR);
  free (StaA);
  free (StaD);

  sprintf (DiagExec,
	   ", nb_err:%lu, nb_cnf:%lu, nb_dcnf:%lu, nb_gain:%lu, nb_type:%lu, nb_bad:%lu",
	   CR.nb_err, CR.nb_cnf, CR.nb_dcnf, CR.nb_gain, CR.nb_type,
	   CR.nb_bad);

  return OP_OK;
}

void
ID_Decode_sta_Gill_HS (oper * optr)
{
  int idx = 0;
  strcpy (optr->Nom, "Decode_sta_Gill_HS");
  optr->Version = "Revision:$";
  optr->Date = "$Date:$";
  optr->fctptr = OP_Decode_sta_Gill_HS;
  optr->NbArg = 19;		/* doit rester inf. a FIL_MAX_ARG */

  /* StaA */
  optr->Arg_Car[idx].direction = DIR_IN;
  optr->Arg_Car[idx].categorie = VECTOR;
  optr->Arg_Car[idx].typ = ATYC_UI8;
  optr->Arg_Car[idx].array_dim = "1";
  optr->Arg_Car[idx].type_sample = "any";
  optr->Arg_Car[idx].sample = "any";
  optr->Arg_Car[idx].unite = "";
  idx++;

  /* StaD */
  optr->Arg_Car[idx].direction = DIR_IN;
  optr->Arg_Car[idx].categorie = VECTOR;
  optr->Arg_Car[idx].typ = ATYC_UI8;
  optr->Arg_Car[idx].array_dim = "1";
  optr->Arg_Car[idx].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[idx].type_sample = "any";
  optr->Arg_Car[idx].sample = "any";
  optr->Arg_Car[idx].unite = "";
  idx++;

  /* time_Sta */
  optr->Arg_Car[idx].direction = DIR_IN;
  optr->Arg_Car[idx].categorie = VECTOR;
  optr->Arg_Car[idx].typ = ATYC_IF64;
  optr->Arg_Car[idx].array_dim = "1";
  optr->Arg_Car[idx].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[idx].type_sample = "any";
  optr->Arg_Car[idx].sample = "any";
  optr->Arg_Car[idx].unite = "s";
  idx++;

  for (idx = 3; idx < optr->NbArg; idx++)
    {
      optr->Arg_Car[idx].direction = DIR_OUT;
      optr->Arg_Car[idx].categorie = VECTOR;
      optr->Arg_Car[idx].array_dim = "1";
      optr->Arg_Car[idx].sample = "0";
    }
  idx = 3;

  /* Err */
  optr->Arg_Car[idx].typ = ATYC_IF32;
  optr->Arg_Car[idx].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[idx].ref_time = "$Arg5.nom";
  optr->Arg_Car[idx].unite = "bit";
  optr->Arg_Car[idx].famille = "\"controle\"";
  optr->Arg_Car[idx].name = "\"Code d'erreur de l'anemometre\"";
  optr->Arg_Car[idx].en_name = "\"Error Code of anemometer\"";
  idx++;

  /* time_err */
  optr->Arg_Car[idx].typ = ATYC_IF64;
  optr->Arg_Car[idx].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[idx].unite = "second";
  optr->Arg_Car[idx].famille = "\"temps\"";
  idx++;

  /* Conf */
  optr->Arg_Car[idx].typ = ATYC_IF32;
  optr->Arg_Car[idx].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[idx].ref_time = "$Arg7.nom";
  optr->Arg_Car[idx].unite = "bit";
  optr->Arg_Car[idx].famille = "\"controle\"";
  optr->Arg_Car[idx].name = "\"Configuration de l'anemometre\"";
  optr->Arg_Car[idx].en_name = "\"Anemometer Configuration\"";
  idx++;

  /* time_cnf */
  optr->Arg_Car[idx].typ = ATYC_IF64;
  optr->Arg_Car[idx].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[idx].unite = "second";
  optr->Arg_Car[idx].famille = "\"temps\"";
  idx++;

  /* Data_conf */
  optr->Arg_Car[idx].typ = ATYC_IF32;
  optr->Arg_Car[idx].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[idx].ref_time = "$Arg9.nom";
  optr->Arg_Car[idx].unite = "bit";
  optr->Arg_Car[idx].famille = "\"controle\"";
  optr->Arg_Car[idx].name = "\"Configuration des sorties de l'anemometre\"";
  optr->Arg_Car[idx].en_name = "\"Data Output Configuration\"";
  idx++;

  /* time_dcnf */
  optr->Arg_Car[idx].typ = ATYC_IF64;
  optr->Arg_Car[idx].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[idx].unite = "second";
  optr->Arg_Car[idx].famille = "\"temps\"";
  idx++;

  /*  Pair1_gain */
  optr->Arg_Car[idx].typ = ATYC_IF32;
  optr->Arg_Car[idx].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[idx].ref_time = "$Arg13.nom";
  optr->Arg_Car[idx].unite = "bit";
  optr->Arg_Car[idx].famille = "\"controle\"";
  optr->Arg_Car[idx].name = "\"Gain des transducteurs 1 de l'anemometre\"";
  optr->Arg_Car[idx].en_name = "\"Channel pair 1 Gain level\"";
  idx++;

  /*  Pair2_gain */
  optr->Arg_Car[idx].typ = ATYC_IF32;
  optr->Arg_Car[idx].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[idx].ref_time = "$Arg13.nom";
  optr->Arg_Car[idx].unite = "bit";
  optr->Arg_Car[idx].famille = "\"controle\"";
  optr->Arg_Car[idx].name = "\"Gain des transducteurs 2 de l'anemometre\"";
  optr->Arg_Car[idx].en_name = "\"Channel pair 2 Gain level\"";
  idx++;

  /*  Pair3_gain */
  optr->Arg_Car[idx].typ = ATYC_IF32;
  optr->Arg_Car[idx].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[idx].ref_time = "$Arg13.nom";
  optr->Arg_Car[idx].unite = "bit";
  optr->Arg_Car[idx].famille = "\"controle\"";
  optr->Arg_Car[idx].name = "\"Gain des transducteurs 3 de l'anemometre\"";
  optr->Arg_Car[idx].en_name = "\"Channel pair 3 Gain level\"";
  idx++;

  /* time_gain */
  optr->Arg_Car[idx].typ = ATYC_IF64;
  optr->Arg_Car[idx].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[idx].unite = "second";
  optr->Arg_Car[idx].famille = "\"temps\"";
  idx++;

  /* Type */
  optr->Arg_Car[idx].typ = ATYC_IF32;
  optr->Arg_Car[idx].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[idx].ref_time = "$Arg15.nom";
  optr->Arg_Car[idx].unite = "bit";
  optr->Arg_Car[idx].famille = "\"controle\"";
  optr->Arg_Car[idx].name = "\"Type d'anemometre\"";
  optr->Arg_Car[idx].en_name = "\"Anemometer Type\"";
  idx++;

  /* time_typ */
  optr->Arg_Car[idx].typ = ATYC_IF64;
  optr->Arg_Car[idx].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[idx].unite = "second";
  optr->Arg_Car[idx].famille = "\"temps\"";
  idx++;

  /* Incl_X */
  optr->Arg_Car[idx].typ = ATYC_IF32;
  optr->Arg_Car[idx].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[idx].ref_time = "$Arg17.nom";
  optr->Arg_Car[idx].unite = "degree";
  optr->Arg_Car[idx].famille = "\"controle\"";
  optr->Arg_Car[idx].name = "\"Inclinaison axe X de l'anemometre\"";
  optr->Arg_Car[idx].en_name = "\"Anemometer X-Axis Inclinometer\"";
  idx++;

  /* time_InclX */
  optr->Arg_Car[idx].typ = ATYC_IF64;
  optr->Arg_Car[idx].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[idx].unite = "second";
  optr->Arg_Car[idx].famille = "\"temps\"";
  idx++;

  /* Incl_Y */
  optr->Arg_Car[idx].typ = ATYC_IF32;
  optr->Arg_Car[idx].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[idx].ref_time = "$Arg19.nom";
  optr->Arg_Car[idx].unite = "degree";
  optr->Arg_Car[idx].famille = "\"controle\"";
  optr->Arg_Car[idx].name = "\"Inclinaison axe Y de l'anemometre\"";
  optr->Arg_Car[idx].en_name = "\"Anemometer Y-Axis Inclinometer\"";
  idx++;

  /* time_InclY */
  optr->Arg_Car[idx].typ = ATYC_IF64;
  optr->Arg_Car[idx].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[idx].unite = "second";
  optr->Arg_Car[idx].famille = "\"temps\"";
}

void
ID_Decode_sta_Gill_HS_flt (oper * optr)
{
  ID_Decode_sta_Gill_HS (optr);
  strcpy (optr->Nom, "Decode_sta_Gill_HS_flt");
  optr->fctptr = OP_Decode_sta_Gill_HS_flt;

  optr->Arg_Car[0].typ = ATYC_IF32;
  optr->Arg_Car[1].typ = ATYC_IF32;
}
