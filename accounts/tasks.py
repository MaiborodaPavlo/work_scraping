from django.core.mail import EmailMultiAlternatives
from work_scraping.celery import app
from work_scraping.settings import EMAIL_HOST_USER


@app.task
def send_contact_email(data):
    html = f"""
<p>City: {data['city']}</p>
<p>Language: {data['language']}</p>
<p>Requester email: {data['email']}</p>
"""
    subject = 'City/Language request'
    msg = EmailMultiAlternatives(subject, subject, EMAIL_HOST_USER, [EMAIL_HOST_USER])
    msg.attach_alternative(html, "text/html")
    msg.send()
