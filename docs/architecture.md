# System Architecture

This document outlines the high-level architecture of the application, which has transitioned from a monolith to a microservices architecture using the Strangler Fig pattern.

## Overview

The system consists of several primary components deployed via Docker, leveraging a Gateway for identity enforcement:

1. **Frontend (React / Vite)**
   - Serves the user interface with a mock Persona selector.
   - Communicates exclusively with the API Gateway.

2. **API Gateway (Python / FastAPI) - Macroservice**
   - **Identity Layer**: Intercepts the `X-Persona` header to enforce Role-Based Access Control (Admin, User, Viewer).
   - **Routing Layer**: Implements the Strangler Fig pattern by proxying `/api/audit` traffic to the Audit Microservice, and all other traffic to the Legacy Monolith.

3. **Legacy Monolith Backend (Python / FastAPI)**
   - Continues to serve the core `/api/items` domain.
   - Handles item creation, toggling status, and deletions.

4. **Audit Microservice (Python / FastAPI)**
   - A newly extracted domain handling only the `/api/audit` endpoint.
   - Operates independently from the monolith to allow isolated scaling and deployment.

5. **Database (PostgreSQL)**
   - Persists application state for both services (currently shared to reduce operational overhead during the initial transition).
   - Maintains transactional integrity with audit triggers.

## Architecture Diagram

```mermaid
flowchart TD
    User([User]) -->|HTTP/HTTPS + X-Persona| Frontend[React Frontend (Port 5173)]
    
    Frontend -->|REST API Calls| Gateway[API Gateway (Port 8080)]
    
    subgraph Gateway Layer
        Gateway -->|Persona Validation| Router[Routing Engine]
    end

    Router -->|/api/items| Monolith[Legacy Items Monolith (Port 8000)]
    Router -->|/api/audit| Audit[Audit Microservice (Port 8002)]

    Monolith --> DB[(PostgreSQL Database)]
    Audit --> DB
    
    subgraph Docker Compose Environment
        Frontend
        Gateway
        Monolith
        Audit
        DB
    end
```

## Infrastructure

The infrastructure is provisioned using Docker Compose for local orchestration, allowing rapid iteration across the distributed services.
