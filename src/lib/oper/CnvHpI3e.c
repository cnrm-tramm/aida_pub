/*******************************************************************
* OPERATOR      CnvHpI3e.c FUNCTION ANSI-C
*
* PURPOSE       Conversion d'un vecteur "HP_float" en vecteur "float"  
*
* DESCRIPTION   RAS 
*
* VERSION       1.0
*
*               IN      HP_float  vect_dbl	vecteur "Hp_Float" 
*
*               OUT     float   vect_flt	vecteur "float"	
*
* ENTRY         NONE
*
* SUBPROGRAMS   NONE
*
* REFERENCES   	Norme IEEE754 et documentation HP
*
* AUTHOR        C. Allet. Transformation en operateur par GMEI/MMA
*             
* COPYRIGHT     Meteo-France and CNRS/INSU/DT
*              
*******************************************************************/

#define _POSIX_SOURCE 1
#define _XOPEN_SOURCE 600

#include <stdio.h>
#include <string.h>
#include <math.h>
#include "struct_oper.h"

#ifdef __hppa
#define HP9000
#endif

/*
   **  CNVHPI3E.C
   **    module contenant les procédures de conversion flottant HP -> IEEE
   **
   **    Remarque : la conversion est correcte, aux erreurs d'arrondi près,
   **      en Turboc C 2.0
   **
   **    Les champs de bits ne sont pas décrit de la même façon en TURBO C 2.0
   **    et en C ANSI de HP-UX
   **
   **      Turbo C : la description va de la Droite vers la Gauche
   **        page 329 du manuel utilisateur
   **       struct mystruct  {
   **         int       i : 2 ;
   **         unsigned  j : 5 ;
   **         int         : 4 ;
   **         int       k : 1 ;
   **         int       m : 4 ;
   **       } a ;
   **   2 octets   |15|14|13|12|11|10|09|08|07|06|05|04|03|02|01|00|
   **              |     m     | k|non utilisé|       j      |  i  |
   **
   **
   **      C hp-ux : la description va de la Gauche vers la Droite
   **        page C-13 HP-C/HP-UX ref manual
   **       struct {
   **         unsigned char  a : 7 ;
   **         unsigned char  b : 3 ;
   **         unsigned char  c : 7 ;
   **         unsigned char  d : 2 ;
   **         unsigned short e : 13 ;
   **       } x ;
   **   avec le pragma HP_ALIGN NATURAL
   **   4 octets   | byte 0 | byte 1 | byte 2 | byte 3 |
   **              |01234567|01234567|01234567|01234567|
   **              |aaaaaaab|bbcccccc|cddeeeee|eeeeeeee|
   **
   **   avec le pragma HP_ALIGN HPUX_WORD
   **   6 octets   | byte 0 | byte 1 | byte 2 | byte 3 | byte 5 | byte 6 |
   **              |01234567|01234567|01234567|01234567|01234567|01234567|
   **              |aaaaaaa |bbb     |ccccccc |dd      |eeeeeeee|eeeee   |
   **
   #define            VERSION   "3.00.01"
   #define            UPDATE    "30/10/92"
   **
   **       écrit par Christian ALLET, modifié par Nathalie Lebreton
 */

#include <stdlib.h>
#include <stdio.h>
#include <math.h>

#ifdef HP9000
#pragma  HP_ALIGN NATURAL	/* compacte les champs de bits  */
#endif

/*       prototype des fonctions                                        */

float convfloat (long int);	/* conversion  HP -> IEEE   */
long abs_fl_hp (float);		/* valeur absolue flot HP   */

