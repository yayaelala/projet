import datefinder
from django.shortcuts import render
from horizon_pricer.models.data.db.db_tables import *
from horizon_pricer.models.data.db.db_loading import *
from horizon_pricer.models.data.db.db_queries import *

import colander
from deform import Form
import deform

class Date_deb_Input(colander.MappingSchema):
    date_deb = colander.SchemaNode(
                colander.Date(),
                title="Date début",
                name='ndate_deb'
            )

class Date_fin_Input(colander.MappingSchema):
    date_fin = colander.SchemaNode(
                colander.Date(),
                title="Date fin",
                name='ndate_fin'
            )

class Dates(colander.Schema):
    date_deb = Date_deb_Input()
    date_fin = Date_fin_Input()

def my_view(request):
    schema = Dates()
    process_btn = deform.form.Button(name='submit', title="submit")
    myform = Form(schema, buttons=(process_btn,))

    dbs = dbsession()

    if request.method == 'POST':
        controls = request.POST

        try:
            if 'date' in request.POST:
                lres = list(request.POST.items())
                ldates = []

                for el in lres:
                    for x in datefinder.find_dates(el[1]):
                        ldates.append(x.strftime("%Y-%m-%d"))

                date_d = ldates[0]
                date_f = ldates[1]

                one = query_tenors_range(date_d, date_f, dbs)

                if not one:
                    one = 'date inexistante'
            else:
                one = 'Nothing'

            rendered_form_import_courbe = myform.render()

            return render(request, 'template_imports.jinja2', {'form': rendered_form_import_courbe, 'one': one})

        except deform.exception.ValidationFailure as e:
            rendered_form_import_courbe = e.render()
            return render(request, 'template_imports.jinja2', {'form': rendered_form_import_courbe})

    else:
        rendered_form_import_courbe = myform.render()
        return render(request, 'template_imports.jinja2', {'form': rendered_form_import_courbe, 'one': 'initial value'})
