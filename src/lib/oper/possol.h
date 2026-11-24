/* déclaration de la routine en FORTRAN
 * pour appel depuis le C */

extern void
possol (const int *JQUANT, const double *TU, const double *XLON,
	const double *XLAT, double *THETA0, double *PHI0, double *AMUZERO);
