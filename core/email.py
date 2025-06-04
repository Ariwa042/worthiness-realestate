from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags

def send_valuation_request_email(valuation_request):
    """Send email notification for new valuation request"""
    subject = f'New Valuation Request from {valuation_request.name}'
    html_message = render_to_string('core/emails/valuation_request.html', {
        'valuation': valuation_request
    })
    plain_message = strip_tags(html_message)
    
    # Email to admin/agent
    send_mail(
        subject=subject,
        message=plain_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[valuation_request.branch.email],
        html_message=html_message
    )
    
    # Confirmation email to customer
    customer_subject = 'Your Valuation Request Has Been Received'
    customer_html = render_to_string('core/emails/valuation_confirmation.html', {
        'valuation': valuation_request
    })
    customer_plain = strip_tags(customer_html)
    
    send_mail(
        subject=customer_subject,
        message=customer_plain,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[valuation_request.email],
        html_message=customer_html
    )

def send_property_enquiry_email(enquiry):
    """Send email notification for new property enquiry"""
    subject = f'New Property Enquiry from {enquiry.name}'
    html_message = render_to_string('core/emails/property_enquiry.html', {
        'enquiry': enquiry
    })
    plain_message = strip_tags(html_message)
    
    # Email to admin/agent
    send_mail(
        subject=subject,
        message=plain_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[settings.ADMIN_EMAIL],
        html_message=html_message
    )
    
    # Confirmation email to customer
    customer_subject = 'Your Property Enquiry Has Been Received'
    customer_html = render_to_string('core/emails/enquiry_confirmation.html', {
        'enquiry': enquiry
    })
    customer_plain = strip_tags(customer_html)
    
    send_mail(
        subject=customer_subject,
        message=customer_plain,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[enquiry.email],
        html_message=customer_html
    )

def send_appointment_email(appointment):
    """Send email notification for new viewing appointment"""
    subject = f'New Viewing Appointment from {appointment.first_name} {appointment.last_name}'
    html_message = render_to_string('core/emails/appointment.html', {
        'appointment': appointment
    })
    plain_message = strip_tags(html_message)
    
    # Email to admin/agent
    send_mail(
        subject=subject,
        message=plain_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[settings.ADMIN_EMAIL],
        html_message=html_message
    )
    
    # Confirmation email to customer
    customer_subject = 'Your Viewing Appointment Has Been Scheduled'
    customer_html = render_to_string('core/emails/appointment_confirmation.html', {
        'appointment': appointment
    })
    customer_plain = strip_tags(customer_html)
    
    send_mail(
        subject=customer_subject,
        message=customer_plain,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[appointment.email],
        html_message=customer_html
    )

def send_appointment_status_update_email(appointment):
    """Send email notification when appointment status changes"""
    subject = f'Your Viewing Appointment Has Been {appointment.get_status_display()}'
    html_message = render_to_string('core/emails/appointment_status_update.html', {
        'appointment': appointment
    })
    plain_message = strip_tags(html_message)
    
    send_mail(
        subject=subject,
        message=plain_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[appointment.email],
        html_message=html_message
    )
