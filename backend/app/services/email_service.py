import structlog
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional, Dict, Any
import os
import re
from app.config import settings

logger = structlog.get_logger(__name__)

class EmailService:
    def __init__(self):
        self.smtp_server = settings.SMTP_SERVER
        self.smtp_port = settings.SMTP_PORT
        self.smtp_username = settings.SMTP_USERNAME
        self.smtp_password = settings.SMTP_PASSWORD or settings.SENDGRID_API_KEY
        self.email_from = settings.EMAIL_FROM
        self.sendgrid_api_key = settings.SENDGRID_API_KEY

    def send_email(self, to_email: str, subject: str, html_content: str, text_content: Optional[str] = None) -> bool:
        """Send email using SMTP or SendGrid API fallback"""
        # Validate email
        if not self._validate_email(to_email):
            logger.error("Invalid email address", to_email=to_email)
            return False

        # Try SMTP first
        if self._send_via_smtp(to_email, subject, html_content, text_content):
            return True

        # Fallback to SendGrid API if available
        if self.sendgrid_api_key:
            return self._send_via_sendgrid(to_email, subject, html_content, text_content)

        logger.error("No email provider available", to_email=to_email)
        return False

    def _send_via_smtp(self, to_email: str, subject: str, html_content: str, text_content: Optional[str] = None) -> bool:
        """Send email using SMTP"""
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.email_from
            msg['To'] = to_email

            # Add text part
            if text_content:
                text_part = MIMEText(text_content, 'plain')
                msg.attach(text_part)

            # Add HTML part
            html_part = MIMEText(html_content, 'html')
            msg.attach(html_part)

            # Send email
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.smtp_username, self.smtp_password)
            server.sendmail(self.email_from, to_email, msg.as_string())
            server.quit()

            logger.info("Email sent via SMTP", to_email=to_email, subject=subject)
            return True

        except Exception as e:
            logger.warning("SMTP failed, trying SendGrid fallback", error=str(e), to_email=to_email)
            return False

    def _send_via_sendgrid(self, to_email: str, subject: str, html_content: str, text_content: Optional[str] = None,
                          template_id: Optional[str] = None, dynamic_data: Optional[Dict[str, Any]] = None) -> bool:
        """Send email using SendGrid API with optional dynamic template support"""
        try:
            import sendgrid
            from sendgrid.helpers.mail import Mail, Email, To, Content, Personalization

            sg = sendgrid.SendGridAPIClient(api_key=self.sendgrid_api_key)
            from_email = Email(self.email_from)
            to_email_obj = To(to_email)

            if template_id and dynamic_data:
                # Use dynamic template
                mail = Mail(from_email=from_email, to_emails=[to_email_obj])
                mail.template_id = template_id
                personalization = Personalization()
                personalization.add_to(to_email_obj)
                personalization.dynamic_template_data = dynamic_data
                mail.add_personalization(personalization)
                logger.info("Sending email via SendGrid with dynamic template", to_email=to_email, template_id=template_id)
            else:
                # Fallback to basic content
                content = Content("text/html", html_content)
                mail = Mail(from_email, to_email_obj, subject, content)
                logger.info("Sending email via SendGrid with basic content", to_email=to_email, subject=subject)

            response = sg.client.mail.send.post(request_body=mail.get())
            if response.status_code == 202:
                logger.info("Email sent via SendGrid", to_email=to_email, subject=subject, template_id=template_id)
                return True
            else:
                logger.error("SendGrid API error", status_code=response.status_code, to_email=to_email, template_id=template_id)
                return False

        except ImportError:
            logger.warning("SendGrid library not installed, skipping API fallback", to_email=to_email)
            return False
        except Exception as e:
            logger.error("SendGrid API failed", error=str(e), to_email=to_email, template_id=template_id)
            return False

    def _validate_email(self, email: str) -> bool:
        """Validate email address format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None

    def send_welcome_email(self, to_email: str, user_name: str, company_name: str = "Your Company") -> bool:
        """Send welcome email to new user"""
        subject = f"Welcome to Workforce App, {user_name}!"
        html_content = f"""
        <html>
        <body>
            <h2>Welcome to Workforce App, {user_name}!</h2>
            <p>Your account has been successfully created for <strong>{company_name}</strong>. You can now log in and start managing your workforce efficiently.</p>
            <p>Key features available:</p>
            <ul>
                <li>Dashboard with real-time KPIs</li>
                <li>Task and shift management</li>
                <li>Chat and notifications</li>
                <li>Employee profiles and approvals</li>
            </ul>
            <p>If you have any questions, please contact our support team.</p>
            <br>
            <p>Best regards,<br>The Workforce App Team</p>
        </body>
        </html>
        """
        text_content = f"Welcome to Workforce App, {user_name}! Your account for {company_name} has been created. Log in to access dashboard, tasks, chat, and more."
        return self.send_email(to_email, subject, html_content, text_content)

    def send_password_reset_email(self, to_email: str, reset_token: str, user_name: str = "User") -> bool:
        """Send password reset email using SendGrid dynamic template"""
        reset_url = f"{os.getenv('FRONTEND_URL', 'http://localhost:3000')}/reset-password?token={reset_token}"
        template_id = "d-password-reset"
        dynamic_data = {
            "username": user_name,
            "reset_link": reset_url
        }
        logger.info("Sending password reset email", to_email=to_email, user_name=user_name, reset_token=reset_token[:8] + "...")
        return self._send_via_sendgrid(to_email, "", "", template_id=template_id, dynamic_data=dynamic_data)

    def send_notification_email(self, to_email: str, title: str, message: str, user_name: str = "User") -> bool:
        """Send notification email"""
        subject = f"Workforce App Notification: {title}"
        html_content = f"""
        <html>
        <body>
            <h2>{title}</h2>
            <p>Hello {user_name},</p>
            <p>{message}</p>
            <p>You can view all notifications in your <a href="{os.getenv('FRONTEND_URL', 'http://localhost:3000')}/notifications">dashboard</a>.</p>
            <br>
            <p>Best regards,<br>The Workforce App Team</p>
        </body>
        </html>
        """
        text_content = f"Hello {user_name}, {title}: {message}. View in dashboard: {os.getenv('FRONTEND_URL', 'http://localhost:3000')}/notifications"
        return self.send_email(to_email, subject, html_content, text_content)

# Global email service instance
email_service = EmailService()
