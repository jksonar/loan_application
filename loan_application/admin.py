from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, LoanType, LoanApplication, Document, Notification

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'role', 'phone_number', 'is_staff')
    list_filter = ('role', 'is_staff', 'is_active')
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email', 'phone_number', 'address')}),
        ('Permissions', {'fields': ('role', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'role', 'phone_number', 'address'),
        }),
    )
    search_fields = ('username', 'email', 'phone_number')
    ordering = ('username',)

@admin.register(LoanType)
class LoanTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'interest_rate', 'max_amount', 'tenure_min', 'tenure_max')
    search_fields = ('name',)

@admin.register(LoanApplication)
class LoanApplicationAdmin(admin.ModelAdmin):
    list_display = ('user', 'loan_type', 'amount', 'status', 'application_date', 'last_updated')
    list_filter = ('status', 'loan_type', 'application_date')
    search_fields = ('user__username', 'user__email')
    readonly_fields = ('application_date', 'last_updated')

@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ('loan_application', 'document_type', 'uploaded_at', 'verified')
    list_filter = ('verified', 'document_type', 'uploaded_at')
    search_fields = ('loan_application__user__username', 'document_type')
    readonly_fields = ('uploaded_at',)

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'title', 'notification_type', 'created_at', 'read')
    list_filter = ('notification_type', 'read', 'created_at')
    search_fields = ('user__username', 'title')
    readonly_fields = ('created_at',)
