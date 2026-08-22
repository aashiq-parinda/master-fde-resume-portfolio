terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

# ==============================================================================
# 1. NETWORKING (VPC, Subnets, Route Tables, NAT Gateways)
# ==============================================================================

data "aws_availability_zones" "available" {
  state = "available"
}

resource "aws_vpc" "integration_vpc" {
  cidr_block           = var.vpc_cidr
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = {
    Name        = "integration-vpc"
    Environment = var.environment
  }
}

# Public Subnets (ALB, NAT Gateways)
resource "aws_subnet" "public" {
  count                   = 2
  vpc_id                  = aws_vpc.integration_vpc.id
  cidr_block              = var.public_subnet_cidrs[count.index]
  availability_zone       = data.aws_availability_zones.available.names[count.index]
  map_public_ip_on_launch = true

  tags = {
    Name        = "integration-public-subnet-${count.index + 1}"
    Environment = var.environment
  }
}

# Private Subnets (App Tasks, Private RDS Databases)
resource "aws_subnet" "private" {
  count             = 2
  vpc_id            = aws_vpc.integration_vpc.id
  cidr_block        = var.private_subnet_cidrs[count.index]
  availability_zone = data.aws_availability_zones.available.names[count.index]

  tags = {
    Name        = "integration-private-subnet-${count.index + 1}"
    Environment = var.environment
  }
}

resource "aws_internet_gateway" "igw" {
  vpc_id = aws_vpc.integration_vpc.id

  tags = {
    Name        = "integration-igw"
    Environment = var.environment
  }
}

# NAT Gateway for ECS tasks in private subnets to request external legacy services
resource "aws_eip" "nat_eip" {
  domain     = "vpc"
  depends_on = [aws_internet_gateway.igw]
}

resource "aws_nat_gateway" "nat" {
  allocation_id = aws_eip.nat_eip.id
  subnet_id     = aws_subnet.public[0].id

  tags = {
    Name        = "integration-nat-gateway"
    Environment = var.environment
  }
}

# Route Tables
resource "aws_route_table" "public" {
  vpc_id = aws_vpc.integration_vpc.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.igw
  }

  tags = {
    Name        = "integration-public-rt"
    Environment = var.environment
  }
}

resource "aws_route_table" "private" {
  vpc_id = aws_vpc.integration_vpc.id

  route {
    cidr_block     = "0.0.0.0/0"
    nat_gateway_id = aws_nat_gateway.nat.id
  }

  tags = {
    Name        = "integration-private-rt"
    Environment = var.environment
  }
}

resource "aws_route_table_association" "public" {
  count          = 2
  subnet_id      = aws_subnet.public[count.index].id
  route_table_id = aws_route_table.public.id
}

resource "aws_route_table_association" "private" {
  count          = 2
  subnet_id      = aws_subnet.private[count.index].id
  route_table_id = aws_route_table.private.id
}

# ==============================================================================
# 2. SECURITY GROUPS (Firewalls)
# ==============================================================================

resource "aws_security_group" "alb_sg" {
  name        = "integration-alb-sg"
  description = "Controls public inbound access to ALB"
  vpc_id      = aws_vpc.integration_vpc.id

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_security_group" "ecs_sg" {
  name        = "integration-ecs-sg"
  description = "Restricts inbound traffic to ALB target group"
  vpc_id      = aws_vpc.integration_vpc.id

  ingress {
    from_port       = 8001
    to_port         = 8001
    protocol        = "tcp"
    security_groups = [aws_security_group.alb_sg.id]
  }

  # Outbound access to download packages/poll legacy APIs via NAT
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_security_group" "db_sg" {
  name        = "integration-db-sg"
  description = "Restricts database inbound traffic to ECS security group only"
  vpc_id      = aws_vpc.integration_vpc.id

  ingress {
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [aws_security_group.ecs_sg.id]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# ==============================================================================
# 3. DATABASE (RDS PostgreSQL, Multi-AZ)
# ==============================================================================

resource "aws_db_subnet_group" "db_subnet_group" {
  name       = "integration-db-subnet-group"
  subnet_ids = aws_subnet.private[*].id

  tags = {
    Name = "integration-db-subnet-group"
  }
}

resource "aws_db_instance" "integration_postgres" {
  identifier             = "integration-postgres-db"
  allocated_storage      = 20
  engine                 = "postgres"
  engine_version         = "15.4"
  instance_class         = var.db_instance_class
  db_name                = var.db_name
  username               = var.db_username
  password               = var.db_password
  db_subnet_group_name   = aws_db_subnet_group.db_subnet_group.name
  vpc_security_group_ids = [aws_security_group.db_sg.id]
  skip_final_snapshot    = true
  multi_az               = var.environment == "production" ? true : false

  tags = {
    Name        = "integration-postgres-instance"
    Environment = var.environment
  }
}

# ==============================================================================
# 4. SECRETS MANAGEMENT (AWS Secrets Manager)
# ==============================================================================

resource "aws_secretsmanager_secret" "integration_secrets" {
  name                    = "integration-platform-env-secrets"
  recovery_window_in_days = 0
}

resource "aws_secretsmanager_secret_version" "integration_secrets_val" {
  secret_id = aws_secretsmanager_secret.integration_secrets.id
  secret_string = jsonencode({
    DB_HOST                 = aws_db_instance.integration_postgres.address
    DB_PORT                 = "5432"
    DB_NAME                 = var.db_name
    DB_USER                 = var.db_username
    DB_PASSWORD             = var.db_password
    REST_SOURCE_API_KEY     = var.rest_api_key
    XML_SOURCE_USERNAME     = var.xml_username
    XML_SOURCE_PASSWORD     = var.xml_password
    WEBHOOK_SIGNATURE_KEY   = var.webhook_secret
  })
}

# ==============================================================================
# 5. CONTAINER COMPUTE (ECS Cluster, Task Def, Service)
# ==============================================================================

resource "aws_ecs_cluster" "integration_cluster" {
  name = "integration-platform-cluster"
}

# IAM Role for ECS Execution (Pulling images, fetching secrets)
resource "aws_iam_role" "ecs_execution_role" {
  name = "integration-ecs-execution-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action    = "sts:AssumeRole"
        Effect    = "Allow"
        Principal = { Service = "ecs-tasks.amazonaws.com" }
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "ecs_execution_policy" {
  role       = aws_iam_role.ecs_execution_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

resource "aws_iam_role_policy" "secrets_access_policy" {
  name = "ecs-secrets-manager-access"
  role = aws_iam_role.ecs_execution_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect   = "Allow"
        Action   = ["secretsmanager:GetSecretValue"]
        Resource = [aws_secretsmanager_secret.integration_secrets.arn]
      }
    ]
  })
}

