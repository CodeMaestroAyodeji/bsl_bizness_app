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
    invoice_date = forms.DateField(widget=forms.DateInput(attrs={'placeholder': 'DD/MM/YYYY'}), input_formats=['%d/%m/%Y', '%Y-%m-%d'])
    terms = forms.CharField(widget=forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}), required=False)
    invoice_number = forms.CharField(max_length=255, required=False) # For editing

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['vendor'].choices = [("", "Select a Vendor")] + [(str(v.id), v.name) for v in Vendor.objects.all()]

class InvoiceItemForm(forms.Form):
    description = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Description'}))
    quantity = forms.FloatField(widget=forms.NumberInput(attrs={'class': 'form-control quantity item-input', 'placeholder': 'Quantity'}))
    unit_price = forms.DecimalField(widget=forms.NumberInput(attrs={'class': 'form-control unit_price item-input', 'placeholder': 'Unit Price'}))
    discount = forms.DecimalField(required=False, widget=forms.NumberInput(attrs={'class': 'form-control discount item-input', 'placeholder': 'Discount'}))
    tax = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'class': 'form-check-input tax item-input'}))

InvoiceItemFormSet = forms.formset_factory(InvoiceItemForm, extra=1)

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['profile_picture', 'phone_number', 'address', 'bio']


# --- Purchase Order Forms ---

class PurchaseOrderItemForm(forms.Form):
    description = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Item description'})
    )
    quantity = forms.FloatField(
        initial=1.0,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'min': '0'})
    )
    unit_price = forms.DecimalField(
        initial=0.0,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'min': '0'})
    )

PurchaseOrderItemFormSet = forms.formset_factory(PurchaseOrderItemForm, extra=1)

class PurchaseOrderForm(forms.Form):
    vendor = forms.ChoiceField(choices=[])
    po_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}), label="PO Date")
    po_number = forms.CharField(max_length=50, required=False, help_text="Leave blank to auto-generate.", label="PO Number")
    terms = forms.CharField(widget=forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}), required=False, label="Terms & Conditions")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['vendor'].choices = [("", "Select a Vendor")] + [(str(v.id), v.name) for v in Vendor.objects.all()]
