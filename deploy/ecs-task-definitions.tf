# ECS Task Definitions

# API Service Task Definition
resource "aws_ecs_task_definition" "api" {
  family                   = "${var.project_name}-api"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = 1024
  memory                   = 2048
  execution_role_arn       = aws_iam_role.ecs_task_execution_role.arn
  task_role_arn           = aws_iam_role.ecs_task_role.arn

  container_definitions = jsonencode([
    {
      name  = "api"
      image = "${aws_ecr_repository.app.repository_url}:latest"
      
      portMappings = [
        {
          containerPort = 8000
          protocol      = "tcp"
        }
      ]

      environment = [
        {
          name  = "NODE_ENV"
          value = "production"
        },
        {
          name  = "DATABASE_URL"
          value = "postgresql://genx_user:${random_password.db_password.result}@${aws_db_instance.postgres.endpoint}:5432/genx_trading"
        },
        {
          name  = "MONGODB_URL"
          value = "mongodb://admin:${random_password.mongo_password.result}@${aws_docdb_cluster.mongo.endpoint}:27017/genx_trading?ssl=true&replicaSet=rs0&readPreference=secondaryPreferred&retryWrites=false"
        },
        {
          name  = "REDIS_URL"
          value = "rediss://:${random_password.redis_password.result}@${aws_elasticache_replication_group.redis.configuration_endpoint_address}:6379"
        },
        {
          name  = "SECRET_KEY"
          value = random_password.secret_key.result
        },
        {
          name  = "LOG_LEVEL"
          value = "INFO"
        }
      ]

      secrets = [
        {
          name      = "BYBIT_API_KEY"
          valueFrom = "${aws_secretsmanager_secret.app_secrets.arn}:BYBIT_API_KEY::"
        },
        {
          name      = "BYBIT_API_SECRET"
          valueFrom = "${aws_secretsmanager_secret.app_secrets.arn}:BYBIT_API_SECRET::"
        }
      ]

      logConfiguration = {
        logDriver = "awslogs"
        options = {
          awslogs-group         = aws_cloudwatch_log_group.ecs.name
          awslogs-region        = var.aws_region
          awslogs-stream-prefix = "api"
        }
      }

      healthCheck = {
        command     = ["CMD-SHELL", "curl -f http://localhost:8000/health || exit 1"]
        interval    = 30
        timeout     = 5
        retries     = 3
        startPeriod = 60
      }

      essential = true
    }
  ])

  tags = {
    Name        = "${var.project_name}-api-task"
    Environment = var.environment
  }
}

# Discord Bot Task Definition
resource "aws_ecs_task_definition" "discord_bot" {
  family                   = "${var.project_name}-discord-bot"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = 256
  memory                   = 512
  execution_role_arn       = aws_iam_role.ecs_task_execution_role.arn
  task_role_arn           = aws_iam_role.ecs_task_role.arn

  container_definitions = jsonencode([
    {
      name  = "discord-bot"
      image = "${aws_ecr_repository.app.repository_url}:latest"
      
      command = ["python", "services/discord_bot.py"]

      environment = [
        {
          name  = "DATABASE_URL"
          value = "postgresql://genx_user:${random_password.db_password.result}@${aws_db_instance.postgres.endpoint}:5432/genx_trading"
        },
        {
          name  = "API_URL"
          value = "http://${aws_lb.main.dns_name}"
        }
      ]

      secrets = [
        {
          name      = "DISCORD_TOKEN"
          valueFrom = "${aws_secretsmanager_secret.app_secrets.arn}:DISCORD_TOKEN::"
        }
      ]

      logConfiguration = {
        logDriver = "awslogs"
        options = {
          awslogs-group         = aws_cloudwatch_log_group.ecs.name
          awslogs-region        = var.aws_region
          awslogs-stream-prefix = "discord-bot"
        }
      }

      essential = true
    }
  ])

  tags = {
    Name        = "${var.project_name}-discord-bot-task"
    Environment = var.environment
  }
}

