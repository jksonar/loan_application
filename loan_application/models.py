from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator

class User(AbstractUser):
    CUSTOMER = 'customer'
    BANK_STAFF = 'bank_staff'
    ADMIN = 'admin'
    
    ROLE_CHOICES = [
        (CUSTOMER, 'Customer'),
        (BANK_STAFF, 'Bank Staff'),
        (ADMIN, 'Admin'),
    ]
    
    # Add related_name arguments to avoid clashes
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='loan_user_set',
        blank=True,
        verbose_name='groups',
        help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='loan_user_set',
        blank=True,
        verbose_name='user permissions',
        help_text='Specific permissions for this user.',
    )
    
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=CUSTOMER)
    phone_number = models.CharField(max_length=15)
    address = models.TextField()

class LoanType(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    interest_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    required_documents = models.TextField()
    max_amount = models.DecimalField(max_digits=12, decimal_places=2)
    tenure_min = models.IntegerField(help_text='Minimum tenure in months')
    tenure_max = models.IntegerField(help_text='Maximum tenure in months')

    def __str__(self):
        return self.name

class LoanApplication(models.Model):
    STATUS_CHOICES = [
        ('enquiry', 'Initial Enquiry'),
        ('documents_pending', 'Documents Pending'),
        ('under_verification', 'Under Verification'),
        ('additional_documents_required', 'Additional Documents Required'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('disbursed', 'Disbursed')
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    loan_type = models.ForeignKey(LoanType, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    tenure = models.IntegerField(help_text='Tenure in months')
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='enquiry')
    application_date = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)
    notes = models.TextField(blank=True)

    def get_status_color(self):
        status_colors = {
            'pending': 'warning',
            'approved': 'success',
            'rejected': 'danger',
            'processing': 'info'
        }
        return status_colors.get(self.status, 'secondary')

class Document(models.Model):
    loan_application = models.ForeignKey(LoanApplication, on_delete=models.CASCADE)
    document_type = models.CharField(max_length=100)
    file = models.FileField(upload_to='loan_documents/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    verified = models.BooleanField(default=False)
    verification_notes = models.TextField(blank=True)

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)
    notification_type = models.CharField(max_length=50)

class StatusHistory(models.Model):
    loan_application = models.ForeignKey(LoanApplication, on_delete=models.CASCADE)
    status = models.CharField(max_length=20)
    notes = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']
