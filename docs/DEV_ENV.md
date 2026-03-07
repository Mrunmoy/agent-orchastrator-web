# Development Environment

## Choice
This project uses **Nix** as the primary dev environment (not Docker).

## Why Nix
1. Fast local iteration for autonomous agents without container rebuild cycles.
2. Reproducible toolchain pinned in `flake.nix`.
3. Works naturally with local CLI agents (`codex`, `claude`, `ollama`) and host file access.
4. Easier UI screenshot/testing loop during development.

## Enter Environment
```bash
cd <repo-root>
nix develop
```

## Autonomous UI Workflow
```bash
make serve      # run local static server
make test-ui    # run Playwright smoke test
make ui-shot    # capture screenshot artifact
make verify     # run core automated checks
```

Screenshots are stored in:
- `artifacts/screenshots/mockup-test.png`
- `artifacts/screenshots/mockup-latest.png`

## LAN Access

Run the backend and frontend on your local network so phones, tablets, and
laptops can reach the UI.

### Quick Start
```bash
nix develop              # enter the dev shell
make dev-up-lan          # start both services on 0.0.0.0
```

The script prints a banner with the LAN IP and URLs:
```
  Backend URL:   http://192.168.x.x:8000
  Frontend URL:  http://192.168.x.x:5173
  Health check:  curl http://192.168.x.x:8000/api/health
```

Open the **Frontend URL** on any device connected to the same Wi-Fi / LAN.

### Localhost-Only Start
```bash
make dev-up
```

### Status / Logs / Stop
```bash
make dev-status
make dev-logs
make dev-down
```

### Custom Ports
```bash
scripts/dev_stack.sh start --lan --backend-port 9000 --frontend-port 3000
```

### Firewall Notes
If other devices cannot connect, make sure your firewall allows inbound
traffic on the backend and frontend ports (default 8000 and 5173):

```bash
# UFW example
sudo ufw allow 8000/tcp
sudo ufw allow 5173/tcp

# firewalld example
sudo firewall-cmd --add-port=8000/tcp --add-port=5173/tcp
```

### Stopping
Use:
```bash
make dev-down
```
