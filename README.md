# URLSpec: URL Shortening and Analytics Service

**URLSpec** is a lightweight and efficient tool designed for managing and specifying URL routing patterns, optimized for high-performance web services. Built with **FastAPI**, it supports seamless URL mapping, caching with Redis, and persistence using SQLite. The application is structured to simplify the development and deployment of shortened routing mechanisms.

---

## Core Components

### 1. **Routers**
- Handles the primary URL management logic.
- Provides endpoints for:
  - Adding new URL routes.
  - Fetching existing routes and redirecting them back
  - Analytics for each and every shortened urls
- Includes validation for route specifications to ensure compatibility with FastAPI’s standards.

### 2. **Redis Integration**
- Implements caching for faster retrieval of frequently accessed routes.
- Reduces writer-database load and improves overall performance.

### 3. **Exception Handling**
- Configured for handling invalid URLs and expired urls
- If an URL is expired appropriate mssgs is shown to the user and its cleaned from DB

---

## Setting Up Locally

Follow these steps to set up the project on your local
```
pip install virtualenv
python -m venv env
source env/bin/activate  # On Windows use `env\Scripts\activate`
pip install -r requirements.txt

# brew install redis // in case of mac or accoridngly as per ur distro
RUN redis-server
```

To run the app locally

```
# set up sample .env referring from sample.env

python3 main.py

## or you may use nohup to run the process in background as well
```

Head over to http://localhost:port/docs to access the app

