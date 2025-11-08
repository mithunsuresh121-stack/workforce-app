import pytest
from unittest.mock import patch, MagicMock
from app.services.email_service import EmailService
from app.config import settings

class TestEmailService:
    def setup_method(self):
        self.email_service = EmailService()

    @patch('smtplib.SMTP')
    def test_send_email_via_smtp_success(self, mock_smtp):
        """Test successful email sending via SMTP"""
        mock_server = MagicMock()
        mock_smtp.return_value = mock_server

        result = self.email_service.send_email(
            "test@example.com", "Test Subject", "<p>Test</p>", "Test"
        )

        assert result is True
        mock_smtp.assert_called_once_with(settings.SMTP_SERVER, settings.SMTP_PORT)
        mock_server.starttls.assert_called_once()
        mock_server.login.assert_called_once()
        mock_server.sendmail.assert_called_once()
        mock_server.quit.assert_called_once()

    @patch('smtplib.SMTP')
    def test_send_email_via_smtp_failure_fallback_to_sendgrid(self, mock_smtp):
        """Test SMTP failure with SendGrid fallback"""
        mock_smtp.side_effect = Exception("SMTP failed")

        with patch.object(self.email_service, '_send_via_sendgrid', return_value=True) as mock_sendgrid:
            self.email_service.sendgrid_api_key = "test_key"
            result = self.email_service.send_email(
                "test@example.com", "Test Subject", "<p>Test</p>", "Test"
            )

            assert result is True
            mock_sendgrid.assert_called_once()

    def test_send_welcome_email(self):
        """Test welcome email template"""
        with patch.object(self.email_service, 'send_email', return_value=True) as mock_send:
            result = self.email_service.send_welcome_email(
                "test@example.com", "John Doe", "Test Company"
            )

            assert result is True
            mock_send.assert_called_once()
            args = mock_send.call_args[0]
            assert "test@example.com" in args
            assert "Welcome to Workforce App, John Doe!" in args[1]
            assert "Test Company" in args[2]

    def test_send_password_reset_email(self):
        """Test password reset email template"""
        with patch.object(self.email_service, 'send_email', return_value=True) as mock_send:
            result = self.email_service.send_password_reset_email(
                "test@example.com", "reset_token_123", "John Doe"
            )

            assert result is True
            mock_send.assert_called_once()
            args = mock_send.call_args[0]
            assert "test@example.com" in args
            assert "Password Reset Request - Workforce App" in args[1]
            assert "Hello John Doe," in args[2]
            assert "reset_token_123" in args[2]

    def test_send_notification_email(self):
        """Test notification email template"""
        with patch.object(self.email_service, 'send_email', return_value=True) as mock_send:
            result = self.email_service.send_notification_email(
                "test@example.com", "Task Assigned", "You have a new task", "John Doe"
            )

            assert result is True
            mock_send.assert_called_once()
            args = mock_send.call_args[0]
            assert "test@example.com" in args
            assert "Workforce App Notification: Task Assigned" in args[1]
            assert "Hello John Doe," in args[2]
            assert "You have a new task" in args[2]

    @patch('sendgrid.SendGridAPIClient')
    def test_send_via_sendgrid_success(self, mock_sg_client):
        """Test SendGrid API sending"""
        mock_client = MagicMock()
        mock_sg_client.return_value = mock_client
        mock_response = MagicMock()
        mock_response.status_code = 202
        mock_client.client.mail.send.post.return_value = mock_response

        self.email_service.sendgrid_api_key = "test_key"
        result = self.email_service._send_via_sendgrid(
            "test@example.com", "Subject", "<p>Content</p>"
        )

        assert result is True
        mock_sg_client.assert_called_once_with(api_key="test_key")

    @patch('sendgrid.SendGridAPIClient')
    def test_send_via_sendgrid_failure(self, mock_sg_client):
        """Test SendGrid API failure"""
        mock_client = MagicMock()
        mock_sg_client.return_value = mock_client
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_client.client.mail.send.post.return_value = mock_response

        self.email_service.sendgrid_api_key = "test_key"
        result = self.email_service._send_via_sendgrid(
            "test@example.com", "Subject", "<p>Content</p>"
        )

        assert result is False

    def test_send_via_sendgrid_no_library(self):
        """Test SendGrid fallback when library not installed"""
        # Temporarily remove sendgrid from sys.modules to simulate ImportError
        import sys
        original_sendgrid = sys.modules.get('sendgrid')
        if 'sendgrid' in sys.modules:
            del sys.modules['sendgrid']

        try:
            self.email_service.sendgrid_api_key = "test_key"
            result = self.email_service._send_via_sendgrid(
                "test@example.com", "Subject", "<p>Content</p>"
            )
            assert result is False
        finally:
            if original_sendgrid:
                sys.modules['sendgrid'] = original_sendgrid
