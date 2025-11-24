# FASTAPI Learning Notes - Project 4

## Basic sqlite3 Command

* .schema - To list down present tables
* select * from <table_name>;
* insert into <table_name> (column_name1, column_name2, .....) values (value1, value2, .....);
* .mode table
* delete from <table_name> where <column_name> = `<value>`;
* update <table_name> set <column_name1> = value1, <column_name2> = `<value>` where <column_name> = `<value>`;

---

## JWT Authentication

JWT authentication in FastAPI is about issuing a signed token after login and then verifying that token on every protected request instead of using sessions or cookies.

### What is a JWT?

* A JWT (JSON Web Token) is a compact string used to securely transmit claims (like user id, roles, expiry) between client and server.
* It has three parts: header, payload, and signature, combined like `header.payload.signature` and separated by dots.
* The header specifies type and signing algorithm (for example `HS256`), the payload holds data such as `sub` (subject/user id) and `exp` (expiry), and the signature ensures the token was not tampered with.

### High-level flow in FastAPI

In a typical FastAPI JWT setup, the flow is:

1. User calls a `/token` or `/login` endpoint with username and password (usually using the OAuth2 password flow form).
2. The server verifies the password (after hashing comparison) and, if valid, creates a JWT that encodes the user identity and expiration.
3. The client stores this JWT (often in memory or local storage) and sends it on each request in the `Authorization: Bearer <token>` header.
4. FastAPI dependencies decode and verify the JWT on each protected endpoint and reject the request if the token is missing, invalid, or expired

### JWT structure (just enough theory)

* Header example (conceptually): it says “this is a JWT and signed with HS256.”
* Payload example: it typically includes `sub` for the user identifier, plus claims like `exp` (expiry time), and sometimes roles or permissions.
* Signature: created by taking the base64-encoded header and payload, adding a secret key, and running the chosen algorithm to produce a final signed token.
  **As long as only your backend knows the secret key, no one else can forge a valid signature, so you can trust the payload content after verification.**

### Core pieces in FastAPI JWT auth

FastAPI mainly uses:

* A secret key and algorithm constants used to sign/verify tokens (for example `SECRET_KEY` and `ALGORITHM="HS256"`).
* A function to create access tokens that takes a payload dict, adds `exp`, and returns the encoded JWT string.
* Password hashing utilities (`Argon2`, `bcrypt`, etc.) to store hashed passwords and verify logins securely.
* `OAuth2PasswordBearer` from `fastapi.security` to declare that endpoints expect a Bearer token in the `Authorization` header.
* Dependencies like `get_current_user` that read the token, decode it with `jwt.decode`, load the user, and raise `HTTPException(401)` if anything fails.

### Why JWT is popular for APIs

* Stateless: the server does not need to store session data; all necessary info is in the token, and validity is checked via the signature and expiry.
* Decoupled clients: web, mobile, and other services can all use the same backend and store the token however they want.
* Easy integration with FastAPI: the security dependencies and OpenAPI docs support Bearer tokens, making interactive testing simple.

### Common pitfalls and best practices

* Never store plain passwords; always hash them with a strong algorithm like `Argon2` or `bcrypt` and verify hashes during login.
* Set reasonable expiration (for example `15–60` minutes) and consider refresh tokens for long-lived sessions.
* Keep your `SECRET_KEY` out of source control and load it from environment variables or secrets management.
* Always validate signature and expiry when decoding; reject tokens that are expired or malformed.

--

## 🚀 **Alembic — Complete Introduction & Commands**

Alembic is the **official database migration tool** for SQLAlchemy.

It helps you:

* Track schema changes over time
* Apply migrations safely
* Revert (downgrade) changes when needed
* Maintain database consistency across environments

### 📌 Key Alembic Commands

#### 1. Initialize Alembic in your project

