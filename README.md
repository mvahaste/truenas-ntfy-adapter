# TrueNAS Ntfy Adapter

TrueNAS does not natively provide a way to send alerts and notifications to a Ntfy server. This repo 'abuses' the TrueNAS Slack alert integration and provides a fake slack webhook endpoint to forward alerts to a Ntfy server.
Note that Slack is not required at all for this integration to work.

Forked from [truenas-gotify-adapter](https://github.com/ZTube/truenas-gotify-adapter) by [ZTube](https://github.com/ZTube).

## Installation & Usage

1. Apps -> Discover Apps -> Custom App -> Install via YAML

```yaml
services:
  truenas-ntfy-adapter:
    container_name: truenas-ntfy-adapter
    image: ghcr.io/mvahaste/truenas-ntfy-adapter:main
    restart: unless-stopped
    environment:
      - NTFY_URL=<your-ntfy-url> # e.g. https://ntfy.example.com/
    network_mode: host
```

2. System -> Alert Settings -> Add
    - _Type_: Slack
    - _Webhook URL_: http://localhost:31662
    - Click _Send Test Alert_ to test the connection
    - Save

## Environment Variables

| Variable    | Description                                                                             | Default   |          |
|-------------|-----------------------------------------------------------------------------------------|-----------|----------|
| NTFY_URL    | The URL of your Ntfy server (e.g. https://ntfy.example.com/)                            | *None*    | Required |
| NTFY_TOKEN  | The token to authenticate with your Ntfy server (e.g. tk_AgQdq7mVBoFD37zQVN29RhuMzNIz2) | *None*    | Optional |
| LISTEN_HOST | The host/IP to bind the adapter to                                                      | 127.0.0.1 | Optional |
| LISTEN_PORT | The port to bind the adapter to                                                         | 31662     | Optional |
| VERIFY_CERT | Verify the SSL certificate of the Ntfy server                                           | true      | Optional |
