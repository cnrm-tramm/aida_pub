include $(AIDA_HOME)/config/local_cfg.mk

ifndef UDUNITS2_INC_PATH
UDUNITS2_INC_PATH	= /usr/include/udunits2
endif
CC = gcc
CFLAGS				= $(C_DEBUG_INFO_FLAGS)  -Wall #$(C_STRICT_FLAGS) #-Wextra
INCLUDES			= -I$(AIDA_HOME)/include -I$(UDUNITS2_INC_PATH) -I$(PYTHON_INC_PATH)
LIB_PATH			= -L/usr/local/lib -L$(AIDA_HOME)/lib -L$(LIB_PATH_FORTRAN) -L$(LIB_PATH_PYTHON)
ALLDEFINES			= $(INCLUDES)
LIBS				= -lgene -lrapt -lgsl -lgslcblas -lm -l$(PYTHON_3_Y)
STD_LIBRARY_NAME	= oper
DEPEND_FILE			= oper.depend

C_SRCS= \
oper_util.c \
poly.c \
unit.c \
thermo.c \
2D_common.c \
select_flag_diff_data.c \
Sortie_spectre.c \
Sortie_givrage.c \
PlusI.c \
MoinsI.c \
Foiss.c \
Fogging_2D.c \
Bill_Hall_DOF_2D.c \
Duroure_2D.c \
Compte_img_2D.c \
Oper_1.c \
Plus.c \
Plus_flt.c \
Plus_flt_tab.c \
Plus_dbl.c \
Moins.c \
Moins_flt.c \
Moins_dbl.c \
Fois.c \
Div.c \
Div_tab.c \
Poly_1_flt.c \
PolyCal1.c \
Poly_1_flt_domain.c \
Poly_1_dbl.c \
Poly_1_XY_flt.c \
PolyCal1_dbl.c \
Poly_2_flt.c \
PolyCal2.c \
Poly_4_flt.c \
Poly_5_flt.c \
Poly1_XsurY.c \
Poly1_XsurY_flt.c \
Poly2_gamme_flt.c \
Poly_exp.c \
Poly_exp_domain.c \
Logistic_domain.c \
Hyperb_poly_flt.c \
Hyperb_poly.c \
Cyclic_4_flt.c \
Sqrt_f.c \
Pow_f.c \
Atan2.c \
Sin.c \
Cos.c \
Module_2D_flt.c \
Module_3D_flt.c \
Module_tab_flt.c \
Geo2mobile_2D.c \
Geo2mobile_3D.c \
Mobile2geo_3D.c \
Rotat_rep_vent_moy.c \
UV2ddff.c \
polgeo2rect.c \
Inter.c \
Inter_dbl.c \
Inter_Angl.c \
Ech.c \
Ech_dbl.c \
Ech_I16.c \
Ech_partiel.c \
Ech_tps_impos.c \
Ech_tps_impos_I16.c \
Ech_tps_impos_tab.c \
Estim_RA_Staley_Jurica.c \
MoyEch.c \
MoyEch_dbl.c \
MoyEch_Angl.c\
MoyEch_mnq_Angl_auto_unit.c\
MoyEch_Angl_auto_unit.c\
MoyEch_ff.c\
MoyEch_mnq.c\
MoyEch_mnq_CAP.c\
MoyEch_mnq_int.c\
MoyEch_mnq_dbl.c\
MoyEch_tps_impos_tab.c \
MoyEch_tps_impos_dbl.c \
MoyEch_1D_flt.c\
MoyEch_tps_bnds.c \
SomEch_tps_bnds.c \
StdEch_tps_bnds.c \
VarEch_tps_bnds.c \
MoyHarmEch_tps_bnds.c \
MoyHarmInvEch_tps_bnds.c \
PercentileEch_tps_bnds.c \
PercentileInvEch_tps_bnds.c \
QuantileEch_tps_bnds.c \
PourcentSeuilEch_tps_bnds.c \
MinEch_tps_bnds.c \
MaxEch_tps_bnds.c \
MoyInvEch_tps_bnds.c \
StdInvEch_tps_bnds.c \
HbnMoyInvEch_tps_bnds.c \
CovarXYmaxEch_tps_bnds.c \
PresenceNuageEch_tps_bnds.c \
Var_Ech.c\
MaxEch.c\
Max_rel.c\
MaxEch_raf.c\
Som.c \
Som_25_to_10.c \
Som_1D.c \
Som_1D_flt.c \
Som_1D36.c \
Som_1D20.c \
TVirt.c \
TPrimew.c \
TPot.c \
TPotBolton.c \
TPotEq.c \
TPotEqBolton.c \
TotEch.c\
RapM_Td.c \
RapM_Tdf.c \
RapM_Tdf_choix_ew.c \
RapM_Hu.c \
RapM_satur_liq.c \
RapM_satur.c \
Hu_RapM.c \
Hu_Ha.c \
Hui_Ha.c \
Hui_Hu.c \
RapM_Ha.c \
RapM_Ha_approx.c \
Ha_Hu.c \
Ha_RapM.c \
Ha_Td.c \
Td_Ha.c \
Td_Hu.c \
Tdf_Hu.c \
ew.c \
AltiPress.c \
AltiPressInc.c \
HumW_T_Td.c \
HumW_T_Td_nolimit.c \
HumW_T_Tdf.c \
HumI_T_Td.c \
HumCarb.c \
HumEmpir.c \
HumCapa.c \
Calib_aerodata_hum.c  \
Calc_Static_RH_From_Dynamic_RH_V1.c \
Dynamic_RH_from_static.c \
Correc_Tdf_P.c \
CalcVent.c \
CalcVentNA.c \
CalcVent_rect.c \
Cal_angl_inc.c \
CalcVent_repgeo.c \
CalcVent_rect_repgeo.c \
CalcVent_h_simple.c \
CalcVent_h_sans_derap.c \
CalcVent_h_repav.c \
Pression.c \
Cor_dPrad_angle.c \
Cor_flow_FF.c \
Cor_deltah.c \
Cor_deltaFF.c \
Cor_flow_azi_POM.c \
Cor_flow_tot_POM.c \
Cor_flow_dist.c \
Correc_rep_sonique.c \
Correc_battements_comptage.c \
Correl.c \
Tair.c \
V_Air_Ts.c  \
aero_vit_conv.c  \
aero_inv_vit_conv.c  \
lwckp.c\
lwc_lwc300.c\
liwc_mix_nev.c\
correcKingdata.c\
ha_lyman_td.c\
ha_lyman_td_reg.c\
ha_lyman_td_satur.c\
conc_tab_sa_const.c\
dens_cdp.c\
cdp_conc.c\
cdp_conc_cor.c\
cdp_tconc_lwc.c\
tconc_lwc_lin_tab.c\
oap230Y_conc.c\
oap230Y_conc_tab.c\
IndRefra.c\
IndRefra_cortp.c\
ha_irefra.c\
ecef_to_enu.c\
GPS_to_UTC.c \
GPS_to_UTC_irreg.c \
GPS_to_UTC_auto.c \
async_to_regul.c\
Interpol_irreg.c\
Interpol_irreg_mnq.c\
fssp_activ.c\
fssp_activ_calc.c\
fssp_tconc.c\
fssp_conc_part.c\
fssp_conc_tab.c\
fssp_tconc_cor.c\
fssp_lwc.c\
fssp_lwc_lin.c\
fssp_lwc_lin_tab.c\
fssp_dmoy_lin.c\
fssp_deff_lin.c\
fssp_tauspec.c\
fssp_tauspec_tab.c\
fssp_Tbar.c\
fssp_eqn.c\
fssp_ncor_acrs.c\
fssp_ncor_specacr.c\
fssp_ncor_specrs.c\
fssp_ncor_loc.c\
fssp_ncor_activ.c\
Stat_Spectr.c\
pms1d_dens.c\
pms1d15_lwc.c\
pms1d30_lwc.c\
number_to_mass_concentration.c \
som_15vect.c\
som_30vect.c\
scalar5_to_tab.c\
scalar7_to_tab.c\
scalar15_to_tab.c\
scalar30_to_tab.c\
scalar31_to_tab.c\
Extr_tab.c \
Extr_UI16tabflt.c \
Extr_tabflt.c \
Extr_tabflt2flt.c \
Remplace_col_tab_flt.c \
Remplace_col_tab_flt_flag.c \
correc_time_cal.c\
correc_time_rec.c\
Cre_time_reg.c\
Cre_time_bnds_reg.c\
Cre_time_hm.c\
Cre_time_hms.c\
rayon_IR.c\
rayon_IR_auto_tempe.c\
thermist.c\
thermist_cnvt.c\
CnvFlt2Dbl.c\
CnvDbl2Flt.c\
CnvHpI3e.c \
Decod_Top_CAM.c\
Decale.c\
lwcsex.c\
Vair_axeX.c\
DensAirsec.c\
Tair_soni.c\
V_AirH_Ts.c\
valid_td.c\
Ecrete.c \
Ecrete_t.c \
Qualite_vent_relatif.c \
Valide_vent_givrage.c \
Cmp_vent_dop_gps.c \
Combine_vent_dop_gps.c \
Valid_empir_deltaFF.c \
Valid_empir_tboitier.c \
Decale_1D.c\
Som_Col.c\
Som_Col_flt.c\
correc_saut.c\
correc_saut_mnq.c\
correc_pics_angle_auto_unit.c\
correc_saut_angle_auto_unit.c\
cont_time.c\
Correc_hors_bornes.c \
Correc_hors_bornes_flag.c \
Remplace_hors_bornes.c \
Remplace_hors_bornes_dbl.c \
Remplace_mnq_angl_auto_unit.c\
Remplace_par_filtre_RC.c \
Correc_hors_stat.c \
Correc_discont.c \
Mod0_dbl.c\
Mod0.c\
Decale_quantile.c\
Poly2_XsurY.c\
Poly2_XsurY_flt.c\
Cor_JNO2.c \
Cor_dens.c \
Cor_dens_int.c \
Cor_inv_dens.c \
Filtre_moy.c\
Filtre_Gen.c\
Filtre_RC.c\
Filtre_RC_sdph.c\
Filtre_RC_sdph_paliers.c\
Errstat_Allet99.c\
Genere_constant.c\
Genere_constant_flt.c\
Genere_constant_I16.c\
Tair_soni_ha.c\
Differ_flt.c \
Differ_dbl.c \
Differ_centre_XY.c \
Differ_centre_XfYd.c \
Deriv_Angl.c\
Deriv_Angl_Univ.c\
Deriv_Temps.c\
Vrot_repav.c\
Genere_scie.c\
Hum_refra.c\
Inv_PolyCal2.c\
Irefra_calc.c\
Reg_lin.c\
Reg_lin2.c\
Ote_Base.c\
Ote_Base_auto.c\
Set_freqech_reftime.c\
Set_reftime.c\
Humspec_Hu_approx.c\
Humspec_Hu.c\
Humspec_RapM.c\
choix_vent_app.c\
select_data.c\
select_flag_data.c\
select_inter_data.c\
select_X_selon_Y.c\
select_X_selon_YvarY.c\
select_flt_selon_dbl.c\
select_flt_selon_byte.c\
CnvInt2Flt.c\
CalcVent_h_simple_auto_unit.c\
CalcVent_h_repav_auto_unit.c\
Rotat_horiz_auto.c\
Chang_gam_angl.c\
Oliver_lisse.c\
inclinaison_absolue.c\
Calc_sst.c \
remplace_valeur.c\
DM_to_dec.c\
inclino.c\
Decode_sta_Gill_HS.c \
Flux_correl_vect.c\
Flux_correl.c\
Correl_vect.c\
Correl_wq.c\
Correl_var.c\
Covar_XY.c\
Reg_Pol2.c\
Calcul_Ps.c\
Corefra_calc.c\
Puissance.c\
Puissance_flt.c\
Puissance_poly1.c\
DensAir.c\
Rotat_uv.c\
hum_lent_pomme.c\
Constante_dans_plage.c\
select_sur_vect.c\
Complete_X_avec_Y.c\
Complete_X_avec_Y_dbl.c\
Transforme_flag_mat_CAPITOUL.c\
decale_creneau.c \
ddff2UV.c\
CalcVent_h_polaire.c \
Deriv_Cumul_rr.c\
Rain_rate_Hasse.c\
Diff_dd.c\
Mol_exact.c\
Mol_approx.c\
gauss.c\
Rotat_2D_rep_vent_moy.c \
dd2pi2ddpi.c \
TKE.c \
Log_flt.c \
Cumul.c \
Tsoni.c \
Arrondi.c \
Covar_XY_ctl.c \
Stationnarite_Covar_XY.c \
StatEch_tps_impos.c \
PressAlti.c \
PressAltiVect.c \
Comble_interpolin.c \
Correct_fortes_rr_pluvio.c \
Assure_croit.c\
Genere_flag.c \
Et_logique.c \
ITC.c \
ITC_model_Foken.c \
ITC_flag.c \
Combine_flag_EC_Foken.c \
Combine_flag_EC_CarboEurope.c \
Stationnarite_flag.c \
Stationnarite_Ustar.c \
remplace_X_selon_Y.c \
Poly1_seuil_flt.c \
Cor_ondulation_geoide84.c \
TPot_hum_Marquet.c \
Calc_flag_filfin.c \
Rotat_XY.c \
Rotat_uv_vent_moy.c \
Flux_corWPL.c \
Flux_LE_from_mass.c \
Correc_pics_mnq.c \
Flux_Hs_from_cov.c \
Flux_mvt_from_cov.c \
Ustar_from_cov.c \
Remplace_selon_flag.c \
AltiPressOACI.c \
PressAltiOACI.c \
Filtre_spectral_1D.c \
Profil_Diff_Mol.c \
ProfilMobile2geo_1D.c \
Lidar_Zref.c \
Lidar_Zref_ecart.c \
Nuage_lidar.c \
Qualite_profil_lidar.c \
Inv_Klett_sa.c  \
Inv_Klett_aod.c  \
Extract_param_profil.c \
Humrel_Humspec.c \
Combine_XY_selon_flag.c \
Comble_spline.c \
Profil_Diff_Mol_reel.c \
volumic_to_mass_concentration.c \
Synchro_spline.c \
Flag_to_percent.c \
Cospectre_Chaleur_Moncrieff97.c \
Cospectre_Mouvement_Moncrieff97.c \
FT_analytique_Moncrieff.c \
CorFlux_spectral.c \
Covar_XY_max.c \
Moy_pond_4vect.c