<pre class="overflow-visible!" data-start="797" data-end="844"><div class="contain-inline-size rounded-2xl relative bg-token-sidebar-surface-primary"><div class="sticky top-9"><div class="absolute end-0 bottom-0 flex h-9 items-center pe-2"><div class="bg-token-bg-elevated-secondary text-token-text-secondary flex items-center gap-4 rounded-sm px-2 font-sans text-xs"></div></div></div><div class="overflow-y-auto p-4" dir="ltr"><code class="whitespace-pre!"><span><span>alembic</span><span> init </span><span>alembic</span><span>
</span></span></code></div></div></pre>

#### 2. Create a new migration script

<pre class="overflow-visible!" data-start="797" data-end="844"><div class="contain-inline-size rounded-2xl relative bg-token-sidebar-surface-primary"><div class="sticky top-9"><div class="absolute end-0 bottom-0 flex h-9 items-center pe-2"><div class="bg-token-bg-elevated-secondary text-token-text-secondary flex items-center gap-4 rounded-sm px-2 font-sans text-xs"></div></div></div><div class="overflow-y-auto p-4" dir="ltr"><code class="whitespace-pre!"><span><span>alembic</span><span> revision -m </span><span>"your message here"</span><span>
</span></span></code></div></div></pre>

This generates an empty migration file in `versions/`.

You manually write `upgrade()` and `downgrade()` code.

Creates:

* `alembic/` folder
* `alembic.ini`
* `env.py` (main configuration logic)
* `versions/` directory (migration scripts go here)

#### **3. Create migrations automatically (autogenerate)**

<pre class="overflow-visible!" data-start="1022" data-end="1079"><div class="contain-inline-size rounded-2xl relative bg-token-sidebar-surface-primary"><div class="sticky top-9"><div class="absolute end-0 bottom-0 flex h-9 items-center pe-2"><div class="bg-token-bg-elevated-secondary text-token-text-secondary flex items-center gap-4 rounded-sm px-2 font-sans text-xs"></div></div></div><div class="overflow-y-auto p-4" dir="ltr"><code class="whitespace-pre!"><span><span>alembic</span><span> revision --autogenerate -m </span><span>"your message"</span><span>
</span></span></code></div></div></pre>

Requires:

* SQLAlchemy models imported correctly
* `target_metadata` set in `env.py`

Alembic will compare DB schema vs. models and generate diffs.

#### **4. Apply migrations (upgrade DB schema)**

Upgrade to the  **latest revision** :

<pre class="overflow-visible!" data-start="1326" data-end="1354"><div class="contain-inline-size rounded-2xl relative bg-token-sidebar-surface-primary"><div class="sticky top-9"><div class="absolute end-0 bottom-0 flex h-9 items-center pe-2"><div class="bg-token-bg-elevated-secondary text-token-text-secondary flex items-center gap-4 rounded-sm px-2 font-sans text-xs"></div></div></div><div class="overflow-y-auto p-4" dir="ltr"><code class="whitespace-pre!"><span><span>alembic upgrade </span><span>head</span><span>
</span></span></code></div></div></pre>

Upgrade to a specific revision:

<pre class="overflow-visible!" data-start="1393" data-end="1430"><div class="contain-inline-size rounded-2xl relative bg-token-sidebar-surface-primary"><div class="sticky top-9"><div class="absolute end-0 bottom-0 flex h-9 items-center pe-2"><div class="bg-token-bg-elevated-secondary text-token-text-secondary flex items-center gap-4 rounded-sm px-2 font-sans text-xs"></div></div></div><div class="overflow-y-auto p-4" dir="ltr"><code class="whitespace-pre!"><span><span><span class="language-xml">alembic upgrade <revision_id</span></span><span>>
</span></span></code></div></div></pre>

Upgrade one version forward:

<pre class="overflow-visible!" data-start="1466" data-end="1492"><div class="contain-inline-size rounded-2xl relative
bg-token-sidebar-surface-primary"><div class="sticky top-9"><div class="absolute end-0 bottom-0 flex h-9 items-center pe-2"><div class="bg-token-bg-elevated-secondary text-token-text-secondary flex items-center gap-4 rounded-sm px-2 font-sans text-xs"></div></div></div><div class="overflow-y-auto p-4" dir="ltr"><code class="whitespace-pre!"><span><span>alembic</span><span> upgrade +</span><span>1</span><span>
</span></span></code></div></div></pre>

