from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.views.generic import ListView, DetailView, UpdateView
from django.urls import reverse_lazy
from .models import LoanType, LoanApplication, Document, Notification
from .forms import (
    CustomUserCreationForm, LoanEnquiryForm, DocumentUploadForm,
    LoanApplicationUpdateForm, UserProfileUpdateForm
)

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, 'Account created successfully! Please log in.')
            return redirect('login')
    else:
        form = CustomUserCreationForm()
    return render(request, 'loan_application/register.html', {'form': form})

class LoanTypeListView(ListView):
    model = LoanType
    template_name = 'loan_application/loan_types.html'
    context_object_name = 'loan_types'

@login_required
def loan_enquiry(request):
    if request.method == 'POST':
        form = LoanEnquiryForm(request.POST)
        if form.is_valid():
            loan_application = form.save(commit=False)
            loan_application.user = request.user
            loan_application.save()
            messages.success(request, 'Loan enquiry submitted successfully!')
            return redirect('loan_application_detail', pk=loan_application.pk)
    else:
        form = LoanEnquiryForm()
    return render(request, 'loan_application/loan_enquiry.html', {'form': form})

class LoanApplicationDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = LoanApplication
    template_name = 'loan_application/loan_application_detail.html'
    
    def test_func(self):
        application = self.get_object()
        return self.request.user == application.user or self.request.user.role in ['bank_staff', 'admin']

@login_required
def upload_documents(request, pk):
    loan_application = get_object_or_404(LoanApplication, pk=pk)
    if request.method == 'POST':
        form = DocumentUploadForm(request.POST, request.FILES)
        if form.is_valid():
            document = form.save(commit=False)
            document.loan_application = loan_application
            document.save()
            messages.success(request, 'Document uploaded successfully!')
            return redirect('loan_application_detail', pk=pk)
    else:
        form = DocumentUploadForm()
    return render(request, 'loan_application/upload_documents.html', {
        'form': form,
        'loan_application': loan_application
    })

class LoanApplicationUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = LoanApplication
    form_class = LoanApplicationUpdateForm
    template_name = 'loan_application/loan_application_update.html'
    
    def test_func(self):
        return self.request.user.role in ['bank_staff', 'admin']
    
    def get_success_url(self):
        return reverse_lazy('loan_application_detail', kwargs={'pk': self.object.pk})

    def form_valid(self, form):
        response = super().form_valid(form)
        # Create notification for status update
        Notification.objects.create(
            user=self.object.user,
            title='Loan Application Status Updated',
            message=f'Your loan application status has been updated to {self.object.status}',
            notification_type='status_update'
        )
        return response

@login_required
def profile(request):
    if request.method == 'POST':
        form = UserProfileUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('profile')
    else:
        form = UserProfileUpdateForm(instance=request.user)
    return render(request, 'loan_application/profile.html', {'form': form})

class MyLoanApplicationsView(LoginRequiredMixin, ListView):
    model = LoanApplication
    template_name = 'loan_application/my_applications.html'
    context_object_name = 'applications'
    
    def get_queryset(self):
        return LoanApplication.objects.filter(user=self.request.user).order_by('-application_date')

class NotificationListView(LoginRequiredMixin, ListView):
    model = Notification
    template_name = 'loan_application/notifications.html'
    context_object_name = 'notifications'
    
    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user, read=False).order_by('-created_at')


class BankStaffDashboardView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = LoanApplication
    template_name = 'loan_application/bank_staff_dashboard.html'
    context_object_name = 'applications'
    
    def test_func(self):
        return self.request.user.role in ['bank_staff', 'admin']
    
    def get_queryset(self):
        return LoanApplication.objects.all().order_by('-application_date')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['pending_applications'] = self.get_queryset().filter(status='pending').count()
        context['approved_applications'] = self.get_queryset().filter(status='approved').count()
        context['rejected_applications'] = self.get_queryset().filter(status='rejected').count()
        return context

class DocumentVerificationView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = Document
    template_name = 'loan_application/document_verification.html'
    context_object_name = 'document'
    
    def test_func(self):
        return self.request.user.role in ['bank_staff', 'admin']
    
    def post(self, request, *args, **kwargs):
        document = self.get_object()
        action = request.POST.get('action')
        if action == 'verify':
            document.is_verified = True
            document.verification_notes = request.POST.get('notes')
            document.save()
            messages.success(request, 'Document verified successfully!')
        elif action == 'reject':
            document.is_verified = False
            document.verification_notes = request.POST.get('notes')
            document.save()
            messages.warning(request, 'Document rejected!')
        return redirect('loan_application_detail', pk=document.loan_application.pk)

class CustomerTrackingView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = LoanApplication
    template_name = 'loan_application/customer_tracking.html'
    context_object_name = 'application'
    
    def test_func(self):
        return self.request.user.role in ['bank_staff', 'admin']
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        application = self.get_object()
        context['documents'] = application.document_set.all().order_by('-upload_date')
        context['notifications'] = application.user.notification_set.all().order_by('-created_at')[:10]
        context['status_history'] = application.statushistory_set.all().order_by('-timestamp')
        return context
