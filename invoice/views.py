from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout
from .models import Vendor, Client
from .forms import VendorForm, ClientForm
from PIL import Image, ImageDraw, ImageFont
from django.core.files.base import ContentFile
import io
from .decorators import roles_required

def generate_logo(name):
    initials = ''.join([s[0] for s in name.split()])
    img = Image.new('RGB', (100, 100), color = (73, 109, 137))
    d = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype("arial.ttf", 40)
    except IOError:
        font = ImageFont.load_default()
    d.text((25,25), initials, fill=(255,255,0), font=font)
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    return ContentFile(buffer.getvalue())

def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # user.profile.role = 'project_manager'  # Assign default role
            # user.profile.save()
            login(request, user)
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'signup.html', {'form': form})

def home(request):
    vendors = Vendor.objects.all()
    return render(request, 'home.html', {'vendors': vendors})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('home')  # Redirect to a home page after login
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})

@roles_required(allowed_roles=['admin', 'project_manager', 'accountant'])
def vendor_list(request):
    vendors = Vendor.objects.all()
    return render(request, 'vendor_list.html', {'vendors': vendors})

import base64

@roles_required(allowed_roles=['admin', 'project_manager', 'accountant'])
def vendor_detail(request, pk):
    vendor = Vendor.objects.get(pk=pk)
    return render(request, 'vendor_detail.html', {'vendor': vendor})

@roles_required(allowed_roles=['admin', 'project_manager'])
def vendor_create(request):
    if request.method == 'POST':
        form = VendorForm(request.POST, request.FILES)
        if form.is_valid():
            data = form.cleaned_data
            logo = data.pop('logo', None)
            vendor = Vendor(**data)
            if logo:
                vendor.logo.put(logo, content_type=logo.content_type)
            vendor.user_id = request.user.id
            vendor.save()
            return redirect('vendor_list')
    else:
        form = VendorForm()
    return render(request, 'vendor_form.html', {'form': form})

@roles_required(allowed_roles=['admin', 'project_manager'])
def vendor_update(request, pk):
    vendor = Vendor.objects.get(pk=pk)
    if request.method == 'POST':
        form = VendorForm(request.POST, request.FILES)
        if form.is_valid():
            data = form.cleaned_data
            if 'logo' in request.FILES:
                vendor.logo.replace(request.FILES['logo'])
                data.pop('logo')
            vendor.update(**data)
            return redirect('vendor_list')
    else:
        form = VendorForm(initial=vendor.to_mongo().to_dict())
    return render(request, 'vendor_form.html', {'form': form})

@roles_required(allowed_roles=['admin'])
def vendor_delete(request, pk):
    vendor = Vendor.objects.get(pk=pk)
    if request.method == 'POST':
        vendor.delete()
        return redirect('vendor_list')
    return render(request, 'vendor_confirm_delete.html', {'vendor': vendor})

def logout_view(request):
    logout(request)
    return redirect('home')

@roles_required(allowed_roles=['admin'])
def client_settings(request):
    client = Client.load()
    logo_data = None
    if client.logo:
        logo_data = base64.b64encode(client.logo.read()).decode('utf-8')
    if request.method == 'POST':
        form = ClientForm(request.POST, request.FILES)
        if form.is_valid():
            data = form.cleaned_data
            logo = data.pop('logo', None)
            client.update(**data)
            if logo:
                client.logo.replace(logo, content_type=logo.content_type)
            client.save()
            return redirect('client_settings')
    else:
        form = ClientForm(initial=client.to_mongo().to_dict())
    return render(request, 'client_settings.html', {'form': form, 'client': client, 'logo_data': logo_data})

from django.contrib.auth.models import User
from .forms import UserRoleForm

@roles_required(allowed_roles=['admin'])
def user_list(request):
    users = User.objects.all()
    return render(request, 'user_list.html', {'users': users})

@roles_required(allowed_roles=['admin'])
def user_edit_role(request, pk):
    user = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        form = UserRoleForm(request.POST, instance=user.profile)
        if form.is_valid():
            form.save()
            return redirect('user_list')
    else:
        form = UserRoleForm(instance=user.profile)
    return render(request, 'user_edit_role.html', {'form': form, 'user': user})

from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from .models import Invoice, InvoiceItem, Vendor
from .forms import InvoiceForm, InvoiceItemFormSet
from django.forms import formset_factory
from mongoengine.errors import DoesNotExist

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from mongoengine.queryset.visitor import Q

