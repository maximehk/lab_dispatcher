## Installation Steps:

1. Add your SSH keys to the `./ssh` directory.
2. Authorize these SSH keys on the Mikrotik device.
3. Download a credential file for your service account from the cloud console.
4. Reference the downloaded credential file in your `compose.yaml` file.
5. Review the `compose.yaml` file to update the environment variables
6. Start the container e.g `docker compose up -d`