/*----------------------------------------------------------------------*/
/* convfloat :                                                          */
/*       convertit les flottants HP REAL*4 en code INTEL   ieee         */
/*       sans inversion de mots ou d'octets                             */
/*        version 3.00.00 du 30/10/1992, Christian ALLET                */
/*        d'après la version 1.01 du 31/08/1989, ChA                    */
/*----------------------------------------------------------------------*/
float 
convfloat (long int bloc)	/* valeur à traduire   */
{

#if defined(PCAT) || defined(__i386__) || defined(__i486__) || defined(__i586__) || defined(__i686__) || defined(__x86_64__)
  struct fl_HP
    {				/* de la droite vers la gauche   */
      unsigned sigexp:1;	/* poids faibles à gauche   */
      unsigned exp:7;
      unsigned man_7_0:8;

      unsigned man_14_8:7;	/* frontière de mot 16 bits      */
      unsigned man_20_15:7;
      unsigned man_21:1;
      unsigned sig_man:1;	/* poids forts à droite     */
    };

  struct fl_i3e
    {
      unsigned man_0:1;		/* poids faibles à gauche   */
      unsigned man_8_1:8;
      unsigned man_15_9:7;

      unsigned man_22_16:7;	/* frontière de mot 16 bits      */
      unsigned exp:8;
      unsigned signe:1;		/* poids forts à droite     */
    };
#endif

#ifdef    HP9000
  struct fl_HP
    {				/* de la gauche vers la droite   */
      unsigned sig_man:1;	/* poids forts à gauche     */
      unsigned man_21:1;
      unsigned man_20_15:7;
      unsigned man_14_8:7;	/* frontiére 16 bits inutile ici */
      unsigned man_7_0:8;
      unsigned exp:7;
      unsigned sigexp:1;	/* poids faibles à droite   */
    };

  struct fl_i3e
    {
      unsigned signe:1;		/* poids forts à gauche     */
      unsigned exp:8;
      unsigned man_22_16:7;	/* frontiére 16 bits inutile ici */
      unsigned man_15_9:7;
      unsigned man_8_1:8;
      unsigned man_0:1;		/* poids faibles à droite   */
    };
#endif

  union
    {
      long int mot_il;
      float mot_fl;
      struct fl_HP mhp;
    }
  lu, aux;

  union flottant_i3e
    {
      float mot_fl;
      long int mot_il;
      struct fl_i3e mi;
    }
  ecr;

  if (!bloc)
    return 0;			/* cas nul, pour éviter exception */

  lu.mot_il = bloc;		/* chargement du mot hp          */

  if (lu.mhp.sig_man)
    {				/* cas des nombres négatifs      */

      aux.mot_il = abs_fl_hp (lu.mot_fl);	/* valeur absolue float HP  */
      ecr.mot_fl = convfloat (aux.mot_il);	/* conversion float positif */
      ecr.mi.signe = 1;		/* changement du signe      */

      return ecr.mot_fl;
    }

  else
    {				/* cas des nombres positifs > 1  */
      if (lu.mhp.sigexp)
	{			/* nombres < 0.5            */
	  aux.mhp.exp = (~lu.mhp.exp) + 1;	/* complément à 2      */
	  ecr.mi.exp = 0x7E - aux.mhp.exp;	/* exposant cadré 127, après */
	  /* décalage de la mantisse  */
	}

      else			/* nombres >= 0.5           */
	ecr.mi.exp = 0x7E + lu.mhp.exp;		/* exposant cadré 127, après */
      /* décalage de la mantisse  */

      ecr.mi.signe = lu.mhp.sig_man;	/* signe mantisse inchangé  */
      ecr.mi.man_22_16 = lu.mhp.man_20_15;	/* mantisse décalée /bit21hp */
      ecr.mi.man_15_9 = lu.mhp.man_14_8;	/* mantisse milieu          */
      ecr.mi.man_8_1 = lu.mhp.man_7_0;	/* mantisse pds faibles     */

      ecr.mi.man_0 = 0;		/* remplit dernier bit faibl */

      return ecr.mot_fl;
    }
}