# Telegram Bot Task Definition
resource "aws_ecs_task_definition" "telegram_bot" {
  family                   = "${var.project_name}-telegram-bot"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = 256
  memory                   = 512
  execution_role_arn       = aws_iam_role.ecs_task_execution_role.arn
  task_role_arn           = aws_iam_role.ecs_task_role.arn

  container_definitions = jsonencode([
    {
      name  = "telegram-bot"
      image = "${aws_ecr_repository.app.repository_url}:latest"
      
      command = ["python", "services/telegram_bot.py"]

      environment = [
        {
          name  = "DATABASE_URL"
          value = "postgresql://genx_user:${random_password.db_password.result}@${aws_db_instance.postgres.endpoint}:5432/genx_trading"
        },
        {
          name  = "API_URL"
          value = "http://${aws_lb.main.dns_name}"
        }
      ]

      secrets = [
        {
          name      = "TELEGRAM_TOKEN"
          valueFrom = "${aws_secretsmanager_secret.app_secrets.arn}:TELEGRAM_TOKEN::"
        }
      ]

      logConfiguration = {
        logDriver = "awslogs"
        options = {
          awslogs-group         = aws_cloudwatch_log_group.ecs.name
          awslogs-region        = var.aws_region
          awslogs-stream-prefix = "telegram-bot"
        }
      }

      essential = true
    }
  ])

  tags = {
    Name        = "${var.project_name}-telegram-bot-task"
    Environment = var.environment
  }
}

# WebSocket Feed Task Definition
resource "aws_ecs_task_definition" "websocket_feed" {
  family                   = "${var.project_name}-websocket-feed"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = 512
  memory                   = 1024
  execution_role_arn       = aws_iam_role.ecs_task_execution_role.arn
  task_role_arn           = aws_iam_role.ecs_task_role.arn

  container_definitions = jsonencode([
    {
      name  = "websocket-feed"
      image = "${aws_ecr_repository.app.repository_url}:latest"
      
      command = ["python", "services/websocket_feed.py"]

      environment = [
        {
          name  = "DATABASE_URL"
          value = "postgresql://genx_user:${random_password.db_password.result}@${aws_db_instance.postgres.endpoint}:5432/genx_trading"
        },
        {
          name  = "REDIS_URL"
          value = "rediss://:${random_password.redis_password.result}@${aws_elasticache_replication_group.redis.configuration_endpoint_address}:6379"
        }
      ]

      secrets = [
        {
          name      = "BYBIT_API_KEY"
          valueFrom = "${aws_secretsmanager_secret.app_secrets.arn}:BYBIT_API_KEY::"
        },
        {
          name      = "BYBIT_API_SECRET"
          valueFrom = "${aws_secretsmanager_secret.app_secrets.arn}:BYBIT_API_SECRET::"
        }
      ]

      logConfiguration = {
        logDriver = "awslogs"
        options = {
          awslogs-group         = aws_cloudwatch_log_group.ecs.name
          awslogs-region        = var.aws_region
          awslogs-stream-prefix = "websocket-feed"
        }
      }

      essential = true
    }
  ])

  tags = {
    Name        = "${var.project_name}-websocket-feed-task"
    Environment = var.environment
  }
}

# Scheduler Task Definition
resource "aws_ecs_task_definition" "scheduler" {
  family                   = "${var.project_name}-scheduler"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = 256
  memory                   = 512
  execution_role_arn       = aws_iam_role.ecs_task_execution_role.arn
  task_role_arn           = aws_iam_role.ecs_task_role.arn

  container_definitions = jsonencode([
    {
      name  = "scheduler"
      image = "${aws_ecr_repository.app.repository_url}:latest"
      
      command = ["python", "services/scheduler.py"]

      environment = [
        {
          name  = "DATABASE_URL"
          value = "postgresql://genx_user:${random_password.db_password.result}@${aws_db_instance.postgres.endpoint}:5432/genx_trading"
        },
        {
          name  = "API_URL"
          value = "http://${aws_lb.main.dns_name}"
        }
      ]

      logConfiguration = {
        logDriver = "awslogs"
        options = {
          awslogs-group         = aws_cloudwatch_log_group.ecs.name
          awslogs-region        = var.aws_region
          awslogs-stream-prefix = "scheduler"
        }
      }

      essential = true
    }
  ])

  tags = {
    Name        = "${var.project_name}-scheduler-task"
    Environment = var.environment
  }
}

