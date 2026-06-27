# OLTP Architecture and Audit Capability

This document details the database-layer enhancements applied to harden the application for OLTP (Online Transaction Processing) workloads. **These changes shift state management to PostgreSQL**, guaranteeing audit integrity independently of the application layer. Furthermore, the architecture utilizes an API Gateway to enforce identity boundaries before traffic reaches the downstream services.

## Architectural Changes

### 1. Database-Level Auditing
We implemented native PostgreSQL triggers to manage audit logs. Relying on application-layer logging introduces race conditions and consistency risks. 
- **Trigger Function**: `audit_trigger_func()` executes automatically on all `INSERT`, `UPDATE`, and `DELETE` operations on the `items` table.
- **Audit Table**: `audit_logs` captures `table_name`, `action`, `record_id`, and a strict UTC `created_at` timestamp.

### 2. Compound Indexing
To simulate high-read production environments, we deployed explicit compound indexes.
- `ix_items_name_desc`: Accelerates text-based lookups across `name` and `description`.
- `ix_item_status_time`: Optimizes filtering by `completed` status and `updated_at` time bounds.
- `ix_audit_table_action`: Secures sub-millisecond retrieval of audit records grouped by operation type.

### 3. Persona Enforcement (API Gateway)
All requests to the backend API now route through an API Gateway (Macroservice). The Gateway inspects the `X-Persona` header to apply RBAC (Role-Based Access Control) rules before passing traffic to the legacy Monolith or the new Audit Microservice.
- **Admin**: Full access.
- **User**: Read and Write access, blocked from `DELETE`.
- **Viewer**: Read-only access across the board.

## API Endpoints

### Data Mutation (Audited via Legacy Monolith)
These endpoints are routed to the legacy monolith and trigger the PostgreSQL functions transparently.
- `POST /api/items` - Creates a new item and auto-generates `created_at` / `updated_at`. Logs `INSERT`.
- `PUT /api/items/{id}` - Toggles completion status and auto-updates `updated_at`. Logs `UPDATE`.
- `DELETE /api/items/{id}` - Removes the record from the active table. Logs `DELETE`.

### Audit Retrieval (Strangler Fig Microservice)
This endpoint is routed by the Gateway specifically to the new standalone Audit Microservice.
- `GET /api/audit`
  - **Description**: Returns the chronological ledger of database mutations.
  - **Parameters**: `limit` (default 50)
  - **Response**:
    ```json
    [
      {
        "id": 1,
        "table_name": "items",
        "action": "INSERT",
        "record_id": 1,
        "created_at": "2026-06-26T17:34:02.719304"
      }
    ]
    ```
