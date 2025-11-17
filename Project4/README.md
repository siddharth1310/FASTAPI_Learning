# Basic sqlite3 Command

* .schema - To list down present tables
* select * from <table_name>;
* insert into <table_name> (column_name1, column_name2, .....) values (value1, value2, .....);
* .mode table
* delete from <table_name> where <column_name> = `<value>`;
* update <table_name> set <column_name1> = value1, <column_name2> = `<value>` where <column_name> = `<value>`;

# JWT Authentication

JWT authentication in FastAPI is about issuing a signed token after login and then verifying that token on every protected request instead of using sessions or cookies.

## What is a JWT?

* A JWT (JSON Web Token) is a compact string used to securely transmit claims (like user id, roles, expiry) between client and server.
* It has three parts: header, payload, and signature, combined like `header.payload.signature` and separated by dots.
* The header specifies type and signing algorithm (for example `HS256`), the payload holds data such as `sub` (subject/user id) and `exp` (expiry), and the signature ensures the token was not tampered with.

## High-level flow in FastAPI

In a typical FastAPI JWT setup, the flow is:

1. User calls a `/token` or `/login` endpoint with username and password (usually using the OAuth2 password flow form).
2. The server verifies the password (after hashing comparison) and, if valid, creates a JWT that encodes the user identity and expiration.
3. The client stores this JWT (often in memory or local storage) and sends it on each request in the `Authorization: Bearer <token>` header.
4. FastAPI dependencies decode and verify the JWT on each protected endpoint and reject the request if the token is missing, invalid, or expired

## JWT structure (just enough theory)

* Header example (conceptually): it says “this is a JWT and signed with HS256.”
* Payload example: it typically includes `sub` for the user identifier, plus claims like `exp` (expiry time), and sometimes roles or permissions.
* Signature: created by taking the base64-encoded header and payload, adding a secret key, and running the chosen algorithm to produce a final signed token.
  **As long as only your backend knows the secret key, no one else can forge a valid signature, so you can trust the payload content after verification.**

## Core pieces in FastAPI JWT auth

FastAPI mainly uses:

* A secret key and algorithm constants used to sign/verify tokens (for example `SECRET_KEY` and `ALGORITHM="HS256"`).
* A function to create access tokens that takes a payload dict, adds `exp`, and returns the encoded JWT string.
* Password hashing utilities (`Argon2`, `bcrypt`, etc.) to store hashed passwords and verify logins securely.
* `OAuth2PasswordBearer` from `fastapi.security` to declare that endpoints expect a Bearer token in the `Authorization` header.
* Dependencies like `get_current_user` that read the token, decode it with `jwt.decode`, load the user, and raise `HTTPException(401)` if anything fails.

## Why JWT is popular for APIs

* Stateless: the server does not need to store session data; all necessary info is in the token, and validity is checked via the signature and expiry.
* Decoupled clients: web, mobile, and other services can all use the same backend and store the token however they want.
* Easy integration with FastAPI: the security dependencies and OpenAPI docs support Bearer tokens, making interactive testing simple.

## Common pitfalls and best practices

* Never store plain passwords; always hash them with a strong algorithm like `Argon2` or `bcrypt` and verify hashes during login.
* Set reasonable expiration (for example `15–60` minutes) and consider refresh tokens for long-lived sessions.
* Keep your `SECRET_KEY` out of source control and load it from environment variables or secrets management.
* Always validate signature and expiry when decoding; reject tokens that are expired or malformed.
