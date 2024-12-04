# URLSpec: URL Shortening and Analytics Service

![image](https://github.com/user-attachments/assets/398aac7c-4d49-4059-83f7-0fa087bdfe2d)


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

Using Dockerfile

```
cd src
docker build -t urlspec:v1 .
docker run --env-file ../.env -it {{container_id}}
```

Head over to http://localhost:port/docs to access the app

## Tech Stack

- **Backend Framework:** [FastAPI](https://fastapi.tiangolo.com/) (Python-based, asynchronous, high-performance web framework)
- **Cache:** [Redis](https://redis.io/) (In-memory key-value store for caching)
- **Database:** SQLite (Lightweight SQL database for persistent storage)
- **Deployment Platform:** AWS (EC2 + API Gateway) (Supports scalable cloud deployment)