#### **5. Revert migrations (downgrade DB schema)**

Go back one version:

<pre class="overflow-visible!" data-start="1577" data-end="1605"><div class="contain-inline-size rounded-2xl relative bg-token-sidebar-surface-primary"><div class="sticky top-9"><div class="absolute end-0 bottom-0 flex h-9 items-center pe-2"><div class="bg-token-bg-elevated-secondary text-token-text-secondary flex items-center gap-4 rounded-sm px-2 font-sans text-xs"></div></div></div><div class="overflow-y-auto p-4" dir="ltr"><code class="whitespace-pre!"><span><span>alembic</span><span> downgrade -</span><span>1</span><span>
</span></span></code></div></div></pre>

Go back multiple versions:

<pre class="overflow-visible!" data-start="1639" data-end="1667"><div class="contain-inline-size rounded-2xl relative bg-token-sidebar-surface-primary"><div class="sticky top-9"><div class="absolute end-0 bottom-0 flex h-9 items-center pe-2"><div class="bg-token-bg-elevated-secondary text-token-text-secondary flex items-center gap-4 rounded-sm px-2 font-sans text-xs"></div></div></div><div class="overflow-y-auto p-4" dir="ltr"><code class="whitespace-pre!"><span><span>alembic</span><span> downgrade -</span><span>2</span><span>
</span></span></code></div></div></pre>

Downgrade to a specific revision:

<pre class="overflow-visible!" data-start="1708" data-end="1747"><div class="contain-inline-size rounded-2xl relative bg-token-sidebar-surface-primary"><div class="sticky top-9"><div class="absolute end-0 bottom-0 flex h-9 items-center pe-2"><div class="bg-token-bg-elevated-secondary text-token-text-secondary flex items-center gap-4 rounded-sm px-2 font-sans text-xs"></div></div></div><div class="overflow-y-auto p-4" dir="ltr"><code class="whitespace-pre!"><span><span><span class="language-xml">alembic downgrade <revision_id</span></span><span>>
</span></span></code></div></div></pre>

Reset database to base (initial state):

<pre class="overflow-visible!" data-start="1794" data-end="1824"><div class="contain-inline-size rounded-2xl relative bg-token-sidebar-surface-primary"><div class="sticky top-9"><div class="absolute end-0 bottom-0 flex h-9 items-center pe-2"><div class="bg-token-bg-elevated-secondary text-token-text-secondary flex items-center gap-4 rounded-sm px-2 font-sans text-xs"></div></div></div><div class="overflow-y-auto p-4" dir="ltr"><code class="whitespace-pre!"><span><span>alembic downgrade </span><span>base</span><span>
</span></span></code></div></div></pre>

#### **6. Show migration history**

<pre class="overflow-visible!" data-start="1865" data-end="1888"><div class="contain-inline-size rounded-2xl relative bg-token-sidebar-surface-primary"><div class="sticky top-9"><div class="absolute end-0 bottom-0 flex h-9 items-center pe-2"><div class="bg-token-bg-elevated-secondary text-token-text-secondary flex items-center gap-4 rounded-sm px-2 font-sans text-xs"></div></div></div><div class="overflow-y-auto p-4" dir="ltr"><code class="whitespace-pre!"><span><span>alembic </span><span>history</span><span>
</span></span></code></div></div></pre>

Show a detailed tree:

<pre class="overflow-visible!" data-start="1912" data-end="1945"><div class="contain-inline-size rounded-2xl relative bg-token-sidebar-surface-primary"><div class="sticky top-9"><div class="absolute end-0 bottom-0 flex h-9 items-center pe-2"><div class="bg-token-bg-elevated-secondary text-token-text-secondary flex items-center gap-4 rounded-sm px-2 font-sans text-xs"></div></div></div><div class="overflow-y-auto p-4" dir="ltr"><code class="whitespace-pre!"><span><span>alembic </span><span>history</span><span> --verbose
</span></span></code></div></div></pre>

