*-------------------------------------------------------------------
* programme de calcul de flux - station type SAMER
*
*   calcul des flux de chaleur sensible et latente par la
*   methode aerodynamique, en utilisant 2 niveaux de mesure
*   de la vitesse du vent et de la temperature.
*
*  entrees :
* ==========
*    dv	    : reel   : ffhau - ffbas en m/s
*    ffhau  : reel   : vitesse du vent niveau sup. en m/s
*    dt_air : reel   : thaut - tbas ≥C
*    t      : reel   : tempe sous abri ≥C
*    rn     : entier : rayonnement net  W/m2
*    phi0   : entier : flux dans le sol  W/m2
*    hveg   : reel   : hauteur de vegetation  m
*    hbas   : reel   : hauteur niveau inf. des mesures  m
*    p      : reel   : pression  hPa
*    humid  : entier : humidite  %
*  sorties :
* ==========
*    hs     : entier : flux de chaleur sensible  W/m2
*    le     : entier : flux de chaleur latente  W/m2
*    z0     : reel   : rugosit≈  m
*    vlmon  : reel   : longueur de Monin Obukhov
*    ustar  : reel   : vitesse de frottement  m/s
*    tstar  : reel   : ?
*
*  remarques :
* --------------
*     1.5 m entre le niveau sup. et inf. des mesures
*     Les notations font reference a la note 6 de GMEI
*       x1 = niveau bas      x2 = niveau haut
*--------------------------------------------------------------------
c      implicit NONE

      subroutine calf_dp(dv,ffhau,dt_air,t,rn,phi0,hveg,hbas,p,humid,
     *	    hs,le,z0,vlmon,ustar,tstar)

      real karman
      integer rn,phi0,humid,hs,le

	vm=-999.
	ivm=nint(vm)
c initialisations des sorties
	hs=ivm
	vhs=vm
	le=ivm
	z0=vm
	vlmon=vm
	ustar=vm
	tstar=vm

c tests possibilites de calcul

	if ((dv.eq.vm).or.(dt_air.eq.vm).or.(t.eq.vm)) return
	if ((hveg.eq.vm).or.(hbas.eq.vm)) return
	pres=p
	if (p.eq.vm) pres=1000.
	hu=humid
	if (humid.eq.vm) hu=50.
	
c initialisations
	t0=273.15
	karman=.4
	cp=1005.

c calculs initiaux
	hdep=2.*hveg/3.
	hhau=hbas+1.5
	tk=vm
	if (t.ne.vm) tk=t+t0
	roo=rho(pres,t,hu)
	zu1=hbas-hdep
	zu2=hhau-hdep

c verification anemo bas hors vegetation
	if (hbas.lt.hveg) return

c cas de la "convection libre"
c---------------------------------
	if (dv.lt.0.) return
	if (dv.le..01) then
	  ustar=0.
	  tstar=vm
	  vlmon=0
	  vhs=0.
	  go to 20
	endif
	
c cas neutre
c---------------------------------
	if (abs(dt_air).le..01) then
	  ustar=karman*dv/alog(zu2/zu1)
	  tstar=0.
	  vlmon=9999.*sign(1.,dt_air)
	  vhs=0.
	  go to 20
	endif
	
c autres cas
c----------------
c calcul de L Monin-Obukhov par iterations
	niter=0
	vlmon=1000000.
10	continue
	niter=niter+1
	vlm1=vlmon
c calcul de ustar  equation 24
	deno=alog(zu2/zu1)-psim(zu2/vlm1)+psim(zu1/vlm1)
	ustar=karman*dv/deno
c calcul de tstar  equation 25
	deno=alog(zu2/zu1)-psih(zu2/vlm1)+psih(zu1/vlm1)
	tstar=karman*dt_air/deno
	vlmon=tk*ustar*ustar/(karman*9.81*tstar)
c verification de l'iteration sur vlmon
	coeff=vlmon-vlm1
	seuil=.05
	if (abs(vlmon).ge.1) then
	  coeff=coeff/vlmon
	  seuil=.01
	endif
c calcul de hs par equation 27
	if (abs(coeff).lt.seuil) then
	  vhs=-roo*cp*ustar*tstar
	else
	  if (niter.lt.25) then
	    go to 10
	  else
c formule de Itier : cas tres stable - non convergence
	    print *,'Itier'
	    dnum=karman*karman*roo*cp*dv*dt_air
	    vhs=(-dnum/(alog(zu2/zu1)**2.))/10.
	    ustar=vm
	    tstar=vm
	    vlmon=vm
	  endif
	endif

c calcul du flux de chaleur latente
c------------------------------------
20	continue
	hs=nint(vhs)
	if ((rn.ne.ivm).and.(phi0.ne.ivm)) le=rn-phi0-hs

c calcul de la rugosite
c----------------------
	if (ustar.gt..03) 
     *	  z0=exp(alog(zu2)-karman*(ffhau/ustar)-psim(zu2/vlmon))

c limitation de vlmon
c----------------------
	if (abs(vlmon).gt.9999) vlmon=sign(9999.,vlmon)

	return
	end

*******************************************************************
* psim = profil de vent
*******************************************************************

	function psim(csi)
	
c regime instable
	if (csi.le.0) then
	   x=(1-16*csi)**.25
	   psim=alog((1+x)*(1+x)*(1+x*x)/8.)-2*atan(x)+1.5707963
	else
	   psim=-5*csi
	endif
	return
	end

*******************************************************************
* psih = profil de tempe
*******************************************************************

	function psih(csi)
	
c regime instable
	if (csi.le.0) then
	   y=(1-16*csi)**.25
	   psih=2*alog((1+y*y)/2.)
	else
	   psih=-5*csi
	endif
	return
	end

*******************************************************************
	
***********************************************************************
*
*  @(#) rho.f -  libmto.a  -  Puech d.  -  05/87
*
*
*   objet :  calcul de la masse volumique d'une particule d'air humide
*  ========  definie par : pression , temperature , humidite .
*
*
*   reference :  triplet-roche     p.90,91
*  ============
*
*
*   entrees :
*  ===========
*	    arguments
*	   -----------
*    pres   : reel   : pression em mb
*    temp   : reel   : temperature en celsius
*    humi   : reel   : humidite en %
*
*
*   sortie :
*  ==========
*	    nom de fonction
*	   -----------------
*    rho     : reel   : masse en kg/m**3
*
*
*   fonction utilisee:
*  ====================
*    tvir_4m  ( bibmto.a )
*
***********************************************************************
 
	function rho(pres,temp,humi)
 
	t0=273.15
	ra=287.05
	tvk=tvir_4m(pres,temp,humi)+t0
	rho=(pres*100.)/(ra*tvk)
 
	return
	end
***********************************************************************

      function tvir_4m(pres,temp,humi)
c@(#)  function tvir(deg C)(pres(mb),temp(deg C),humi(%))
*************************************************************
*
*   objet :  calcul de la temperature virtuelle d'une particule
*  ========  donnee definie par : pression , temperature , humidite .
*    pres   : reel   : pression em mb
*    temp   : reel   : temperature en celsius
*    humi   : reel   : humidite en %
*    tvir   : reel   : temperature en celsius
*************************************************************
*
      character *20 sccsid
      data sccsid /'"@(#)tvir.f	1.1"'/
      ew=6.112*exp((17.67*temp)/(temp+243.5))
      e=humi*ew/100.
      rmel=.622*1000.*e/(pres-e)
      r=rmel*.001
      t0=273.15
      tk=temp+t0
      tvk=(1+1.608*r)*tk/(1+r)
      tvir_4m=tvk-t0
      return
      end
