from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from django.urls import reverse
from django.db import models
from .forms import PropertyEnquiryForm, ValuationRequestForm, AppointmentForm
from .models import Branch, PropertyEnquiry, ValuationRequest, Appointments
from property.models import Property
from .email import (
    send_valuation_request_email, 
    send_property_enquiry_email, 
    send_appointment_email,
    send_appointment_status_update_email
)

def index(request):    # Get and shuffle featured properties
    featured_properties = list(Property.objects.filter(
        featured=True, 
        property_status='available'
    ).prefetch_related('images'))
    import random
    random.shuffle(featured_properties)
    
    # Get properties by type for CTAs
    sale_properties = Property.objects.filter(
        property_status='available',
        listing_type='sale'
    ).count()
    
    rent_properties = Property.objects.filter(
        property_status='available',
        listing_type='rent'
    ).count()
    
    # Get branches with their latest valuations
    branches = Branch.objects.prefetch_related(
        'valuation_requests'
    ).annotate(
        recent_valuations=models.Count('valuation_requests')
    ).order_by('-recent_valuations')[:3]
    
    # Get property counts by type for search CTAs
    property_types = Property.objects.filter(
        property_status='available'
    ).values('property_type').annotate(
        count=models.Count('id')
    ).order_by('-count')
    
    # Get unique cities for quick search
    cities = Property.objects.filter(
        property_status='available'
    ).exclude(
        city__isnull=True
    ).values_list('city', flat=True).distinct()[:10]
    
    context = {
        'featured_properties': featured_properties,
        'sale_properties_count': sale_properties,
        'rent_properties_count': rent_properties,
        'branches': branches,
        'property_types': property_types,
        'popular_cities': cities,
        'cta_cards': [
            {
                'title': 'Search Properties',
                'description': 'Find your dream home from our extensive property listings',
                'link': reverse('property:property_search'),
                'icon': 'search'
            },
            {
                'title': 'Request Valuation',
                'description': 'Get a free valuation of your property from our experts',
                'link': reverse('core:request_valuation'),
                'icon': 'calculator'
            },
            {
                'title': 'Contact Branch',
                'description': 'Get in touch with our local experts for personalized service',
                'link': reverse('core:branch_list'),
                'icon': 'office'
            }
        ]
    }
    return render(request, 'home.html', context)

def submit_valuation_request(request):
    if request.method == 'POST':
        form = ValuationRequestForm(request.POST)
        if form.is_valid():
            try:
                valuation = form.save()
                # Send email notifications
                send_valuation_request_email(valuation)
                
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'status': 'success',
                        'message': 'Thank you for your valuation request. We will contact you soon.'
                    })
                messages.success(request, 'Thank you for your valuation request. We will contact you soon.')
                return redirect('core:valuation_success')
            except Exception as e:
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'status': 'error',
                        'message': 'An error occurred while submitting your request.'
                    }, status=400)
                messages.error(request, 'An error occurred while submitting your request.')
                return redirect('core:request_valuation')
    else:
        form = ValuationRequestForm()
    
    return render(request, 'core/request_valuation.html', {'form': form})

def submit_property_enquiry(request):
    if request.method == 'POST':
        form = PropertyEnquiryForm(request.POST)
        if form.is_valid():
            try:
                enquiry = form.save(commit=False)
                property_id = request.POST.get('property_id')
                enquiry.property = get_object_or_404(Property, id=property_id)
                enquiry.save()
                
                # Send email notifications
                send_property_enquiry_email(enquiry)
                
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'status': 'success',
                        'message': 'Thank you for your enquiry. We will contact you soon.'
                    })
                messages.success(request, 'Thank you for your enquiry. We will contact you soon.')
                return redirect('property:property_detail', slug=enquiry.property.slug)
            except Exception as e:
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'status': 'error',
                        'message': 'An error occurred while submitting your enquiry.'
                    }, status=400)
                messages.error(request, 'An error occurred while submitting your enquiry.')
                return redirect('property:property_detail', slug=request.POST.get('property_slug'))
        else:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'status': 'error',
                    'message': 'Please correct the errors in the form.',
                    'errors': form.errors
                }, status=400)
            messages.error(request, 'Please correct the errors in the form.')
            return redirect('property:property_detail', slug=request.POST.get('property_slug'))

def schedule_appointment(request, slug):
    property = get_object_or_404(Property, slug=slug)
    if request.method == 'POST':
        form = AppointmentForm(request.POST)
        if form.is_valid():
            try:
                appointment = form.save(commit=False)
                appointment.property = property
                appointment.save()
                #send_appointment_email(appointment)
                messages.success(request, 'Your viewing appointment has been scheduled. We will contact you to confirm.')
                return redirect('property:property_detail', slug=property.slug)
            except Exception as e:
                import traceback
                print('Error scheduling appointment:', e)
                traceback.print_exc()
                messages.error(request, f'An error occurred while scheduling your appointment: {e}')
        # If form is invalid or exception, fall through to render form with errors
    else:
        form = AppointmentForm()
    context = {
        'form': form,
        'property': property
    }
    return render(request, 'core/schedule_appointment.html', context)

def request_valuation(request):
    branches = Branch.objects.all()
    
    if request.method == 'POST':
        form = ValuationRequestForm(request.POST)
        if form.is_valid():
            try:
                valuation = form.save(commit=False)
                # Assign to the selected branch or default to first branch
                branch_id = request.POST.get('branch_id')
                if branch_id:
                    branch = get_object_or_404(Branch, id=branch_id)
                else:
                    branch = branches.first()
                valuation.branch = branch
                valuation.save()
                
                messages.success(request, 'Thank you for requesting a valuation. We will contact you to arrange a convenient time.')
                return redirect('home')
            except Exception as e:
                messages.error(request, 'An error occurred while submitting your valuation request.')
    else:
        form = ValuationRequestForm()
    
    context = {
        'form': form,
        'branches': branches
    }
    return render(request, 'core/request_valuation.html', context)

def branch_list(request):
    branches = Branch.objects.all()
    context = {
        'branches': branches
    }
    return render(request, 'core/branch_list.html', context)

def branch_detail(request, id):
    branch = get_object_or_404(Branch, id=id)
    context = {
        'branch': branch,
        'valuation_requests': branch.valuation_requests.all()[:5]
    }
    return render(request, 'core/branch_detail.html', context)
