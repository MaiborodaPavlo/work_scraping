from django.core.mail import EmailMultiAlternatives
from work_scraping.celery import app
from work_scraping.settings import EMAIL_HOST_USER


@app.task
def send_contact_email(data):
    html = f"<p>City: {data['city']}</p>"
    html += f"<p>Language: {data['language']}</p>"
    html += f"<p>Requester email: {data['email']}</p>"
    msg = EmailMultiAlternatives('City/Language request', 'City/Language request', EMAIL_HOST_USER, [EMAIL_HOST_USER])
    msg.attach_alternative(html, "text/html")
    msg.send()