#### **7. See current revision (what your DB is on)**

<pre class="overflow-visible!" data-start="2005" data-end="2028"><div class="contain-inline-size rounded-2xl relative bg-token-sidebar-surface-primary"><div class="sticky top-9"><div class="absolute end-0 bottom-0 flex h-9 items-center pe-2"><div class="bg-token-bg-elevated-secondary text-token-text-secondary flex items-center gap-4 rounded-sm px-2 font-sans text-xs"></div></div></div><div class="overflow-y-auto p-4" dir="ltr"><code class="whitespace-pre!"><span><span>alembic </span><span>current</span><span>
</span></span></code></div></div></pre>

#### **8. Stamp a revision without running migrations**

Useful when the DB already matches the schema.

<pre class="overflow-visible!" data-start="2138" data-end="2164"><div class="contain-inline-size rounded-2xl relative bg-token-sidebar-surface-primary"><div class="sticky top-9"><div class="absolute end-0 bottom-0 flex h-9 items-center pe-2"><div class="bg-token-bg-elevated-secondary text-token-text-secondary flex items-center gap-4 rounded-sm px-2 font-sans text-xs"></div></div></div><div class="overflow-y-auto p-4" dir="ltr"><code class="whitespace-pre!"><span><span>alembic stamp </span><span>head</span><span>
</span></span></code></div></div></pre>

Or stamp a specific revision:

<pre class="overflow-visible!" data-start="2197" data-end="2232"><div class="contain-inline-size rounded-2xl relative bg-token-sidebar-surface-primary"><div class="sticky top-9"><div class="absolute end-0 bottom-0 flex h-9 items-center pe-2"><div class="bg-token-bg-elevated-secondary text-token-text-secondary flex items-center gap-4 rounded-sm px-2 font-sans text-xs"></div></div></div><div class="overflow-y-auto p-4" dir="ltr"><code class="whitespace-pre!"><span><span><span class="language-xml">alembic stamp <revision_id</span></span><span>>
</span></span></code></div></div></pre>

#### **9. Check differences before auto-generating (dry run)**

<pre class="overflow-visible!" data-start="2301" data-end="2361"><div class="contain-inline-size rounded-2xl relative bg-token-sidebar-surface-primary"><div class="sticky top-9"><div class="absolute end-0 bottom-0 flex h-9 items-center pe-2"><div class="bg-token-bg-elevated-secondary text-token-text-secondary flex items-center gap-4 rounded-sm px-2 font-sans text-xs"></div></div></div><div class="overflow-y-auto p-4" dir="ltr"><code class="whitespace-pre!"><span><span>alembic revision </span><span>--autogenerate</span><span> -m "msg" </span><span>--head-only</span><span>
</span></span></code></div></div></pre>

Or see the diff without creating the file:

<pre class="overflow-visible!" data-start="2407" data-end="2468"><div class="contain-inline-size rounded-2xl relative bg-token-sidebar-surface-primary"><div class="sticky top-9"><div class="absolute end-0 bottom-0 flex h-9 items-center pe-2"><div class="bg-token-bg-elevated-secondary text-token-text-secondary flex items-center gap-4 rounded-sm px-2 font-sans text-xs"></div></div></div><div class="overflow-y-auto p-4" dir="ltr"><code class="whitespace-pre!"><span><span>alembic </span><span>--raiseerr</span><span> revision </span><span>--autogenerate</span><span> -m "check"
</span></span></code></div></div></pre>

---

### 🧠 **Best Practices**

#### ✔ Always verify autogenerated migrations

Alembic can detect incorrect diffs — always open the file.

#### ✔ Commit your migration files in Git

The `versions/` folder must be version-controlled.

#### ✔ Keep `env.py` clean

This is where you configure:

* DB URL
* target metadata
* schema search path
* async or sync engine

#### ✔ Never manually edit previous migrations unless absolutely necessary

Create new migrations instead.

## FASTAPI Commands

With Package Manager - UV

fastapi run app/main.py --reload --host 127.0.0.1 --port 8080
