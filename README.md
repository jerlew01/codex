# Mobile IP Browser Proxy

This script starts an HTTP proxy on the local machine and injects carrier
specific headers to preserve a mobile IP identity.  When used with Proxifier
configure the proxy as follows:

1. **Proxy Server**
   - Address: `127.0.0.1`
   - Port: `8080` (or the value of the `PROXY_PORT` environment variable)
   - Protocol: **HTTP**

2. **Proxy Rules** (in priority order)
   1. `Localhost` – destination addresses `127.0.0.1`/`::1` – **Direct**
   2. `Local Network` – destination addresses in `10.0.0.0/8`,
      `172.16.0.0/12`, or `192.168.0.0/16` – **Direct**
   3. `IP Verification Sites` – domains `ipinfo.io`, `api.ipify.org`,
      `ifconfig.me`, `icanhazip.com`, `checkip.amazonaws.com` – **Proxy**
   4. `Streaming Sites` – domains `twitch.tv`, `youtube.com` – **Proxy**
   5. `Default` – all other traffic – **Direct**

Set the rules in this order so verification and streaming traffic
is routed through the proxy while all other traffic goes directly.
The proxy listens on `127.0.0.1:8080` by default but you can override the port
with the `PROXY_PORT` environment variable.  Set `PROXY_DYNAMIC=true` if you
need the script to allocate multiple proxy ports.  The script also sends its own
IP verification requests through this proxy so Proxifier's `Localhost` rule must
allow direct connections to `127.0.0.1`.
