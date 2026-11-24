/* déclaration de la routine en FORTRAN
 * pour appel depuis le C */

extern void
assiet (const int *JQUANT, const double *TU, const double *XLON, const double *XLAT,
        const double *CAP, const double *ROLL, const double *PITCH,
        const double *OFROL, const double *OFTAG, const double *SWDOWN, double *SWCOR);