/*----------------------------------------------------------------------*/
/* abs_fl_hp :                                                          */
/*       retourne la valeur absolue d'un flottant HP REAL*4             */
/*       version 3.00.00 du 30/10/1992, Christian ALLET                 */
/*       d'après la version 1.02 du 05/11/1989, ChA                     */
/*----------------------------------------------------------------------*/
long 
abs_fl_hp (float fl_in)		/* valeur négative     */
{
#if defined(PCAT) || defined(__i386__) || defined(__i486__) || defined(__i586__) || defined(__i686__) || defined(__x86_64__) 
  struct fl_HP_1
  {				/* de la gauche vers la droite   */
    unsigned sigexp:1;		/* poids faibles à gauche   */
    unsigned exp:7;
    unsigned man_7_0:8;

    unsigned man_15_8:8;	/* frontière de mot 16 bits      */
    unsigned man_21_16:7;
    unsigned sig_man:1;		/* poids forts à droite     */
  };
  struct fl_HP_2
    {
      unsigned low:16;		/* poids faibles à gauche   */

      unsigned man_20_8:14;	/* frontière de mot 16 bits      */
      unsigned man_21:1;
      unsigned sig_man:1;	/* poids forts à droite     */
    };

  struct fl_aux
    {
      unsigned pds_7_0:8;	/* poids faibles à gauche   */
      unsigned pds_15_8:8;

      unsigned pds_21_16:7;	/* frontière de mot 16 bits      */
      unsigned retenue:1;

      unsigned bidon:8;		/* poids forts à droite     */
    };
#endif

#ifdef   HP9000
  struct fl_HP_1
    {				/* de la droite vers la gauche   */
      unsigned sig_man:1;	/* poids forts à gauche     */
      unsigned man_21_16:7;
      unsigned man_15_8:8;	/* frontière 16 bits inutile ici */
      unsigned man_7_0:8;
      unsigned exp:7;
      unsigned sigexp:1;	/* poids faibles à droite   */
    };

  struct fl_HP_2
    {
      unsigned sig_man:1;	/* poids forts à gauche     */
      unsigned man_21:1;
      unsigned man_20_8:14;	/* frontière de mot 16 bits      */
      unsigned low:16;		/* poids faibles à droite   */
    };

  struct fl_aux
    {
      unsigned bidon:8;		/* poids forts à gauche     */
      unsigned retenue:1;
      unsigned pds_21_16:7;	/* frontière de mot 16 bits      */
      unsigned pds_15_8:8;
      unsigned pds_7_0:8;	/* poids faibles à droite   */
    };
#endif

  union
    {
      long int mot_il;
      float mot_fl;
      struct fl_HP_1 mhp;
      struct fl_HP_2 puis;	/* pour mettre 1 bit 1/2    */
    }
  lu, v_abs;

  union
    {
      long int mot_il;
      float mot_fl;
      struct fl_aux mhp;
    }
  aux, res;

  if (fl_in > 0)
    return fl_in;		/* pas de recherche    */

  lu.mot_fl = fl_in;		/* cas négatif, charge */

  aux.mot_il = ~0;		/* raz FFFFFFFF        */
  res.mot_il = 0;		/* raz                 */

  aux.mhp.pds_7_0 = lu.mhp.man_7_0;	/* poids faibles mantis */
  aux.mhp.pds_15_8 = lu.mhp.man_15_8;	/* poids milieu     "  */
  aux.mhp.pds_21_16 = lu.mhp.man_21_16;		/* poids forts      "  */

  res.mot_il = (~aux.mot_il) + 1;	/* complément à 2      */

  v_abs.mhp.sigexp = lu.mhp.sigexp;	/* signe exposant inchangé  */
  v_abs.mhp.exp = lu.mhp.exp;	/* exposant inchangé   */
  v_abs.mhp.man_7_0 = res.mhp.pds_7_0;	/* poids faibles       */
  v_abs.mhp.man_15_8 = res.mhp.pds_15_8;	/* poids milieu        */
  v_abs.mhp.man_21_16 = res.mhp.pds_21_16;	/* poids forts         */
  v_abs.mhp.sig_man = 0;	/* signe mantisse      */

  if (res.mhp.retenue)
    {				/* cas où l'exposant est modifié */
      res.mhp.retenue = 0;
      if (res.mot_il)		/* débordement à gauche mant */
	v_abs.mhp.exp = lu.mhp.exp >> 1;	/* décalage à droite exposan */

      else
	{			/* cas des puissances de 2  */
	  v_abs.mhp.exp = lu.mhp.exp + 1;	/* addition puissance 2 */
	  v_abs.puis.man_21 = 1;	/* bit de poids 1/2    */
	}
    }
/*  printf ("\nv_abs.mot_il = h%08X\n", v_abs.mot_il) ; */
  return v_abs.mot_il;
}

long
CnvHpI3e (unsigned long ndata,
	  long int *vect_HPflt,
	  float *vect_flt)
{
  unsigned long i;

  for (i = 0; i < ndata; i++)
    {
      vect_flt[i] = convfloat (vect_HPflt[i]);
    }

  return i;
}

/* fonction d'enrobage */

int
OP_CnvHpI3e (unsigned long Nbval, void *ArgList[], char *DiagExec)
{
  long CodRet;

  sprintf (DiagExec, "CnvHpI3e (%lu ech); ", Nbval);

  CodRet = CnvHpI3e (Nbval,
		     (long int *) ArgList[0],
		     (float *) ArgList[1]);

  sprintf (&(DiagExec[strlen (DiagExec)]), "%ld valeurs converties.", CodRet);

  return OP_OK;
}

void
ID_CnvHpI3e (oper * optr)
{
  strcpy (optr->Nom, "CnvHpI3e");
  optr->Version = "1.0";
  optr->Date = "01/21/96";
  optr->fctptr = OP_CnvHpI3e;
  optr->type = OPERTYP_FMT_TRANSFORM;
  optr->NbArg = 2;

  optr->Arg_Car[0].direction = DIR_IN;
  optr->Arg_Car[0].categorie = VECTOR;
  optr->Arg_Car[0].typ = ATYC_HF32;
  optr->Arg_Car[0].array_dim = "1";
  optr->Arg_Car[0].type_sample = "any";
  optr->Arg_Car[0].sample = "any";
  optr->Arg_Car[0].unite = "any";

  optr->Arg_Car[1].direction = DIR_OUT;
  optr->Arg_Car[1].categorie = VECTOR;
  optr->Arg_Car[1].typ = ATYC_IF32;
  optr->Arg_Car[1].array_dim = "1";
  optr->Arg_Car[1].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[1].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[1].sample = "$Arg1.sample";
  optr->Arg_Car[1].ref_time = "$Arg1.ref_time";
  optr->Arg_Car[1].unite = "$Arg1.unit";
  optr->Arg_Car[1].name = "$Arg1.name";
  optr->Arg_Car[1].en_name = "$Arg1.english_name";
  optr->Arg_Car[1].famille = "$Arg1.famille";
}
