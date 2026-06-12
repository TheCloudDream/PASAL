
# PASAL 🛍️

> A high-performance local marketplace platform built as a modular monolith using FastAPI, PostgreSQL, and Redis.
>
> PASAL enables neighborhood residents to discover and purchase products from local small businesses while providing merchants with a simple platform to manage inventory and orders.

---

## 📖 Overview

PASAL is designed as a **production-inspired e-commerce system** that demonstrates both modern backend development and DevOps practices.

The project focuses on:

* Secure JWT-based authentication
* Role-based access control (Buyers & Sellers)
* High-speed shopping cart operations using Redis
* Reliable order processing with PostgreSQL
* Modular monolith architecture for maintainability
* Containerization and future Kubernetes deployment

### Why PASAL?

Most beginner e-commerce projects become large, tightly coupled codebases.

PASAL follows a **modular monolith architecture**, where each domain owns its logic while remaining deployable as a single application.

This provides:

* Simpler development
* Faster deployment
* Easier testing
* Clear path toward microservices if needed

---

## 🏗️ Architecture

```text
┌─────────────────────┐
│      Client         │
└──────────┬──────────┘
           │ HTTP
           ▼
┌─────────────────────┐
│      FastAPI        │
│  Modular Monolith   │
└───────┬─────┬───────┘
        │     │
        │     │
        ▼     ▼
 PostgreSQL   Redis
 Persistent   Active Cart
 Data Store   Storage
```

### Core Modules

| Module    | Responsibility                 |
| --------- | ------------------------------ |
| Auth      | Authentication & authorization |
| Users     | Buyer & seller management      |
| Products  | Product catalog management     |
| Cart      | Redis-powered shopping cart    |
| Orders    | Checkout & order processing    |
| Inventory | Stock validation and updates   |

---

## 🛠 Technology Stack

### Backend

* FastAPI
* Uvicorn
* Pydantic

### Database

* PostgreSQL

### Cache

* Redis

### Security

* JWT Authentication
* Password Hashing (Passlib)

### Future Infrastructure

* Docker
* Kubernetes
* Terraform
* CI/CD Pipelines

---

# 🚀 Getting Started

## Prerequisites

Install the following:

* Python 3.11+
* PostgreSQL
* Redis
* Git

Verify installation:

```bash
python --version
psql --version
redis-server --version
git --version
```

---

## 1. Clone Repository

```bash
git clone https://github.com/yourusername/pasal.git
cd pasal
```

---

## 2. Create Environment Variables

Create a `.env` file in the project root:

```env
PROJECT_NAME=PASAL Local Marketplace

DEBUG=True

DATABASE_URL=postgresql://postgres:postgres@localhost:5432/pasal_db

REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0

JWT_SECRET_KEY=replace_with_secure_key
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
```

Generate a secure secret:

```bash
openssl rand -hex 32
```

Copy the generated value into `JWT_SECRET_KEY`.

---

## 3. Create Python Virtual Environment

Linux / macOS:

```bash
python3 -m venv venv
source venv/bin/activate
```

Windows:

```powershell
python -m venv venv
venv\Scripts\activate
```

---

## 4. Install Dependencies

```bash
pip install -r requirements.txt
```

Or manually:

```bash
pip install \
fastapi \
uvicorn \
psycopg2-binary \
redis \
pydantic \
passlib \
python-jose
```

---

## 5. Create PostgreSQL Database

Start PostgreSQL and create the database:

```sql
CREATE DATABASE pasal_db;
```

---

## 6. Start Redis

Linux/macOS:

```bash
redis-server
```

Docker:

```bash
docker run -p 6379:6379 redis
```

---

## 7. Run the Application

```bash
uvicorn app.main:app --reload
```

You should see:

```text
INFO: Uvicorn running on http://127.0.0.1:8000
```

---

# 🌐 API Access

### Base URL

```text
http://127.0.0.1:8000
```

### Interactive Swagger Documentation

```text
http://127.0.0.1:8000/docs
```

### ReDoc Documentation

```text
http://127.0.0.1:8000/redoc
```

---

# 🧭 API Overview

