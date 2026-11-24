*-------------------------------------------------------------------
* programme de calcul de Delta-Q, station SAMER/GILL
*
*   calcul des profils d'humidite deduit du calcul des
*   flux de chaleur sensible et latente par la
*   methode aerodynamique, en utilisant 2 niveaux de mesure
*   de la vitesse du vent et de la temperature.
*
*  entrees :
* ==========
*    dv	    : reel   : ffhau - ffbas en m/s
*    dt_air : reel   : thaut - tbas en deg C
*    t      : reel   : tempe sous abri deg C
*    p      : reel   : pression a 2 metres hpa
*    tv     : reel   : tempe virtuelle deg C
*    hveg   : reel   : hauteur de vegetation  m
*    hbas   : reel   : hauteur niveau inf. des mesures (1,70)  m
*    le     : reel   : flux de chaleur latente methode des correlations W/m2
*  sorties :
* ==========
*    qstar  : reel   : ?
*    deltaq : reel   : difference d'humidite entre hgill et hbas
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

      subroutine caldq_ot(dv,dt_air,t,p,tv,hveg,hbas,le,qstar,deltaq)

c declarations

      real dv, dt_air, t, p, tv, hveg, hbas, le, qstar, deltaq
      real karman, tk, tvk

c initialisations

	vm=-999.

	qstar=vm
	deltaq=vm
	tk=vm

	t0=273.15
	karman=.4
	cp=1005.
	hhau=6.

c tests possibilites de calcul

	if ((dv.eq.vm).or.(t.eq.vm)) return
	if (dt_air.eq.vm) return
	if ((hveg.eq.vm).or.(hbas.eq.vm)) return
	if (le.eq.vm) return
		pres=p
	if (p.eq.vm) pres=1013.
	
c calculs initiaux
	hdep=2.*hveg/3.
	if (t.ne.vm) tk=t+t0
	if (tv.ne.vm) tvk=tv+t0
	zu1=hbas-hdep
	zu2=hhau-hdep
	roo=roh(pres,tvk)

c verification anemo bas hors vegetation
	if (hbas.lt.hveg) return

	print *,'In F, LE=', le

c cas de la "convection libre"
c---------------------------------
	if (dv.lt.0.) return
	if (dv.le..01) then
	  ustar=0.
	  deltaq=vm
	  qstar=vm
	  go to 20
	endif
	
c cas neutre
c---------------------------------
	if (abs(dt_air).le..01) then
	  ustar=karman*dv/alog(zu2/zu1)
	  qstar=-le/(roo*ustar*lw(t))
	  deltaq=qstar*alog(zu2/zu1)/karman
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
        deno1=alog(zu2/zu1)-psiv(zu2/vlm1)+psiv(zu1/vlm1)
	ustar=karman*dv/deno1
c calcul de tstar  equation 25
        deno=alog(zu2/zu1)-psie(zu2/vlm1)+psie(zu1/vlm1)
        tstar=karman*dt_air/deno
        vlmon=tk*ustar*ustar/(karman*9.81*tstar)
c verification de l'iteration sur vlmon
	coeff=vlmon-vlm1
	seuil=.05
	if (abs(vlmon).ge.1) then
	  coeff=coeff/vlmon
	  seuil=.01
	endif
c calcul de deltaq par equation 27
	if (abs(coeff).lt.seuil) then
          qstar=-le/(roo*ustar*lw(t))
	  deltaq=qstar*deno/karman
c     deltaq=-le*deno/(roo*ustar*karman*lw(t))
	else
	  if (niter.lt.25) then
	    go to 10
	  else
c formule de Itier : cas tres stable - non convergence
	    print *,'Itier'
	    deltaq=vm
	    qstar=vm
	  endif
	endif

c------------------------------------
20	continue

c limitation de vlmon
c----------------------

        if (abs(vlmon).gt.9999) vlmon=sign(9999.,vlmon)
	return
	end

********************************************************************
* lw = chaleur latente de vaporisation - temp en degres C, en J/deg/g
********************************************************************

        function lw(temp)
	lw=(2.501-(.00237*temp))*1.e+03
	return
	end

*********************************************************
* psiv = profil de vent (psiv=psim)
**********************************************************

        function psiv(csi)
c regime instable
        if (csi.le.0) then
	x=(1-16*csi)**.25
	psiv=alog((1+x)*(1+x)*(1+x*x)/8.)-2*atan(x)+1.5707963
	else
       		psiv=-5*csi
	endif
	return
	end

*******************************************************************
* psie = profil de temperature et d'humidite (psie=psih)
*******************************************************************

	function psie(csi)
	
c regime instable
	if (csi.le.0) then
		y=(1-16*csi)**.25
		psie=2*alog((1+y*y)/2.)
	else
	   psie=-5*csi
	endif
	return
	end

***************************************************************
*   rho = densite de l'air en kg/m**3 (pres en hPa)
***************************************************************

        function roh(pres,tvk)

        ra=287.05

        roh=(pres*100.)/(ra*tvk)

        return
        end
********************************************************************
