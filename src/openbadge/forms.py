from django import forms


class H2DailyForm(forms.Form):
    member_key = forms.CharField(label='Member key', max_length=32)
    date = forms.DateField(label='Date')
    #graph_left = forms.CharField(label='Graph Left', widget=forms.Textarea)
    #graph_right = forms.CharField(label='Graph Right', widget=forms.Textarea)
    participation_div_days = forms.CharField(label='Participation Chart Div Days', widget=forms.Textarea)
    participation_script_days = forms.CharField(label='Participation Chart Script Days', widget=forms.Textarea)
    participation_div_weeks = forms.CharField(label='Participation Chart Div Weeks', widget=forms.Textarea)
    participation_script_weeks = forms.CharField(label='Participation Chart Script Weeks', widget=forms.Textarea)