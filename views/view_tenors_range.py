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

class DateRangeInput(colander.MappingSchema):
    date_start = colander.SchemaNode(
                colander.Date(),
                title="Date Initiale",
            )
    date_end = colander.SchemaNode(
                colander.Date(),
                title="Date Finale",
            )


def render_form_taux_range():
    class MySchema(colander.MappingSchema):
        date_range = DateRangeInput()

    schema = MySchema()  
    form = deform.Form(schema, buttons=('submit',))

    return form.render()  

def my_view(request, template_name='template_tenors_range.jinja2'):
    schema = DateRangeInput()
    process_btn = deform.form.Button(name='Submit', title="Submit")
    myform = Form(schema, buttons=(process_btn,))

    if request.method == 'POST':
        context = {}

        if 'date_start' in request.POST and 'date_end' in request.POST:
            date_start = request.POST['date_start']
            date_end = request.POST['date_end']
            one = query_tenors_range(format(date_start), format(date_end), dbs)
        else:
            one = 'Nothing'
            
        rendered_form_taux = myform.render()

        context.update({'form': rendered_form_taux, 'one': one})
    
        return render(request, template_name, context)

    else:
        rendered_form_taux = myform.render()
        context = {'rendered_form_taux': rendered_form_taux}
        return render(request, template_name, context)