@login_required
@roles_required(allowed_roles=['admin', 'project_manager', 'accountant'])
def invoice_list(request):
    invoices_list = Invoice.objects.all()

    # Search and filter
    query = request.GET.get('q')
    if query:
        vendor_ids = [vendor.id for vendor in Vendor.objects.filter(name__icontains=query)]
        invoices_list = invoices_list.filter(
            Q(invoice_number__icontains=query) | Q(vendor__in=vendor_ids)
        )

    # Pagination
    paginator = Paginator(invoices_list, 10) # 10 invoices per page
    page = request.GET.get('page')
    try:
        invoices = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        invoices = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        invoices = paginator.page(paginator.num_pages)

    return render(request, 'invoice_list.html', {'invoices': invoices})

@login_required
@roles_required(allowed_roles=['admin', 'project_manager', 'accountant'])
def invoice_detail(request, pk):
    try:
        invoice = Invoice.objects.get(pk=pk)
        client = Client.load()
    except DoesNotExist:
        return redirect('invoice_list') # Or render a 404 page
    return render(request, 'invoice_detail.html', {'invoice': invoice, 'client': client})

@login_required
@roles_required(allowed_roles=['admin', 'project_manager'])
def invoice_create(request):
    if request.method == 'POST':
        invoice_form = InvoiceForm(request.POST)
        formset = InvoiceItemFormSet(request.POST)
        if invoice_form.is_valid() and formset.is_valid():
            vendor_id = invoice_form.cleaned_data['vendor']
            vendor = Vendor.objects.get(pk=vendor_id)
            invoice = Invoice(
                vendor=vendor,
                invoice_date=invoice_form.cleaned_data['invoice_date'],
                terms=invoice_form.cleaned_data['terms'],
            )
            # If invoice_number is provided in the form, use it. Otherwise, it will be auto-generated on save.
            if invoice_form.cleaned_data['invoice_number']:
                invoice.invoice_number = invoice_form.cleaned_data['invoice_number']

            items = []
            for item_form in formset:
                if item_form.cleaned_data: # Only process forms with data
                    item = InvoiceItem(
                        description=item_form.cleaned_data['description'],
                        quantity=item_form.cleaned_data['quantity'],
                        unit_price=item_form.cleaned_data['unit_price'],
                        discount=item_form.cleaned_data.get('discount', 0.0),
                        tax=item_form.cleaned_data.get('tax', False)
                    )
                    items.append(item)
            invoice.items = items
            invoice.save()
            return redirect('invoice_list')
    else:
        invoice_form = InvoiceForm()
        formset = InvoiceItemFormSet()
    return render(request, 'invoice_form.html', {'invoice_form': invoice_form, 'formset': formset})

@login_required
@roles_required(allowed_roles=['admin', 'project_manager'])
def invoice_update(request, pk):
    try:
        invoice = Invoice.objects.get(pk=pk)
    except DoesNotExist:
        return redirect('invoice_list')

    if request.method == 'POST':
        invoice_form = InvoiceForm(request.POST)
        formset = InvoiceItemFormSet(request.POST)
        if invoice_form.is_valid() and formset.is_valid():
            vendor_id = invoice_form.cleaned_data['vendor']
            vendor = Vendor.objects.get(pk=vendor_id)

            invoice.vendor = vendor
            invoice.invoice_date = invoice_form.cleaned_data['invoice_date']
            invoice.terms = invoice_form.cleaned_data['terms']
            invoice.invoice_number = invoice_form.cleaned_data['invoice_number'] # Update invoice number if changed

            items = []
            for item_form in formset:
                if item_form.cleaned_data:
                    item = InvoiceItem(
                        description=item_form.cleaned_data['description'],
                        quantity=item_form.cleaned_data['quantity'],
                        unit_price=item_form.cleaned_data['unit_price'],
                        discount=item_form.cleaned_data.get('discount', 0.0),
                        tax=item_form.cleaned_data.get('tax', False)
                    )
                    items.append(item)
            invoice.items = items
            invoice.save()
            return redirect('invoice_list')
    else:
        # Populate invoice form
        initial_invoice_data = {
            'vendor': str(invoice.vendor.id),
            'invoice_date': invoice.invoice_date.strftime('%Y-%m-%d'),
            'terms': invoice.terms,
            'invoice_number': invoice.invoice_number,
        }
        invoice_form = InvoiceForm(initial=initial_invoice_data)

        # Populate formset
        initial_items_data = []
        for item in invoice.items:
            initial_items_data.append({
                'description': item.description,
                'quantity': item.quantity,
                'unit_price': item.unit_price,
                'discount': item.discount,
                'tax': item.tax,
            })
        formset = InvoiceItemFormSet(initial=initial_items_data)

    return render(request, 'invoice_form.html', {'invoice_form': invoice_form, 'formset': formset, 'invoice': invoice})

