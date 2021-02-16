from django import forms

class DateInput(forms.DateInput):
    input_type = "date"

class FlightForm(forms.Form):
    departure = forms.CharField(max_length=64, widget=forms.TextInput(attrs={'class': "form-control", 
    'id':"depatures_input", 'placeholder': "from"}))
    arrival = forms.CharField(max_length=64, widget=forms.TextInput(attrs={'class': "form-control", 
    'id':"arrivals_input", 'placeholder': "to"}))
    date = forms.DateField(widget=DateInput(attrs={'class': "form-control", 'id': "date"}))
    back = forms.DateField(label='back:', required=False, widget=DateInput(attrs={'class': "form-control", 'id': "back"}))


gender_types = (
    ('F', "Female"),
    ('M', "Male"),
    ('O', "Other")
)
class PassengerForm(forms.Form):
    first_name = forms.CharField(max_length=64, widget=forms.TextInput(attrs={'class': "form-control"}))
    last_name = forms.CharField(max_length=64, widget=forms.TextInput(attrs={'class': "form-control"}))
    date_of_birth = forms.DateField(widget=DateInput(attrs={'class': "form-control", 
    'id': "start", 'name': "trip-start", 'value': "2020-08-20", 'min': "1920-01-01", 'max': "2021-12-12"}))
    gender = forms.ChoiceField(choices = gender_types) 