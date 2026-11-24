/*****************************************************
*
* OPERATOR         ProfilMobile2geo_1D.c   FUNCTION  ANSI-C
*
* PURPOSE          rotates vertical profile from a mobile platform
*                  coordinatesi to geographic coordinates
*
* DESCRIPTION      Convert coordinates of a 1D-vector vector expressed in
*                  a mobile platform referential to a geographical 
*                  referential, according to its heading, roll and pitch.
*
* VERSION          1.1
*
* ARGUMENTS  
*            IN   float   X  		any     Data from sensor (use o,nly for $Arg1.bornes) 
*            IN   float   Z_x  		m       Vertical coordinates of data related to the plateform ($Arg1.bornes) 
*            IN   float   nb_z  		X array dimension  ($Arg1.array_dim)
*            IN   float   vert_direction     	1 upward direction, -1 downward  of X measurements
*	     IN	   float   Roul 	degree  Roll angle of the platform
*	                                         (positive when right/starboard
*	                                         side is sunken)
*	     IN    float   Tang 	degree   Pitch angle of the platform
*	                                         (positive when the nose is risen)
*	                           
*	     IN    float   Alti  	m      	Altitude of mobile
*
*	     OUT   float   Z   		m	Altitude of X measurements
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
* CHANGES          
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
#include "load_oper.h"

#include <Python.h>
#include <numpy/arrayobject.h>


void
ProfilMobile2geo_1D (unsigned long NLoop,
	       const float *X,
	       const float *Z_x,
	       const int nb_z,
	       const int vert_direction,
	       const float *Roul,
	       const float *Tang, 
	       const float *Alti, 
	       float *Alti_x)
{
  unsigned long i, k;
  register double coro, cota, d_vert_dir;
  register double Deg2Rad = M_PI / 180.0;
  register double Roul_rad, Tang_rad;
  double Z_xmoy[nb_z];

  d_vert_dir = (double)vert_direction;

  /* le tableau de bornes Z_x est un tableau de dimension [nb_z, 2] 
   * on fait la moyenne des bornes */
  for ( k= 0; k < nb_z; k++ )
     {
      Z_xmoy[k] = ( Z_x[k*2] + Z_x[k*2+1])/2.;
     }
  for (i = 0; i < NLoop; i++)
    {
      Roul_rad = Roul[i] * Deg2Rad;
      Tang_rad = Tang[i] * Deg2Rad;

      coro = cos (Roul_rad);
      cota = cos (Tang_rad);


      for ( k= 0; k < nb_z; k++ )
        {
	  Alti_x[ i*nb_z + k] = Alti[i] + d_vert_dir * cota*coro * Z_xmoy[k]  ;
	}

    }
}


/* la fonction d'enrobage classique */

int
OP_ProfilMobile2geo_1D (unsigned long NbVal, void *ArgList[], char *DiagExec)
{

  int codret, k;
  int Nbcol;
  PyObject *pArgs, *pValue, *pFunc;
  float *bornes;
  
  /* on récupére le tableau de bornes à partir de ArgListe[2] */
  Py_Initialize();
  import_array();

  Nbcol = *(int*)ArgList[2];

  bornes = (float *)malloc( sizeof(float)*Nbcol*2);
 
  pFunc = import_py_oper ( "AIDA", "strBornes_to_array");

  pArgs = PyTuple_New(1);
  pValue = PyUnicode_FromString((char*)ArgList[1]);
  PyTuple_SetItem(pArgs, 0, pValue);
  PyErr_Print();

  pValue = PyObject_CallObject(pFunc, pArgs);
  PyErr_Print();
  codret=PyObject_to_ArgList ( pValue, &bornes, 1 );
  Py_DECREF(pFunc); 
  Py_DECREF(pArgs);
  Py_DECREF(pValue);


  (void) sprintf (DiagExec, "ProfilMobile2geo_1D, NbVal=%lu", NbVal);

  ProfilMobile2geo_1D (NbVal,
		 (float *) ArgList[0],
		 bornes,
		 *((int *) ArgList[2]),
		 *((int *) ArgList[3]),
		 (float *) ArgList[4],
		 (float *) ArgList[5],
		 (float *) ArgList[6],
         (float *) ArgList[7]);

  free(bornes);

  return OP_OK;
}

