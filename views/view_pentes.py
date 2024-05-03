from django.shortcuts import render
from sqlalchemy.exc import SQLAlchemyError
from horizon_pricer.models.data.db.db_tables import *
from horizon_pricer.models.data.db.db_queries import *
from horizon_pricer.models.data.db.db_loading import *

from horizon_pricer.models.data.db.helpers.p_factory import *

import datefinder
from deform import Form, Button
from colander import MappingSchema, SchemaNode, Date
import deform, colander
import datetime as dt

dbs = dbsession()

class Date_Marche_Input(colander.MappingSchema):
    date_marche = colander.SchemaNode(
                colander.Date(),
                title="Date Marché",
            )

class DatesSchema(colander.SequenceSchema):
    date = Date_Marche_Input()

class Dates(colander.Schema):
    dates = Date_Marche_Input()

def render_form_taux():
    class MySchema(colander.MappingSchema):
        date = colander.SchemaNode(colander.Date())

    schema = MySchema()  
    form = deform.Form(schema, buttons=('submit',))

    return form.render()  


def my_view(request, template_name='template_pentes.jinja2'):
    schema = Dates()
    process_btn = deform.form.Button(name='Submit', title="Submit")
    myform = Form(schema, buttons=(process_btn,))

    if request.method == 'POST':
        context = {}

        if 'date' in request.POST:
            date_m = request.POST['date']
            print(to_date(date_m))
            one = query_tenors(format(date_m), dbs)
        else:
            one = 'Nothing'
            

        rendered_form_taux = myform.render()

        context.update({'form': rendered_form_taux, 'one': one})
    
        return render(request, template_name, context)

    else:
        rendered_form_taux = myform.render()
        context = {'rendered_form_taux': rendered_form_taux}
        return render(request, template_name, context)