# IAM Role for ECS Task itself (Writing records to database, etc.)
resource "aws_iam_role" "ecs_task_role" {
  name = "integration-ecs-task-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action    = "sts:AssumeRole"
        Effect    = "Allow"
        Principal = { Service = "ecs-tasks.amazonaws.com" }
      }
    ]
  })
}

resource "aws_ecs_task_definition" "integration_task" {
  family                   = "integration-service-task"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = "256"
  memory                   = "512"
  execution_role_arn       = aws_iam_role.ecs_execution_role.arn
  task_role_arn            = aws_iam_role.ecs_task_role.arn

  container_definitions = jsonencode([
    {
      name      = "integration-app"
      image     = "nginx:alpine" # Placeholder image, CI/CD replaces with build artifact
      essential = true
      portMappings = [
        {
          containerPort = 8001
          hostPort      = 8001
        }
      ]
      secrets = [
        { name = "DB_HOST", valueFrom = "${aws_secretsmanager_secret.integration_secrets.arn}:DB_HOST::" },
        { name = "DB_PORT", valueFrom = "${aws_secretsmanager_secret.integration_secrets.arn}:DB_PORT::" },
        { name = "DB_NAME", valueFrom = "${aws_secretsmanager_secret.integration_secrets.arn}:DB_NAME::" },
        { name = "DB_USER", valueFrom = "${aws_secretsmanager_secret.integration_secrets.arn}:DB_USER::" },
        { name = "DB_PASSWORD", valueFrom = "${aws_secretsmanager_secret.integration_secrets.arn}:DB_PASSWORD::" },
        { name = "REST_SOURCE_API_KEY", valueFrom = "${aws_secretsmanager_secret.integration_secrets.arn}:REST_SOURCE_API_KEY::" },
        { name = "XML_SOURCE_USERNAME", valueFrom = "${aws_secretsmanager_secret.integration_secrets.arn}:XML_SOURCE_USERNAME::" },
        { name = "XML_SOURCE_PASSWORD", valueFrom = "${aws_secretsmanager_secret.integration_secrets.arn}:XML_SOURCE_PASSWORD::" },
        { name = "WEBHOOK_SIGNATURE_KEY", valueFrom = "${aws_secretsmanager_secret.integration_secrets.arn}:WEBHOOK_SIGNATURE_KEY::" }
      ]
      environment = [
        { name = "ENV", value = var.environment }
      ]
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = "/ecs/integration-app"
          "awslogs-region"        = var.aws_region
          "awslogs-stream-prefix" = "ecs"
          "awslogs-create-group"  = "true"
        }
      }
    }
  ])
}

resource "aws_ecs_service" "integration_service" {
  name            = "integration-platform-service"
  cluster         = aws_ecs_cluster.integration_cluster.id
  task_definition = aws_ecs_task_definition.integration_task.arn
  desired_count   = 2
  launch_type     = "FARGATE"

  network_configuration {
    subnets          = aws_subnet.private[*].id
    security_groups  = [aws_security_group.ecs_sg.id]
    assign_public_ip = false
  }

  load_balancer {
    target_group_arn = aws_lb_target_group.integration_tg.arn
    container_name   = "integration-app"
    container_port   = 8001
  }

  depends_on = [aws_lb_listener.http_listener]
}

# ==============================================================================
# 6. ROUTING LAYER (Application Load Balancer)
# ==============================================================================

resource "aws_lb" "integration_alb" {
  name               = "integration-platform-alb"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.alb_sg.id]
  subnets            = aws_subnet.public[*].id

  tags = {
    Name        = "integration-alb"
    Environment = var.environment
  }
}

resource "aws_lb_target_group" "integration_tg" {
  name        = "integration-app-tg"
  port        = 8001
  protocol    = "HTTP"
  vpc_id      = aws_vpc.integration_vpc.id
  target_type = "ip"

  health_check {
    path                = "/api/sources" # Check registry endpoint for health pings
    protocol            = "HTTP"
    matcher             = "200"
    interval            = 30
    timeout             = 5
    healthy_threshold   = 3
    unhealthy_threshold = 3
  }
}

resource "aws_lb_listener" "http_listener" {
  load_balancer_arn = aws_lb.integration_alb.arn
  port              = "80"
  protocol          = "HTTP"

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.integration_tg.arn
  }
}
