DataTablesForm
==============

DataTablesForm is a simple Django app for connecting the datatables 1.10 js plugin with a standard django ModelForm.

Quick start
-----------

1. Add "datatablesform" to your INSTALLED_APPS setting like this::

        INSTALLED_APPS = [
            ...
            'datatablesform',
        ]

2. Create a form inheriting from DataTablesForm::

        from datatablesform import forms 
        ....
        class MyModelForm(forms.DataTablesForm):
            list_display = ['field1', 'field2', 'fk_field__field', 'class_method_with_allow_tags"]
        
            class Meta:
                model = MyModel
                fields = '__all__'

3. Use the previous form in any view::
    
        def my_form_view(request):
            ....
            form = MyModelForm()
            #_filters = {k,v for k,v in any_model_filter_wanted}
            #_exclude = {k,v for k,v in any_model_exclude_filter_wanted}
            script_table = form.factory_table() #form.factory_table(_filters, _exclude)
            table = 'MyModel'
            return render(request, "my_form_template.html", locals())


4. Be aware of having the needed datatables static files in your "my_form_template", also you'll need to create a table element and include the script_table::
    
        <link href="your_static_dir" rel="stylesheet"/>
        ....
        <table class="dataTable" id="table-{{table}}"></table>
        ....
        <script src="your_static_dir">...</script>
        ....
        {{script_table|safe}}

5. You can always make an ajax request to retrieve the script or use the code to your best.

