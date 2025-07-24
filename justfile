[private]
list:
  just -l

# Prod 🚀
[group('docker')]
docker-up:
  cd pubsub_listener && uv lock
  docker build pubsub_listener -t pubsub_listener:latest
  docker compose up --force-recreate -d

# Show logs 🚀
[group('docker')]
docker-logs:
  docker compose logs -f 

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
  rm -rf */.venv **/*/__pycache__ */.python-version .DS_Store


# Open the GitHub repository
[macos]
[group('maintenance')]
github:
  open "https://github.com/maximehk/lab_dispatcher"


# Download secrets from 1password
max-init-secrets:
  op read "op://homelab/homelab-dispatcher-docker-ssh-key/private key" > homelab_api/ssh/id_ed25519
  op read "op://homelab/homelab-dispatcher-docker-ssh-key/public key" > homelab_api/ssh/id_ed25519.pub
  op read "op://homelab/homelab-dispatcher-dot-env/.env" > .env
  op read "op://homelab/homelab-dispatcher-google-creds.json/creds.json" > pubsub_listener/creds.json
