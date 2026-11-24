#include <Python.h>
/*** #include "oper.h"***/

#define OPLD_OK		 0
#define OPLD_ERROR      -1      /* generic error  */
#define OPLD_INVVAL     -2      /* Invalid parameter value */
#define OPLD_NOTFOUND   -3      /* File not found          */
#define OPLD_NOACCESS   -4      /* Couldn't access file   */
#define OPLD_NOMEM      -5      /* Memory allocation error */
#define OPLD_NOTALIB    -6      /* Bad format */

extern int
Init_Liste_Oper_dyn (const char *const PathLib, oper ** liste);

extern const char *
OPLD_erreur (int NumErreur);

extern void
Free_Liste_Oper (oper ** liste);

extern PyObject*
import_py_oper ( char *module, char *oper );

extern int
PyObject_to_ArgList ( PyObject *py_o, float **ArgList, int nbarg );

extern int 
PyObject_2_Ctab_float ( PyObject *py_o, float *Ctab );




