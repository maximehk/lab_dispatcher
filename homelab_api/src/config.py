import os

class Config:
    def check_config(self):
        _ = self.host
        _ = self.allowed_emails
        _ = self.ip_ttl
        _ = self.mikrotik_https_allowlist

    @property
    def host(self):
        value = os.environ.get("MIKROTIK_HOST")
        if not value:
            raise ValueError("MIKROTIK_HOST environment variable is not set.")
        return value

    @property
    def allowed_emails(self):
        emails = [email.strip() for email in os.environ.get("ALLOWED_EMAILS", "").split(",")]
        if not emails or emails == [""]:
            raise ValueError("ALLOWED_EMAILS environment variable is not set.")
        return emails

    @property
    def ip_ttl(self):
        value = os.environ.get("IP_TTL")
        if not value:
            raise ValueError("IP_TTL environment variable is not set.")
        return value

    @property
    def mikrotik_https_allowlist(self):
        value = os.environ.get("MIKROTIK_HTTPS_ALLOWLIST")
        if not value:
            raise ValueError("MIKROTIK_HTTPS_ALLOWLIST environment variable is not set.")
        return value
