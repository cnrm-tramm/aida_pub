#!/usr/bin/env python3

import numpy as np

def Hauteur_CL_Lidar(pr2, z, base_cld, width_wave,thr_cloud,zmin_bl,zmax_bl,zmax_tl ) :
    """
    calculate height of boundary layer and top layer width a constant width wavelet
    
    Input
        pr2 : lidar signal
        base_cld : cloud base altitude 
        width_wave : width of wavelet : 210/15
        thr_cloud : threshold on convolution between RCS and wavelet to detect clouds : -10
        zmax_bl : maximum altitude for base layer
        zmax_tl : maximum altitude for top layer

    Output :
        z_bl : altitude of boundary layer
        z_tl : to altitude of bounbary layer


    Auteur :  CNRM/GMEI/TRAMM février 2018
                transcodage de scilab en Python a partir de la filiere BASIC du LOA 
                fonction scilab originale : cov_haarv2.sci


    """

    z = z[:,0]
    base_cld = base_cld[:,0]
    #Precaution car divise ensuite par PR2
    idx = np.where (pr2 == 0)
    if (not idx[0].any) == False :
        pr2[idx[0]]=1.E-8

    #enregistrement des valeurs zmax
    zmax_blrec=zmax_bl
    zmax_tlrec=zmax_tl

    z_bl = []
    z_tl = []
    
# on moyenne avant pour les tests mais ce sera à faire dans un autre
# operateur 

    # nproc = 10
    # vec=list(range(0, pr2.shape[0] ))
    # pr2_m = np.empty(pr2.shape)
    # for i in range(0, pr2.shape[0] ) :

    #     i1 = max (0, int(vec[i]-nproc/2) )
    #     i2 = min ( int(vec[i]+nproc/2), len(vec) -1 )
    #     #indok=list( range(i1, i2+1 )) 
    #     #idx=np.where( (ind>=0) & (ind<len(vec)))
    #     #indok=ind[idx[0]]
    #     pr2_m[i,:]=np.mean(pr2[i1:i2+1,:],axis=0)


    for pr2_i, base_i in zip(pr2, base_cld) :

        # - - - wavelet - - - 
        vresol=np.mean(np.diff(z))
        a=width_wave/vresol
        h=np.zeros(len(pr2_i))
        h[0:int(a/2)]=-1
        h[int(a/2):int(a)]=1

        #réinitialisation des altitudes max
        zmax_tl=zmax_tlrec
        zmax_bl=zmax_blrec
     
        #on normalise au max en dessous 2000m
        i2000 = np.argmin( abs(2000-z) )
        pr2_i=pr2_i/max(pr2_i[0:i2000+1])
    
        # - - - convolution - - - -
        con=np.convolve(pr2_i,h)
        con[0:int(a)]=np.nan #//n'a pas de sens quand en dessous
   
        # - - - - - - - - - - - - - - - - - - - - - - - - 
        #if cloud detected, zmax has to be under the base
        #si nuage bas, alors laisser trouver le pic du nuage, sinon on cherche en dessous
        if  base_i<=zmax_bl :
            if base_i>=1500 :
                zmax_bl=base_i-300
            else :
                zmax_bl=base_i
        # - - - - - - - - - - - - - - - - - - - - - - - - 
    
    
        iblmax = np.nanargmin(abs(zmax_bl-z))
        iblmin = np.nanargmin(abs(zmin_bl-z))
    
    
        #mprintf('%i %i\n',iblmin,iblmax);
        if iblmin>=iblmax :
            iblmin=iblmax-1

        # - - - couche limite : max de convolution
        #on vérifie que le minimum de la convolution est supérieur à -10. Sinon, nuage, cherche en dessous
        ind = np.where(con[0:int(iblmax)+1] <thr_cloud)[0]
        if len(ind)>0 :
            if ind[0]<=iblmax : 
                bl = np.nanargmax( con[iblmin:ind[0]])
                bl = bl+iblmin+1
            else :
                bl = np.nanargmax( con[iblmin:iblmax+1])
                bl =bl +iblmin+1
        else :
            try :
                bl = np.nanargmax(con[iblmin:iblmax+1])
                bl = bl +iblmin+1
            except :
                z_bl.append(np.nan)
                continue
    
    #     # - - - - - - - - - - - - - - - - - - - - - - - - 
    #     #if cloud detected, zmax has to be under the base
    #     if  base_i<=zmax_tlrec :
    #         if base_i>=1500 : 
    #             zmax_tl=base_i-300
    #         else :
    #             zmax_tl=base_i
    #     # - - - - - - - - - - - - - - - - - - - - - - - - 
    
    #     itlmax=np.argmin(abs(zmax_tl-z))
    
    
    #     # top layer    
    #     thr=3
    #     i6500=np.argmin(abs(6500.-z))
    #     i7000=np.argmin(abs(7000.-z))
    
    #     moy=np.mean(con[i6500:i7000+1])
    #     std=np.std(con[i6500:i7000+1])
    #     over=[]

    #     #print('i = {}, ind = {}, iblmin={}, iblmax={}, bl = {}, moy={}, std= {}'.format(i, ind, iblmin, iblmax, bl[i], moy, std) )

    #     while (len(over)==0) :
    #         if thr<=2.5 : 
    #             break

    #         thr=thr-0.05
    #         thr_over=(moy+thr*std)
        
    #         over= np.where( con[0:itlmax+1] >=thr_over)[0]
    
        # if len(over)>0 :
        #     #recupere juste si au dessus du seuil.
        #     tl=over[-1]-a/2
        #     print(z[tl])
        #     z_tl.append(z[tl])
        # else :
        #     z_tl.append(np.nan)

    
        bl=int(bl-a/2)

        z_bl.append(z[bl])
        z_tl = z_bl

    return z_bl,z_tl
