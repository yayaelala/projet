import datetime
import pandas as pd
import numpy as np

from sqlalchemy import create_engine

from horizon.horizon_pricer.models.pricer.module_interpolation import courbe_bam_delta, interpolation_tenors_bam, get_volume_courbe_strates

from horizon.horizon_pricer.models.data.db.db_queries import query_courbe_range, query_tenors_range, query_tenors

from horizon.horizon_pricer.models.data.db.db_loading import dbsession, engine_lite

dbs = dbsession()


gen_date_ini = datetime.date(2019,9,6)
gen_date_fin = datetime.date(2021,9,6)


def import_generated_tenors(gen_date_ini, gen_date_fin):

    dcourbe = query_courbe_range(gen_date_ini, gen_date_fin, dbs)

    list_dates_courbes = []

    for el in dcourbe['date_marche']:
        list_dates_courbes.append(el)

    set_dates_courbes = set(list_dates_courbes)

    dico_res = {}

    for el_date in set_dates_courbes:

        dg = interpolation_tenors_bam(el_date)
        dg.to_sql('bkam_courbe_tenors', con = engine_lite,if_exists='append', index = False)

def get_tenors_main(gen_date_ini, gen_date_fin) -> pd.DataFrame(): # type: ignore

    dcourbe = query_courbe_range(gen_date_ini, gen_date_fin, dbs)
    dcourbe = dcourbe.sort_values('date_marche')
    dcourbe_f = dcourbe.drop_duplicates()
    list_dates_courbes = []

    for el in dcourbe_f['date_marche']:
        list_dates_courbes.append(el)

    set_dates_courbes = set(list_dates_courbes)

    dico_res = {}
    try:
        for el_date in set_dates_courbes:
            dg = query_tenors(el_date, dbs)
            dico= {ty:tx for (ty,tx) in list(zip(dg['tenors_y'],dg['taux']))}
            dico_res[dg['date_marche'][0]] = dico
    except:
        pass

    heads_tenors = ['date_marche', '13s', '26s', '52s', '1an', '2ans', '3ans', '4ans', '5ans', '6ans', '7ans', '8ans', '9ans', '10ans', '11ans', '12ans', '13ans', '14ans', '15ans', '16ans', '17ans', '18ans', '19ans', '20ans', '21ans', '22ans', '23ans', '24ans', '25ans', '26ans', '27ans', '28ans', '29ans', '30ans']


    dres = pd.DataFrame().from_dict(dico_res, orient='index')
    dres.reset_index(drop=False, inplace=True, col_level=1)
    dres.columns = heads_tenors
    dres = dres.sort_values('date_marche',ascending=True)

    return dres

def get_tenors_pentes(gen_date_ini, gen_date_fin) -> pd.DataFrame(): # type: ignore

    df = get_tenors_main(gen_date_ini, gen_date_fin)

    t_dates = df['date_marche']
    t_13s = df['13s'].apply(lambda x: np.float64(x))
    t_26s = df['26s'].apply(lambda x: np.float64(x))
    t_52s = df['52s'].apply(lambda x: np.float64(x))
    t_1y = df['1an'].apply(lambda x: np.float64(x))
    t_2y = df['2ans'].apply(lambda x: np.float64(x))
    t_3y = df['3ans'].apply(lambda x: np.float64(x))
    t_4y = df['4ans'].apply(lambda x: np.float64(x))
    t_5y = df['5ans'].apply(lambda x: np.float64(x))
    t_6y = df['6ans'].apply(lambda x: np.float64(x))
    t_7y = df['7ans'].apply(lambda x: np.float64(x))
    t_8y = df['8ans'].apply(lambda x: np.float64(x))
    t_9y = df['9ans'].apply(lambda x: np.float64(x))
    t_10y = df['10ans'].apply(lambda x: np.float64(x))
    t_11y = df['11ans'].apply(lambda x: np.float64(x))
    t_12y = df['12ans'].apply(lambda x: np.float64(x))
    t_13y = df['13ans'].apply(lambda x: np.float64(x))
    t_14y = df['14ans'].apply(lambda x: np.float64(x))
    t_15y = df['15ans'].apply(lambda x: np.float64(x))
    t_16y = df['16ans'].apply(lambda x: np.float64(x))
    t_17y = df['17ans'].apply(lambda x: np.float64(x))
    t_18y = df['18ans'].apply(lambda x: np.float64(x))
    t_19y = df['19ans'].apply(lambda x: np.float64(x))
    t_20y = df['20ans'].apply(lambda x: np.float64(x))
    t_21y = df['21ans'].apply(lambda x: np.float64(x))
    t_22y = df['22ans'].apply(lambda x: np.float64(x))
    t_23y = df['23ans'].apply(lambda x: np.float64(x))
    t_24y = df['24ans'].apply(lambda x: np.float64(x))
    t_25y = df['25ans'].apply(lambda x: np.float64(x))
    t_26y = df['26ans'].apply(lambda x: np.float64(x))
    t_27y = df['27ans'].apply(lambda x: np.float64(x))
    t_28y = df['28ans'].apply(lambda x: np.float64(x))
    t_29y = df['29ans'].apply(lambda x: np.float64(x))
    t_30y = df['30ans'].apply(lambda x: np.float64(x))


    results_pentes = {

      'date_marche': t_dates,
      'delta_26_13': ((t_26s - t_13s) * 10000),
      'delta_52_26': ((t_52s - t_26s) * 10000),
      'delta_2y_1y': ((t_2y - t_1y) * 10000),
      'delta_3y_2y': ((t_3y - t_2y) * 10000),
      'delta_4y_3y': ((t_4y - t_3y) * 10000),
      'delta_5y_4y': ((t_5y - t_4y) * 10000),
      'delta_6y_5y': ((t_6y - t_5y) * 10000),
      'delta_7y_6y': ((t_7y - t_6y) * 10000),
      'delta_8y_7y': ((t_8y - t_7y) * 10000),
      'delta_9y_8y': ((t_9y - t_8y) * 10000),
      'delta_10y_9y': ((t_10y - t_9y) * 10000),
      'delta_11y_10y': ((t_11y - t_10y) * 10000),
      'delta_12y_11y': ((t_12y - t_11y) * 10000),
      'delta_13y_12y': ((t_13y - t_12y) * 10000),
      'delta_14y_13y': ((t_14y - t_13y) * 10000),
      'delta_15y_14y': ((t_15y - t_14y) * 10000),
      'delta_16y_15y': ((t_16y - t_15y) * 10000),
      'delta_17y_16y': ((t_17y - t_16y) * 10000),
      'delta_18y_17y': ((t_18y - t_17y) * 10000),
      'delta_19y_18y': ((t_19y - t_18y) * 10000),
      'delta_20y_19y': ((t_20y - t_19y) * 10000),
      'delta_21y_20y': ((t_21y - t_20y) * 10000),
      'delta_22y_21y': ((t_22y - t_21y) * 10000),
      'delta_23y_22y': ((t_23y - t_22y) * 10000),
      'delta_24y_23y': ((t_24y - t_23y) * 10000),
      'delta_25y_24y': ((t_25y - t_24y) * 10000),
      'delta_26y_25y': ((t_26y - t_25y) * 10000),
      'delta_27y_26y': ((t_27y - t_26y) * 10000),
      'delta_28y_27y': ((t_28y - t_27y) * 10000),
      'delta_29y_28y': ((t_29y - t_28y) * 10000),
      'delta_30y_29y': ((t_30y - t_29y) * 10000)
    }

    df_resultats_pentes = pd.DataFrame(results_pentes)

    return df_resultats_pentes
