# Performance requirements and configurations for the AlertMind AI backend

# This file outlines guidelines for handling high alert ingestion rates and response times.

HIGH_ALERT_INGESTION_RATE = 1000  # Maximum alerts per second
MAX_RESPONSE_TIME = 200  # Maximum response time in milliseconds

# Performance tuning parameters
DATABASE_CONNECTION_POOL_SIZE = 20  # Size of the database connection pool
DATABASE_CONNECTION_TIMEOUT = 30  # Timeout for database connections in seconds

# Caching configurations
CACHE_ENABLED = True  # Enable caching for frequently accessed data
CACHE_EXPIRATION_TIME = 300  # Cache expiration time in seconds

# Load testing configurations
LOAD_TEST_USERS = 100  # Number of concurrent users for load testing
LOAD_TEST_DURATION = 60  # Duration of load test in seconds

# Monitoring and logging configurations
ENABLE_PERFORMANCE_MONITORING = True  # Enable performance monitoring
LOG_LEVEL = "INFO"  # Logging level for performance-related logs

# Additional performance-related configurations can be added as needed.