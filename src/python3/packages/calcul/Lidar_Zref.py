#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import numpy as np

def Lidar_Zref(x, z, z1, z2, step) :
    """ 
    Lidar_Zref : calcul altitude  reference Lidar 

    Input arguments
    ---------------
  
        - x: the Pr2 signal from the LIDAR remote sensing
        - z: altitudes above the ground level (in meters)
        - z1: minimal altitude for reference altitude (in meters)
        - z2: maximal altitude for reference altitude (in meters)
        - step : 
  
    Output argument
   ---------------
  
        - zref : Minimum altitude wher there is only molecular diffusion  
  
    Auteur 
   -----
        -  Auteur :  CNRM/GMEI/TRAMM février 2018
                transcodage de scilab en Python a partir de la filiere BASIC du LOA 
                fonction scilab originale : f_Zref.sci
    """

    zref = np.empty(0)

    istep = int(step)

#    step=5
    for x_i, z_i in zip( x, z) : 

        if ( np.isnan(x_i[:]).any() or np.isnan(z_i[:]).any() ) :
            zref=np.append(zref, np.nan)
            continue

        i1 = np.argmin(abs(z_i-z1))
        i2 = np.argmin(abs(z_i-z2))

        # sliding average by convolution
        avg = np.convolve(x_i,np.ones((2*(istep)))/(2.*step),'same')
        # on decalle de +1 pour avoir le même retour que la fonction convolve
        # de Scilab
        avg = avg[1:]
        avg=avg[i1:i2+1]

        # minimum on this average
        imin = np.argmin(avg)
        yy=imin+i1

# around the minimum, closest value between X and avg
        dif=x_i[i1:i2+1]-avg
        i_around_min = max(imin-istep, 0)
        i_around_max = min(imin+istep, len(avg)) + 1

        yy2=np.argmin(abs(dif[int(i_around_min): int(i_around_max)]))

        iref=int(yy+yy2-istep-1)

        zr = np.min( (z2, z_i[iref]) )
        zref=np.append(zref, zr)

        

#    print('Zref diagno i1, i2, yy, yy2, zref', i1, i2, yy, yy2, zref)
#    print('X : ', X[ i1+i_around_min:i1+i_around_max +1 ])
#    print('avg : ', avg[ i_around_min:i_around_max +1 ])
#    print('abs(dif) :', abs(dif[i_around_min: i_around_max]))

    return(zref)

