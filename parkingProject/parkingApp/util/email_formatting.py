def email_format (status, user_name, userid, **kwargs): 
    result_format = {
        "subject": "",
        "message": "",
        "html_message": "",
    }

    if status == 'taken': 
        result_format['subject'] = "🚨 Someone took your parking spot!"
        result_format['message'] = "Another vehicle has been detected in your reserved spot."
        result_format['html_message'] = f"""
            <html>
                <body>
                    <h2 style="color:red;">Alert: Unauthorized Vehicle Detected</h2>
                    <p>Dear {user_name},</p>
                    <p>It seems someone else has parked in your reserved spot. Was that you?</p>
                    <a href="http://your-app.com/verify-parking?user={userid}" 
                        style="display:inline-block; padding:10px 15px; background-color:#ff4444; color:white; 
                                text-decoration:none; border-radius:5px; margin-top:10px;">
                        Yes, it was me
                    </a>
                    <p style="font-size:13px; color:gray;">If not, we'll take care of it 🚓</p>
                </body>
            </html>
        """
    elif status == "undefined":
            result_format['subject'] = "❓ We couldn't recognize your vehicle"
            result_format['message'] = "We couldn’t verify if the vehicle belongs to you."
            result_format['html_message'] = f"""
                <html>
                    <body>
                        <h2 style="color:#0253ff;">Vehicle not recognized</h2>
                        <p>Dear {user_name},</p>
                        <p>We couldn’t clearly recognize your license plate. Please confirm your identity:</p>
                        <a href="http://your-app.com/verify-identity?user={userid}" 
                           style="display:inline-block; padding:10px 15px; background-color:#0253ff; color:white; 
                                  text-decoration:none; border-radius:5px;">
                            Confirm Now
                        </a>
                    </body>
                </html>
            """

    elif status == "late":
        result_format['subject'] = "⌛ Your reservation has expired"
        result_format['message'] = "Your reserved parking spot is now available to others."
        result_format['html_message'] = f"""
            <html>
                <body>
                    <h2 style="color:#0253ff;">Time’s up, {user_name}</h2>
                    <p>Your reserved parking spot was released because you didn’t arrive on time.</p>
                    <p>You can <a href="http://your-app.com/reserve-again?user={userid}">reserve again</a> if needed.</p>
                    <p style="font-size:13px; color:gray;">Thanks for using Smart Parking!</p>
                </body>
            </html>
        """

    elif status == "arrived":
            result_format['subject'] = f"🚗 Welcome to your parking spot!"
            result_format['message'] = f"Hello {user_name}, we recognize you at the parking lot!"
            result_format['html_message'] = f"""
                <html>
                    <body>
                        <h2 style="color:#0253ff;">Welcome, {user_name}!</h2>
                        <p>We’ve detected your vehicle in your reserved parking spot. Enjoy your stay 🚙</p>
                        <p style="font-size:13px; color:gray;">No further action is needed.</p>
                    </body>
                </html>
            """
    elif status == "forgot":
        result_format['subject'] = f"🅿️ Did you forget to check out?"
        result_format['message'] = f"Hi {user_name}, it looks like your parking spot is now empty, but your session is still active. Please check the app to end it. Thanks!"
        result_format['html_message'] = f"""
            <html>
                <body>
                    <p>Hi {user_name},</p>
                    <p>We noticed your parking spot is empty, but your session is still active.</p>
                    <p>Please open the app to end it. Thanks!</p>
                </body>
            </html>
        """

    elif status == "admin_unknown":
        result_format['subject'] = f"🚨 Unknown Driver is parking in your parking lot"
        result_format['message'] = f"Hi {user_name}, it looks like your parking spot is occupied, but you're not getting paid! Check it out."
        result_format['html_message'] = f"""
            <html>
                <body>
                    <p>Hi {user_name},</p>
                    <p>It looks like your parking spot no. {kwargs['pid']} is occupied, but you're not getting paid!</p>
                    <p>Phone number: {kwargs['phone_number']}</p>
                    <p>License number: {kwargs['license_number']}</p>
                    <p>Check it out. Thanks!</p>
                </body>
            </html>
        """
    
    elif status == "unknown_car":
        result_format['subject'] = "🚨 Unknown Car in Your Parking Spot"
        result_format['message'] = f"Hi {user_name}, someone is using your parking spot but we couldn’t identify the vehicle. Please check the spot."
        result_format['html_message'] = f"""
            <html>
                <body>
                    <h2 style="color:red;">Unknown Vehicle Detected</h2>
                    <p>Hi {user_name},</p>
                    <p>We've detected that your parking spot no. {kwargs['pid']} is currently occupied by an unknown vehicle.</p>
                    <p>Please go check the spot and take any necessary action.</p>
                    <p style="font-size:13px; color:gray;">– Smart Parking Team</p>
                </body>
            </html>
        """


    return result_format