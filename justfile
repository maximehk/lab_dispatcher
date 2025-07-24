[private]
list:
  just -l

# Prod 🚀
[group('docker')]
docker-up:
  docker build .
  docker compose up --force-recreate -d

# Show logs 🚀
[group('docker')]
docker-logs:
  docker logs -f lab_dispatcher

# Shell into the container 🚀
[group('docker')]
docker-shell:
  docker exec -it lab_dispatcher /bin/sh

# DEV mode
[group('docker')]
docker-watch:
  docker compose watch

# Delete temporary files
[group('maintenance')]
clean:
  rm -rf .venv __pycache__ .python-version .DS_Store


# Open the GitHub repository
[macos]
[group('maintenance')]
github:
  open "https://github.com/maximehk/lab_dispatcher"


# Download secrets from 1password
max-init-secrets:
  op read "op://homelab/homelab-dispatcher-docker-ssh-key/private key" > ssh/id_ed25519
  op read "op://homelab/homelab-dispatcher-docker-ssh-key/public key" > ssh/id_ed25519.pub
  op read "op://homelab/homelab-dispatcher-dot-env/.env" > .env
  op read "op://homelab/homelab-dispatcher-google-creds.json/creds.json" > creds.json
