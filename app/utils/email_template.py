def registration_message(code: str, year: int) -> str:
    message = f"""
        <!DOCTYPE html>
        <html>
        <head>
        <meta charset="UTF-8">
        <title>Verify Your Email - GroupifyAssist</title>
        </head>
        <body style="font-family: Arial, sans-serif; background-color: #f4f4f4; padding: 20px;">
        <table width="100%" cellpadding="0" cellspacing="0">
            <tr>
            <td>
                <table width="600" align="center" cellpadding="20" cellspacing="0" style="background-color: #ffffff; border-radius: 8px;">
                <tr>
                    <td align="center" style="background-color: #4caf50; color: white; padding: 10px 0; border-top-left-radius: 8px; border-top-right-radius: 8px;">
                    <h2>GroupifyAssist</h2>
                    </td>
                </tr>
                <tr>
                    <td>
                    <h3>Hello,</h3>
                    <p>Thank you for signing up with <strong>GroupifyAssist</strong>! To complete your registration, please enter the verification code below:</p>
                    <p style="font-size: 24px; font-weight: bold; color: #4caf50; text-align: center;">{ code }</p>
                    <p>This code will expire in 10 minutes. If you did not request this, please ignore this message.</p>
                    <p>Thank you,<br><strong>The GroupifyAssist Team</strong></p>
                    </td>
                </tr>
                <tr>
                    <td align="center" style="font-size: 12px; color: #888888; padding-top: 20px;">
                    © { year } GroupifyAssist. All rights reserved.
                    </td>
                </tr>
                </table>
            </td>
            </tr>
        </table>
        </body>
        </html>
        """
    return message


def registration_success(year: int, email: str) -> str:
    message = f"""
        <!DOCTYPE html>
    <html>
    <head>
    <meta charset="UTF-8">
    <title>Registration Successful - GroupifyAssist</title>
    </head>
    <body style="font-family: Arial, sans-serif; background-color: #f8f8f8; padding: 20px;">
    <table width="100%" cellpadding="0" cellspacing="0">
        <tr>
        <td>
            <table width="600" align="center" cellpadding="20" cellspacing="0" style="background-color: #ffffff; border-radius: 8px;">
            <tr>
                <td align="center" style="background-color: #4caf50; color: white; padding: 10px 0; border-top-left-radius: 8px; border-top-right-radius: 8px;">
                <h2>GroupifyAssist</h2>
                </td>
            </tr>
            <tr>
                <td>
                <h3>Welcome to GroupifyAssist!</h3>
                <p>Hi <strong>{ email }</strong>,</p>
                <p>Your registration was successful. You can now log in and start creating or managing groups with smart, bias-free logic and customizable preferences.</p>
                <p>If you have any questions or need support, feel free to contact our team.</p>
                <p>Thank you for joining us,<br><strong>The GroupifyAssist Team</strong></p>
                </td>
            </tr>
            <tr>
                <td align="center" style="font-size: 12px; color: #888888; padding-top: 20px;">
                © {{ year }} GroupifyAssist. All rights reserved.
                </td>
            </tr>
            </table>
        </td>
        </tr>
    </table>
    </body>
    </html>

    """
    return message