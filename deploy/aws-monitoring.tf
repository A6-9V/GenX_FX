# CloudWatch Monitoring and Alarms

# SNS Topic for alerts
resource "aws_sns_topic" "alerts" {
  name = "${var.project_name}-alerts"

  tags = {
    Name        = "${var.project_name}-alerts"
    Environment = var.environment
  }
}

# SNS Topic Subscription (email)
resource "aws_sns_topic_subscription" "email_alerts" {
  count     = var.alert_email != "" ? 1 : 0
  topic_arn = aws_sns_topic.alerts.arn
  protocol  = "email"
  endpoint  = var.alert_email
}

# CloudWatch Alarms for ECS Services
resource "aws_cloudwatch_metric_alarm" "ecs_cpu_high" {
  for_each = toset(["api", "discord-bot", "telegram-bot", "websocket-feed", "scheduler", "ai-trainer"])

  alarm_name          = "${var.project_name}-${each.key}-cpu-high"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "CPUUtilization"
  namespace           = "AWS/ECS"
  period              = "120"
  statistic           = "Average"
  threshold           = "80"
  alarm_description   = "This metric monitors ECS ${each.key} CPU utilization"
  alarm_actions       = [aws_sns_topic.alerts.arn]

  dimensions = {
    ServiceName = "${var.project_name}-${each.key}"
    ClusterName = aws_ecs_cluster.main.name
  }

  tags = {
    Name        = "${var.project_name}-${each.key}-cpu-alarm"
    Environment = var.environment
  }
}

resource "aws_cloudwatch_metric_alarm" "ecs_memory_high" {
  for_each = toset(["api", "discord-bot", "telegram-bot", "websocket-feed", "scheduler", "ai-trainer"])

  alarm_name          = "${var.project_name}-${each.key}-memory-high"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "MemoryUtilization"
  namespace           = "AWS/ECS"
  period              = "120"
  statistic           = "Average"
  threshold           = "85"
  alarm_description   = "This metric monitors ECS ${each.key} memory utilization"
  alarm_actions       = [aws_sns_topic.alerts.arn]

  dimensions = {
    ServiceName = "${var.project_name}-${each.key}"
    ClusterName = aws_ecs_cluster.main.name
  }

  tags = {
    Name        = "${var.project_name}-${each.key}-memory-alarm"
    Environment = var.environment
  }
}

# RDS Alarms
resource "aws_cloudwatch_metric_alarm" "rds_cpu_high" {
  alarm_name          = "${var.project_name}-rds-cpu-high"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "CPUUtilization"
  namespace           = "AWS/RDS"
  period              = "120"
  statistic           = "Average"
  threshold           = "80"
  alarm_description   = "This metric monitors RDS CPU utilization"
  alarm_actions       = [aws_sns_topic.alerts.arn]

  dimensions = {
    DBInstanceIdentifier = aws_db_instance.postgres.id
  }

  tags = {
    Name        = "${var.project_name}-rds-cpu-alarm"
    Environment = var.environment
  }
}

resource "aws_cloudwatch_metric_alarm" "rds_connections_high" {
  alarm_name          = "${var.project_name}-rds-connections-high"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "DatabaseConnections"
  namespace           = "AWS/RDS"
  period              = "120"
  statistic           = "Average"
  threshold           = "80"
  alarm_description   = "This metric monitors RDS connection count"
  alarm_actions       = [aws_sns_topic.alerts.arn]

  dimensions = {
    DBInstanceIdentifier = aws_db_instance.postgres.id
  }

  tags = {
    Name        = "${var.project_name}-rds-connections-alarm"
    Environment = var.environment
  }
}

resource "aws_cloudwatch_metric_alarm" "rds_free_storage_low" {
  alarm_name          = "${var.project_name}-rds-storage-low"
  comparison_operator = "LessThanThreshold"
  evaluation_periods  = "1"
  metric_name         = "FreeStorageSpace"
  namespace           = "AWS/RDS"
  period              = "300"
  statistic           = "Average"
  threshold           = "10737418240" # 10GB in bytes
  alarm_description   = "This metric monitors RDS free storage space"
  alarm_actions       = [aws_sns_topic.alerts.arn]

  dimensions = {
    DBInstanceIdentifier = aws_db_instance.postgres.id
  }

  tags = {
    Name        = "${var.project_name}-rds-storage-alarm"
    Environment = var.environment
  }
}

