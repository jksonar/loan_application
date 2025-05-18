from django.urls import path
from . import views

urlpatterns = [
    # Authentication and User Management
    path('register/', views.register, name='register'),
    path('profile/', views.profile, name='profile'),
    
    # Loan Types
    path('', views.LoanTypeListView.as_view(), name='home'),
    path('loan-types/', views.LoanTypeListView.as_view(), name='loan_types'),
    
    # Loan Applications
    path('loan-enquiry/', views.loan_enquiry, name='loan_enquiry'),
    path('my-applications/', views.MyLoanApplicationsView.as_view(), name='my_applications'),
    path('application/<int:pk>/', views.LoanApplicationDetailView.as_view(), name='loan_application_detail'),
    path('application/<int:pk>/update/', views.LoanApplicationUpdateView.as_view(), name='loan_application_update'),
    
    # Documents
    path('application/<int:pk>/upload-documents/', views.upload_documents, name='upload_documents'),
    
    # Notifications
    path('notifications/', views.NotificationListView.as_view(), name='notifications'),
    
    # Bank Staff Views
    path('staff/dashboard/', views.BankStaffDashboardView.as_view(), name='bank_staff_dashboard'),
    path('staff/document/<int:pk>/verify/', views.DocumentVerificationView.as_view(), name='document_verification'),
    path('staff/customer/<int:pk>/track/', views.CustomerTrackingView.as_view(), name='customer_tracking'),
]