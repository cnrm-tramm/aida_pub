      SUBROUTINE ASSIET (JQUANT,TU,XLON,XLAT,CAP,ROLL,PITCH,
     + OFROL,OFTAG,SWDOWN,SWCOR)
C CORRECTION D'ASSIETTE POUR LES FLUX SW DESCENDANTS
c    -Auteur : Gérard Brogniez, mars 2013.
c        Groupe Interactions Rayonnement - Nuages
c        UMR CNRS 8518 - Laboratoire d’Optique Atmosphérique (LOA)
c        F - 59655 Villeneuve d’Ascq Cedex - France
c        http://www-loa.univ-lille1.fr/
c        Ajout de commentaires et adaptation au fonctionnement dans
c        l'environnement AIDA par Bruno Piguet, Meteo-France,
c        CNRM-GAME, Toulouse.
c
c    -Licence : Diffusion restreinte. Droit d'utilisation limité
c       au traitement des mesures des avions de recherche
c       environnementale français.
c  
c   JQUANT : Numero du jour dans l'année
c   TU : Heure TU, en secondes
c   XLON : Longitude
c   XLAT : Latitude
c   CAP : Cap geographique, en degrés
c   ROLL : roulis/gîte de la plate-forme (degrés, orientation :  ?usuelle avion ?)
c   PITCH : tangage de la plate-forme (degrés, orientation :  ?usuelle avion ?)
c   OFROL : Décalage entre le roulis de l'instrument et celui de la plate-forme
c   OFTAG : Décalage entre le tangage de l'instrument et celui de la plate-forme
c   SWDOWN : Flux SW descendant brut
c   SWCOR : Flux SW descendant corrigé de l'attitude
      IMPLICIT NONE
      INTEGER JQUANT
!     Version tableau : INTEGER JQUANT(*), etc ... ??
      DOUBLE PRECISION TU, XLON, XLAT
      DOUBLE PRECISION CAP, ROLL, PITCH
      DOUBLE PRECISION OFROL, OFTAG
      DOUBLE PRECISION OFROLL, OFTAGC
      DOUBLE PRECISION SWDOWN, SWCOR
      DOUBLE PRECISION PI, FAC
      DOUBLE PRECISION R, P, DELP
      DOUBLE PRECISION DSIR, DCOR, DSIP, DCOP
      DOUBLE PRECISION DSIA, DCOA, DTAH
      DOUBLE PRECISION DCX, DCY, DCZ
      DOUBLE PRECISION DNX, DNY, DNZ
      DOUBLE PRECISION HD
      DOUBLE PRECISION FM, FM0, FM1, FM2, FM3
      DOUBLE PRECISION AMU1, AM
      DOUBLE PRECISION THETA0, PHI0, AMUZERO, H0
      DOUBLE PRECISION XAS, XN
      DOUBLE PRECISION ZA, ZB, ZC
C-------------------------------------------------
      PI=DACOS(-1.0D+00); FAC=PI/180.0D+00
C Attention OFROL et OFTAG sont theoriquement figes pour un avion donne
C Les valeurs ci-dessous correspondent au F20
c      OFROL=-0.3D+00
c      OFTAG=-1.3D+00
C-------------------------------------------------
c      WRITE(6,*)'OFFSET ROULIS =',OFROL
c      WRITE(6,*)'OFFSET TANGAGE =',OFTAG
      OFROLL=OFROL*FAC
      OFTAGC=OFTAG*FAC
C-----------------------------------------------------
      HD=TU/3600.0D+00
      IF(CAP.LT.0.0D+00) CAP=CAP+360.0D+00
      CALL POSSOL(JQUANT,HD,XLON,XLAT,THETA0,PHI0,AMUZERO)

C----------------------------------------------------------------
C Calcul de la correction d'incidence solaire sur le capteur
    
      DELP=(PHI0-CAP)*FAC
      H0=(90.0D+00-THETA0)*FAC
      DSIA=DSIN(DELP);DCOA=DCOS(DELP);DTAH=DTAN(H0)
      R=ROLL*FAC;P=PITCH*FAC
      DSIR=DSIN(R);DCOR=DCOS(R);DSIP=DSIN(P);DCOP=DCOS(P)
      DCX=-DCOP*DCOA/DTAH-DSIP
      DCY=-(DSIP*DSIR*DCOA+DCOR*DSIA)/DTAH+DCOP*DSIR
      DCZ=-(DSIP*DCOR*DCOA-DSIR*DSIA)/DTAH+DCOP*DCOR
      DNX=DSIN(OFTAGC)
      DNY=DSIN(OFROLL)
      DNZ=DSQRT(1.0D0-DNX*DNX-DNY*DNY)
      XN=DNX*DCX+DNY*DCY+DNZ*DCZ

C----------------------------------------------------------------
C Correction de cosinus
      FM0=3.9D+00;FM1=-12.5D+00;FM2=17.5D+00;FM3=-8.9D+00 
      FM=FM0+FM1*AMUZERO+FM2*AMUZERO*AMUZERO+FM3*AMUZERO*AMUZERO*AMUZERO
      XAS=1.0D+00-FM/100.0D+00
C----------------------------------------------------------------
C 1/(Air Mass Factor)
C  Permet d'eventuellement ramener la mesure de SWdown a une incidence normale
      ZA=0.50572D+00;ZB=6.07995D+00;ZC=1.6364D+00
      AMU1=ZA*(THETA0+ZB)**(-ZC)
      AM=AMUZERO+AMU1
c     AM=1.0D+00/(AMUZERO+AMU1)
C---------------------------------------------------------------------------
C Impression des corrections
c     WRITE(6,*)HD,XLAT,XLON,CAP,DELP/FAC,R/FAC,P/FAC
c    &,THETA0,PHI0,XN,AMUZERO,XAS,AM
c      WRITE(6,*)HD,XLAT,XLON,AM,XN*XAS
C La correction consiste a diviser le flux SWdown par le produit XN*XAS
C--------------------------------------------------------------------------
      SWCOR = SWDOWN/(XN*XAS)
      RETURN
      END
