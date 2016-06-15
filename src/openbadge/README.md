# External Reports

## Generate Plots+Charts
To generate plots and charts for the external reports for all meetings within a range of dates, `cd` into the project directory, then run this command:

`python src/manage.py generateplots --start_date={YYYY-MM-DD} --end_date={YYYY-MM-DD}`

Reports for each group can be viewed through _{{hostname}}/report/<group_key>_

# Views

## Adding Pages to OpenBadge App

### Making Views 
1. Add a view in _openbadge/views.py_ for each page.
2. Link view to _openbadge/urls.py_ by appending to _urlpatterns_: 

   `url(regex, views.view_name[, name='view_name'])`
3. [Optional: Templates]

Create an html template in _openbadge/templates/openbadge/template_name.html_ and `return render(request, 'openbadge/template_name.html', args)` at the end of your view.

To make life easier, add custom template tags and filters in _openbadge/templatetags/extras.py_ and use in templates by adding `{% load extras %}` to top of template. Use filter by `{{ somevariable|filter_name }}`

### Superuser-Only
Add `@user_passes_test(lambda u: u.is_superuser)` to the top of the view
