# Dev Log

![task](task.jpg)

Certain libraries required by the project lack support in Python 3.12. The project was developed using Python 3.11.8.

## Design Overview

Our project's development consistently aims to minimize alterations to the existing framework.

### Friends

The key design of the friends feature is the utilization of SQLAlchemy's ORM framework. We crafted tables for friendships and pending friend requests, employing a many-to-many self-referential relationship schema. This approach streamlines querying and managing friendships. However, given the intricacies of SQLAlchemy 2's syntax, we opted for a unidirectional design for the friendship table.

**Implemetation Details**:

1. Design of relational database tables for users, friendships, and pending friend requests.
2. Integration of a user interface to showcase friends and pending friend requests, leveraging Flask's Jinja2 templating engine.
3. Creation of an input field and JavaScript functionality to initiate friend requests.
4. Implementation of buttons and JavaScript for accepting or declining friend requests.
5. Development of backend routes and database operations to process friend requests.
6. Incorporation of validation checks during the process of adding friends to the database.
7. Addition of JavaScript enabling users to initiate chats by clicking on a friend's name.

### Chat

The chat feature is designed to be **end-to-end encrypted and verified**, mandating that all encryption and decryption occur on the **client-side**. We employed the Web Crypto API for this purpose.

Symmetric encryption is adept at encrypting and decrypting vast data volumes but is susceptible to **man-in-the-middle attacks** during key exchange. Although asymmetric encryption also necessitates a secure public key exchange, it can leverage a **Certificate Authority (CA)** to authenticate the public key.

In this project, we assume the server's reliability in transmitting public keys. For enhanced security, employing a CA to authenticate the public key or using **a pre-established secure channel** (e.g., in-person) for key exchange could be considered, though these are beyond our project's scope.

We opted against hybrid encryption, finding asymmetric encryption sufficiently efficient for real-time text chat on contemporary computers, with no noticeable delay in our encryption and decryption tests.

The encryption algorithm used is RSA-OAEP, and the signing algorithm is RSA-PSS.

**Implemetation Details**:

1. Generation of RSA key pairs upon registration.
2. Storage and retrieval of public keys in the database.
3. Storage of public and private keys in the browser's local storage.
4. Encryption and decryption of messages.
5. Signing and verification of messages.
6. Display of messages in the chat window.

### History

The history feature is crafted to archive chat conversations in a database, ensuring the server cannot decipher the messages. Although utilizing users' passwords as the encryption key is a logical approach, we opt for the user's public key for encryption. This choice stems from several key factors:

1. The user's original password is transmitted to the server during registration and login.
2. The incoming messages are already secured with the user's public key, making the encryption of outgoing messages with the user's public key a coherent strategy.

**Implementation Details**:

1. Creation of a relational database table for chat conversations.
2. Archiving and fetching chat conversations from the database.
3. Encrypting outgoing messages using the user's public key.
4. Refreshing the history upon sending and receiving messages.
5. Displaying the chat history upon entering a chat session.

### Password

The password is hashed with salt using the bcrypt library. The salt is stored alongside the hashed password.

### HTTPS

To reduce browser warnings when using a self-signed certificate for `localhost` (127.0.0.1), we need to ensure that the certificate includes the correct Common Name (CN) or Subject Alternative Name (SAN) for `localhost` and possibly include other relevant fields. Modern browsers and clients rely heavily on the SAN field, as the CN field is deprecated for this purpose in many contexts.

Following are the steps to generate a self-signed certificate for `localhost` using OpenSSL:

#### Step 1: Create a Configuration File for OpenSSL

Create a new file named `localhost.cnf`.

This configuration includes both a DNS entry and an IP entry for `localhost` and `127.0.0.1`, respectively.

#### Step 2: Generate the Self-Signed Certificate with SAN

Using the configuration file created in Step 1, generate a new self-signed certificate and private key by running:

```bash
openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout localhost.key -out localhost.crt -config localhost.cnf -extensions 'v3_req'
```

#### Step 3: Configure Flask to Use the Certificate and Key

Change the flask app's `app.run()` method to include the `ssl_context` parameter:

```python
if __name__ == '__main__':
    app.run(ssl_context=('localhost.crt', 'localhost.key'))
```

Use `python app.py` to run the Flask app.

#### Step 4: Add the Certificate to trusted certificates

This can be done via the settings of the browser or the operating system. The certificate should be added to the trusted root certificate authorities.
