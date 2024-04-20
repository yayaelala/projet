from django.shortcuts import render
from sqlalchemy.exc import SQLAlchemyError
from horizon_pricer.models.data.db.db_tables import *
from horizon_pricer.models.data.db.db_queries import *

import datefinder
from deform import Form, Button
from colander import MappingSchema, SchemaNode, Date
import deform

class Date_deb_Input(MappingSchema):
    date_deb = SchemaNode(Date(),
                          title="Date début",
                          name='ndate_deb')

class Date_fin_Input(MappingSchema):
    date_fin = SchemaNode(Date(),
                          title="Date fin",
                          name='ndate_fin')

class Dates(MappingSchema):
    date_deb = Date_deb_Input()
    date_fin = Date_fin_Input()

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

    if 'submit' in request.POST:
        controls = request.POST.items()

        try:
            if request.POST.get('date_deb') and request.POST.get('date_fin'):
                lres = list(request.POST.items())
                ldates = [x[1] for x in lres]
                date_d = datefinder.find_dates(ldates[0])[0].strftime("%Y-%m-%d")
                date_f = datefinder.find_dates(ldates[1])[0].strftime("%Y-%m-%d")

                one = query_tenors_range(date_d, date_f, request.dbsession)

                if not one:
                    one = 'date inexistante'
            else:
                one = 'Nothing'
                print(one)

            rendered_form_tenors_range = myform.render()
            return render(request, 'template_tenors_range.jinja2', {'form': rendered_form_tenors_range, 'one': one})

        except deform.ValidationFailure as e:
            rendered_form_tenors_range = e.render()
            return render(request, 'template_tenors_range.jinja2', {'form': rendered_form_tenors_range, 'error_msg': db_err_msg})

        except SQLAlchemyError:
            return render(request, 'template_tenors_range.jinja2', {'error_msg': db_err_msg})

    else:
        rendered_form_tenors_range = myform.render()
        return render(request, 'template_tenors_range.jinja2', {'form': rendered_form_tenors_range})
