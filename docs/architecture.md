# System Architecture

This document outlines the high-level architecture of the application.

## Overview

The system consists of three primary components deployed via Docker:

1. **Frontend (React / Vite)**
   - Serves the user interface.
   - Communicates with the backend REST API.

2. **Backend (Python / FastAPI) - N-Tier Architecture**
   - **API Layer**: Handles routing and HTTP requests.
   - **Service Layer**: Orchestrates business logic and validations.
   - **Repository Layer**: Encapsulates all data access and ORM logic.
   - **Data Layer**: Manages SQLAlchemy ORM entities and DB triggers.
   - **Schemas**: Validates input/output via Pydantic.

3. **Database (PostgreSQL)**
   - Persists application state.
   - Maintains transactional integrity with audit triggers.

## Architecture Diagram

```mermaid
flowchart TD
    User([User]) -->|HTTP/HTTPS| Frontend[React Frontend (Port 5173)]
    
    subgraph Backend [FastAPI Backend]
        API[API / Controllers]
        Services[Service Layer]
        Repos[Repository Layer]
        Models[Models & Schemas]
    end

    Frontend -->|REST API Calls| API
    API --> Services
    Services --> Repos
    Repos --> Models
    Repos -->|SQLAlchemy| DB[(PostgreSQL Database)]
    
    subgraph Docker Compose Environment
        Frontend
        Backend
        DB
    end
```

## Infrastructure

The infrastructure is provisioned using Terraform. Currently, it's set up to mock local resources for a fully offline development environment.
