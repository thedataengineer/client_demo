# System Architecture

This document outlines the high-level architecture of the application.

## Overview

The system consists of three primary components deployed via Docker:

1. **Frontend (React / Vite)**
   - Serves the user interface.
   - Communicates with the backend REST API.

2. **Backend (Python / FastAPI)**
   - Handles business logic.
   - Exposes RESTful endpoints.
   - Connects to the database using SQLAlchemy.

3. **Database (PostgreSQL)**
   - Persists application state.

## Architecture Diagram

```mermaid
flowchart TD
    User([User]) -->|HTTP/HTTPS| Frontend[React Frontend (Port 5173)]
    Frontend -->|REST API Calls| Backend[FastAPI Backend (Port 8000)]
    Backend -->|SQLAlchemy| DB[(PostgreSQL Database (Port 5432))]
    
    subgraph Docker Compose Environment
        Frontend
        Backend
        DB
    end
```

## Infrastructure

The infrastructure is provisioned using Terraform. Currently, it's set up to mock local resources for a fully offline development environment.