@login_required
@roles_required(allowed_roles=['admin', 'project_manager'])
def invoice_delete(request, pk):
    try:
        invoice = Invoice.objects.get(pk=pk)
    except DoesNotExist:
        return redirect('invoice_list')

    if request.method == 'POST':
        invoice.delete()
        return redirect('invoice_list')
    return render(request, 'invoice_confirm_delete.html', {'invoice': invoice})

from django.http import HttpResponse
from django.template.loader import render_to_string
import zipfile
import os
from io import BytesIO

@login_required
@roles_required(allowed_roles=['admin', 'project_manager', 'accountant'])
def invoice_print_preview(request, pk):
    try:
        invoice = Invoice.objects.get(pk=pk)
        client = Client.load() # Assuming there's only one client or a way to determine the client
    except DoesNotExist:
        return redirect('invoice_list')
    return render(request, 'invoice_print.html', {'invoice': invoice, 'client': client})

@login_required
@roles_required(allowed_roles=['admin', 'project_manager', 'accountant'])
def invoice_bulk_download(request):
    if request.method == 'POST':
        invoice_ids = request.POST.getlist('invoice_ids')
        if not invoice_ids:
            return redirect('invoice_list')

        zip_buffer = BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w') as zf:
            for invoice_id in invoice_ids:
                try:
                    invoice = Invoice.objects.get(pk=invoice_id)
                    client = Client.load()
                    
                    logo_data = None
                    if client.logo and client.logo.grid_id:
                        logo_data = base64.b64encode(client.logo.read()).decode('utf-8')

                    # Render invoice to HTML
                    html_content = render_to_string('invoice_print.html', {'invoice': invoice, 'client': client, 'logo_data': logo_data})
                    
                    # Add to zip file
                    filename = f"invoice_{invoice.invoice_number.replace('/', '_')}.html"
                    zf.writestr(filename, html_content)

                except DoesNotExist:
                    # Skip if invoice not found
                    continue
        
        response = HttpResponse(zip_buffer.getvalue(), content_type='application/zip')
        response['Content-Disposition'] = 'attachment; filename="invoices.zip"'
        return response
    return redirect('invoice_list')



from django.http import HttpResponse

def vendor_logo(request, pk):
    vendor = Vendor.objects.get(pk=pk)
    try:
        if vendor.logo and vendor.logo.grid_id:
            return HttpResponse(vendor.logo.read(), content_type=vendor.logo.content_type)
    except AttributeError:
        pass  # Fall through to generating a logo

    # Generate a logo
    name = vendor.name
    initials = ''.join([s[0] for s in name.split()]).upper()
    
    # Create a circular image
    img = Image.new('RGBA', (100, 100), (255, 255, 255, 0))
    draw = ImageDraw.Draw(img)
    
    # Draw a circle
    draw.ellipse((0, 0, 100, 100), fill=(73, 109, 137), outline=None)
    
    # Add text
    try:
        font = ImageFont.truetype("arial.ttf", 40)
    except IOError:
        font = ImageFont.load_default()
    
    # Center the text
    text_width = font.getlength(initials)
    position = ((100 - text_width) / 2, 25)
    draw.text(position, initials, fill=(255, 255, 0), font=font)
    
    # Save to buffer
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    return HttpResponse(buffer.getvalue(), content_type='image/png')

from .forms import ProfileForm

@login_required
def profile(request):
    profile = request.user.profile
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form = ProfileForm(instance=profile)
    return render(request, 'profile.html', {'form': form})


# --- Purchase Order Views ---
from .models import PurchaseOrder, PurchaseOrderItem
from .forms import PurchaseOrderForm, PurchaseOrderItemFormSet
# from weasyprint import HTML

@login_required
@roles_required(allowed_roles=['admin', 'project_manager', 'accountant'])
def po_list(request):
    po_list = PurchaseOrder.objects.order_by('-po_date')

    query = request.GET.get('q')
    if query:
        vendor_ids = [vendor.id for vendor in Vendor.objects.filter(name__icontains=query)]
        po_list = po_list.filter(
            Q(po_number__icontains=query) | Q(vendor__in=vendor_ids)
        )

    paginator = Paginator(po_list, 10)
    page = request.GET.get('page')
    try:
        purchase_orders = paginator.page(page)
    except PageNotAnInteger:
        purchase_orders = paginator.page(1)
    except EmptyPage:
        purchase_orders = paginator.page(paginator.num_pages)

    return render(request, 'po_list.html', {'purchase_orders': purchase_orders})