## Authentication

| Method | Endpoint         | Access |
| ------ | ---------------- | ------ |
| POST   | `/auth/register` | Public |
| POST   | `/auth/token`    | Public |

### Register

```http
POST /auth/register
```

Creates a new buyer or seller account.

### Login

```http
POST /auth/token
```

Returns a JWT access token.

---

## Products

| Method | Endpoint         | Access |
| ------ | ---------------- | ------ |
| GET    | `/products`      | Public |
| GET    | `/products/{id}` | Public |
| POST   | `/products`      | Seller |
| PUT    | `/products/{id}` | Seller |
| DELETE | `/products/{id}` | Seller |

---

## Cart

Redis-backed for low-latency operations.

| Method | Endpoint           |
| ------ | ------------------ |
| GET    | `/cart`            |
| POST   | `/cart/items`      |
| DELETE | `/cart/items/{id}` |

---

## Orders

| Method | Endpoint       |
| ------ | -------------- |
| POST   | `/orders`      |
| GET    | `/orders`      |
| GET    | `/orders/{id}` |

Checkout flow:

1. Validate inventory
2. Create order record
3. Deduct stock
4. Commit transaction
5. Clear Redis cart

---

# 📂 Project Structure

```text
pasal/
│
├── app/
│   ├── auth/
│   ├── users/
│   ├── products/
│   ├── cart/
│   ├── orders/
│   ├── inventory/
│   ├── database/
│   └── main.py
│
├── tests/
│
├── .env
├── requirements.txt
└── README.md
```

---

# 🔒 Security Features

* JWT Authentication
* Password Hashing
* Role-Based Authorization
* Input Validation
* Protected Seller Endpoints
* Secure Environment Configuration

---

# 🛣️ Roadmap

## Backend

* [ ] Product search
* [ ] Product categories
* [ ] Pagination
* [ ] Image uploads
* [ ] Email notifications

## DevOps

### Docker & Containerization

- [x] Backend Docker Container
- [x] Frontend Docker Container
- [x] PostgreSQL Container
- [x] Redis Container
- [x] Docker Compose Multi-Container Environment
- [x] Custom Docker Network

### Reliability & Operations

- [ ] Health Checks
- [ ] Restart Policies
- [ ] Application Logging
- [ ] Environment Configuration Management

### CI/CD

- [ ] GitHub Repository Setup
- [ ] GitHub Actions CI Pipeline
- [ ] Automated Testing
- [ ] Docker Image Build Automation
- [ ] Container Registry (GHCR)

### Deployment

- [ ] VPS Deployment
- [ ] Reverse Proxy (Caddy)
- [ ] HTTPS / SSL Configuration

### Monitoring & Observability

- [ ] Monitoring
- [ ] Metrics Collection
- [ ] Log Aggregation
- [ ] Alerting

### Kubernetes (Ubuntu VM Lab)

- [ ] Ubuntu Server VM Setup (VirtualBox)
- [ ] Docker Installation on VM
- [ ] Kubernetes Cluster Setup
- [ ] kubectl Configuration
- [ ] Kubernetes Namespaces
- [ ] ConfigMaps
- [ ] Secrets Management
- [ ] Deploy Backend to Kubernetes
- [ ] Deploy Frontend to Kubernetes
- [ ] Deploy PostgreSQL to Kubernetes
- [ ] Deploy Redis to Kubernetes
- [ ] Kubernetes Services
- [ ] Ingress Controller
- [ ] Persistent Volumes
- [ ] End-to-End Kubernetes Deployment

### Infrastructure as Code

- [ ] Terraform Fundamentals
- [ ] Infrastructure Provisioning with Terraform

---

# 🎯 Learning Objectives

PASAL is also a portfolio project intended to demonstrate:

* Backend Engineering
* System Design
* Database Design
* Caching Strategies
* Authentication & Security
* Docker
* Kubernetes
* Terraform
* DevOps Practices

---

## 📜 License

MIT License

---

## 👨‍💻 Author

Built as a backend and DevOps portfolio project to explore scalable marketplace architecture and cloud-native deployment practices.
