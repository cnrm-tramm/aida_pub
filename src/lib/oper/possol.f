      SUBROUTINE possol(JQUANT,HD,XLON,XLAT,THETA0,PHI0,AMUZERO)
C POSITION DU SOLEIL(ANGLE ZENITHAL,AZIMUTAL,ANGLE PHI0 EN DEGRES)
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
c     Arguments :
c     HD : Heure UTC (heure décimale)
c     XLON : Longitude
c     XLAT : Latitude
      IMPLICIT NONE
      INTEGER JQUANT
      DOUBLE PRECISION HD, XLON, XLAT, THETA0, PHI0, AMUZERO
      DOUBLE PRECISION A0, A1, A2, A3, A4
      DOUBLE PRECISION B0, B1, B2, B3, B4, B5, B6
      DOUBLE PRECISION PI, FAC, PI2
      DOUBLE PRECISION XJ
      DOUBLE PRECISION TET, CT, ST, C2T, S2T, C3T, S3T
      DOUBLE PRECISION AH, AZ, AZIM, CAZ
      DOUBLE PRECISION ET, TSM, TSV
      DOUBLE PRECISION DELTA, ELEV
      DOUBLE PRECISION XLA
      PI=DACOS(-1.0D+00);FAC=PI/180.0D+00;PI2=2.0D+00*PI
C**************************************************
      A0=-.000075D+00;A1=-.001868D+00;A2= .032077D+00
      A3= .014615D+00;A4= .040849D+00
      B0= .006918D+00;B1=-.399912D+00;B2= .070257D+00;B3=-.006758D+00
      B4= .000907D+00;B5=-.002697D+00;B6= .001480D+00
      XJ=FLOAT(JQUANT)
      TET=2.0D+00*PI*(XJ-1.0D+00)/365.0D+00
      CT = DCOS(TET); ST = DSIN(TET)
      C2T = DCOS(2.0D+00*TET); S2T = DSIN(2.0D+00*TET)
      C3T = DCOS(3.0D+00*TET); S3T = DSIN(3.0D+00*TET)
      XLA = XLAT*FAC
C-----------------------------------------
C TEMPS SOLAIRE MOYEN (HEURE DECIMALE)
      TSM = HD + XLON/15.0D+00
C-----------------------------------------
C EQUATION DU TEMPS (en mn.dec)
      ET = A0 + A1*CT + A2*ST + A3*C2T + A4*S2T
      ET = ET*12.0D+00*60.0D+00/PI
C-----------------------------------------
C TEMPS SOLAIRE VRAI(heure decimale)
      TSV = TSM-ET/60.0D+00
C-----------------------------------------
C ANGLE HORAIRE (heure decimale)
      AH = TSV-12.0D+00
C ANGLE HORAIRE (radian)
      AH = AH*15.0D+00*FAC
C-----------------------------------------
C DECLINAISON SOLAIRE (radian)
      DELTA = B0 + B1*CT + B2*ST + B3*C2T + B4*S2T + B5*C3T + B6*S3T
C-----------------------------------------
C POSITION DU SOLEIL
      AMUZERO = DSIN(XLA)*DSIN(DELTA)+DCOS(XLA)*DCOS(DELTA)*DCOS(AH)
      ELEV = DASIN(AMUZERO)
      AZ = DCOS(DELTA)*DSIN(AH)/DCOS(ELEV)
c     AZ=test_limit(DCOS(DELTA)*DSIN(AH)/DCOS(ELEV))
      if(az.gt.1.0d+00) az=1.0d+00
      if(az.lt.-1.0d+00) az=-1.0d+00
      CAZ = -DCOS(XLA)*DSIN(DELTA)+DSIN(XLA)*DCOS(DELTA)*DCOS(AH)
      CAZ = CAZ/DCOS(ELEV)
      AZIM = DASIN(AZ)
      IF(CAZ.LE.0.) AZIM=PI-AZIM
      IF(CAZ.GT.0.AND.AZ.LE.0) AZIM=2.0D+00*PI+AZIM
      AZIM = AZIM+PI
      IF(AZIM.GT.PI2) AZIM=AZIM-PI2
C ANGLE SOLAIRE ZENITHAL
      THETA0 = 90.0D+00-ELEV/FAC
C ANGLE SOLAIRE AZIMUTAL
      PHI0 = AZIM/FAC
      RETURN
      END
C =======================================================
