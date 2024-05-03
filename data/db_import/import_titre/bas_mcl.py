import pandas as pd
import datetime as dt
import re
from sqlalchemy import (
    create_engine
)
from xml.etree.ElementTree import ElementTree

from horizon.horizon_pricer.models.data.db.db_loading import engine_lite
from horizon.horizon_pricer.models.data.db.db_tables import Mcl
from horizon.horizon_pricer.models.data.db.helpers.p_factory import to_date, format


FIELDS_MAPPER = {
    'INSTRID': 'code_isin',
    'INSTRTYPE': 'famille_instrument',
    'INSTRCTGRY': 'categorie_instrument',
    'ENGPREFERREDNAME': 'libelle_court',
    'ENGLONGNAME': 'description',
    'ISSUERCD': 'isin_emetteur',
    'ISSUECAPITAL': 'capital_emis',
    'ISSUESIZE': 'qt_emise',
    'PRMYDTLSDUMMYDATE1': 'date_jouissance',
    'ISSUEDT': 'date_emission',
    'MATURITYDT_L': 'date_echeance',
    'PARVALUE': 'nominal',
    'INTERESTTYPE': 'type_coupon',
    'FORM': 'forme_detention',
    'GUARANTEE': 'garantie',
    'NEWPARVALUE': 'nominal_actuel',
    'INTERESTPERIODCTY': 'periodicite',
    'INTERESTRATE': 'taux_facial',
    'REDEMPTIONTYPE': 'type_remboursement',
    'AMORTFREQ': 'periodicite_amortissement',
    'EXCHIND': 'cote',
    'MNEMONIQUE': 'mnemonique',
    'AGENTID': 'isin_centralisateur',
    'PREFERREDNAMEISSUER': 'nom_emetteur',
    'PREFERREDNAMEREGISTRAR': 'code_enregistrement',
    'CouponPayDates': 'dates_coupons',
    'INSTRSTATUS': 'statut_instrument'
}

def join_dates_coupons(coupon_node):
    return ";".join([x.text for x in coupon_node])

def load_file_mcl(p):
    et = ElementTree(file=p)
    root = et.getroot()

    dbt = root.find('Debts')
    dico = {}
    for node in root:
        ll = []
        for child in node:
            ll.append(child)
        dico[node.tag] = ll

    dbt = dico['Debts']

    lll = []
    h = []

    for x in dbt[2]:
        h.append(x.tag)

    for i in range(len(dbt)):
        lf = []

        for x in dbt[i]:
            if x.tag == 'CouponPayDates':
                dates_coupons = join_dates_coupons(x)
            else:
                dates_coupons = x.text

            lf.append(dates_coupons)

        lll.append(lf)

    rv = [dict(zip(h, el)) for el in lll]
    return rv

def traitement_file_mcl(records: list) -> pd.DataFrame:
    df = pd.DataFrame(records)

    rv = df.rename(columns=FIELDS_MAPPER)

    rv['isin_centralisateur'] = rv['isin_centralisateur'].replace(["00000000"], '')
    rv['date_emission'] = rv['date_emission'].apply(lambda x: format(x))
    rv['date_echeance'] = rv['date_echeance'].apply(lambda x: format(x))

    # traitement date echeance
    dh = rv[(rv['date_echeance'] <= dt.date(2020, 12, 31))]
    ind = dh.index
    rv.drop(ind, inplace=True)

    # traitement date jouissance
    s_year_em = rv['date_emission'].map(lambda x: x.year)
    s_month_em = rv['date_emission'].map(lambda x: x.month)
    s_day_em = rv['date_emission'].map(lambda x: x.day)

    s_months_ech = rv['date_echeance'].map(lambda x: x.month)
    s_days_ech = rv['date_echeance'].map(lambda x: x.day)
    s_year_ech = rv['date_echeance'].map(lambda x: x.year)

    mat_ini = rv['date_echeance'] - rv['date_emission']

    l = []

    for year_em, month_ech, days_ech, month_em, day_em, year_ech, mi in zip(s_year_em, s_months_ech, s_days_ech, s_month_em, s_day_em, s_year_ech, mat_ini):

        if (int(day_em) < int(days_ech)) and (int(month_em) < int(month_ech)) and (year_ech == year_em) and (mi.days < 366):

            res = dt.date((int(year_em)), month_em, day_em)  # emission

        elif (int(day_em) <= int(days_ech)) and (int(month_em) > int(month_ech)) and (year_ech > year_em) and (mi.days > 366):

            res = dt.date((int(year_em + 1)), month_ech, days_ech)  # echeance

        elif (int(day_em) <= int(days_ech)) and (int(month_em) < int(month_ech)) and (year_ech > year_em) and (mi.days > 366):

            res = dt.date((int(year_em)), month_ech, days_ech)  # echeance

        elif (int(day_em) > int(days_ech)) and (int(month_ech) > int(month_em)):

            res = dt.date(int(year_em) + 1, month_ech, days_ech)

        elif (int(day_em) > int(days_ech)) and (int(month_em) > int(month_ech)):

            res = dt.date(int(year_em) + 1, month_ech, days_ech)

        elif (int(day_em) > int(days_ech)) and (int(month_em) == int(month_ech)):

            res = dt.date(int(year_em) + 1, month_ech, days_ech)

        else:
            res = dt.date(int(year_em), month_em, day_em)
        l.append(res)

    rv['date_jouissance'] = l
    drv = pd.DataFrame(rv)
    return drv

def import_file_mcl(p):
    file = load_file_mcl(p)
    df = traitement_file_mcl(file)
    return df


if __name__ == '__main__':

    filename = 'REPV_0001_ALL_28052021.xml'

    #p = f"/Users/yaya-/project/project_front/pricer/titre/{filename}"
    p = f"C:\\Users\\yaya-\\Projects_main\\horizon\\horizon_pricer\\models\\data\\mcl_files\\{filename}"

    file = load_file_mcl(p)
    df = traitement_file_mcl(file)

    dg = import_file_mcl(p)

    dg.to_sql('mcl', con = engine_lite, if_exists='append', index = False)
