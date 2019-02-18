from flask import render_template, flash, json, make_response, redirect
from flask_appbuilder.baseviews import expose_api, get_order_args, get_filter_args, BaseView
from flask_appbuilder.models.sqla.interface import SQLAInterface
from flask_appbuilder import ModelView, SimpleFormView
from flask_appbuilder.security.decorators import has_access_api, permission_name
import mistune
from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatters import html
from pygments.util import ClassNotFound
import mistune
from mistune import Markdown
from mistune import Renderer
from app import appbuilder, db
from app.form import ReverseTableForm
from app.models import COLUMNS



@appbuilder.app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html', base_template=appbuilder.base_template, appbuilder=appbuilder), 404


class CodeContentRenderer(Renderer):
    """
    Markdown renderer for article rich-text content.
    This renderer improve following features:
    - Syntax highlight for <code> block.
    - Lazy load of vue-lazyload library for <img> tag.
    """

    def __init__(self, **kwargs):
        super(CodeContentRenderer, self).__init__(**kwargs)

    def block_code(self, code, lang=None):
        if not lang:
            # language type is not specified, use default method.
            return super(CodeContentRenderer, self).block_code(code, lang)
        try:
            # try to get lexer
            lexer = get_lexer_by_name(lang, stripall=True)
            formatter = html.HtmlFormatter(style='fruity')
            return highlight(code, lexer, formatter)
        except ClassNotFound:
            return super(CodeContentRenderer, self).block_code(code, lang)








class MyFormView(SimpleFormView):
    form = ReverseTableForm
    form_title = '逆向生成golang代码'
    form_template = 'reverse_edit.html'


    def tranform_string(self,string_name):
        new_string_name_cap = ''.join([t.lower().capitalize() for t in str(string_name).split("_")])
        new_string_name_low ='_'.join([t.lower() for t in str(string_name).split("_")])
        return new_string_name_cap,new_string_name_low


    def form_post(self, form):

        ret_list = list()
        has_time_column = False
        data = db.get_engine(bind="information_schema").execute(
            "select t.TABLE_SCHEMA,t.TABLE_NAME,t.COLUMN_NAME,t.ORDINAL_POSITION,t.IS_NULLABLE,t.DATA_TYPE,t.COLUMN_KEY,t.EXTRA from columns t where t.TABLE_SCHEMA='{0}' AND t.TABLE_NAME='{1}' ORDER BY t.ORDINAL_POSITION".format(form.table_schema.data,form.table_name.data)).fetchall()
        for i in data:
            table_name_init = i['TABLE_NAME']
            table_name_cap,table_name_low= self.tranform_string(i['TABLE_NAME'])
            column_name_cap,column_name_low =self.tranform_string(i['COLUMN_NAME'])
            data_type = 'string'
            if i["DATA_TYPE"] in ["tinyint","int","bigint"]:
                data_type = 'int'
            if i["DATA_TYPE"] in ["double","float"]:
                data_type = 'float32'
            if i["DATA_TYPE"] in ["datetime","timestamp","time"]:
                data_type = '*time.Time'
                has_time_column = True

            ret_list.append({
                "column_name_cap": column_name_cap,
                "column_name_low": column_name_low,
                "data_type": data_type
            })

        model_code = render_template("gorm_model_template.html",
            table_name_init=table_name_init,
            table_name_cap = table_name_cap,
            table_name_low = table_name_low,
            has_time_column = has_time_column,
            ret_list = ret_list)
        # print(model_code)

        renderer = CodeContentRenderer()
        markdown = mistune.Markdown(renderer=renderer)
        golang_code = markdown(model_code)


        widgets = self._get_edit_widget(form=form)
        return self.render_template(
            self.form_template,
            title=self.form_title,
            widgets=widgets,
            appbuilder=self.appbuilder,
            model_code = model_code,golang_code =golang_code
        )




appbuilder.add_view(MyFormView, "My form View", icon="fa-group", label='逆向生成',
                    category="My Forms", category_icon="fa-cogs")


class ApiMpsView(BaseView):

    @expose_api(name='query_schema', url='/api/query_schema', methods=['GET'])
    @has_access_api
    @permission_name('list')
    def query_schema(self):
        ret_list = list()
        data = db.get_engine(bind="information_schema").execute('select distinct t.TABLE_SCHEMA from columns t').fetchall()
        for i in data:
            ret_list.append({'id': str(i['TABLE_SCHEMA']), 'text': str(i['TABLE_SCHEMA'])})
        print(ret_list)
        ret_json = json.dumps(ret_list)
        print(ret_json)
        response = make_response(ret_json, 200)
        response.headers['Content-Type'] = "application/json"
        return response


    @expose_api(name='query_table', url='/api/query_table/<table_schema>', methods=['GET'])
    @has_access_api
    @permission_name('list')
    def query_table(self, table_schema):
        ret_list = list()
        data = db.get_engine(bind="information_schema").execute("select distinct t.TABLE_NAME from columns t where t.TABLE_SCHEMA='{0}'".format(table_schema)).fetchall()
        for i in data:
            ret_list.append({'id': str(i['TABLE_NAME']), 'text': str(i['TABLE_NAME'])})
        print(ret_list)
        ret_json = json.dumps(ret_list)
        response = make_response(ret_json, 200)
        response.headers['Content-Type'] = "application/json"
        return response


appbuilder.add_view_no_menu(ApiMpsView)

# db.create_all()