@login_required
@roles_required(allowed_roles=['admin', 'project_manager', 'accountant'])
def po_detail(request, pk):
    try:
        po = PurchaseOrder.objects.get(pk=pk)
        client = Client.load()
    except DoesNotExist:
        return redirect('po_list')
    return render(request, 'po_detail.html', {'po': po, 'client': client})

@login_required
@roles_required(allowed_roles=['admin', 'project_manager'])
def po_create(request):
    if request.method == 'POST':
        po_form = PurchaseOrderForm(request.POST)
        formset = PurchaseOrderItemFormSet(request.POST)
        if po_form.is_valid() and formset.is_valid():
            vendor_id = po_form.cleaned_data['vendor']
            vendor = Vendor.objects.get(pk=vendor_id)
            po = PurchaseOrder(
                vendor=vendor,
                po_date=po_form.cleaned_data['po_date'],
                terms=po_form.cleaned_data['terms'],
            )
            if po_form.cleaned_data.get('po_number'):
                po.po_number = po_form.cleaned_data['po_number']

            items = []
            for item_form in formset:
                if item_form.cleaned_data:
                    item = PurchaseOrderItem(**item_form.cleaned_data)
                    items.append(item)
            po.items = items
            po.save()
            return redirect('po_list')
    else:
        po_form = PurchaseOrderForm()
        formset = PurchaseOrderItemFormSet()
    return render(request, 'po_form.html', {'po_form': po_form, 'formset': formset})

@login_required
@roles_required(allowed_roles=['admin', 'project_manager'])
def po_update(request, pk):
    try:
        po = PurchaseOrder.objects.get(pk=pk)
    except DoesNotExist:
        return redirect('po_list')

    if request.method == 'POST':
        po_form = PurchaseOrderForm(request.POST)
        formset = PurchaseOrderItemFormSet(request.POST)
        if po_form.is_valid() and formset.is_valid():
            vendor_id = po_form.cleaned_data['vendor']
            po.vendor = Vendor.objects.get(pk=vendor_id)
            po.po_date = po_form.cleaned_data['po_date']
            po.terms = po_form.cleaned_data['terms']
            po.po_number = po_form.cleaned_data['po_number']

            items = []
            for item_form in formset:
                if item_form.cleaned_data:
                    item = PurchaseOrderItem(**item_form.cleaned_data)
                    items.append(item)
            po.items = items
            po.save()
            return redirect('po_list')
    else:
        initial_po_data = {
            'vendor': str(po.vendor.id),
            'po_date': po.po_date.strftime('%Y-%m-%d'),
            'terms': po.terms,
            'po_number': po.po_number,
        }
        po_form = PurchaseOrderForm(initial=initial_po_data)
        initial_items_data = [item.to_mongo().to_dict() for item in po.items]
        formset = PurchaseOrderItemFormSet(initial=initial_items_data)

    return render(request, 'po_form.html', {'po_form': po_form, 'formset': formset, 'po': po})

@login_required
@roles_required(allowed_roles=['admin', 'project_manager'])
def po_delete(request, pk):
    try:
        po = PurchaseOrder.objects.get(pk=pk)
    except DoesNotExist:
        return redirect('po_list')

    if request.method == 'POST':
        po.delete()
        return redirect('po_list')
    return render(request, 'po_confirm_delete.html', {'po': po})

@login_required
@roles_required(allowed_roles=['admin', 'project_manager', 'accountant'])
def po_download(request, pk):
    po = get_object_or_404(PurchaseOrder, pk=pk)
    client = Client.load()
    html_string = render_to_string('po_detail.html', {'po': po, 'client': client})
    pdf_file = HTML(string=html_string, base_url=request.build_absolute_uri()).write_pdf()
    
    response = HttpResponse(pdf_file, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="PO_{po.po_number}.pdf"'
    return response

@login_required
@roles_required(allowed_roles=['admin', 'project_manager', 'accountant'])
def po_bulk_download(request):
    if request.method == 'POST':
        po_ids = request.POST.getlist('po_ids')
        if not po_ids:
            return redirect('po_list')

        zip_buffer = BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
            for po_id in po_ids:
                po = get_object_or_404(PurchaseOrder, pk=po_id)
                client = Client.load()
                html_string = render_to_string('po_detail.html', {'po': po, 'client': client})
                pdf_file = HTML(string=html_string, base_url=request.build_absolute_uri()).write_pdf()
                filename = f"PO_{po.po_number.replace('/', '-')}.pdf"
                zf.writestr(filename, pdf_file)
        
        response = HttpResponse(zip_buffer.getvalue(), content_type='application/zip')
        response['Content-Disposition'] = 'attachment; filename="purchase_orders.zip"'
        return response
    return redirect('po_list')
