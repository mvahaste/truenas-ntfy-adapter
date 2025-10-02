#!/usr/bin/env python3
import os
import sys
from aiohttp import web
from aiohttp import ClientSession


# The url the alerts should be forwarded to.
# Format: http[s]://{host}:{port}/
NTFY_BASEURL = os.environ.get("NTFY_URL")
# The access token for the Ntfy application
# Example: tk_AgQdq7mVBoFD37zQVN29RhuMzNIz2
NTFY_TOKEN = os.environ.get("NTFY_TOKEN")

# The IP address the service should listen on
# Defaults to localhost for security reasons
LISTEN_HOST = os.environ.get("LISTEN_HOST", "127.0.0.1")
# The port the service should listen on
# Defaults to 31662
LISTEN_PORT = int(os.environ.get("LISTEN_PORT", "31662"))

# Control whether the validity of the SSL certificate
# of the Ntfy server should be checked.
# Useful for allowing self signed certificates
#
# SECURITY: Consider disabling verification of the
# certificate is highly insecure as it allows for MITM attacks to
# intercept messages and even the secret Ntfy Token
VERIFY_CERT = not os.environ.get("VERIFY_CERT", "true").lower() in ("false", "no", "n")


routes = web.RouteTableDef()


# Listen to POST requests on /message/{topic}
@routes.post("/message/{topic}")
async def on_message(request):
    content = await request.json()

    # Extract topic from URL path
    topic = request.match_info.get("topic")

    # The content of the alert message
    message = content["text"].strip().partition("\n")

    # Extract notification title from the message
    title = message[0].strip()
    message = message[2].strip()

    # Log the received message to the console
    log_title = title if title else "(no title)"
    log_header = f"{log_title} (topic: {topic})"

    print(f"========== {log_header} ==========")
    print(message)
    print("=" * (len(log_header) + 22))

    # Forward the alert to Ntfy
    ntfy_response = await send_ntfy_message(message, NTFY_TOKEN, topic, title=title)

    # Check for HTTP response status code 'success'
    if ntfy_response.status == 200:
        print(">> Forwarded successfully\n")
    elif ntfy_response.status in [400, 401, 403]:
        print(f">> Unauthorized! Token NTFY_TOKEN='{NTFY_TOKEN}' is incorrect\n")
    else:
        print(
            f">> Unknown error while forwarding to Ntfy. Error Code {ntfy_response.status}\n"
        )

    # Return the status code to TrueNAS
    return web.Response(status=ntfy_response.status)


# Send an arbitrary alert to Ntfy
async def send_ntfy_message(message, token, topic, title=None, priority=None):
    headers = {}

    # Optional Ntfy features
    if token:
        headers["Authorization"] = token
    if title:
        headers["Title"] = title
    if priority:
        headers["Priority"] = priority

    # Construct the full ntfy URL with topic
    ntfy_url = f"{NTFY_BASEURL.rstrip('/')}/{topic}"

    async with ClientSession() as session:
        async with session.post(
            ntfy_url, headers=headers, data=message, ssl=VERIFY_CERT
        ) as resp:
            return resp


if __name__ == "__main__":
    # Check if env variables are set
    if NTFY_BASEURL is None:
        sys.exit("Set Ntfy Endpoint via 'NTFY_URL=http[s]://{host}:{port}/'!")

    if NTFY_TOKEN is None:
        print("WARNING: No Ntfy Token set, running without authentication")

    if not VERIFY_CERT:
        print("WARNING: Running without certificate validation of the Ntfy endpoint")

    print("TrueNAS Ntfy Forwarder started")
    print(f"Listening on http://{LISTEN_HOST}:{LISTEN_PORT}/message/{{topic}}")
    print(f"Forwarding to {NTFY_BASEURL.rstrip('/')}/{{topic}}")

    # Listen
    app = web.Application()
    app.add_routes(routes)
    web.run_app(app, host=LISTEN_HOST, port=LISTEN_PORT)
