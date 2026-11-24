/******************************************************************
*
* OPERATOR      Poly1_seuil_flt.c   FUNCTION  ANSI-C
*
* PURPOSE       Applique un polynome de degré 1 selon la valeur
* du paramètre par rapport à un seuil donné 
*
* DESCRIPTION    
*
* VERSION       $Revision: 5097 $
*
* ARGUMENTS   IN  float  X_in		Any      "X" parametre d'entree 
* 	      IN  float  Seuil		Any      Seuil appliqué à X pour le choix du polynome
*             IN  float  A_0     	Any      Coefficient de degre 0 si X < Seuil
*             IN  float  A_1     	Any      coefficient de degre 1 si X < Seuil 
*             IN  float  B_0     	Any      Coefficient de degre 0 si X >= Seuil
*             IN  float  B_1     	Any      coefficient de degre 1 si X >= Seuil 
*	      IN  char   unit_out                Unite  du resultat 
*
*             OUT float  X_out   	unit_out Resultat
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
unsigned long
Poly1_seuil_flt (unsigned long NLoop,
		 const float *X_in,
		 float Seuil, 
		 float A_0,
		 float A_1,
                 float B_0,
                 float B_1,
                 float *X_out)
{
  unsigned long i;

  for (i = 0; i < NLoop; i++)
    {
      if (X_in[i] < Seuil )
	{
	  X_out[i] = A_0 + A_1* X_in[i];
	}
      else
	{
	  X_out[i] = B_0 + B_1* X_in[i];
	}

    }
  return 0;
}


/* la fonction d'enrobage classique */

int
OP_Poly1_seuil_flt (unsigned long NbVal, void *ArgList[], char *DiagExec)
{
  int CodRet;
  int NCar;

  NCar = sprintf (DiagExec, "Poly1_seuil_flt : (%ld echant.) ", NbVal) ;
  if (NCar < 0)
    NCar = 0;
  DiagExec += NCar;

  /* L'argument Nr 6 n'est pas passé à la routine de calcul : il ne
   * sert qu'à remplir le champ "unit" du vecteur de sortie. */
  CodRet = Poly1_seuil_flt (NbVal,
			    (float *) ArgList[0],
			    *((float *) ArgList[1]),
			    *((float *) ArgList[2]),
			    *((float *) ArgList[3]),
			    *((float *) ArgList[4]),
			    *((float *) ArgList[5]),
                            (float *) ArgList[7]);


  return OP_OK;
}

/* la fonction de description de l'operateur et ses arguments */

void
ID_Poly1_seuil_flt (oper * optr)
{
  int i; 

  strcpy (optr->Nom, "Poly1_seuil_flt");
  optr->Version = "$Revision: 5097 $";
  optr->Date = "$Date: 2013-03-25 13:23:40 +0100 (lun. 25 mars 2013) $";
  optr->fctptr = OP_Poly1_seuil_flt;
  optr->NbArg = 8;

  /* X_in */
  optr->Arg_Car[0].direction = DIR_IN;
  optr->Arg_Car[0].categorie = VECTOR;
  optr->Arg_Car[0].typ = ATYC_IF32;
  optr->Arg_Car[0].array_dim = "1";
  optr->Arg_Car[0].type_sample = "any";
  optr->Arg_Car[0].sample = "any";
  optr->Arg_Car[0].unite = "any";
  optr->Arg_Car[0].famille = "any";

  for (i =1 ; i<= 5; i++) 
     {
  	optr->Arg_Car[i].direction = DIR_IN;
  	optr->Arg_Car[i].categorie = COEFFICIENT;
  	optr->Arg_Car[i].array_dim = "1";
  	optr->Arg_Car[i].typ = ATYC_IF32;
  	optr->Arg_Car[i].unite = "any";
  	optr->Arg_Car[i].type_sample = NULL;	/* sans signification pour COEFFICIENT */
  	optr->Arg_Car[i].sample = NULL;
      }

  optr->Arg_Car[6].direction = DIR_IN;
  optr->Arg_Car[6].categorie = COEFFICIENT;
  optr->Arg_Car[6].array_dim = "1";
  optr->Arg_Car[6].typ = ATYC_STRING;
  optr->Arg_Car[6].type_sample = NULL;
  optr->Arg_Car[6].sample = NULL;
  optr->Arg_Car[6].unite = "any";

  optr->Arg_Car[7].direction = DIR_OUT;
  optr->Arg_Car[7].categorie = VECTOR;
  optr->Arg_Car[7].typ = ATYC_IF32;
  optr->Arg_Car[7].array_dim = "1";
  optr->Arg_Car[7].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[7].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[7].sample = "$Arg1.sample";
  optr->Arg_Car[7].ref_time = "$Arg1.ref_time";
  optr->Arg_Car[7].unite = "$Arg7";
  optr->Arg_Car[7].famille = "$Arg1.famille";
}
