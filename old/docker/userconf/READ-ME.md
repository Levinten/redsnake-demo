# RedSnake Server — Installation & Setup

## Prerequisites

- A Linux server (Ubuntu/Debian recommended)
- Internet access for pulling Docker images and cloning repositories

---

## 1. Install Docker & Docker Compose

### Ubuntu / Debian

```bash
# Remove old versions (if any)
sudo apt-get remove -y docker docker-engine docker.io containerd runc 2>/dev/null

# Install required packages
sudo apt-get update
sudo apt-get install -y ca-certificates curl gnupg

# Add Docker's official GPG key
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | \
  sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg

# Add the Docker repository
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] \
  https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Install Docker Engine and Compose plugin
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io \
  docker-buildx-plugin docker-compose-plugin

# Let your user run docker without sudo (re-login required)
sudo usermod -aG docker $USER
```

Log out and back in, then verify:

```bash
docker --version
docker compose version
```

---

## 2. Configure the Environment

Edit the `.env` file in this directory (`userconf/.env`).
At a minimum you **must** change every value marked `change-me`:

| Variable | What to set |
|---|---|
| `SECRET_KEY` | A long random string (e.g. `openssl rand -hex 32`) |
| `POSTGRES_PASSWORD` | Strong database password |
| `DATABASE_URL` | Update the password part to match `POSTGRES_PASSWORD` |
| `REDIS_PASSWORD` | Strong Redis password |
| `REDIS_URL` | Update the password part to match `REDIS_PASSWORD` |
| `CELERY_BROKER_URL` | Update the password part to match `REDIS_PASSWORD` |
| `CELERY_RESULT_BACKEND` | Update the password part to match `REDIS_PASSWORD` |

### Quick password generation

```bash
# Generate random passwords
openssl rand -hex 32          # SECRET_KEY
openssl rand -base64 24       # POSTGRES_PASSWORD / REDIS_PASSWORD
```

---

## 3. Set Up the Scripts Repository (SSH Key)

RedSnake pulls automation scripts from a Git repository at container startup.

### 3.1 Generate an SSH deploy key

```bash
ssh-keygen -t ed25519 -C "redsnake-deploy" -f userconf/ssh/id_rsa -N ""
```

This creates two files:

- `userconf/ssh/id_rsa` — **private key** (stays on the server, never share)
- `userconf/ssh/id_rsa.pub` — **public key** (upload to your Git host)

### 3.2 Upload the public key to GitHub / GitLab

**GitHub:**
1. Go to your scripts repository → **Settings** → **Deploy keys**
2. Click **Add deploy key**
3. Paste the contents of `userconf/ssh/id_rsa.pub`
4. Leave "Allow write access" **unchecked** (read-only is sufficient)

**GitLab:**
1. Go to your scripts repository → **Settings** → **Repository** → **Deploy keys**
2. Add the public key contents

### 3.3 Set the repository URL in `.env`

```dotenv
GIT_REPO_URL=git@github.com:your-org/your-scripts-repo.git
GIT_BRANCH=main
```

> **Note:** Use the **SSH** URL (`git@...`), not HTTPS, since authentication
> uses the deploy key.

---

## 4. SSL / TLS Certificates (Production)

For development the default configuration uses plain HTTP — no certificates needed.
For production you should enable HTTPS:

### 4.1 Generate self-signed certificates (testing only)

```bash
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout userconf/certs/privkey.pem \
  -out userconf/certs/fullchain.pem \
  -subj "/CN=localhost"
```

For real deployments, use certificates from **Let's Encrypt** or your organisation's CA.
Place them in `userconf/certs/`:

- `fullchain.pem` — certificate chain
- `privkey.pem` — private key

### 4.2 Switch the `.env` to HTTPS mode

```dotenv
NGINX_CONF=nginx.conf
LISTEN_PORT=443
OUTSIDE_PORT=443
OUTSIDE_FQDN=your-server.example.com
```

---

## 5. Build & Start

All commands are run from the `docker/` directory.

```bash
cd docker

# Build images and start all services in the background
docker compose --env-file ./userconf/.env up -d --build
```

### Useful commands

```bash
# View logs (follow)
docker compose --env-file ./userconf/.env logs -f

# View logs for a single service
docker compose --env-file ./userconf/.env logs -f web

# Stop all services
docker compose --env-file ./userconf/.env down

# Stop and remove volumes (⚠ deletes database data)
docker compose --env-file ./userconf/.env down -v

# Rebuild after code changes
docker compose --env-file ./userconf/.env up -d --build
```

---

## 6. Verify

After starting, check that all containers are healthy:

```bash
docker compose --env-file ./userconf/.env ps
```

Then open your browser:

| Mode | URL |
|---|---|
| HTTP (dev) | `http://localhost:8080` |
| HTTPS | `https://your-server.example.com` |

You should see a JSON response from the RedSnake API.

---

## Directory Layout

```
docker/
├── docker-compose.yml      # Service definitions
├── Dockerfile              # Flask app image
├── entrypoint.sh           # Git clone + startup script
├── app/
│   ├── app.py              # Flask application
│   └── requirements.txt    # Python dependencies
├── nginx/
│   ├── nginx.conf          # HTTPS config (production)
│   └── nginx-http.conf     # HTTP config (development)
└── userconf/               # ← YOUR configuration
    ├── .env                # Environment variables (edit this!)
    ├── READ-ME.md          # This file
    ├── certs/              # SSL certificates (HTTPS only)
    │   ├── fullchain.pem
    │   └── privkey.pem
    └── ssh/                # SSH deploy key for Git
        └── id_rsa          # Private key
```