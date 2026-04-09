# Milestone 5 — Service Communication Matrix

## Sync Communication (gRPC)
Used for real-time validation and data retrieval where a response is mandatory before proceeding.

| Caller Service | Provider Service | Use Case | RPC Method |
| :--- | :--- | :--- | :--- |
| **projectService** | employeeService | Validate employee exists before project assignment. | `GetEmployee` |
| **financeService** | projectService | Validate project exists before recording revenue/cost. | `GetProject` |
| **authService**| employeeService | Verify user profile details upon token refresh. | `GetEmployeeByEmail` |
| **analyticsService**| financeService | Get real-time revenue snapshots for dashboarding. | `GetRevenueSummary` |

## Async Communication (Kafka)
Used for downstream updates and decoupling heavy workloads.

| Topic | Event | Producer | Primary Consumers |
| :--- | :--- | :--- | :--- |
| `employee-events` | `EMPLOYEE_CREATED` | employeeService | aiService, notificationService |
| `project-events` | `PROJECT_CREATED` | projectService | analyticsService, aiService |
| `finance-events` | `REVENUE_ADDED` | financeService | analyticsService, notificationService |
| `project-events` | `ASSIGNMENT_CREATED`| projectService | analyticsService |
