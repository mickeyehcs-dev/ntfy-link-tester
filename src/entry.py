from workers import WorkerEntrypoint, Response, fetch
from urllib.parse import urlparse, parse_qs

class Default(WorkerEntrypoint):
    async def fetch(self, request):
        parsed_url = urlparse(request.url)
        params = parse_qs(parsed_url.query)
        click_source = params.get("source", ["Direct GitHub Deploy"])

        # 🚨 REPLACE THIS with your actual secret ntfy topic name!
        ntfy_url = "https://ntfy.sh/mickeyehcsserver"
        
        ntfy_headers = {
            "Title": "🔗 Link Opened!",
            "Priority": "default",
            "Tags": "rocket,globe_with_meridians",
            "Content-Type": "text/plain"
        }
        
        message_body = f"Someone opened your link via: {click_source}."

        try:
            await fetch(ntfy_url, {
                "method": "POST",
                "headers": ntfy_headers,
                "body": message_body
            })
            
            html_response = """
            <html>
                <body style="font-family:sans-serif; text-align:center; padding-top:50px;">
                    <h1 style="color:#2ecc71;">✅ Worker Triggered via GitHub!</h1>
                    <p>Cloudflare automatically deployed this from Git and sent your notification.</p>
                </body>
            </html>
            """
            return Response(html_response, headers={"Content-Type": "text/html"})

        except Exception as e:
            return Response(f"Error firing notification: {str(e)}", status=500)
