#!/usr/bin/env python3


#------------------------------------------------------
def AIDA_name_to_CF_name ( nom_vect  ) :
    """
    Essaye de déterminer CF standard_name du nom du vecteur
    """

    base_dict = {
                  "air_pressure" :
                    {   "famille" : ["pre", ],
                        "mots_clefs_name" : ["air", "_s_av", "_s_ar", "_s_adc", "_sb", "_psbav", "_psbar", ]
                    },
                  "air_temperature" :
                    {   "famille" : ["tpr", ],
                        "mots_clefs_name" : ["air", "_s_", "_saero", "_srt", "_srd_", "_sucap", ]
                    },

                  "air_potential_temperature" :
                    {   "famille" : ["tpr", ],
                        "mots_clefs_name" : ["pot",]
                    },

		          "virtual_temperature" :
                    {   "famille" : ["tpr", ],
                        "mots_clefs_name" : ["virt",]
                    },

                  "wind_speed" :
                    {   "famille" : ["ven", ],
                        "mots_clefs_name" : ["ff", "_ff_", "wind_speed" ]
                    },
                  "wind_from_direction" :
                    {   "famille" : ["ven", ],
                        "mots_clefs_name" : ["dd", "_dd_", "wind_dir" ]
                    },
                  "wind_speed_of_gust" :
                    {   "famille" : ["ven", ],
                        "mots_clefs_name" : ["ff3",]
                    },
                  "eastward_wind" :
                    {   "famille" : ["ven", ],
                        "mots_clefs_name" : ["_e_","_u_","_ug_",]
                    },
                  "northward_wind" :
                    {   "famille" : ["ven", ],
                        "mots_clefs_name" : ["_n_", "_vg_",]
                    },
                  "upward_air_velocity" :
                    {   "famille" : ["ven", ],
                        "mots_clefs_name" : ["_w_", "_v_", ]
                    },
                  "relative_humidity" :
                    {   "famille" : ["hum", ],
                        "mots_clefs_name" : ["_rel", ]
                    },
                  "humidity_mixing_ratio" :
                    {   "famille" : ["hum", ],
                        "mots_clefs_name" : ["_rapm", "rapm", ]
                    },
                  "specific_humidity" :
                    {   "famille" : ["hum", ],
                        "mots_clefs_name" : ["_spec", ]
                    },
                  "surface_upwelling_shortwave_flux_in_air" :
                    {   "famille" : ["ray", ],
                        "mots_clefs_name" : ["_rgm", ]
                    },
                  "surface_downwelling_shortwave_flux_in_air" :
                    {   "famille" : ["ray", ],
                        "mots_clefs_name" : ["_rgd", ]
                    },
                  "surface_upwelling_longwave_flux_in_air" :
                    {   "famille" : ["ray", ],
                        "mots_clefs_name" : ["_irm", ]
                    },
                  "surface_downwelling_longwave_flux_in_air" :
                    {   "famille" : ["ray", ],
                        "mots_clefs_name" : ["ird", ]
                    },
                  "surface_net_downward_radiative_flux" :
                    {   "famille" : ["flx", ],
                        "mots_clefs_name" : ["_rn", ]
                    },
                  "diffuse_downwelling_shortwave_flux_in_air" :
                    {   "famille" : ["ray", ],
                        "mots_clefs_name" : ["_rdiff", "_diff" ]
                    },
                  "surface_brightness_temperature" :
                    {   "famille" : ["ray", ],
                        "mots_clefs_name" : ["_tsurf", ]
                    },
                  "soil_temperature" :
                    {   "famille" : ["tpr", ],
                        "mots_clefs_name" : ["_sol", ]
                    },
                  "volume_fraction_of_condensed_water_in_soil" :
                    {   "famille" : ["hum", ],
                        "mots_clefs_name" : ["_sol", ]
                    },
                  "upward_latent_heat_flux_in_air" :
                    {   "famille" : ["flx", ],
                        "mots_clefs_name" : ["_le", "_le_"]
                    },
                  "upward_water_vapor_flux_in_air" :
                    {   "famille" : ["flx", ],
                        "mots_clefs_name" : ["_h2o_flux_"]
                    },
                  "surface_upward_mole_flux_of_carbon_dioxide" :
                    {   "famille" : ["flx", ],
                        "mots_clefs_name" : ["_co2_flux_"]
                    },
                  "upward_sensible_heat_flux_in_air" :
                    {   "famille" : ["flx", ],
                        "mots_clefs_name" : ["_hs", "_h_" ]
                    },
                  "downward_heat_flux_in_soil" :
                    {   "famille" : ["flx", ],
                        "mots_clefs_name" : ["_phi", ]
                    },
                  "thickness_of_rainfall_amount" :
                    {   "famille" : ["prp", ],
                        "mots_clefs_name" : ["_cumul", "_rr_min"]
                    },
                  "rainfall_rate" :
                    {   "famille" : ["prp", ],
                        "mots_clefs_name" : ["_intens", ]
                    },



# pas encore de definition pour ustar
#                  "???" :
#                    {   "famille" : ["flx", ],
#                        "mots_clefs_name" : ["_ustar", ]
#                    },
                  "altitude" :
                    {   "famille" : ["alt", ],
                        "mots_clefs_name" : ["_hautwgs84", "_alti", "_aipov", "_adc", ]
                    },

                  "height" :
                    {   "famille" : ["alt", ],
                        "mots_clefs_name" : ["_ralt", "_ra05", "_ra15","_haut"  ]
                    },


                  "status_flag" :
                    {   "famille" : ["ctl", ],
                        "mots_clefs_name" : ["flag", "_qc_" ]
                    },


                  "latitude" :
                    {   "famille" : ["pos", ],
                        "mots_clefs_name" : ["_lat",]
                    },


                  "longitude" :
                    {   "famille" : ["pos", ],
                        "mots_clefs_name" : ["_lon",]
                    },



                  "platform_orientation" :
                    {   "famille" : ["att", ],
                        "mots_clefs_name" : ["_cap",]
                    },


                  "platform_course" :
                    {   "famille" : ["nav", ],
                        "mots_clefs_name" : ["_route", "_traipov", "_trgps" ]
                    },


                  "platform_roll" :
                    {   "famille" : ["att", ],
                        "mots_clefs_name" : ["_roll", "_roul",  ]
                    },


                  "platform_pitch" :
                    {   "famille" : ["att", ],
                        "mots_clefs_name" : ["_pitch", "_tang", ]
                    },


                  "platform_speed_wrt_air" :
                    {   "famille" : ["vit", ],
                        "mots_clefs_name" : ["_p_pav", "_tas", ]
                    },


                  "platform_speed_wrt_ground" :
                    {   "famille" : ["vit", ],
                        "mots_clefs_name" : ["_s_", ]
                    },


                  "platform_roll_rate_starboard_down" :
                    {   "famille" : ["vit", ],
                        "mots_clefs_name" : ["_rx_", ]
                    },

                  "platform_pitch_rate_fore_up" :
                    {   "famille" : ["vit", ],
                        "mots_clefs_name" : ["_ry_", ]
                    },


                  "platform_yaw_rate_fore_starboard" :
                    {   "famille" : ["vit", ],
                        "mots_clefs_name" : ["_rz_", ]
                    },

                  "platform_surge_rate_fore" :
                    {   "famille" : ["vit", ],
                        "mots_clefs_name" : ["_x_", ]
                    },

                  "platform_sway_rate_starboard" :
                    {   "famille" : ["vit", ],
                        "mots_clefs_name" : ["_y_", ]
                    },

                  "dew_point_temperature" :
                    {   "famille" : ["hum", ],
                        "mots_clefs_name" : ["_td", ]
                    },


                  "mass_concentration_of_water_vapor_in_air" :
                    {   "famille" : ["hum", ],
                        "mots_clefs_name" : ["_abs_", ]
                    },


  		          "mass_concentration_of_cloud_liquid_water_in_air" :
                    {   "famille" : ["lwc", ],
                        "mots_clefs_name" : ["_lwc300_", "_ger_" ]
                    },


                  "upwelling_longwave_flux_in_air" :
                    {   "famille" : ["ray", ],
                        "mots_clefs_name" : ["_ir_b", ]
                    },

                  "downwelling_longwave_flux_in_air" :
                    {   "famille" : ["ray", ],
                        "mots_clefs_name" : ["_ir_h", ]
                    },

                  "upwelling_shortwave_flux_in_air" :
                    {   "famille" : ["ray", ],
                        "mots_clefs_name" : ["_glob_b", "_pir_b" ]
                    },

                  "downwelling_shortwave_flux_in_air" :
                    {   "famille" : ["ray", ],
                        "mots_clefs_name" : ["_glob_h", "_pir_h" ]
                    },

                  "brightness_temperature" :
                    {   "famille" : ["ray", ],
                        "mots_clefs_name" : ["_tb_ce332_", ]
                    },

                  "upwelling_shortwave_radiance_in_air" :
                    {   "famille" : ["ray", ],
                        "mots_clefs_name" : ["_lum_ce332_", ]
                    },

                  "air_density" :
                    {   "famille" : ["tmd", ],
                        "mots_clefs_name" : ["_rhoa_"]
                    },
                  "visibility_in_air" :
                    {   "famille" : ["opt", ],
                        "mots_clefs_name" : ["_visi_m", "_pom_"]
                    }

                }

    famille_vect = nom_vect[0:3]
    cf_name = None
    for n,d in list(base_dict.items()) :

        if ( any(mot in nom_vect.lower() for mot in d["mots_clefs_name"] ) ) \
           and ( any(mot in famille_vect for mot in d["famille"] )) :
           cf_name = n
           break

    return (cf_name)

#--------------progr principal pour appeler en ligen de commande
# décodage des arguments

import argparse

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("nom_vect", help="nom du fichier vecteur")
    args=parser.parse_args()

    print(AIDA_name_to_CF_name (args.nom_vect))

