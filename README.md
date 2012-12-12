## SSH tunnel over HTTPS

This tool bypasses firewalls and proxies that block SSH traffic. It achieves that by tunnelling the SSH traffic over HTTPS.

### How to use

1. Install and execute the server script on your SSH server. The script will listen on TCP port 443 (HTTPS) and relay all traffic to the local SSH daemon.
2. Configure and execute the client script. The script will connect over HTTPS through the designated proxy to the server script. Finally, it will obfuscate and relay traffic from local port 900 to the server script.
3. Connect with your SSH client to 127.0.0.1:900.
