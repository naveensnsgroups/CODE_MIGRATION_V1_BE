import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.core.config import settings

class EmailService:
    @staticmethod
    def send_access_request_email(owner_email: str, repo_url: str, request_user: str) -> bool:
        """
        Surgically sends an access request email to the repository owner.
        """
        if not settings.EMAIL_HOST_USER or not settings.EMAIL_HOST_PASSWORD:
            print("[Email Service] ERROR: SMTP credentials not configured.")
            return False
            
    @staticmethod
    def send_access_request_email(owner_email: str, repo_url: str, request_user: str) -> bool:
        """
        Surgically sends a minimalist, professional HTML access request email.
        """
        if not settings.EMAIL_HOST_USER or not settings.EMAIL_HOST_PASSWORD:
            print("[Email Service] ERROR: SMTP credentials not configured.")
            return False
            
        repo_name = repo_url.rstrip('/').split('/')[-1]
        github_collab_url = f"{repo_url.rstrip('/')}/settings/access"
        
        # 🧪 Intelligence Branding Update
        display_user = "Code Migration Team"
        display_platform = "Code Migration-1.0"
        
        try:
            # 📬 Construct Professional HTML Intelligence Email
            subject = f"Access Request: {repo_name} | Code Migration Hub"
            
            # --- Minimalist Industrial HTML Template ---
            html_body = f"""
            <!DOCTYPE html>
            <html>
            <body style="margin: 0; padding: 0; background-color: #ffffff; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;">
                <table width="100%" border="0" cellspacing="0" cellpadding="40" style="background-color: #ffffff;">
                    <tr>
                        <td align="center">
                            <table width="600" border="0" cellspacing="0" cellpadding="0" style="background-color: #ffffff; border: 1px solid #e4e4e7;">
                                <!-- Header -->
                                <tr>
                                    <td style="background-color: #09090b; padding: 20px 30px;">
                                        <h1 style="color: #ffffff; margin: 0; font-size: 11px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.2em;">Code Migration Intelligence</h1>
                                    </td>
                                </tr>
                                
                                <!-- Body -->
                                <tr>
                                    <td style="padding: 45px 50px;">
                                        <h2 style="color: #09090b; font-size: 20px; font-weight: 700; margin: 0 0 15px 0; letter-spacing: -0.02em;">Repository Access Request</h2>
                                        
                                        <p style="color: #71717a; font-size: 13px; line-height: 1.6; margin-bottom: 35px;">
                                            A security-cleared developer is requesting read-only access to a private repository for automated code analysis and migration intelligence.
                                        </p>
                                        
                                        <!-- Minimal Metadata Table -->
                                        <table width="100%" border="0" cellspacing="0" cellpadding="0" style="margin-bottom: 40px; border-top: 1px solid #f4f4f5;">
                                            <tr>
                                                <td width="120" style="padding: 15px 0; color: #a1a1aa; font-size: 10px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; border-bottom: 1px solid #f4f4f5;">Requester</td>
                                                <td style="padding: 15px 0; color: #09090b; font-size: 13px; font-weight: 500; border-bottom: 1px solid #f4f4f5;">{display_user}</td>
                                            </tr>
                                            <tr>
                                                <td style="padding: 15px 0; color: #a1a1aa; font-size: 10px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; border-bottom: 1px solid #f4f4f5;">Platform</td>
                                                <td style="padding: 15px 0; color: #09090b; font-size: 13px; font-weight: 500; border-bottom: 1px solid #f4f4f5;">{display_platform}</td>
                                            </tr>
                                            <tr>
                                                <td style="padding: 15px 0; color: #a1a1aa; font-size: 10px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; border-bottom: 1px solid #f4f4f5;">Repository</td>
                                                <td style="padding: 15px 0; color: #09090b; font-size: 13px; font-weight: 600; font-family: monospace;">{repo_name}</td>
                                            </tr>
                                        </table>
                                        
                                        <!-- Action Button -->
                                        <div style="text-align: left;">
                                            <a href="{github_collab_url}" style="display: inline-block; background-color: #fbbf24; color: #09090b; padding: 14px 28px; text-decoration: none; font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.1em; border-radius: 2px;">
                                                Manage Collaborators
                                            </a>
                                        </div>
                                    </td>
                                </tr>
                                
                                <!-- Footer -->
                                <tr>
                                    <td style="padding: 25px 50px; background-color: #fafafa; border-top: 1px solid #f4f4f5;">
                                        <p style="color: #a1a1aa; font-size: 9px; font-weight: 500; margin: 0; line-height: 1.5;">
                                            This request was generated by the Code Migration Intelligence Workbench.<br>
                                            <span style="color: #d4d4d8;">Ref ID: {repo_name.hex()[:8] if hasattr(repo_name, 'hex') else 'CM-AUTO-01'}</span>
                                        </p>
                                    </td>
                                </tr>
                            </table>
                        </td>
                    </tr>
                </table>
            </body>
            </html>
            """
            
            # Plain text fallback
            text_body = f"Requester: {display_user}\nPlatform: {display_platform}\nRepository: {repo_url}\nApprove here: {github_collab_url}"
            
            msg = MIMEMultipart("alternative")
            msg['From'] = settings.EMAIL_HOST_USER
            msg['To'] = owner_email
            msg['Subject'] = subject
            
            msg.attach(MIMEText(text_body, 'plain'))
            msg.attach(MIMEText(html_body, 'html'))

            # 🚀 Secure SMTP Transmission
            with smtplib.SMTP(settings.EMAIL_HOST, settings.EMAIL_PORT) as server:
                server.starttls()
                server.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
                server.send_message(msg)
                
            print(f"[Email Service] Elite Access request sent to {owner_email} for {repo_name}")
            return True
            
        except Exception as e:
            print(f"[Email Service] FAILED to send email: {str(e)}")
            return False

email_service = EmailService()
