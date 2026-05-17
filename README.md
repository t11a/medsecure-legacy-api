# Overview
This is a Devin sample app project demonstrating an automated security remediation pipeline using GitHub Actions, CodeQL, and the Devin API.

## Automated Remediation Workflow

The following diagram illustrates the end-to-end automated workflow for fixing CodeQL security alerts:

```mermaid
graph TD
    subgraph "GitHub Repository"
        A(Engineer pushes code) --> B{CodeQL Scan}
        B -- Vulnerability detected --> C[Security Alert Created]
        
        M(Engineer merges PR) --> N{CodeQL Scan}
        N -- Vulnerability fixed --> O[Security Alert Closed]
    end

    subgraph "Automated Remediation Pipeline"
        C -->|workflow_run| D[Trigger Devin Action]
        D --> E[Python Script]
        E -->|Check GitHub API| F{Open Alert & No PR?}
        F -- Yes --> G[Call Devin API]
        F -- No --> H[Skip / Idempotency]
    end

    subgraph "Cognition Devin"
        G --> I[Devin Session Starts]
        I --> J[Devin clones repo & fixes code]
        J --> K[Devin creates Pull Request]
    end

    K -.->|Review & Merge| M
```