# Attention : la liste ci-dessous ne contient pas seulement les fonctions
# ecrites en Fortran, mais *toutes celles qui dépendent de fonctions
# ecrites en Fortran*. Cela permet, sur les machines qui ne disposent pas d'un
# compilateur Fortran, de remplacer la definition ci-dessous par
# une definition vide (F_SRCS= ).
F_SRCS= \
possol.f \
corassiet.f \
calf_dp.f \
pos_sol_loa.c \
pos_sol_fixe_loa.c \
Cor_rgd_assiet.c \
Flux_dq.c \
caldq_ot.f\
Flux_dt.c \
caldt_ot.f \
Flux_Aero.c \
Flux_Aero_v2.c

# La liste ci-dessous contient les fonctions
# dépendantes de LAPACK.
ifndef WITHOUT_LAPACK
LAPACK_SRCS= Habit_2D.c
LAPACK_LIBS= -llapack -lblas
else
LAPACK_SRCS= 
LAPACK_LIBS= 
endif

# Deux etapes pour les "F_SRCS", car ils peuvent etre en C ou Fortran.
F_OBJS_inter	= ${F_SRCS:.f=.o}
F_OBJS			= ${F_OBJS_inter:.c=.o}
C_OBJS			= ${C_SRCS:.c=.o}
LAPACK_OBJS		= ${LAPACK_SRCS:.c=.o}
# liste des *.c qui sont dans F_SRCS
C_F_SRCS                = $(filter %.c,$(F_SRCS)) 
HDRS			= ${C_SRCS:.c=.h} ${C_F_SRCS:.c=.h}
SRCS			= $(C_SRCS) $(F_SRCS) $(LAPACK_SRCS)
OBJS			= $(C_OBJS) $(F_OBJS) $(LAPACK_OBJS)

