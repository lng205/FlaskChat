1. **Generate the CA Key:**
   ```bash
   openssl genrsa -out myCA.key 2048
   ```

2. **Create and self-sign the CA Certificate:**
   ```bash
   openssl req -x509 -new -nodes -key myCA.key -sha256 -days 825 -out myCA.pem
   ```

   You'll be prompted to enter details for the certificate, such as country, state, and organization.

### Step 3: Create a Certificate Signed by Your CA for a Domain

1. **Create a private key for your server:**
   ```bash
   openssl genrsa -out mydomain.key 2048
   ```

2. **Create a certificate signing request (CSR):**
   ```bash
   openssl req -new -key mydomain.key -out mydomain.csr
   ```

3. **Create a configuration file for the domain to include proper extensions:**
   Save this as `mydomain.ext`:
   ```
   authorityKeyIdentifier=keyid,issuer
basicConstraints=CA:FALSE
keyUsage = digitalSignature, nonRepudiation, keyEncipherment, dataEncipherment
subjectAltName = @alt_names

[alt_names]
IP.1 = 127.0.0.1
   ```

   Replace `example.com` with your domain name.

4. **Generate the SSL certificate using the CA:**
   ```bash
   openssl x509 -req -in mydomain.csr -CA myCA.pem -CAkey myCA.key -CAcreateserial -out mydomain.crt -days 500 -sha256 -extfile mydomain.ext
   ```

### Step 4: Trusting the CA on Your Mac

1. **Add the CA to your system's trust store:**
  