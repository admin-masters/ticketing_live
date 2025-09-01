from django.core.mail import send_mail
from django.template.loader import render_to_string

def send_ticket_email(subject, template_name, context, recipient_email):
    """
    Utility to send HTML email for tickets.
    """
    email_body = render_to_string(template_name, context)
    send_mail(
        subject,
        '',  # Plain-text version (leave blank if not needed)
        'no-reply@yourdomain.com',  # Update this to your email
        [recipient_email],
        html_message=email_body,  # Rendered HTML
        fail_silently=False,
    )