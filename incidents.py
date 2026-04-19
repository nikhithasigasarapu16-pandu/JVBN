# incidents.py
# Fake but realistic incident data for your demo

PAST_INCIDENTS = [
    {
        "id": "INC-001",
        "title": "Database connection timeout",
        "error": "ERROR: Connection to postgres://prod-db:5432 timed out after 30s",
        "cause": "Max connection pool limit reached (100/100 connections active)",
        "resolution": "Restarted connection pool, increased max_connections to 200 in postgresql.conf",
        "time_to_resolve": "14 minutes",
        "severity": "critical"
    },
    {
        "id": "INC-002",
        "title": "API gateway returning 502 errors",
        "error": "502 Bad Gateway - upstream server unreachable",
        "cause": "Memory leak in Node.js service caused OOM crash",
        "resolution": "Restarted the Node.js pods, deployed memory leak fix in v2.3.1",
        "time_to_resolve": "22 minutes",
        "severity": "high"
    },
    {
        "id": "INC-003",
        "title": "CPU spike to 100% on app servers",
        "error": "System load average: 32.5, CPU: 100% for 8 minutes",
        "cause": "Unoptimized SQL query running full table scan on orders table (12M rows)",
        "resolution": "Killed the query, added composite index on (user_id, created_at)",
        "time_to_resolve": "9 minutes",
        "severity": "high"
    },
    {
        "id": "INC-004",
        "title": "Redis cache unavailable",
        "error": "RedisConnectionError: Could not connect to Redis at cache-01:6379",
        "cause": "Redis ran out of memory, eviction policy set to noeviction caused it to reject writes",
        "resolution": "Flushed stale keys, changed eviction policy to allkeys-lru, added 4GB RAM",
        "time_to_resolve": "18 minutes",
        "severity": "critical"
    },
    {
        "id": "INC-005",
        "title": "SSL certificate expired",
        "error": "SSL_ERROR_RX_RECORD_TOO_LONG - certificate expired Jan 15 2024",
        "cause": "Auto-renewal cron job failed silently 30 days prior",
        "resolution": "Manually renewed cert via certbot, fixed cron job and added expiry alerting",
        "time_to_resolve": "31 minutes",
        "severity": "critical"
    },
    {
        "id": "INC-006",
        "title": "Disk space full on logging server",
        "error": "No space left on device - /var/log partition at 100%",
        "cause": "Log rotation misconfigured, debug logs accumulating for 3 weeks",
        "resolution": "Deleted old logs, fixed logrotate config, set max log retention to 7 days",
        "time_to_resolve": "11 minutes",
        "severity": "medium"
    }
]