# NOIR-Employee Portal with AI Chatbot

A containerized employee management system built with **FastAPI, PostgreSQL, Docker, SQLAlchemy, CRUD APIs, and an AI chatbot**.

This project is designed as a practical learning project to understand how a modern backend application connects an API, relational database, and chatbot while running inside Docker containers.


## Project Overview

The **Employee Portal** allows users to manage employee information through REST APIs and interact with the employee database through a chatbot.

The system supports:

* Creating employees
* Viewing employees
* Viewing a single employee
* Updating employee information
* Deleting employees
* Searching employee records
* Asking the chatbot questions about employees
* Adding new employees using natural-language chatbot commands
* Storing all employee information in PostgreSQL
* Running the application and database using Docker

### Example Chatbot Interaction

**User:**

> Add a new employee named Ali Khan. His email is [ali.khan@example.com](mailto:ali.khan@example.com). He works as a Data Analyst in the Data Science department and earns 90,000.

**Chatbot:**

> Employee Ali Khan has been added successfully.

The chatbot extracts the required information and communicates with the FastAPI backend to create the employee record.

---

# Learning Objectives

The main purpose of this project is to learn how different backend technologies work together.

By completing this project, I will learn:

### 1. Docker

* What containers are
* Why containers are useful
* How to create a Dockerfile
* How to build Docker images
* How to run containers
* How Docker networking works
* How environment variables are configured

### 2. PostgreSQL

* Creating databases
* Creating tables
* Defining columns and data types
* Primary keys
* Constraints
* Inserting data
* Updating data
* Deleting data
* Querying data

### 3. FastAPI

* Creating APIs
* API routes
* HTTP methods
* Request parameters
* Request bodies
* Response models
* Pydantic validation
* Automatic API documentation

### 4. CRUD

Understanding the four fundamental database operations:

| Operation | HTTP Method | Purpose           |
| --------- | ----------- | ----------------- |
| Create    | POST        | Add employee      |
| Read      | GET         | Retrieve employee |
| Update    | PUT/PATCH   | Modify employee   |
| Delete    | DELETE      | Remove employee   |

### 5. Database Integration

Learn how FastAPI communicates with PostgreSQL using SQLAlchemy.

### 6. Chatbot Integration

Learn how a chatbot can understand a user's request and use backend APIs/database operations to perform actions.

---

# System Architecture

```text
                    ┌──────────────────────┐
                    │       User           │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │   Chatbot / Client   │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │       FastAPI        │
                    │      REST API        │
                    └──────────┬───────────┘
                               │
                    ┌──────────▼───────────┐
                    │      SQLAlchemy      │
                    │        ORM           │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │     PostgreSQL       │
                    │      Database        │
                    └──────────────────────┘
```

---

# Docker Architecture

The application uses multiple containers:

```text
┌─────────────────────────────────────────────┐
│              Docker Compose                 │
│                                             │
│  ┌─────────────────┐   ┌─────────────────┐  │
│  │  FastAPI        │   │   PostgreSQL    │  │
│  │  Container      │──▶│  Container     │   │
│  │                 │   │                 │  │
│  │  Python         │   │   Database      │  │
│  │  FastAPI        │   │   employees     │  │
│  │  SQLAlchemy     │   │                 │  │
│  └─────────────────┘   └─────────────────┘  │
│                                             │
└─────────────────────────────────────────────┘
```

Docker Compose allows both containers to communicate through a Docker network.

---

# Project Structure

```text
employee-portal/
│
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── database.py
│   ├── models.py
│   ├── schemas.py
│   ├── crud.py
│   └── chatbot.py
│
├── data/
│   └── employees.csv
│
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── .env
├── .gitignore
└── README.md
```

---

# Database

The project uses **PostgreSQL** as the relational database.

## Employee Table

The employee table contains 8 columns:

```text
employees
│
├── employee_id
├── first_name
├── last_name
├── email
├── department
├── job_title
├── salary
└── hire_date
```

### Example Record

```text
ID: 1
Name: Ayesha Khan
Email: ayesha.khan@example.com
Department: Data Science
Job Title: Data Analyst
Salary: 85000
Hire Date: 2023-01-15
```

The initial database will contain **50 dummy employee records**.

---

# API Endpoints

## Create Employee

```http
POST /employees
```

Creates a new employee.

Example request:

```json
{
    "first_name": "Ali",
    "last_name": "Khan",
    "email": "ali.khan@example.com",
    "department": "Data Science",
    "job_title": "Data Analyst",
    "salary": 90000,
    "hire_date": "2026-08-28"
}
```

---

## Get All Employees

```http
GET /employees
```

Returns all employees.

---

## Get Employee by ID

```http
GET /employees/{employee_id}
```

Example:

```http
GET /employees/10
```

---

## Update Employee

```http
PUT /employees/{employee_id}
```

Updates an existing employee.

---

## Delete Employee

```http
DELETE /employees/{employee_id}
```

Deletes an employee.

---

## Chatbot

```http
POST /chat
```

Allows users to communicate with the employee system using natural language.

Example:

```json
{
    "message": "Add a new employee named Sara Ahmed who works as a Data Analyst."
}
```

