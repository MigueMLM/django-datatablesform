# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import inspect
import json
from django.template.loader import render_to_string
from django.forms import ModelForm


class DataTablesForm(ModelForm):
    list_display = [] #relations fk__field
    init_option_list = [{"label": '---------', "value": ''}]

    def get_related_options(self, model):
        return [{"label": o.__unicode__(), "value": o.id} for o in model.objects.all()]

    def get_choices_options(self, choices):
        return  [{"label": ch[1], "value": ch[0]} for ch in choices]

    def create_col(self, field, related=None):
        f_type = field.get_internal_type()
        col = {
            "name": field.name,
            "label": field.verbose_name,
            "field": field,
            "required": not field.null and not related,
            "related": related,
            }
        if f_type == 'ForeignKey' and not related:
            options = self.init_option_list + self.get_related_options(field.related_model)
            col["options"] = json.dumps(options)
            col["type"] = 'select'
        elif f_type == 'FileField':
            col['type'] = 'image'
        else:
            if field.choices:
                options = self.get_choices_options(field.choices)
                col["options"] = json.dumps(options)
                col["type"] = 'select' if len(options) > 2  else 'radio'
            elif f_type == 'DateField':
                col["type"] = 'datetime'
            elif f_type == 'DateTimeField':
                col["type"] = 'datetime'
            elif f_type == 'BooleanField':
                col["type"] = 'checkbox'
        return col

    def create_columns(self):
        columns = []
        self.list_display = ['id',] + self.list_display
        for field in self.list_display:
            if not '__' in field:
                if inspect.ismethod(getattr(self._meta.model, field)):
                    columns.append({
                        'name': field,
                        'label': getattr(self._meta.model, field).short_description,
                        'field': None,
                        'related': None,
                        })
                else:
                    f = self._meta.model._meta.get_field(field) 
                    columns.append(self.create_col(f))
            else:
                r_model = getattr(self._meta.model, field.split('__')[0]).field.related_model
                r_field = r_model._meta.get_field(field.split('__')[1])
                if r_field:
                    columns.append(self.create_col(r_field, related = field.split('__')[0]))
        return columns

    def create_table(self, qs):
        datatable = []
        columns = self.create_columns()
        
        for obj in qs:
            row = {}
            for col in columns:
                if col['field']:
                    f_type = col["field"].get_internal_type()
                    if not col['related']:
                        value = getattr(obj, col["name"])
                    else:
                        value = getattr(getattr(obj, col["related"]), col['name']) if getattr(obj, col["related"]) else ''

                    if f_type == 'ForeignKey' and not col['related']:
                        row[col["name"]] = value.id if value else ""
                    elif f_type == 'DateField':
                        row[col["name"]] = ('<span hidden>' + value.strftime('%Y/%m/%d') + '</span>' + value.strftime('%d/%m/%Y')) if value else ""
                    elif f_type == 'DateTimeField':
                        row[col["name"]] = ('<span hidden>' + value.strftime('%Y/%m/%d %H:%M') + '</span>' + value.strftime('%d/%m/%Y %H:%M')) if value else ""
                    elif f_type == 'TimeField':
                        row[col["name"]] = value.strftime('%H:%M') if value else ""
                    elif f_type == 'FileField':
                        row[col["name"]] = value.url if value else ""
                    else:
                        row[col["name"]] = value if value else ""
                else:
                    value = getattr(obj, col["name"])()
                    row[col['name']] = value if value else ""
            datatable.append(row)

        return (columns, datatable)

    def factory_table(self, _filters=None, _exclude=None):
        if _filters:
            qs = self._meta.model.objects.filter(**_filters)
        else:
            qs = self._meta.model.objects.all()
        if _exclude:
            qs = qs.exclude(**_exclude)
        datatable = self.create_table(qs)
        data = {'columns': datatable[0], 'data': json.dumps(datatable[1]), 'table': self._meta.model.__name__}
        script = render_to_string('datatablesform/script.html', data)
        return script
