from django.db import models
from django.contrib.auth.models import User
import mongoengine as me
from datetime import datetime
from num2words import num2words
from django.utils import timezone

class Vendor(me.Document):
    user_id = me.IntField(required=True)
    name = me.StringField(max_length=255, required=True)
    address = me.StringField(required=True)
    city = me.StringField(max_length=255, required=True)
    state = me.StringField(max_length=255, required=True)
    zip_code = me.StringField(max_length=10, required=False)
    phone_number = me.StringField(max_length=20, required=True)
    email = me.EmailField(required=True)
    tax_tin = me.StringField(max_length=255)
    logo = me.ImageField(upload_to='logos/')
    bank_account_number = me.StringField(max_length=255)
    bank_account_name = me.StringField(max_length=255)
    bank_name = me.StringField(max_length=255)
    invoice_template = me.StringField(max_length=255, choices=[
        ('template1', 'Template 1'),
        ('template2', 'Template 2'),
        ('template3', 'Template 3'),
    ])

    def __str__(self):
        return self.name


class Client(me.Document):
    company_name = me.StringField(max_length=255, default="My Company")
    logo = me.ImageField(upload_to='client_logos/')
    address = me.StringField(default="")
    email = me.EmailField(required=False, null=True)
    phone_number = me.StringField(max_length=20, default="")

    def __str__(self):
        return self.company_name

    @classmethod
    def load(cls):
        obj = cls.objects.first()
        if not obj:
            obj = cls().save()
        return obj


from django.db.models.signals import post_save
from django.dispatch import receiver

class Profile(models.Model):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('accountant', 'Accountant'),
        ('project_manager', 'Project Manager'),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='project_manager')
    profile_picture = models.ImageField(upload_to='profile_pics/', null=True, blank=True)
    phone_number = models.CharField(max_length=20, blank=True)
    address = models.CharField(max_length=255, blank=True)
    bio = models.TextField(blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.user.username} - {self.get_role_display()}'

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    try:
        instance.profile.save()
    except Profile.DoesNotExist:
        Profile.objects.create(user=instance)

class InvoiceItem(me.EmbeddedDocument):
    description = me.StringField(required=True)
    quantity = me.FloatField(required=True)
    unit_price = me.DecimalField(required=True, precision=2)
    discount = me.DecimalField(default=0.0, precision=2)
    tax = me.BooleanField(default=False)

    @property
    def amount(self):
        return self.quantity * float(self.unit_price)

    @property
    def tax_amount(self):
        if self.tax:
            return self.amount * 0.075
        return 0

    @property
    def net_amount(self):
        # As per user's weird calculation
        return self.amount - self.tax_amount - float(self.discount)


class Invoice(me.Document):
    vendor = me.ReferenceField('Vendor', required=True)
    invoice_number = me.StringField(max_length=255, unique=True)
    invoice_date = me.DateTimeField(default=datetime.now)
    terms = me.StringField(default="Please pay within 30 days.")
    items = me.ListField(me.EmbeddedDocumentField(InvoiceItem))

    @property
    def sub_total(self):
        return sum(item.net_amount for item in self.items)

    @property
    def discount_total(self):
        return sum(float(item.discount) for item in self.items)

    @property
    def tax_total(self):
        return sum(item.tax_amount for item in self.items)

    @property
    def total(self):
        # As per user's weird calculation
        return self.sub_total - self.discount_total + self.tax_total

    @property
    def total_in_words(self):
        try:
            # Assuming currency is Naira. The user's example used "Naira".
            return f"{num2words(self.total, to='currency', lang='en_NG').replace('naira', '').replace('(', '').title()} Naira Only"
        except Exception:
            return "" # num2words might not support en_NG fully for currency

    def save(self, *args, **kwargs):
        if not self.invoice_number:
            self.invoice_number = self._generate_invoice_number()
        super().save(*args, **kwargs)

    def _generate_invoice_number(self):
        year = datetime.now().year
        vendor_initials = "".join([name[0] for name in self.vendor.name.split()]).upper()
        last_invoice = Invoice.objects(invoice_number__startswith=f'INV/{vendor_initials}/{year}/').order_by('-invoice_number').first()
        if last_invoice:
            last_number = int(last_invoice.invoice_number.split('/')[-1])
            new_number = last_number + 1
        else:
            new_number = 1
        return f'INV/{vendor_initials}/{year}/{new_number:04d}'


class PurchaseOrderItem(me.EmbeddedDocument):
    description = me.StringField(required=True)
    quantity = me.FloatField(required=True)
    unit_price = me.DecimalField(required=True, precision=2)

    @property
    def amount(self):
        return self.quantity * float(self.unit_price)

class PurchaseOrder(me.Document):
    vendor = me.ReferenceField('Vendor', required=True)
    po_number = me.StringField(max_length=255, unique=True)
    po_date = me.DateTimeField(default=datetime.now)
    terms = me.StringField()
    items = me.ListField(me.EmbeddedDocumentField(PurchaseOrderItem))

    @property
    def sub_total(self):
        return sum(item.amount for item in self.items)

    @property
    def total(self):
        return self.sub_total

    def save(self, *args, **kwargs):
        if not self.po_number:
            self.po_number = self._generate_po_number()
        super().save(*args, **kwargs)

    def _generate_po_number(self):
        year = datetime.now().year
        vendor_initials = "".join([name[0] for name in self.vendor.name.split()]).upper()
        last_po = PurchaseOrder.objects(po_number__startswith=f'PO/{vendor_initials}/{year}/').order_by('-po_number').first()
        new_number = int(last_po.po_number.split('/')[-1]) + 1 if last_po else 1
        return f'PO/{vendor_initials}/{year}/{new_number:04d}'
