from unittest.mock import MagicMock, patch

import pytest

from app.config import settings
from app.services.email_service import EmailService


class TestEmailService:
    def setup_method(self):
        self.email_service = EmailService()

    @patch("smtplib.SMTP")
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

    @patch("smtplib.SMTP")
    def test_send_email_via_smtp_failure_fallback_to_sendgrid(self, mock_smtp):
        """Test SMTP failure with SendGrid fallback"""
        mock_smtp.side_effect = Exception("SMTP failed")

        with patch.object(
            self.email_service, "_send_via_sendgrid", return_value=True
        ) as mock_sendgrid:
            self.email_service.sendgrid_api_key = "test_key"
            result = self.email_service.send_email(
                "test@example.com", "Test Subject", "<p>Test</p>", "Test"
            )

            assert result is True
            mock_sendgrid.assert_called_once()

    def test_send_email_invalid_email(self):
        """Test email validation failure"""
        result = self.email_service.send_email(
            "invalid-email", "Test Subject", "<p>Test</p>", "Test"
        )
        assert result is False

    def test_send_welcome_email(self):
        """Test welcome email template"""
        with patch.object(
            self.email_service, "send_email", return_value=True
        ) as mock_send:
            result = self.email_service.send_welcome_email(
                "test@example.com", "John Doe", "Test Company"
            )

            assert result is True
            mock_send.assert_called_once()
            args = mock_send.call_args[0]
            assert "test@example.com" in args
            assert "Welcome to Workforce App, John Doe!" in args[1]
            assert "Test Company" in args[2]

    @patch("sendgrid.SendGridAPIClient")
    def test_send_via_sendgrid_basic_success(self, mock_sg_client):
        """Test SendGrid API basic sending"""
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

    @patch("sendgrid.SendGridAPIClient")
    def test_send_via_sendgrid_dynamic_template_success(self, mock_sg_client):
        """Test SendGrid API dynamic template sending"""
        mock_client = MagicMock()
        mock_sg_client.return_value = mock_client
        mock_response = MagicMock()
        mock_response.status_code = 202
        mock_client.client.mail.send.post.return_value = mock_response

        self.email_service.sendgrid_api_key = "test_key"
        result = self.email_service._send_via_sendgrid(
            "test@example.com",
            "",
            "",
            template_id="d-password-reset",
            dynamic_data={"username": "John", "reset_link": "http://example.com/reset"},
        )

        assert result is True
        # Verify the call was made
        mock_client.client.mail.send.post.assert_called_once()

    @patch("sendgrid.SendGridAPIClient")
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

        original_sendgrid = sys.modules.get("sendgrid")
        if "sendgrid" in sys.modules:
            del sys.modules["sendgrid"]

        try:
            self.email_service.sendgrid_api_key = "test_key"
            result = self.email_service._send_via_sendgrid(
                "test@example.com", "Subject", "<p>Content</p>"
            )
            assert result is False
        finally:
            if original_sendgrid:
                sys.modules["sendgrid"] = original_sendgrid

    @patch.dict("os.environ", {"FRONTEND_URL": "http://test.com"})
    @patch.object(EmailService, "_send_via_sendgrid", return_value=True)
    def test_send_password_reset_email(self, mock_sendgrid):
        """Test password reset email with dynamic template"""
        result = self.email_service.send_password_reset_email(
            "test@example.com", "reset_token_123", "John Doe"
        )

        assert result is True
        mock_sendgrid.assert_called_once_with(
            "test@example.com",
            "",
            "",
            template_id="d-password-reset",
            dynamic_data={
                "username": "John Doe",
                "reset_link": "http://test.com/reset-password?token=reset_token_123",
            },
        )

    def test_send_notification_email(self):
        """Test notification email template"""
        with patch.object(
            self.email_service, "send_email", return_value=True
        ) as mock_send:
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

    def test_validate_email_valid(self):
        """Test valid email validation"""
        assert self.email_service._validate_email("test@example.com") is True
        assert self.email_service._validate_email("user.name+tag@example.co.uk") is True

    def test_validate_email_invalid(self):
        """Test invalid email validation"""
        assert self.email_service._validate_email("invalid-email") is False
        assert self.email_service._validate_email("test@") is False
        assert self.email_service._validate_email("@example.com") is False
        assert self.email_service._validate_email("") is False
