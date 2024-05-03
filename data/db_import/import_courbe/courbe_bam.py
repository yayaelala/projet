import os
import datetime as dt
import platform as pt
import re

import requests

from sqlalchemy import (
    create_engine
)
from xml.etree.ElementTree import ElementTree

import http.client, urllib.request, urllib.parse, urllib.error, base64, json

import pandas as pd

from horizon.horizon_pricer.models.data.db.db_tables import *

from horizon.horizon_pricer.models.data.db.db_loading import dbsession, engine_lite

from horizon.horizon_pricer.models.data.db.db_queries import *

from horizon.horizon_pricer.models.data.db.helpers.p_factory import to_date, format

from horizon.horizon_pricer.models.pricer.module_tenors import (
    import_generated_tenors, get_tenors_main, get_tenors_pentes
    )

from horizon.horizon_pricer.models.pricer.module_interpolation import (
    courbe_bam_delta, interpolation_tenors_bam, get_volume_courbe_strates
    )


dbs = dbsession()


def load_courbe_bam(d):
    
    url = f'http://www.bkam.ma/export/blockcsv/2340/c3367fcefc5f524397748201aee5dab8/e1d6b9bbf87f86f8ba53e8518e882982?date={d:}&block=e1d6b9bbf87f86f8ba53e8518e882982'

    os.chdir('\\Users\\yaya-\\project\\horizon\\models\\data\\db_import\\import_courbe')
    resp = requests.get(url)
    a = resp.content.decode('ascii', 'ignore')

    with open('courbe.csv', mode='a') as f:
        f.write(a)

    fields = ['date_echeance', 'transactions', 'taux', 'date_valeur']
    try:
        wb = pd.read_csv('courbe.csv',delimiter=';', skipinitialspace=True, engine='python', encoding='latin-1', skiprows = 2)
        os.remove('courbe.csv')

        wb.columns = fields # rename columns
        wbb = wb.apply(lambda x: x.str.strip())
        wg = wbb.drop(wbb[wbb['date_echeance'] == 'Total'].index)

        wg['date_echeance'] = wg['date_echeance'].apply(lambda x: to_date(x))
        wg['date_valeur'] = wg['date_valeur'].apply(lambda x: to_date(x))
        wg['taux'] = wg['taux'].str.replace(' ', '')
        wg['taux'] = wg['taux'].str.replace(',', '.')
        wg['taux'] = wg['taux'].str.replace('%', '')
        #wg['transactions'] = wg['transactions'].str.replace(' ', '')
        #wg['transactions'] = wg['transactions'].str.replace(',', '.')
        wg['taux'] = pd.to_numeric(wg['taux'])
        wg['taux'] = wg['taux']/100
        #wg['transactions'] = pd.to_numeric(wg['transactions'])
        wg.insert(0, 'date_marche', d)
        wg.insert(5, 'date_transaction', wg['date_valeur'])

        df = wg

        return df
    except:
        print(f"Pas de date {d:}")

# ---------- importation courbe Bam
def import_courbe_bam_tobase(d):

    # --- courbe --- #
    quer_courbe = dbs.query(BkamCourbe)
    dquer_courbe = pd.read_sql(quer_courbe.statement, quer_courbe.session.bind)
    dquer_courbe_rt = dquer_courbe.drop(columns='id')
    dquer_courbe_rts = dquer_courbe_rt.sort_values(['date_marche'])
    dquer_courbe_rtsd = dquer_courbe_rts.drop_duplicates(['date_marche','date_echeance','transactions','taux','date_valeur','date_transaction']).sort_values(['date_marche'])

    list_dates_courbes = list(dquer_courbe_rtsd.date_marche)

    if (d in list_dates_courbes):
        print('courbe_existante')
        pass
    else:
        try:
            if (d not in list_dates_courbes):
                load_courbe_bam(d).to_sql('bkam_courbe', con = engine_lite, if_exists='append', index = False)
                print("Done import courbe")
        except:
            print('probleme dimportation courbe')

    # --- tenors --- #
    quer_courbe_tenors = dbs.query(BkamCourbeTenors)
    dquer_courbe_tenors = pd.read_sql(quer_courbe_tenors.statement, quer_courbe_tenors.session.bind)
    dquer_courbe_tenors_rt = dquer_courbe_tenors.drop(columns='id')
    dquer_courbe_tenors_rts = dquer_courbe_tenors_rt.sort_values(['date_marche', 'tenors_d'])
    dquer_courbe_tenors_rtsd = dquer_courbe_tenors_rts.drop_duplicates(['date_marche','tenors_y','tenors_d','taux']).sort_values(['date_marche','tenors_d'])

    list_dates_tenors = list(dquer_courbe_tenors_rtsd.date_marche)

    if (d in list_dates_tenors):
        print('tenors_existant')
        pass
    else:
        try:
            if (d not in list_dates_tenors):
                import_generated_tenors(d,d)
                print("Done import tenors")
        except:
            print('probleme dimportation tenors')


