from django.shortcuts import render
from django.http import HttpResponse
from sqlalchemy.exc import SQLAlchemyError
from horizon_pricer.models.data.db.db_tables import *
from horizon_pricer.models.data.db.db_queries import *

from deform import Form, Button
from colander import MappingSchema, SequenceSchema, SchemaNode, Date
import deform

class Date_Marche_Input(MappingSchema):
    date_marche = SchemaNode(Date(),
                             title="Date Marché")

class DatesSchema(SequenceSchema):
    date = Date_Marche_Input()

class Dates(MappingSchema):
    dates = Date_Marche_Input()

def my_view(request):
    schema = Dates()
    process_btn = Button(name='submit', title="submit")
    myform = Form(schema, buttons=(process_btn,))

    db_err_msg = """\
    Pyramid is having a problem using your SQL database.  The problem
    might be caused by one of the following things:

    1.  You may need to initialize your database tables with `alembic`.
        Check your README.txt for descriptions and try to run it.

    2.  Your database server may not be running.  Check that the
        database server referred to by the "sqlalchemy.url" setting in
        your "development.ini" file is running.

    After you fix the problem, please restart the Pyramid application to
    try it again.
    """

    if request.method == "POST":
        if 'submit' in request.POST:
            controls = request.POST.items()
            try:
                if request.POST.get('date_marche'):
                    date_m = request.POST.get('date_marche')
                    one = query_tenors(date_m, request.dbsession)
                    if not one:
                        one = 'date inexistante'
                else:
                    one = 'Nothing'
                    print(one)

                rendered_form_taux = myform.render()

                return render(request, 'template_taux.jinja2', {'form': rendered_form_taux, 'one': one})

            except deform.ValidationFailure as e:
                rendered_form_taux = e.render()
                return render(request, 'template_taux.jinja2', {'form': rendered_form_taux, 'error_msg': db_err_msg})

            except SQLAlchemyError:
                return render(request, 'template_taux.jinja2', {'error_msg': db_err_msg})

        rendered_form_taux = myform.render()
        return render(request, 'template_taux.jinja2', {'form': rendered_form_taux})

    else:
        rendered_form_taux = myform.render()
        return render(request, 'template_taux.jinja2', {'form': rendered_form_taux})
