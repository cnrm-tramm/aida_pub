/***************************************************************
*
*  EQUATIONS for coincidence corrections.
*
*  ARGUMENTS 	IN	float 	art 	taux de comptage reel 
*		IN	float 	tau	temps de transit
*		
*		OUT	float 	Tbar	temps de transit moyen
*		OUT	float 	crt	taux de comptage "mesure"
*		OUT	float 	Al 	pertes d'activites  
*
*  REFERENCES	The procedures are described in two papers:
*     		Brenguier and Amodei,1989: JAOT, 6, 575-584.
*     		Brenguier ,1989: JAOT, 6, 585-598.
*
***************************************************************/

#include <math.h>

/************************************
* (taud = tau1)                    *
************************************/

void
equ1 (float art,
      float tau,
      float tau1_fs,
      float taur_fs,
      float *Tbar,
      float *crt,
      float *Al)
{
  float T;
  double X, Xd1;

  X = exp (-art * tau);
  Xd1 = exp (-art * tau1_fs);

  if (tau1_fs < tau)
    {
      *Tbar = ((1. - X * Xd1) / (art * X)) - tau1_fs;
      *crt = art * X;
      T = (taur_fs - tau + tau1_fs);
      if (T > 0.)
	*Al = X * (1. - Xd1) * T;
      else
	*Al = 0.;
    }
  else
    {
      *Tbar = ((1. - X * X) / (art * X)) - tau;
      *crt = art * X / (1. + art * X * (tau1_fs - tau));
      *Al = X * (1. - Xd1) * taur_fs;
    }
}

/*********************************************************
     taud=tau2
     idem as equ1 except for activity losses (2.10)
**********************************************************/

void
equ2 (float art,
      float tau,
      float tau1_fs,
      float tau2_fs,
      float taur_fs,
      float *Tbar,
      float *crt,
      float *Al)
{
  float T;
  double X, Xd1, Xd2;

  X = exp (-art * tau);
  Xd2 = exp (-art * tau2_fs);
  Xd1 = exp (-art * tau1_fs);

  if (tau2_fs < tau)
    {
      *Tbar = ((1. - X * Xd2) / (art * X)) - tau2_fs;
      *crt = art * X;
      T = (taur_fs - tau + tau2_fs);
      if (T > 0.)
	*Al = X * (1. - Xd1) * T;
      else
	*Al = 0.;
    }
  else
    {
      *Tbar = ((1. - X * X) / (art * X)) - tau;
      *crt = art * X / (1. + art * X * (tau2_fs - tau));
      *Al = X * (1. - Xd1) * taur_fs;
    }
}