# AI Trainer Task Definition
resource "aws_ecs_task_definition" "ai_trainer" {
  family                   = "${var.project_name}-ai-trainer"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = 1024
  memory                   = 2048
  execution_role_arn       = aws_iam_role.ecs_task_execution_role.arn
  task_role_arn           = aws_iam_role.ecs_task_role.arn

  container_definitions = jsonencode([
    {
      name  = "ai-trainer"
      image = "${aws_ecr_repository.app.repository_url}:latest"
      
      command = ["python", "services/ai_trainer.py"]

      environment = [
        {
          name  = "DATABASE_URL"
          value = "postgresql://genx_user:${random_password.db_password.result}@${aws_db_instance.postgres.endpoint}:5432/genx_trading"
        },
        {
          name  = "MONGODB_URL"
          value = "mongodb://admin:${random_password.mongo_password.result}@${aws_docdb_cluster.mongo.endpoint}:27017/genx_trading?ssl=true&replicaSet=rs0&readPreference=secondaryPreferred&retryWrites=false"
        }
      ]

      logConfiguration = {
        logDriver = "awslogs"
        options = {
          awslogs-group         = aws_cloudwatch_log_group.ecs.name
          awslogs-region        = var.aws_region
          awslogs-stream-prefix = "ai-trainer"
        }
      }

      essential = true
    }
  ])

  tags = {
    Name        = "${var.project_name}-ai-trainer-task"
    Environment = var.environment
  }
}

# ECS Services
resource "aws_ecs_service" "api" {
  name            = "${var.project_name}-api"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.api.arn
  desired_count   = 2
  launch_type     = "FARGATE"

  network_configuration {
    subnets          = aws_subnet.private[*].id
    security_groups  = [aws_security_group.ecs.id]
    assign_public_ip = false
  }

  load_balancer {
    target_group_arn = aws_lb_target_group.api.arn
    container_name   = "api"
    container_port   = 8000
  }

  depends_on = [
    aws_lb_listener.web,
    aws_iam_role_policy_attachment.ecs_task_execution_role_policy
  ]

  tags = {
    Name        = "${var.project_name}-api-service"
    Environment = var.environment
  }
}

resource "aws_ecs_service" "discord_bot" {
  name            = "${var.project_name}-discord-bot"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.discord_bot.arn
  desired_count   = 1
  launch_type     = "FARGATE"

  network_configuration {
    subnets          = aws_subnet.private[*].id
    security_groups  = [aws_security_group.ecs.id]
    assign_public_ip = false
  }

  depends_on = [
    aws_iam_role_policy_attachment.ecs_task_execution_role_policy
  ]

  tags = {
    Name        = "${var.project_name}-discord-bot-service"
    Environment = var.environment
  }
}

resource "aws_ecs_service" "telegram_bot" {
  name            = "${var.project_name}-telegram-bot"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.telegram_bot.arn
  desired_count   = 1
  launch_type     = "FARGATE"

  network_configuration {
    subnets          = aws_subnet.private[*].id
    security_groups  = [aws_security_group.ecs.id]
    assign_public_ip = false
  }

  depends_on = [
    aws_iam_role_policy_attachment.ecs_task_execution_role_policy
  ]

  tags = {
    Name        = "${var.project_name}-telegram-bot-service"
    Environment = var.environment
  }
}

resource "aws_ecs_service" "websocket_feed" {
  name            = "${var.project_name}-websocket-feed"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.websocket_feed.arn
  desired_count   = 1
  launch_type     = "FARGATE"

  network_configuration {
    subnets          = aws_subnet.private[*].id
    security_groups  = [aws_security_group.ecs.id]
    assign_public_ip = false
  }

  depends_on = [
    aws_iam_role_policy_attachment.ecs_task_execution_role_policy
  ]

  tags = {
    Name        = "${var.project_name}-websocket-feed-service"
    Environment = var.environment
  }
}

resource "aws_ecs_service" "scheduler" {
  name            = "${var.project_name}-scheduler"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.scheduler.arn
  desired_count   = 1
  launch_type     = "FARGATE"

  network_configuration {
    subnets          = aws_subnet.private[*].id
    security_groups  = [aws_security_group.ecs.id]
    assign_public_ip = false
  }

  depends_on = [
    aws_iam_role_policy_attachment.ecs_task_execution_role_policy
  ]

  tags = {
    Name        = "${var.project_name}-scheduler-service"
    Environment = var.environment
  }
}

resource "aws_ecs_service" "ai_trainer" {
  name            = "${var.project_name}-ai-trainer"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.ai_trainer.arn
  desired_count   = 1
  launch_type     = "FARGATE"

  network_configuration {
    subnets          = aws_subnet.private[*].id
    security_groups  = [aws_security_group.ecs.id]
    assign_public_ip = false
  }

  depends_on = [
    aws_iam_role_policy_attachment.ecs_task_execution_role_policy
  ]

  tags = {
    Name        = "${var.project_name}-ai-trainer-service"
    Environment = var.environment
  }
}