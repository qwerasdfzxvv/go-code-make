from flask_appbuilder.fields import QuerySelectField
from flask_appbuilder.fieldwidgets import BS3TextFieldWidget, BS3TextAreaFieldWidget,Select2AJAXWidget, Select2Widget,Select2SlaveAJAXWidget
from flask_appbuilder.forms import DynamicForm
from wtforms import SelectField, StringField
from flask_appbuilder.fields import AJAXSelectField
from .models import COLUMNS
from app import  db
from wtforms.validators import DataRequired, NumberRange, Optional
from wtforms.validators import DataRequired, NumberRange, Optional


def allowed_table_name(table_schema=None):
    table_name = []
    if table_schema:
        data = db.get_engine(bind="information_schema").execute(
            "select distinct t.TABLE_NAME from columns t where t.TABLE_SCHEMA='{0}'".format(table_schema)).fetchall()
        for value,lable in enumerate(data):
            table_name.append((value,lable))
        return table_name
    # columns = db.get_engine(bind="information_schema").execute(
    #     "select t.TABLE_SCHEMA,t.TABLE_NAME,t.COLUMN_NAME,t.ORDINAL_POSITION,t.IS_NULLABLE,t.DATA_TYPE,t.COLUMN_KEY,t.EXTRA from columns t where t.TABLE_SCHEMA='report'").fetchall()
    return None

class ReverseTableForm(DynamicForm):

    table_schema = StringField(
        label='数据库',
        validators=[DataRequired()],
        widget=Select2AJAXWidget(endpoint='/apimpsview/api/query_schema',extra_classes="readonly")
    )
    table_name = StringField(
        label='表名',
        validators=[DataRequired()],
        widget=Select2SlaveAJAXWidget(
            master_id='table_schema',
            extra_classes="readonly",
            endpoint='/apimpsview/api/query_table/{{ID}}')
    )
    code_type = SelectField('类型',
                            coerce=str,
                            choices=[('All','All'),('Model','Model'),('Controller','Controller')],
                            validators = [DataRequired()],
                            widget=Select2Widget()
                            )

    code = StringField('代码',
                            widget=BS3TextAreaFieldWidget()
                            )
