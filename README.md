## Installation Steps:

1. Add your SSH keys to the `./ssh` directory (or create new ones with `ssh-keygen`).
2. Authorize the public SSH key on the Mikrotik device.
3. Copy the `.env_template` to `.env` and update its values to match your environment
4. Download a credential file for your service account from the [cloud console](https://console.cloud.google.com/iam-admin/serviceaccounts).
5. Reference the downloaded credential file in your `compose.yaml` file.
6. Start the container e.g `docker build . && docker compose up -d` (alternatively, `just docker-up` if you have [just.env](https://just.systems/))

## Important notes

This is meant to be the first step of a more complex dispatcher (supporting more than just one command). Syncing to a newer version of the repo may break you.
