# External Reports

TODO: add media_lab_logo.png to media/img directory in production server

## Generate Charts
To generate charts for the external reports for all meetings for a specified group within a specified week (starting from Mon June 13, 2016, e.g. Week 2: Mon 2016-06-20 to Sun 2016-06-26), `cd` into the project directory, then run this command:

`python src/manage.py generatecharts --week_num={POSITIVE NUMBER} --group_key={GROUP KEY}`

To generate charts for all meetings for ALL groups, leave out `--group_key={GROUP KEY}`

Reports for each group can be viewed through `{hostname}/weekly_group_report/<group_key>/<week_num>` (admin access only)

## Email Weekly Reports to a Group
To send an email containing the weekly report to a specified group, `cd` into the project directory, then run this command:

`python src/manage.py send_weekly_email --week_num {POSITIVE NUMBER} --group_key {GROUP_KEY}`

To send the weekly email to all groups, use `ALL` as `{GROUP_KEY}`

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
