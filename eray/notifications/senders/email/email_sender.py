from eray.lib.utils.email.er_email import ErEmail

from django.template.loader import get_template
from django.template import Context


class EmailSender():

    def send_notification(notification):
        html_template = 'html/{}.html'.format(notification.notification_type.lower())
        print(html_template)
        text_template = 'text/{}.txt'.format(notification.notification_type.lower())

        html = get_template(html_template)
        text = get_template(text_template)

        context = Context({
                'notification': notification,
            })

        html_body = html.render(context)
        text_body = text.render(context)

        email = ErEmail(
                html_body=html_body,
                text_body=text_body,
                subject='Notification',
                from_email='notifications@eraya',
                to_email=notification.user.email,
                headers=[],
                display_name='Eraya',
            )

        email.send()

        notification.mark_sent()