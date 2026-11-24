*-------------------------------------------------------------------
* programme de calcul de Delta-T, station SAMER/GILL
*
*   calcul des profils de temperatures deduit du calcul des
*   flux de chaleur sensible et latente par la
*   methode aerodynamique, en utilisant 2 niveaux de mesure
*   de la vitesse du vent et de la temperature.
*
*  entrees :
* ==========
*    dv	    : reel   : ffhau - ffbas en m/s
*    t      : reel   : tempe sous abri deg C
*    p      : reel   : pression a 2 metres hpa
*    tv     : reel   : tempe virtuelle deg C
*    hveg   : reel   : hauteur de vegetation  m
*    hs     : reel   : flux de chaleur sensible methode des correlations W/m2
*  sorties :
* ==========
*    tstar  : reel   : ?
*    deltat : reel   : difference de temperatures entre hgill et hbas
*
*  remarques :
* --------------
*     le niveau sup. est a 6 m pour le gill
*     le niveau inf pour les vents
*     est le niveau de mesure du vent le plus proche de 1,70
*     Les notations font reference a la note 6 de GMEI
**    lw   : chaleur en j/g :
**    calcul de la chaleur latente de vaporisation d'une
**    particule definie par sa temperature .
*--------------------------------------------------------------------
c      implicit NONE

      subroutine caldt_ot(dv,t,p,tv,hveg,hs,tstar,deltat)

c declarations

      real dv, t, p, tv, hveg, hs, tstar, deltat
      real karman, tk, tvk

c initialisations

	vm=-999.

	tstar=vm
	deltat=vm
	tk=vm

	t0=273.15
	karman=.4
	cp=1005.
	hhau=6.
	hbas=1.7

c tests possibilites de calcul

	if ((dv.eq.vm).or.(t.eq.vm)) return
	if ((hveg.eq.vm).or.(hbas.eq.vm)) return
	if (hs.eq.vm) return
		pres=p
	if (p.eq.vm) pres=1013.
	
c calculs initiaux
	hdep=2.*hveg/3.
	if (t.ne.vm) tk=t+t0
	if (tv.ne.vm) tvk=tv+t0
	zu1=hbas-hdep
	zu2=hhau-hdep
	roo=rhoh(pres,tvk)

c verification anemo bas hors vegetation
	if (hbas.lt.hveg) return

c cas de la "convection libre"
c---------------------------------
	if (dv.lt.0.) return
	if (dv.le..01) then
	  ustar=0.
	  deltat=vm
	  tstar=vm
	  go to 20
	endif
	
c cas neutre
c---------------------------------
	if (abs(hs).eq.0.) then
	  tstar=0.
	  deltat=0.
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
c Test de coherence sur les valeurs de L M-Ob (valable pour Escompte)	
	if (abs(1/vlm1).gt..05) goto 20
c calcul de ustar  equation 24
        deno1=alog(zu2/zu1)-psivt(zu2/vlm1)+psivt(zu1/vlm1)
	ustar=karman*dv/deno1
c calcul de tstar  equation 25
        deno=alog(zu2/zu1)-psit(zu2/vlm1)+psit(zu1/vlm1)
        tstar=-hs/(roo*cp*ustar)
        vlmon=tk*ustar*ustar/(karman*9.81*tstar)
c verification de l'iteration sur vlmon
	coeff=vlmon-vlm1
	seuil=.05
	if (abs(vlmon).ge.1) then
	  coeff=coeff/vlmon
	  seuil=.01
	endif
c calcul de deltat par equation 27
	if (abs(coeff).lt.seuil) then
	  deltat=tstar*deno/karman
	else
	  if (niter.lt.25) then
	    go to 10
	  else
c formule de Itier : cas tres stable - non convergence
	    print *,'Itier'
            deltat=-alog(zu2/zu1)*alog(zu2/zu1)*10*hs/roo*cp*dv
	    tstar=vm
	  endif
	endif

c------------------------------------
20	continue

c limitation de vlmon
c----------------------

        if (abs(vlmon).gt.9999) vlmon=sign(9999.,vlmon)
	return
	end

*********************************************************
* psiv = profil de vent (psiv=psim)
**********************************************************

        function psivt(csi)
c regime instable
        if (csi.le.0) then
	x=(1-16*csi)**.25
	psivt=alog((1+x)*(1+x)*(1+x*x)/8.)-2*atan(x)+1.5707963
	else
       		psivt=-5*csi
	endif
	return
	end

*******************************************************************
* psie = profil de temperature et d'humidite (psie=psih)
*******************************************************************

	function psit(csi)
	
c regime instable
	if (csi.le.0) then
		y=(1-16*csi)**.25
		psit=2*alog((1+y*y)/2.)
	else
	   psit=-5*csi
	endif
	return
	end

***************************************************************
*   rho = densite de l'air en kg/m**3 (pres en hPa)
***************************************************************

        function rhoh(pres,tvk)

        ra=287.05

        rhoh=(pres*100.)/(ra*tvk)

        return
        end
********************************************************************