.SUFFIXES: .h

.c.o: 
	$(CC) -fcommon $(CFLAGS) $(INCLUDES) $(PICFLAGS) -c $<

.f.o: 
	$(F77) $(F77_NO_UNDERSCORE_FLAGS) $(PICFLAGS) -c $<

.c.h:
	$(CEXTRACT) $(INCLUDES) $< > $*.h

all		: liboper.sl oper.h libload_oper.sl oper_API_desc.txt oper_API_PY_desc.py

# if a dependency file exists, reference it
-include $(DEPEND_FILE)

liboper.sl: $(OBJS) oper.h
	$(CC) $(LD_SHLIB_FLAGS) $(LIB_PATH) -o $@ $(OBJS) $(LIBS) -l load_oper -ludunits2 $(LAPACK_LIBS) $(C_FORTRAN_MIXING_LIB) $(LIBC)

oper.h : $(HDRS) struct_oper.h
	echo "#ifndef _OPER_INCLUDED" > oper.h;\
	echo "#define _OPER_INCLUDED" >>oper.h;\
        cat struct_oper.h >>oper.h ;\
        cat struct_GPS_to_UTC_irreg.h >>oper.h ;\
        cat $(HDRS) >>oper.h ;\
        echo "#endif /* _OPER_INCLUDED */" >>oper.h
	cp oper.h $(AIDA_HOME)/include/