The chatbot determines the user's intention and performs the appropriate operation.

---

# Chatbot Capabilities

The chatbot will eventually support commands such as:

### Searching

> Show me all employees in the Data Science department.

### Finding an employee

> Find employee number 25.

### Counting

> How many employees work in HR?

### Adding

> Add Ali Khan as a Software Engineer in Engineering with a salary of 100000.

### Updating

> Change Ali Khan's salary to 110000.

### Deleting

> Delete employee number 35.

The chatbot will act as a natural-language interface over the CRUD API.

---

# Dockerfile

The `Dockerfile` defines how the FastAPI application container is created.

Conceptually:

```text
Python Base Image
       ↓
Install Dependencies
       ↓
Copy Application
       ↓
Expose Port 8000
       ↓
Start FastAPI
```

---

# Docker Compose

Docker Compose will be used to run:

```text
FastAPI Container
        +
PostgreSQL Container
```

Both services will communicate using Docker's internal network.

---

# Environment Variables

Database configuration will be stored in `.env`.

Example:

```env
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_password
POSTGRES_DB=employees_db
POSTGRES_HOST=db
POSTGRES_PORT=5432
```

The application will construct the database connection using these values.

---

# Running the Project

## 1. Clone the Repository

```bash
git clone <repository-url>
```

Move into the project:

```bash
cd employee-portal
```

---

## 2. Create `.env`

Create a `.env` file:

```env
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_password
POSTGRES_DB=employees_db
POSTGRES_HOST=db
POSTGRES_PORT=5432
```

---

## 3. Build Docker Containers

```bash
docker compose build
```

---

## 4. Start the Application

```bash
docker compose up
```

To run in detached mode:

```bash
docker compose up -d
```

---

## 5. Access FastAPI

Open:

```text
http://localhost:8000
```

FastAPI Swagger documentation:

```text
http://localhost:8000/docs
```

Alternative documentation:

```text
http://localhost:8000/redoc
```

---

# Testing the API

FastAPI provides an interactive Swagger UI.

Open:

```text
http://localhost:8000/docs
```

From there, you can test:

```text
POST /employees
GET /employees
GET /employees/{id}
PUT /employees/{id}
DELETE /employees/{id}
POST /chat
```

---

# Technologies

| Technology     | Purpose                     |
| -------------- | --------------------------- |
| Python         | Backend programming         |
| FastAPI        | REST API framework          |
| PostgreSQL     | Database                    |
| SQLAlchemy     | ORM                         |
| Pydantic       | Data validation             |
| Docker         | Containerization            |
| Docker Compose | Multi-container application |
| REST API       | Communication layer         |
| CRUD           | Employee management         |
| Chatbot        | Natural-language interface  |

---

# Concepts Demonstrated

This project demonstrates the following concepts:

```text
Python
  │
  ▼
FastAPI
  │
  ├── Pydantic
  │
  ├── CRUD
  │
  ▼
SQLAlchemy
  │
  ▼
PostgreSQL
```

And containerization:

```text
Docker
  │
  └── Docker Compose
       │
       ├── FastAPI Container
       │
       └── PostgreSQL Container
```

---

# Future Improvements

Possible future improvements include:

* JWT authentication
* User login and registration
* Employee profile pages
* Role-based access control
* Department management
* Employee search and filtering
* Pagination
* Database migrations using Alembic
* Redis caching
* AI-powered chatbot
* Chat history
* Voice-based chatbot
* Frontend using React
* Employee analytics dashboard
* Docker production deployment
* CI/CD using GitHub Actions
* Cloud deployment

---

# Learning Roadmap

This project will be developed progressively:

### Phase 1 — PostgreSQL

```text
Install PostgreSQL
      ↓
Create Database
      ↓
Create Employees Table
      ↓
Insert 50 Records
      ↓
Practice SQL Queries
```

### Phase 2 — FastAPI

```text
Create FastAPI App
      ↓
Create Routes
      ↓
Connect PostgreSQL
      ↓
Create CRUD APIs
      ↓
Test with Swagger
```

### Phase 3 — Docker

```text
Create Dockerfile
      ↓
Build Image
      ↓
Run FastAPI Container
      ↓
Create PostgreSQL Container
      ↓
Connect Containers
      ↓
Docker Compose
```

### Phase 4 — Chatbot

```text
User Message
      ↓
Intent Detection
      ↓
Extract Employee Information
      ↓
FastAPI Endpoint
      ↓
PostgreSQL
      ↓
Response to User
```

### Phase 5 — Production Improvements

```text
Authentication
      ↓
Validation
      ↓
Error Handling
      ↓
Logging
      ↓
Testing
      ↓
CI/CD
      ↓
Deployment
```

---

# Project Goal

The goal of this project is not only to build an employee portal, but to understand **how a complete backend system works from the database layer to the API layer, containerization layer, and AI interaction layer**.

By the end of the project, the application should demonstrate:

**PostgreSQL → SQLAlchemy → FastAPI → CRUD → Docker → Chatbot**

and provide a strong practical foundation for building larger production-ready backend and AI applications.

