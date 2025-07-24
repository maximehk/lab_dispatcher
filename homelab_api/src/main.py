import logging
import subprocess
from fastapi import FastAPI
import uvicorn
from config import Config
import ipaddress
from fastapi import Request
from fastapi.responses import JSONResponse
app = FastAPI()

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

config = Config()
config.check_config()  # Validate the configuration settings at startup

@app.post("/allow_ip_for_https")
async def allow_ip_for_https(request: Request):
    """Allow a specific IP address to access the API."""

    data = await request.json()
    email = data.get("user", {}).get("email", "")
    ip = data.get("source_ip", "")

    if not email or email not in config.allowed_emails:
        logger.error(f"User with email {email} is not allowed to add IPs.")
        return {"error": "User not allowed"}, 403
    
    if not ip:
        logger.error("No IP address provided.")
        return {"error": "IP address is required"}, 400
    
    try:
        ipaddress.IPv4Address(ip)
    except ipaddress.AddressValueError:
        logger.error(f"Invalid IPv4 address provided: {ip}")
        return {"error": "Invalid IPv4 address"}, 400

    cmd = (
        f'ssh {config.host} "/ip/firewall/address-list/add list={config.mikrotik_https_allowlist} timeout={config.ip_ttl} address={ip} dynamic=yes comment={email}" > /dev/null || '
        f'ssh {config.host} "/ip/firewall/address-list/set [find list={config.mikrotik_https_allowlist} and address={ip}] timeout={config.ip_ttl}  comment={email}"'
    )
    try:
        subprocess.run(cmd, shell=True, check=True)
        logger.info(f"Added {ip} to Mikrotik whitelist.")
    except subprocess.CalledProcessError as e:
        logger.info(f"Failed to add {ip}: {e}")
    return {"message": f"IP {ip} added to whitelist."}, 200


@app.get("/")
def read_root():
    return {"message": "Hello from homelab-api!"}

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