# pour éviter que load_oper.h soit fabriqué par la règle automatique
load_oper.h:
	/bin/true

libload_oper.sl: load_oper.o
	$(CC) $(LD_SHLIB_FLAGS) $(LIB_PATH) load_oper.o -o $@ -ldl -l$(PYTHON_3_Y)

# "oper.h" n'est pas dans les pre-requis ici parce qu'il est déjà
# dans les pré-requis de liboper.sl
install_oper: liboper.sl
	cp liboper.sl $(AIDA_HOME)/lib
	if test -f llib-loper.ln ; then \
	    cp -f llib-loper.ln $(AIDA_HOME)/lib; \
	fi
	$(EXTRA_CMD_SL_PREREQ)
	cp oper.h $(AIDA_HOME)/include/

install_load_oper: libload_oper.sl
	cp libload_oper.sl $(AIDA_HOME)/lib
	$(EXTRA_CMD_SL_PREREQ)
	cp load_oper.h $(AIDA_HOME)/include/

oper2doc : oper2doc.o
	$(CC) $(CFLAGS) $(ALLDEFINES) oper2doc.o $(LIB_PATH) $(LIBS) -l load_oper -o oper2doc


# Le programme oper_API_write documente ./liboper.sl
# Il n'est donc cohérent de copier oper_API_desc.txt vers $(AIDA_HOME)/lib
# que lorsqu'on est sûrs que ./liboper.sl et $(AIDA_HOME)/lib/liboper.sl sont identiques :
# C'est pour ça que "install_oper" est un pre-requis
install_oper_API_desc.txt: install_oper oper_API_desc.txt
	cp oper_API_desc.txt $(AIDA_HOME)/lib

