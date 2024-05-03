import datetime as dt
import pandas as pd


def format(val):
    a = pd.to_datetime(val, errors='coerce', cache=False).strftime('%d/%m/%Y')
    try:
        date_time_obj = dt.datetime.strptime(a, '%d/%m/%Y')
    except:
        date_time_obj = dt.datetime.strptime(a, '%m/%d/%Y')
    return date_time_obj.date()



def to_date(str_date: str) -> dt.date:
    separateur_choix = ('-', '/')
    filtre = [x for x in separateur_choix if x in str_date]

    if len(filtre) == 1:
        this_sep = filtre[0]
        splitted = str_date.split(this_sep)
        if len(splitted) == 3:
            e1, e2, e3 = [int(x) for x in splitted]
            # Case year is First
            if e1 > 1000:
                rv = dt.date(e1, e2, e3)
            # Case Day is First
            else:
                rv = dt.date(e3, e2, e1)

            return rv

        else:
            msg = f"La date est mal formattée"
            raise ValueError(msg)

    else:
        msg = f"Le séparateur de dates doit être l'un de {separateur_choix}"
        raise ValueError(msg)

def add_years(d, years):
    """Return a date that's `years` years after the date (or datetime)
    object `d`. Return the same calendar date (month and day) in the
    destination year, if it exists, otherwise use the following day
    (thus changing February 29 to March 1).
    """
    try:
        return d.replace(year = d.year + years)
    except ValueError:
        return d + (dt.date(d.year + years, 1, 1) - dt.date(d.year, 1, 1))

def add_days(d, days):

    return d+dt.timedelta(days)
