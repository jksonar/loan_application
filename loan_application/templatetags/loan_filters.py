from django import template

register = template.Library()

@register.filter
def status_color(status):
    status_colors = {
        'enquiry': 'info',
        'documents_pending': 'warning',
        'under_verification': 'primary',
        'additional_documents_required': 'warning',
        'approved': 'success',
        'rejected': 'danger',
        'disbursed': 'success'
    }
    return status_colors.get(status, 'secondary')