import aiosmtplib
from email.message import EmailMessage
from app.core.config import SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASS


async def send_otp_email(email: str, otp: str):
    """
    Send a responsive OTP verification email using aiosmtplib.
    
    Args:
        email (str): Recipient email address
        otp (str): One-time password to send
    """
    message = EmailMessage()
    message["From"] = SMTP_USER
    message["To"] = email
    message["Subject"] = "Your Ctizen Print OTP Verification Code"
    
    # Plain text version
    plain_text = f"""Hello,

Your OTP code is: {otp}

This code will expire in 10 minutes.

Thank you,
The Ctizen Print Team"""

    # HTML version with {{OTP}} replaced
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>Ctizen Print – OTP Verification</title>
  <!--[if mso]>
  <noscript>
    <xml><o:OfficeDocumentSettings><o:PixelsPerInch>96</o:PixelsPerInch></o:OfficeDocumentSettings></xml>
  </noscript>
  <![endif]-->
  <style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700&family=DM+Sans:wght@400;500;600&display=swap');

    * {{ margin: 0; padding: 0; box-sizing: border-box; }}

    body {{
      background-color: #F5F2EE;
      font-family: 'DM Sans', Arial, sans-serif;
      color: #1A1A1A;
      -webkit-font-smoothing: antialiased;
      line-height: 1.4;
    }}

    .email-wrapper {{
      max-width: 600px;
      margin: 40px auto;
      background: #FFFFFF;
      border-radius: 8px;
      overflow: hidden;
      box-shadow: 0 8px 32px rgba(0,0,0,0.12);
    }}

    /* ── Header ── */
    .header {{
      background: linear-gradient(135deg, #D73D32 0%, #C53030 100%);
      padding: 36px 32px 28px;
      position: relative;
      overflow: hidden;
    }}

    .header::before {{
      content: '';
      position: absolute;
      top: -50px; right: -50px;
      width: 200px; height: 200px;
      border-radius: 50%;
      background: rgba(255,255,255,0.08);
    }}

    .brand {{
      font-family: 'Playfair Display', Georgia, serif;
      font-size: clamp(22px, 4.5vw, 28px);
      font-weight: 700;
      color: #FFFFFF;
      letter-spacing: 0.5px;
      position: relative;
      z-index: 1;
      margin-bottom: 4px;
    }}

    .brand span {{
      color: rgba(255,255,255,0.8);
    }}

    .header-tagline {{
      font-size: clamp(10px, 2vw, 12px);
      font-weight: 500;
      color: rgba(255,255,255,0.7);
      letter-spacing: 2px;
      text-transform: uppercase;
      position: relative;
      z-index: 1;
    }}

    /* ── Body ── */
    .body {{
      padding: 40px 32px 32px;
    }}

    .greeting {{
      font-size: clamp(20px, 4vw, 24px);
      font-weight: 600;
      color: #1A1A1A;
      margin-bottom: 16px;
      line-height: 1.3;
    }}

    .greeting em {{
      font-style: normal;
      color: #D73D32;
    }}

    .intro-text {{
      font-size: 15px;
      color: #444444;
      line-height: 1.7;
      margin-bottom: 32px;
    }}

    /* ── OTP Box ── */
    .otp-container {{
      background: #FDF6F5;
      border: 2px solid #F0D0CE;
      border-radius: 12px;
      padding: 32px 24px;
      text-align: center;
      margin-bottom: 28px;
      position: relative;
    }}

    .otp-label {{
      font-size: clamp(11px, 2.5vw, 13px);
      font-weight: 600;
      letter-spacing: 2px;
      text-transform: uppercase;
      color: #D73D32;
      margin-bottom: 16px;
    }}

    .otp-code {{
      font-family: 'Playfair Display', Georgia, serif;
      font-size: clamp(36px, 10vw, 56px);
      font-weight: 700;
      color: #1A1A1A;
      letter-spacing: 8px;
      line-height: 1;
      margin-bottom: 16px;
      text-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }}

    .otp-divider {{
      width: 40px;
      height: 2px;
      background: #D73D32;
      margin: 18px auto;
      border: none;
    }}

    .otp-expiry {{
      font-size: 14px;
      color: #888888;
      font-weight: 500;
    }}

    .otp-expiry strong {{
      color: #D73D32;
    }}

    /* ── Warning ── */
    .warning-box {{
      display: flex;
      align-items: flex-start;
      gap: 12px;
      background: #FAFAFA;
      border-left: 4px solid #D73D32;
      padding: 16px 20px;
      border-radius: 0 8px 8px 0;
      margin-bottom: 28px;
    }}

    .warning-icon {{
      font-size: 18px;
      flex-shrink: 0;
      margin-top: 2px;
    }}

    .warning-text {{
      font-size: 13px;
      color: #555555;
      line-height: 1.6;
    }}

    .warning-text strong {{
      color: #1A1A1A;
    }}

    /* ── Closing ── */
    .closing-text {{
      font-size: 15px;
      color: #444444;
      line-height: 1.7;
      margin-bottom: 24px;
    }}

    .sign-off {{
      font-size: 16px;
      color: #1A1A1A;
      font-weight: 600;
      text-align: center;
      padding-top: 24px;
      border-top: 1px solid #EBEBEB;
    }}

    .sign-off span {{
      color: #D73D32;
    }}

    /* ── Footer ── */
    .footer {{
      background-color: #1A1A1A;
      padding: 28px 32px;
      text-align: center;
    }}

    .footer-brand {{
      font-family: 'Playfair Display', Georgia, serif;
      font-size: 18px;
      color: #FFFFFF;
      letter-spacing: 0.5px;
      margin-bottom: 12px;
    }}

    .footer-brand span {{
      color: #D73D32;
    }}

    .footer-text {{
      font-size: 13px;
      color: #888888;
      line-height: 1.6;
      margin-bottom: 12px;
    }}

    .footer-links {{
      font-size: 12px;
    }}

    .footer-links a {{
      color: #D73D32;
      text-decoration: none;
      margin: 0 12px;
      font-weight: 500;
    }}

    .footer-links a:hover {{
      text-decoration: underline;
    }}

    /* ── Responsive Improvements ── */
    @media only screen and (max-width: 480px) {{
      .email-wrapper {{ 
        margin: 0; 
        border-radius: 0; 
        min-height: 100vh;
      }}
      
      .header, .body, .footer {{ 
        padding-left: 20px !important; 
        padding-right: 20px !important; 
      }}
      
      .otp-container {{ 
        padding: 28px 20px !important; 
        margin: 0 -20px 24px -20px;
        border-radius: 0;
        border-left: none;
        border-right: none;
      }}
      
      .otp-code {{ 
        letter-spacing: 6px !important;
        font-size: 42px !important;
      }}
      
      .warning-box {{
        flex-direction: column;
        gap: 8px;
        text-align: center;
      }}
    }}

    @media screen and (-webkit-min-device-pixel-ratio:0) {{
      .otp-code {{ 
        letter-spacing: 0.6em !important;
      }}
    }}
  </style>
</head>
<body>
<div class="email-wrapper">
  <!-- Header -->
  <div class="header">
    <div class="brand">Ctizen<span> Print</span></div>
    <div class="header-tagline">Verification Mail</div>
  </div>

  <!-- Body -->
  <div class="body">
    <div class="greeting">Hello, <em>welcome back.</em></div>

    <p class="intro-text">
      We received a request to verify your identity on <strong>Ctizen Print</strong>.
      Use the one-time password below to complete your verification. 
      Do not share this code with anyone.
    </p>

    <!-- OTP Box -->
    <div class="otp-container">
      <div class="otp-label">Your One-Time Password</div>
      <div class="otp-code">{otp}</div>
      <hr class="otp-divider" />
      <div class="otp-expiry">This code expires in <strong>10 minutes</strong></div>
    </div>

    <!-- Security Warning -->
    <div class="warning-box">
      <div class="warning-icon">⚠️</div>
      <div class="warning-text">
        <strong>Security Notice:</strong> Ctizen Print will never ask for your OTP via 
        phone, chat, or email reply. If you did not request this code, please ignore 
        this email or contact our support team immediately.
      </div>
    </div>

    <p class="closing-text">
      If you have any trouble or questions, our support team is always here to help.
    </p>

    <div class="sign-off">
      Warm regards,<br/>
      <span>The Ctizen Print Team</span>
    </div>
  </div>

  <!-- Footer -->
  <div class="footer">
    <div class="footer-brand">Ctizen<span> Print</span></div>
    <div class="footer-text">
      © 2026 Ctizen Print. All rights reserved.<br/>
      This is an automated email — please do not reply directly.
    </div>
    <div class="footer-links">
      <a href="#">Privacy Policy</a>
      <a href="#">Terms of Service</a>
      <a href="#">Contact Support</a>
    </div>
  </div>
</div>
</body>
</html>"""

    # Set both plain text and HTML content
    message.set_content(plain_text)
    message.add_alternative(html_content, subtype="html")
    
    try:
        await aiosmtplib.send(
            message,
            hostname=SMTP_HOST,
            port=SMTP_PORT,
            username=SMTP_USER,
            password=SMTP_PASS,
            start_tls=True,
            validate_certs=True
        )
        return {"success": True, "message": "OTP email sent successfully"}
    except Exception as e:
        return {"success": False, "message": f"Failed to send email: {str(e)}"}
