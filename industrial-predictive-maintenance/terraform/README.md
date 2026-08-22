# AWS Production Deployment Infrastructure (Terraform)

This directory contains Terraform scripts to deploy the core services of the **Industrial Predictive Maintenance Platform** to AWS.

## Architecture & Network Design

```mermaid
graph TD
    User([Public Client]) --> ALB[Application Load Balancer]
    subgraph VPC [VPC - 10.0.0.0/16]
        subgraph PublicSubnets [Public Subnets (AZ-1 & AZ-2)]
            ALB
            NAT[NAT Gateway]
        end
        subgraph PrivateSubnets [Private Subnets (AZ-1 & AZ-2)]
            ECS[ECS Fargate Tasks: Ingestion & API]
            RDS[(Multi-AZ RDS Postgres)]
            Redis[(Multi-AZ ElastiCache Redis)]
        end
    end
    ALB -->|Exposes Port 80| ECS
    ECS -->|Pub/Sub & Queue| Redis
    ECS -->|Ingestion & Query| RDS
    ECS -->|Secrets Fetch| SM[AWS Secrets Manager]
```

### Subnet Strategy
*   **Public Subnets**: Houses the public Load Balancer (ALB) and NAT Gateway.
*   **Private Subnets**: Houses the ECS Fargate containers (Ingestion API), ElastiCache Redis, and RDS PostgreSQL DB instance. These services are completely isolated from the open internet. Outbound traffic goes through the NAT Gateway for external calls (like Gemini API).

### Security Group Policies (Least Privilege)
1.  **ALB SG**: Allows ingress from `0.0.0.0/0` on port 80.
2.  **ECS Tasks SG**: Allows ingress from the ALB security group *only* on port 8000 and 8501.
3.  **RDS SG**: Allows ingress on port 5432 *only* from the ECS Tasks security group.
4.  **Redis SG**: Allows ingress on port 6379 *only* from the ECS Tasks security group.

## Secrets Management

Secrets (database password, Gemini API key) are stored in **AWS Secrets Manager**.
*   The ECS task execution IAM role has `secretsmanager:GetSecretValue` permission for this specific secret ARN.
*   Fargate injects these values directly into the containers as environment variables at task start time. No secrets are ever stored on disk or hardcoded in configurations.

## High Availability (HA) & Production Considerations

For production readiness:
1.  **Multi-AZ Database**: The RDS instance uses `multi_az = true` which spins up a hot-standby database in a secondary Availability Zone, automatically syncing and handling failovers.
2.  **Multi-AZ Redis**: ElastiCache Redis is configured as a replication group with 2 nodes across AZs (`automatic_failover_enabled = true` and `multi_az_enabled = true`). If the primary node crashes, the replica promotes in seconds.
3.  **ECS Autoscale**: ECS Fargate runs 2 tasks by default (`desired_count = 2`). In production, configure ECS service autoscaling policies based on CPU/Memory usage.
4.  **TimescaleDB Scale**: For large scale operations, self-manage TimescaleDB on AWS EKS (Kubernetes) using the TimescaleDB Kubernetes Operator with EBS gp3 storage classes, or utilize Timescale Cloud (SaaS) and hook it up via VPC peering.
