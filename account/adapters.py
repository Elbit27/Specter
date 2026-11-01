from allauth.account.adapter import DefaultAccountAdapter
from .models import EmailVerificationCode


class CustomAccountAdapter(DefaultAccountAdapter):
    def send_confirmation_mail(self, request, emailconfirmation, signup):
        # Генерируем 6-значный код
        user = emailconfirmation.email_address.user
        code = EmailVerificationCode.generate_code(user)

        ctx = {
            "user": user,
            "activate_url": self.get_email_confirmation_url(request, emailconfirmation),
            "verification_code": code,
        }

        if signup:
            email_template = "account/email/email_confirmation_signup"
        else:
            email_template = "account/email/email_confirmation"

        self.send_mail(email_template, emailconfirmation.email_address.email, ctx)

        print(f"--- ПИСЬМО ОТПРАВЛЕНО. КОД: {code} ---")