install_oper_API_PY_desc.py.txt: install_oper oper_API_PY_desc.py

# le fichier "oper_API_PY_desc.py" ne peut pas être copié par cette commande
# dans $(PY3_LIB_DIR) parce que ce répertoire n'existe pas encore
install: install_load_oper install_oper install_oper_API_desc.txt install_oper_API_PY_desc.py.txt

oper_API_write: oper_API_write.o liboper.sl libload_oper.sl
	$(CC) $(CFLAGS) $(ALLDEFINES) oper_API_write.o liboper.sl $(LIB_PATH) $(LIBS) -lrapt -l load_oper -o oper_API_write

oper_API_PY_write: oper_API_PY_write.o liboper.sl libload_oper.sl
	$(CC) $(CFLAGS) $(ALLDEFINES) oper_API_PY_write.o liboper.sl $(LIB_PATH) $(LIBS) -l load_oper -o oper_API_PY_write

oper_API_desc.txt: oper_API_write liboper.sl
	./oper_API_write

oper_API_PY_desc.py: oper_API_PY_write liboper.sl
	./oper_API_PY_write

clean:
	rm -f *.o *.sl oper.h oper_API_write oper_API_PY_write oper_API_desc.txt core core.* $(DEPEND_FILE) $(HDRS)

depend:  oper.h
	touch $(DEPEND_FILE)
	$(DEPEND) -f$(DEPEND_FILE) -s "# DO NOT DELETE" -- $(INCLUDES) -- $(SRCS) load_oper.c oper_API_write.c oper_API_PY_write.c

