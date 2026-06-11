from workers import WorkerEntrypoint, Response, fetch, Request
from urllib.parse import urlparse, parse_qs

class Default(WorkerEntrypoint):
    async def fetch(self, request):
        try:
            parsed_url = urlparse(request.url)
            path = parsed_url.path

            # 1. FIX: Block the browser's automatic icon request from triggering alerts
            if path == "/favicon.ico":
                return Response("", status=204)

            ntfy_url = "https://ntfy.sh/mickeyehcsserver"
            status_message = ""

            # 2. Handle Form Submission (POST request from the web page)
            if request.method == "POST":
                # Read form data submitted by user
                form_text = await request.text()
                params = parse_qs(form_text)
                user_content = params.get("custom_message", [""])[0]

                if user_content.strip():
                    ntfy_headers = {
                        "Title": "MICKEY SERVER",
                        "Priority": "high",
                        "Tags": ""
                    }
                    
                    ntfy_request = Request(
                        ntfy_url,
                        method="POST",
                        headers=ntfy_headers,
                        body=user_content
                    )
                    
                    ntfy_res = await fetch(ntfy_request)
                    if ntfy_res.status == 200:
                        status_message = '<p style="color: #2ecc71; font-weight: bold;">🚀 Notification sent successfully!</p>'
                    else:
                        status_message = f'<p style="color: #e74c3c; font-weight: bold;">❌ Failed to send (Status: {ntfy_res.status})</p>'
                else:
                    status_message = '<p style="color: #e67e22; font-weight: bold;">⚠️ Cannot send an empty message.</p>'

            # 3. Render the interactive UI website
            html_response = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <meta name="viewport" content="width=device-width, initial-scale=1">
                <title>ntfy Messenger Portal</title>
            </head>
            <body style="font-family: sans-serif; background-color: #f3f4f6; margin: 0; padding: 40px 20px; display: flex; justify-content: center;">
                <div style="background: white; padding: 30px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); width: 100%; max-width: 450px;">
                    <h2 style="color: #1f2937; margin-top: 0;">Push Notification Panel</h2>
                    <p style="color: #6b7280; font-size: 14px;">Type a message below to broadcast it to your connected device via ntfy.</p>
                    
                    {status_message}

                    <form method="POST" style="margin-top: 20px;">
                        <label style="display: block; font-weight: 600; margin-bottom: 8px; color: #4b5563; font-size: 14px;">Your Message:</label>
                        <textarea name="custom_message" rows="4" placeholder="Enter notification text here..." style="width: 100%; box-sizing: border-box; padding: 12px; border: 1px solid #d1d5db; border-radius: 6px; font-family: inherit; font-size: 15px; resize: none; margin-bottom: 15px;"></textarea>
                        
                        <button type="submit" style="width: 100%; background-color: #3b82f6; color: white; border: none; padding: 12px; font-size: 16px; font-weight: bold; border-radius: 6px; cursor: pointer; transition: background 0.2s;">
                            Send Notification
                        </button>
                    </form>
                </div>
            </body>
            </html>
            """
            return Response(html_response, headers={"Content-Type": "text/html"})

        except Exception as e:
            error_html = f"<h3>System Execution Error</h3><pre>{str(e)}</pre>"
            return Response(error_html, headers={"Content-Type": "text/html"}, status=500)
