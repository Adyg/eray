from django.core.mail import EmailMultiAlternatives


class ErEmail():

    def __init__(self, html_body, text_body, subject, from_email, to_email, headers, display_name):
        self.html_body = html_body
        self.text_body = text_body
        self.subject = subject
        self.from_email = from_email
        self.to_email = to_email
        self.headers = headers
        self.display_name = display_name


    def _format_email(self):
        email = EmailMultiAlternatives(
            subject=self.subject,
            body=self.text_body,
            from_email='%s <%s>' % (self.display_name, self.from_email),
            to=[self.to_email],
            headers=self.headers,
            alternatives=[(self.html_body, "text/html")]
        )

        return email

    def send(self):
        email = self._format_email()

        return email.send()



