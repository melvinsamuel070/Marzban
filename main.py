import click
import logging
import os
import ssl

import uvicorn
from cryptography import x509
from cryptography.hazmat.backends import default_backend

from app import app, logger
from config import (
    DEBUG,
    UVICORN_HOST,
    UVICORN_PORT,
    UVICORN_SSL_CERTFILE,
    UVICORN_SSL_KEYFILE,
    UVICORN_SSL_CA_TYPE,
    UVICORN_UDS
)


def validate_cert_and_key(cert_file_path, key_file_path, ca_type):
    if ca_type == "private":
        logger.warning(f"""
{click.style('IMPORTANT!', blink=True, bold=True, fg="yellow")} 
You're running Marzban with: {click.style('UVICORN_SSL_CA_TYPE', italic=True, fg="magenta")}: {click.style(f'{ca_type}', bold=True, fg="yellow")}. 
Self-signed CAs are useful in testing or internal use cases, they’re not suitable for secure public internet communications.
        """)
        return

    if not os.path.isfile(cert_file_path):
        raise ValueError(f"SSL certificate file '{cert_file_path}' does not exist.")
    if not os.path.isfile(key_file_path):
        raise ValueError(f"SSL key file '{key_file_path}' does not exist.")

    try:
        context = ssl.create_default_context()
        context.load_cert_chain(certfile=cert_file_path, keyfile=key_file_path)
    except ssl.SSLError as e:
        raise ValueError(f"SSL Error: {e}")

    try:
        with open(cert_file_path, 'rb') as cert_file:
            cert_data = cert_file.read()
            cert = x509.load_pem_x509_certificate(cert_data, default_backend())

        if cert.issuer == cert.subject:
            raise ValueError("The certificate is self-signed and not issued by a trusted CA.")

    except Exception as e:
        raise ValueError(f"Certificate verification failed: {e}")


if __name__ == "__main__":

    bind_args = {}

    if UVICORN_SSL_CA_TYPE not in ["public", "private"]:
        UVICORN_SSL_CA_TYPE = "public"

    # =========================
    # SSL MODE (UNCHANGED LOGIC)
    # =========================
    if UVICORN_SSL_CERTFILE and UVICORN_SSL_KEYFILE and UVICORN_SSL_CA_TYPE:
        validate_cert_and_key(UVICORN_SSL_CERTFILE, UVICORN_SSL_KEYFILE, UVICORN_SSL_CA_TYPE)

        bind_args["ssl_certfile"] = UVICORN_SSL_CERTFILE
        bind_args["ssl_keyfile"] = UVICORN_SSL_KEYFILE

        if UVICORN_UDS:
            bind_args["uds"] = UVICORN_UDS
        else:
            bind_args["host"] = UVICORN_HOST
            bind_args["port"] = UVICORN_PORT

    # =========================
    # NO SSL MODE (FIXED HERE)
    # =========================
    else:
        if UVICORN_UDS:
            bind_args["uds"] = UVICORN_UDS
        else:

            logger.warning(f"""
{click.style('IMPORTANT!', blink=True, bold=True, fg="yellow")}
You're running Marzban without SSL cert configuration.
Using reverse proxy (Nginx) is expected for production deployments.
            """)

            # ✅ FIX: always bind to HOST from config (NOT 127.0.0.1)
            bind_args["host"] = UVICORN_HOST or "0.0.0.0"
            bind_args["port"] = UVICORN_PORT

    # =========================
    # DEBUG OVERRIDE (SAFE)
    # =========================
    if DEBUG:
        bind_args["reload"] = True

    try:
        uvicorn.run(
            "main:app",
            **bind_args,
            workers=1,
            reload=DEBUG,
            log_level=logging.DEBUG if DEBUG else logging.INFO
        )
    except FileNotFoundError:
        pass