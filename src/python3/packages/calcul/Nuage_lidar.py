#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" 

Clouderive.py : cette fonction trouve les bases, peaks et top d'un profil lidar PrF
                basé sur Pal, 1992 - Adapté par Mortier A.

   Input arguments
   ---------------
        - PrF : Matrice of RCS (vector)
        - Thr1 : coefficient
        - Thr2 : coefficient
        - z : range vector (m)
        - zmin : altitude beyond extrapolation is done (m)

  
  
   Output argument
   ---------------
  
        - baseok
        - peakok
        - topok
        - flagcld
  
   Auteur 
   ------
        - CNRM/GMEI:TRAMM  P. Richard Fevrier 2018 a partir d'un script
                 scilab ecrit par le LOA.
"""


import numpy as np

def Nuage_lidar (Pr,Thr1,Thr2, Gates, zmin) :

    z = Gates[0,:]
    vresol = z[1] - z[0]
    imin = np.argmin(abs(z - zmin))
    nproc=10

    nbech = len(Pr)

    BaseF = []
    BaseF= np.empty((nbech,6,))
    BaseF[:] = -1

    PeakF = []
    PeakF= np.empty((nbech,6,))
    PeakF[:] = np.nan

    TopF=[]
    TopF= np.zeros((nbech,6,))

    flagcld = np.zeros(nbech)

    flgt = 612

# pour chaque temps :
    for nc in np.arange(nbech) :

        z = Gates[nc,:]

        if ( np.isnan(Pr[nc,:]).any() or np.isnan(z[:]).any() ) :
            BaseF[nc,0:6] = np.nan 
            PeakF[nc,0:6] = np.nan 
            TopF[nc,0:6] = np.nan 
            flagcld[nc] =  np.nan 
            continue

        vec=np.arange(len(Pr))
        if nproc >= 2 :
            ind=np.arange(max(vec[nc]-int(nproc/2),0),min(vec[nc]+int(nproc/2)+1,len(vec)))
        else :
            ind=vec[nc]

        PrF=np.mean(Pr[ind,:], axis=0)


        baseok=np.array([],dtype=int)
        peakok=np.array([],dtype=int)
        topok=np.array([],dtype=int)
        baseok2=np.array([],dtype=int)
        peakok2=np.array([],dtype=int)
        topok2=np.array([],dtype=int)
        base=np.array([],dtype=int)
        top=np.array([],dtype=int)

        if max(PrF[0:100]) <= 0:
            peakok=np.nan
            baseok=np.nan
            topok=np.nan
            base=np.nan
            top=np.nan
            topok2=np.nan
            baseok2=np.nan
            peakok2=np.nan
        else :
            # - - - - - derivee par reg lineaire sur fenetre glissante - - - - -

            pas = 20
            slope = np.zeros(len(z))
            noise = np.zeros(len(z))
            for i in np.arange(int(pas/2),int(len(PrF)-pas/2-pas)) :

                # fast linear regression
                X = z[int(i-pas/2):int(i+pas/2)]
                Y = PrF[int(i-pas/2):int(i+pas/2)];
                X1 = np.ones((len(X),2))
                X1[:,-1] = X
                coefs = np.linalg.lstsq(X1, Y, rcond=None)
                slope[i]=coefs[0][1];

            slope[slope == 0 ] = -1


            #trouve les endroits ou la pente est nulle par changement de signe -
            sig=np.sign(slope)
            sigp1=sig[1:]
            dif=sig[0:-1]-sigp1;
            chgtsign=np.where(dif!=0)[0]
    
            base=np.where(dif==-2)[0]
            peak=np.where(dif==2)[0]
    
            base=base[base>imin]
            peak=peak[peak>imin]

            if len(base) > 0 :
                #si un pic en premier, force a chercher une base avant si possible
                if peak[0] <= base[0] :
                    #derivee seconde
                    slope2=np.zeros(len(slope))
                    slope2[:len(slope)-1]=slope[1:]-slope[0:-1]
                    indice=np.where(slope2[0:peak[0]]/max(slope2[1:peak[0]])>=0.25)[0]
                    if len(indice)>0 :
                        base = np.insert(base,0,indice[-1])
                    else :
                        base = np.insert(base,0,imin+1)

                peak=peak[base>imin+1]
                base=base[base>imin+1]

                #on calcule le bruit en dessous de la base
                pasnoise=8;
                noise=np.zeros(len(base));
                for i in np.arange(len(base)) :
                    if base[i] > pasnoise :
                        noise[i]=np.abs(np.std(PrF[base[i]-pasnoise:base[i]+1], ddof=1))
                    else :
                        break 

                # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
                #on extrapole le bruit de 30 a 15km, et un peu au sol ?
                #polynome d'ordre 2
                #conditions : c=min(noise) et denp.insert(ivee nulle en z=0
                c=min(noise)
                b=0
        
                #le point a 12000m appartient a la droite
                npas=10
                npas=4
                mm=np.argmin(abs((base+1)*vresol-8000))
                if mm>npas :
                    y1=np.mean(noise[mm-npas:mm+npas+1])
                else :
                    y1=np.mean(noise)

                x1=(base[mm]+1)*vresol
                a=(y1-c)/(x1**2)
                pf=a*z**2+b*z+c
        
                #verifie que termine par peak
                if len(base) > len(peak) :
                    base=base[0:len(peak)]
                else :
                    peak=peak[0:len(base)]

                # - - - - - - - - - - - - - T E S T - - - - - - - - - - - - - - - -
                test=[];
                for i in np.arange(len(base)) :
                    test_peak=np.mean(PrF[peak[i]-1:peak[i]+2])
                    test_base=np.mean(PrF[base[i]-1:base[i]+2])
                    if test_base < 0 :
                        test_base = 0

                    if test_peak-test_base>(Thr1*pf[peak[i]]) :
                        test.append(i)

                if len(test)>0 :
                    peakok=peak[test]
                    baseok=base[test]
            
                    #on limite le dernier pic neanmoins aux 15 premiers kms
                    indice=np.where(peakok<=15000/vresol)[0]
                    peakok=peakok[indice]
                    baseok=baseok[indice]
                else :
                    baseok=np.array([],dtype=int)
                    peakok=np.array([],dtype=int)


            if len(peakok) > 0 :
                # On regarde autour de chaque peak le max du PrF et le min du PrF pour la base sur une moyenne glissante
                for i in np.arange(len(peakok)) :
                    mm=np.argmax(PrF[peakok[i]-5:peakok[i]+6])
                    peakok[i]=peakok[i] - 5 + mm
            
            
                    #moyenne glissante
                    vec=np.arange(baseok[i]-5,baseok[i]+6)
            
                    vec_m=np.full(len(vec), np.nan)
                    for ii in np.arange(len(vec)) :
                        vec_m[ii]=np.mean(PrF[vec[ii]-2:vec[ii]+3])

                    #on se concentre sur le minimum de moyenne glissante
                    mm=np.argmin(vec_m)
            
                    mm2=np.argmin(abs(PrF[vec[mm]-3:vec[mm]+4]))
                    baseok[i]=vec[mm]-2+mm2
            
        
                #si en décalant les bases, 2 se superposent, alors on enleve le pic a dessus la base i
                for i in np.arange(len(baseok)-1) :
                    if baseok[i]==baseok[i+1] :
                        baseok[i+1]=1;
                        #le pic est le plus grand entre le i et le i+1
                        mm=np.argmax(PrF[peak[i:i+1]])
                        if mm==0 :
                            peakok[i+1]=1
                        else : 
                            peakok[i]=1

                baseok=baseok[(baseok)>1]
                peakok=peakok[(peakok)>1]
        
                #si en décalant, une base passe au dessus d'un pic, alors on suprime base et pic
                anomal=np.where(peakok-baseok<=0)
                peakok[anomal]=1
                baseok[anomal]=1
                peakok=peakok[(peakok)>1]
                baseok=baseok[(baseok)>1]

            # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    
                if  len(peakok)>0  :
                    # on vérifie que chacundes couches vérifie le critère nuages pour continuer
                    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
                    # - - - - - - - - - - - - - T E S T - - - - - - - - - - - - - - - G
                    MIN=abs(min(PrF[0:int(15000/vresol)]))+0.1
                    peakok2=np.array([],dtype=int)
                    topok2=np.array([],dtype=int)
                    baseok2=np.array([],dtype=int)
                    test=[]

                    for i in np.arange(len(peakok)) :
                        if abs((np.mean(PrF[peakok[i]])+MIN)/(np.mean(PrF[baseok[i]-1:baseok[i]+2])+MIN))>=1.5 :
                            test.append(i)

                    if len(test)>0  :
                        peakok2=peakok[test]
                        baseok2=baseok[test]

                    peakok=np.copy(peakok2)
                    baseok=np.copy(baseok2)

#la suite n'a de sens que si des peaks ont passé le test
            if len(peakok) > 0 :
   
            # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            # - - - - - - - - - - - - - - T O P - - - - - - - - - - - - - - - -
            #pour chaque pic trouvé, on regarde au dessus à partir de quand la derivee croise le zero
                base_tmp = np.copy(baseok)
                peak_tmp=[]
                indice = []
                for i in np.arange(len(peakok)-1) :
                    top = np.insert(top,i,0)
                    vec=np.arange(peakok[i],baseok[i+1]+1)
                #on ne garde que les indices dont le pr2 <= a la base(n)
                    indice=np.where(PrF[vec] <= PrF[baseok[i]])[0]
            
                    if len(indice) > 0 :
                        vec=vec[indice]
                        if len(vec) >= 5  : #se limite a 5 pr ne pas aller trop loin
                            mm=np.argmin(abs(slope[vec[0:5]]))
                        else :
                            mm=np.argmin(abs(slope[vec]))
               
                        top[i]=int(vec[mm])
                    else :
                    #si on ne trouve pas de valeur inférieur, alors supprime la base n+1
                        base_tmp[i+1]=1
        
                baseok=base_tmp[(base_tmp)>1]

                #on cherche alors le peak maximal
                for i in np.arange(len(baseok)) :
                #on cherche les peaks au dessus de la base(i)
                    if i < len(baseok) - 1 :
                        indice=np.where((peakok>baseok[i]) * (peakok<baseok[i+1]))[0]
                    else :
                        indice=np.where(peakok>baseok[i])[0]
            
                    mm=np.argmax(PrF[peakok[indice]])
                    peak_tmp.append(peakok[indice[mm]])

                top=top[(top)>0]
                peakok=peak_tmp
                i=len(peakok)-1

            #on recherche à partir du moment ou le signal devient inférieur à la base
                indice=np.where(PrF<PrF[baseok[-1]])[0]
                indice=indice[(indice)>peakok[-1]]
            #on recherche jusqu' la base du pic supérieur non retenu
            
                if len(indice)==0 :
                    top = np.insert(top,i,peakok[i]+1)
                elif len(indice)>=5 : #se limite à 5 pour ne pas aller trop loin
                    mm=np.argmin(abs(slope[indice[0:5]]))
                    top = np.insert(top,i,indice[mm])
                else :
                    mm=np.argmin(abs(slope[indice]))
                    top = np.insert(top,i,indice[mm])

            
                topok=np.copy(top)
                topok=topok[(topok)>0]
                peakok=np.copy(peak_tmp)
                if len(peakok) != len(topok) :
                    print(baseok)
                    print(topok)
                    print(peakok)

                # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
                #on minimise les top autour des indices trouv√É¬©s
                for i in np.arange(len(topok)) :
                    vec=np.arange(int(topok[i]-5),int(topok[i]+6))
                    vec=vec[(vec)<=len(PrF)-1]
                    mm=np.argmin(PrF[vec])
                    topok[i]=vec[mm]
        
                #si en dealant les tops, 2 se superposent, alors on enleve le pic a dessus la base i
                for i in np.arange(len(topok)-1) :
                    if topok[i]==topok[i+1] :
                        topok[i+1]=1;
                        baseok[i+1]=1
                        #le pic est le plus grand entre le i et le i+1
                        mm=np.argmax(PrF[peak[i,i+1]])
                        if mm==1  :
                            peakok[i+1]=1
                        else :
                            peakok[i]=1
        
                baseok=baseok[(baseok)>1]
                peakok=peakok[(peakok)>1]
                topok=topok[(topok)>1]

                if len(peakok)>0  :
                #si en décalant, une base passe au dessus d'un pic, alors on suprime base et pic
                    anomal=np.where(topok-baseok<=0)[0]
                    peakok[anomal]=1
                    baseok[anomal]=1
                    topok[anomal]=1
                    peakok=peakok[(peakok)>1]
                    baseok=baseok[(baseok)>1]
                    topok=topok[(topok)>1]
            
                    anomal=np.where(topok-peakok<=0)[0]
                    peakok[anomal]=1
                    baseok[anomal]=1
                    topok[anomal]=1
                    peakok=peakok[(peakok)>1]
                    baseok=baseok[(baseok)>1]
                    topok=topok[(topok)>1]
    
                    #un top doit etre en dessous de la base n+1, sinon élimine le trio n+1 ???
                    anomali=np.where(topok[0:-1]-baseok[1:]>0)[0]
                    peakok[anomali]=1
                    baseok[anomali]=1
                    topok[anomali]=1
                    peakok=peakok[(peakok)>1]
                    baseok=baseok[(baseok)>1]
                    topok=topok[(topok)>1]
    
                    #condition at top, P(top)<=P(base)
                    for i in np.arange(len(topok)-1) :
                        if PrF[topok[i]]>=PrF[baseok[i]] :
                            topok[i]=1
                            baseok[i+1]=1
                    #on recherche le pic max entre le pic ipeakok[indice] et i+1 et on vire l'autre
                            mm=np.argmax(PrF[peakok[i:i+2]])
                            if mm==0 :
                                peakok[i+1]=1
                            if mm==1 :
                                peakok[i]=1

                    baseok=baseok[(baseok)>1]
                    topok=topok[(topok)>1]
                    peakok=peakok[(peakok)>1]

                if len(peakok)>0  :
                    #condition at top, P(top)<=P(base_n+1)
                    for i in np.arange(len(topok)-1) :
                        if PrF[topok[i]]<=PrF[baseok[i+1]] :
                            topok[i]=1
                            baseok[i+1]=1
                    #on recherche le pic max entre le pic i et i+1 et on vire l'autre
                            mm=np.argmax(PrF[peakok[i:i+2]])
                            if mm==0 :
                                peakok[i+1]=1
                            if mm==1 :
                                peakok[i]=1

                    baseok=baseok[(baseok)>1]
                    topok=topok[(topok)>1]
                    peakok=peakok[(peakok)>1]

                if len(peakok) > 0 :
                #il faut que la PrF_base(n+1) soit inférieur au PrF_base(n), sinon même couche
                    ref=PrF[baseok[0]]
                    rec=[]
                    for i in np.arange(1,len(baseok)) :
                        if PrF[baseok[i]] <= ref :
                            ref=PrF[baseok[i]]
                            rec.append(i)
                        else :
                            baseok[i]=1;
                            topok[i-1]=1

                    baseok=baseok[(baseok)>1]
                    topok=topok[(topok)>1]
    
                if len(peakok) > 0 :
                #on cherche pour chaque base filtrée le peak maximal associé
                    peaklist=[]
                    baseok=baseok[(baseok)>1]
                    for i in np.arange(len(baseok)-1) :
                        peaklist.append(1)
                        indice=np.where((peakok>baseok[i]) * (peakok<baseok[i+1]))[0]
                        if len(indice)>0 :
                            mm=np.argmax(PrF[peakok[indice]])
                            peaklist[i]=peakok[indice[mm]]
                        else :
                            baseok[i]=1
                            peaklist[i]=1

                    i=len(baseok)-1
                    indice=np.where(peakok>baseok[i])[0]
                    mm=np.argmax(PrF[peakok[indice]])
                    peaklist.append(peakok[indice[mm]])
                    peakok=np.copy(peaklist)
                    peakok=peakok[(peakok)>1]
                    baseok=baseok[(baseok)>1]

                if len(peakok) > 0 :
                # - - - - - - - - - - - - - T E S T - - - - - - - - - - - - - - -
                    MIN=0
                    peakok2=np.array([],dtype=int)
                    topok2=np.array([],dtype=int)
                    baseok2=np.array([],dtype=int)

                    indlow=np.where(topok < 7500/vresol)[0]
                    if len(indlow) > 0 :
                        test1=np.where(abs((PrF[peakok[indlow]]+MIN)/(PrF[topok[indlow]]+MIN))>=Thr2)
                        if len(test1) > 0 :
                            peakok2=peakok[test1]
                            baseok2=baseok[test1]
                            topok2=topok[test1]

                    indhigh=np.where(topok>=7500/vresol)[0]
                    if len(indhigh) > 0  :
                        peakok2 = np.append(peakok2,peakok[indhigh])
                        baseok2 = np.append(baseok2,baseok[indhigh])
                        topok2 = np.append(topok2,topok[indhigh])
                else :
                    baseok=np.array([],dtype=int)
                    peakok=np.array([],dtype=int)
                    topok=np.array([],dtype=int)
                    baseok2=np.array([],dtype=int)
                    peakok2=np.array([],dtype=int)
                    topok2=np.array([],dtype=int)


        baseok2=z[baseok2[(baseok2)>1]]
        topok2=z[topok2[(topok2)>1]]
        peakok2=z[peakok2[(peakok2)>1]]

        BaseF[nc,0:len(baseok2)] = baseok2
        PeakF[nc,0:len(peakok2)] = peakok2
        TopF[nc,0:len(topok2)] = topok2
        flagcld[nc] = len(baseok2)

    return BaseF, PeakF, TopF, flagcld