# ElastiCache Alarms
resource "aws_cloudwatch_metric_alarm" "redis_cpu_high" {
  alarm_name          = "${var.project_name}-redis-cpu-high"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "CPUUtilization"
  namespace           = "AWS/ElastiCache"
  period              = "120"
  statistic           = "Average"
  threshold           = "80"
  alarm_description   = "This metric monitors Redis CPU utilization"
  alarm_actions       = [aws_sns_topic.alerts.arn]

  dimensions = {
    CacheClusterId = "${var.project_name}-redis-001"
  }

  tags = {
    Name        = "${var.project_name}-redis-cpu-alarm"
    Environment = var.environment
  }
}

resource "aws_cloudwatch_metric_alarm" "redis_memory_high" {
  alarm_name          = "${var.project_name}-redis-memory-high"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "DatabaseMemoryUsagePercentage"
  namespace           = "AWS/ElastiCache"
  period              = "120"
  statistic           = "Average"
  threshold           = "85"
  alarm_description   = "This metric monitors Redis memory usage"
  alarm_actions       = [aws_sns_topic.alerts.arn]

  dimensions = {
    CacheClusterId = "${var.project_name}-redis-001"
  }

  tags = {
    Name        = "${var.project_name}-redis-memory-alarm"
    Environment = var.environment
  }
}

# ALB Alarms
resource "aws_cloudwatch_metric_alarm" "alb_response_time_high" {
  alarm_name          = "${var.project_name}-alb-response-time-high"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "TargetResponseTime"
  namespace           = "AWS/ApplicationELB"
  period              = "120"
  statistic           = "Average"
  threshold           = "1"
  alarm_description   = "This metric monitors ALB response time"
  alarm_actions       = [aws_sns_topic.alerts.arn]

  dimensions = {
    LoadBalancer = aws_lb.main.arn_suffix
  }

  tags = {
    Name        = "${var.project_name}-alb-response-time-alarm"
    Environment = var.environment
  }
}

resource "aws_cloudwatch_metric_alarm" "alb_5xx_errors_high" {
  alarm_name          = "${var.project_name}-alb-5xx-errors-high"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "HTTPCode_ELB_5XX_Count"
  namespace           = "AWS/ApplicationELB"
  period              = "120"
  statistic           = "Sum"
  threshold           = "10"
  alarm_description   = "This metric monitors ALB 5XX errors"
  alarm_actions       = [aws_sns_topic.alerts.arn]

  dimensions = {
    LoadBalancer = aws_lb.main.arn_suffix
  }

  tags = {
    Name        = "${var.project_name}-alb-5xx-alarm"
    Environment = var.environment
  }
}

# CloudWatch Dashboard
resource "aws_cloudwatch_dashboard" "main" {
  dashboard_name = "${var.project_name}-dashboard"

  dashboard_body = jsonencode({
    widgets = [
      {
        type   = "metric"
        x      = 0
        y      = 0
        width  = 12
        height = 6

        properties = {
          metrics = [
            ["AWS/ECS", "CPUUtilization", "ServiceName", "${var.project_name}-api", "ClusterName", aws_ecs_cluster.main.name],
            [".", "MemoryUtilization", ".", ".", ".", "."],
            ["AWS/ApplicationELB", "RequestCount", "LoadBalancer", aws_lb.main.arn_suffix],
            [".", "TargetResponseTime", ".", "."]
          ]
          view    = "timeSeries"
          stacked = false
          region  = var.aws_region
          title   = "API Service Metrics"
          period  = 300
        }
      },
      {
        type   = "metric"
        x      = 12
        y      = 0
        width  = 12
        height = 6

        properties = {
          metrics = [
            ["AWS/RDS", "CPUUtilization", "DBInstanceIdentifier", aws_db_instance.postgres.id],
            [".", "DatabaseConnections", ".", "."],
            [".", "FreeStorageSpace", ".", "."]
          ]
          view    = "timeSeries"
          stacked = false
          region  = var.aws_region
          title   = "RDS Metrics"
          period  = 300
        }
      },
      {
        type   = "metric"
        x      = 0
        y      = 6
        width  = 12
        height = 6

        properties = {
          metrics = [
            ["AWS/ElastiCache", "CPUUtilization", "CacheClusterId", "${var.project_name}-redis-001"],
            [".", "DatabaseMemoryUsagePercentage", ".", "."],
            [".", "CurrConnections", ".", "."]
          ]
          view    = "timeSeries"
          stacked = false
          region  = var.aws_region
          title   = "Redis Metrics"
          period  = 300
        }
      },
      {
        type   = "log"
        x      = 12
        y      = 6
        width  = 12
        height = 6

        properties = {
          query   = "SOURCE '${aws_cloudwatch_log_group.ecs.name}'\n| fields @timestamp, @message\n| filter @message like /ERROR/\n| sort @timestamp desc\n| limit 20"
          region  = var.aws_region
          title   = "Recent Errors"
          view    = "table"
        }
      }
    ]
  })

  tags = {
    Name        = "${var.project_name}-dashboard"
    Environment = var.environment
  }
}