void
ID_ProfilMobile2geo_1D (oper * optr)
{
  strcpy (optr->Nom, "ProfilMobile2geo_1D");
  optr->Version = "$Revision: 5097 $";
  optr->Date = "$Date: 2013-03-25 13:23:40 +0100 (lun. 25 mars 2013) $";
  optr->fctptr = OP_ProfilMobile2geo_1D;
  optr->NbArg = 8;

  optr->Arg_Car[0].direction = DIR_IN;
  optr->Arg_Car[0].categorie = VECTOR;
  optr->Arg_Car[0].typ = ATYC_IF32;
  optr->Arg_Car[0].array_dim = "*";
  optr->Arg_Car[0].type_sample = "any";
  optr->Arg_Car[0].sample = "any";
  optr->Arg_Car[0].unite = "any";
  optr->Arg_Car[0].famille = "any";

  optr->Arg_Car[1].direction = DIR_IN;
  optr->Arg_Car[1].categorie = COEFFICIENT;
  optr->Arg_Car[1].typ = ATYC_STRING;
  optr->Arg_Car[1].array_dim = "";
  optr->Arg_Car[1].unite = "m";
  optr->Arg_Car[1].sample = "";
  optr->Arg_Car[1].famille = "";

  optr->Arg_Car[2].direction = DIR_IN;
  optr->Arg_Car[2].categorie = COEFFICIENT;
  optr->Arg_Car[2].typ = ATYC_I32;
  optr->Arg_Car[2].array_dim = "1";
  optr->Arg_Car[2].sample = "";
  optr->Arg_Car[2].unite = "any";
  optr->Arg_Car[2].famille = "";

  optr->Arg_Car[3].direction = DIR_IN;
  optr->Arg_Car[3].categorie = COEFFICIENT;
  optr->Arg_Car[3].typ = ATYC_I32;
  optr->Arg_Car[3].array_dim = "1";
  optr->Arg_Car[3].sample = "";
  optr->Arg_Car[3].unite = "any";
  optr->Arg_Car[3].famille = "";

  /* Roul */
  optr->Arg_Car[4].direction = DIR_IN;
  optr->Arg_Car[4].categorie = VECTOR;
  optr->Arg_Car[4].typ = ATYC_IF32;
  optr->Arg_Car[4].array_dim = "1";
  optr->Arg_Car[4].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[4].type_sample = "any";
  optr->Arg_Car[4].sample = "any";
  optr->Arg_Car[4].unite = "degree";
  optr->Arg_Car[4].famille = "attitude";

  /* Tang */
  optr->Arg_Car[5].direction = DIR_IN;
  optr->Arg_Car[5].categorie = VECTOR;
  optr->Arg_Car[5].typ = ATYC_IF32;
  optr->Arg_Car[5].array_dim = "1";
  optr->Arg_Car[5].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[5].type_sample = "any";
  optr->Arg_Car[5].sample = "any";
  optr->Arg_Car[5].unite = "degree";
  optr->Arg_Car[5].famille = "attitude";

  /* Alti */

  optr->Arg_Car[6].direction = DIR_IN;
  optr->Arg_Car[6].categorie = VECTOR;
  optr->Arg_Car[6].typ = ATYC_IF32;
  optr->Arg_Car[6].array_dim = "1";
  optr->Arg_Car[6].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[6].type_sample = "any";
  optr->Arg_Car[6].sample = "any";
  optr->Arg_Car[6].unite = "m";
  optr->Arg_Car[6].famille = "altitude";
	
  optr->Arg_Car[7].direction = DIR_OUT;
  optr->Arg_Car[7].categorie = VECTOR;
  optr->Arg_Car[7].typ = ATYC_IF32;
  optr->Arg_Car[7].array_dim = "$Arg1.array_dim";
  optr->Arg_Car[7].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[7].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[7].sample = "$Arg1.sample";
  optr->Arg_Car[7].ref_time = "$Arg1.ref_time";
  optr->Arg_Car[7].bornes = "$Arg1.bornes";
  optr->Arg_Car[7].unit_bornes = "$Arg1.unit_bornes";
  optr->Arg_Car[7].unite = "m";
  optr->Arg_Car[7].famille = "\"altitude\"";
}
