from django import forms
from .models import Profile, Vendor

class VendorForm(forms.Form):
    name = forms.CharField(max_length=255)
    address = forms.CharField()
    city = forms.CharField(max_length=255)
    state = forms.CharField(max_length=255)
    zip_code = forms.CharField(max_length=10)
    phone_number = forms.CharField(max_length=20)
    email = forms.EmailField()
    tax_tin = forms.CharField(max_length=255, required=False)
    logo = forms.ImageField(required=False)
    bank_account_number = forms.CharField(max_length=255, required=False)
    bank_account_name = forms.CharField(max_length=255, required=False)
    bank_name = forms.CharField(max_length=255, required=False)
    invoice_template = forms.ChoiceField(choices=[
        ('template1', 'Template 1'),
        ('template2', 'Template 2'),
        ('template3', 'Template 3'),
    ], required=False)

class ClientForm(forms.Form):
    company_name = forms.CharField(max_length=255)
    logo = forms.ImageField(required=False)
    address = forms.CharField(required=False)
    email = forms.EmailField(required=False)
    phone_number = forms.CharField(max_length=20, required=False)

class UserRoleForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['role']

# New Forms for Invoice
class InvoiceForm(forms.Form):
    vendor = forms.ChoiceField(choices=[])
    invoice_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    terms = forms.CharField(widget=forms.Textarea(attrs={'rows': 2}), required=False)
    invoice_number = forms.CharField(max_length=255, required=False) # For editing

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['vendor'].choices = [("", "Select a Vendor")] + [(str(v.id), v.name) for v in Vendor.objects.all()]

class InvoiceItemForm(forms.Form):
    description = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    quantity = forms.FloatField(widget=forms.NumberInput(attrs={'class': 'form-control quantity'}))
    unit_price = forms.DecimalField(widget=forms.NumberInput(attrs={'class': 'form-control unit_price'}))
    discount = forms.DecimalField(required=False, widget=forms.NumberInput(attrs={'class': 'form-control discount'}))
    tax = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'class': 'form-check-input tax'}))

InvoiceItemFormSet = forms.formset_factory(InvoiceItemForm, extra=1)