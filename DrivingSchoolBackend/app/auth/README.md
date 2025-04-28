```shell
# Generate an RSA private key, of size 2048
openssl genrsa -out jwt-private.pem 2048
```

```shell
# Extract the public key from the key pair, which can be used in certificate
openssl rsa -in jwt-private.pem -outform PEM -pubout -out jwt-public.pem
```

Create new directory certs in app directory, go to certs and run these commands.
You may be needed to install OpenSSL.