# Custom Metrics for Trading Platform
resource "aws_cloudwatch_log_metric_filter" "trading_signals" {
  name           = "${var.project_name}-trading-signals"
  log_group_name = aws_cloudwatch_log_group.ecs.name
  pattern        = "[timestamp, request_id=\"*\", level=\"INFO\", message=\"Trading signal generated*\"]"

  metric_transformation {
    name      = "TradingSignals"
    namespace = "GenX/Trading"
    value     = "1"
  }
}

resource "aws_cloudwatch_log_metric_filter" "api_errors" {
  name           = "${var.project_name}-api-errors"
  log_group_name = aws_cloudwatch_log_group.ecs.name
  pattern        = "[timestamp, request_id=\"*\", level=\"ERROR\", ...]"

  metric_transformation {
    name      = "APIErrors"
    namespace = "GenX/API"
    value     = "1"
  }
}

resource "aws_cloudwatch_log_metric_filter" "trade_executions" {
  name           = "${var.project_name}-trade-executions"
  log_group_name = aws_cloudwatch_log_group.ecs.name
  pattern        = "[timestamp, request_id=\"*\", level=\"INFO\", message=\"Trade executed*\"]"

  metric_transformation {
    name      = "TradeExecutions"
    namespace = "GenX/Trading"
    value     = "1"
  }
}

# Alarms for custom metrics
resource "aws_cloudwatch_metric_alarm" "high_api_errors" {
  alarm_name          = "${var.project_name}-high-api-errors"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "APIErrors"
  namespace           = "GenX/API"
  period              = "300"
  statistic           = "Sum"
  threshold           = "10"
  alarm_description   = "This metric monitors API errors"
  alarm_actions       = [aws_sns_topic.alerts.arn]

  tags = {
    Name        = "${var.project_name}-api-errors-alarm"
    Environment = var.environment
  }
}

# Auto Scaling for ECS Services
resource "aws_appautoscaling_target" "api" {
  max_capacity       = 10
  min_capacity       = 2
  resource_id        = "service/${aws_ecs_cluster.main.name}/${aws_ecs_service.api.name}"
  scalable_dimension = "ecs:service:DesiredCount"
  service_namespace  = "ecs"

  tags = {
    Name        = "${var.project_name}-api-autoscaling"
    Environment = var.environment
  }
}

resource "aws_appautoscaling_policy" "api_scale_up" {
  name               = "${var.project_name}-api-scale-up"
  policy_type        = "TargetTrackingScaling"
  resource_id        = aws_appautoscaling_target.api.resource_id
  scalable_dimension = aws_appautoscaling_target.api.scalable_dimension
  service_namespace  = aws_appautoscaling_target.api.service_namespace

  target_tracking_scaling_policy_configuration {
    predefined_metric_specification {
      predefined_metric_type = "ECSServiceAverageCPUUtilization"
    }
    target_value = 70.0
  }
}

resource "aws_appautoscaling_policy" "api_scale_memory" {
  name               = "${var.project_name}-api-scale-memory"
  policy_type        = "TargetTrackingScaling"
  resource_id        = aws_appautoscaling_target.api.resource_id
  scalable_dimension = aws_appautoscaling_target.api.scalable_dimension
  service_namespace  = aws_appautoscaling_target.api.service_namespace

  target_tracking_scaling_policy_configuration {
    predefined_metric_specification {
      predefined_metric_type = "ECSServiceAverageMemoryUtilization"
    }
    target_value = 80.0
  }
}

# Variables for monitoring
variable "alert_email" {
  description = "Email address for alerts"
  type        = string
  default     = ""
}

# Outputs for monitoring
output "sns_topic_arn" {
  value = aws_sns_topic.alerts.arn
}

output "dashboard_url" {
  value = "https://${var.aws_region}.console.aws.amazon.com/cloudwatch/home?region=${var.aws_region}#dashboards:name=${aws_cloudwatch_dashboard.main.dashboard_name}"
}