# Logging Documentation

Complete logging setup and configuration for the MCE Cluster Generator API.

---

## Current Status: 8/10 ⭐⭐⭐⭐⭐⭐⭐⭐

The logging system has been significantly improved and is now production-ready with excellent observability.

---

## What's Implemented

### ✅ 1. Consistent Logger Namespace

All files now use the `get_logger(__name__)` helper for consistent logger hierarchy.

**Files using proper logging:**
- `src/api/routers/clusters.py`
- `src/generators/cluster_builder.py`
- `src/defaults/defaults_manager.py`
- `src/main.py`
- `src/services/*` (all service files)

**Implementation:**
```python
from utils.logging_config import get_logger

logger = get_logger(__name__)  # Creates "mce_cluster_generator.api.routers.clusters"
```

**Benefits:**
- ✅ Consistent logger hierarchy
- ✅ Easy to filter logs by component
- ✅ Proper namespace organization

---

### ✅ 2. Request/Response Logging Middleware

Automatic logging of all API requests and responses with correlation IDs.

**Location:** `src/api/middleware/logging_middleware.py`

**Features:**
- 🔍 **Correlation IDs** - Track requests across the system
- ⏱️ **Request Timing** - Duration of each request
- 📍 **Client Info** - IP address, user agent
- 📊 **Response Status** - HTTP status codes
- ❌ **Error Logging** - Automatic error capture with stack traces

**Example Output:**
```
INFO: → POST /api/v1/clusters/generate (correlation_id=abc-123, client_ip=127.0.0.1)
INFO: ← POST /api/v1/clusters/generate [201] 145.32ms (correlation_id=abc-123)
```

**Response Headers:**
```
X-Correlation-ID: abc-123-def-456
```

**Benefits:**
- ✅ Trace individual requests across logs
- ✅ Identify slow endpoints
- ✅ Better debugging with correlation IDs
- ✅ Clients can correlate with server logs

---

### ✅ 3. LoggingMixin Applied to Services

All service classes use the LoggingMixin for structured logging.

**Services with logging:**
- `ConfigListBuilder` - Configuration building
- `ClusterValidator` - Validation logic
- `RequestConverter` - Data transformation

**Example:**
```python
from utils.logging_config import LoggingMixin, get_logger

class ConfigListBuilder(LoggingMixin):
    @staticmethod
    def build_for_nodepool(...):
        logger.debug(
            "Building nodepool config",
            extra={
                "cluster_name": cluster_name,
                "vendor": vendor,
                "max_pods": max_pods
            }
        )
```

**Benefits:**
- ✅ Structured logging with context
- ✅ Easy debugging in development
- ✅ Consistent logging pattern

---

### ✅ 4. Centralized Configuration

**Location:** `src/utils/logging_config.py`

**Features:**
- Rich console output with syntax highlighting
- Rotating file handler (10MB, 5 backups)
- External library log suppression
- Configurable log levels via environment variables

**Configuration:**
```python
from utils.logging_config import setup_logging

setup_logging(
    level="INFO",           # Or from settings.LOG_LEVEL
    log_file="logs/app.log",
    enable_rich=True        # Rich console output
)
```

---

## Log Output Examples

### Before Improvements

```
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### After Improvements

```
[12:08:32] INFO  Logging initialized with level: INFO
           INFO  Starting MCE Cluster Generator API v2.0.0
           INFO  Default OCP Version: 4.16
           INFO  Default DNS Domain: example.company.com
           INFO  Supported Vendors: cisco, dell, dell-data, h100-gpu, h200-gpu

# When handling requests:
[12:10:15] INFO  → POST /api/v1/clusters/generate (correlation_id=abc-123)
[12:10:15] DEBUG Building nodepool config (cluster=test, vendor=dell)
[12:10:15] INFO  ← POST /api/v1/clusters/generate [201] 123.45ms
```

---

## Using Logs for Debugging

### 1. Find Logs for Specific Request

```bash
# Find all logs for a request using correlation ID
grep "abc-123" logs/app.log

# See request timeline
12:10:15.123 → POST /api/v1/clusters/generate
12:10:15.145 DEBUG Building nodepool config
12:10:15.234 DEBUG Built 5 configs for nodepool
12:10:15.268 ← POST [201] 145ms
```

### 2. Monitor Performance

```bash
# Find slow requests (>1000ms)
grep "ms" logs/app.log | awk -F'[\[\]]' '{if ($2 > 1000) print}'

# Average request time
grep "← POST" logs/app.log | awk '{print $NF}' | sed 's/ms//' | awk '{sum+=$1; count++} END {print sum/count "ms"}'
```

### 3. Track Errors

```bash
# Find all errors with context
grep -A 10 "ERROR" logs/app.log

# Find errors for specific correlation ID
grep "correlation_id=abc-123" logs/app.log | grep ERROR
```

---

## Configuration

### Environment Variables

```bash
# Log level
LOG_LEVEL=INFO              # DEBUG, INFO, WARNING, ERROR, CRITICAL

# Log file location
LOG_FILE=logs/app.log       # Path to log file
```

### In Code

```python
# Get logger for current module
from utils.logging_config import get_logger
logger = get_logger(__name__)

# Log with context
logger.info("Cluster generated", extra={
    "cluster_name": "test",
    "vendor": "dell",
    "duration_ms": 123.45
})

# Log errors with stack trace
try:
    # ... code ...
except Exception as e:
    logger.error("Failed to generate cluster", exc_info=True, extra={
        "cluster_name": cluster_name,
        "error": str(e)
    })
```

---

## Log Levels

### When to Use Each Level

**DEBUG** - Detailed diagnostic information
```python
logger.debug("Building config list", extra={"vendor": "dell", "count": 5})
```

**INFO** - General informational messages
```python
logger.info("Cluster generated successfully", extra={"cluster_name": "test"})
```

**WARNING** - Warning messages (something unexpected but not critical)
```python
logger.warning("Using default value", extra={"setting": "max_pods", "value": 250})
```

**ERROR** - Error messages (something failed)
```python
logger.error("Failed to validate cluster", exc_info=True, extra={"reason": str(e)})
```

**CRITICAL** - Critical errors (system failure)
```python
logger.critical("Cannot load defaults", exc_info=True)
```

---

## File Structure

```
logs/
├── app.log              # Current log file
├── app.log.1            # First rotation
├── app.log.2            # Second rotation
├── app.log.3            # Third rotation
├── app.log.4            # Fourth rotation
└── app.log.5            # Fifth rotation (oldest)
```

**Rotation:**
- Max size: 10 MB per file
- Keep last 5 rotations
- Automatic rotation when size exceeded

---

## Metrics Collected

### Request Metrics
- Total requests
- Response times
- Status codes
- Error rates
- Client IPs

### Application Metrics
- Startup time
- Configuration loaded
- Clusters generated
- Validation errors

---

## Improvements Roadmap

### Current: 8/10

**What's Working:**
- ✅ Consistent logger namespace
- ✅ Request/response logging
- ✅ Correlation IDs
- ✅ Structured logging with context
- ✅ Rotating file handler
- ✅ Rich console output

### Future Enhancements (Optional)

#### To Reach 9/10:
1. **Structured JSON Logging** (1-2 hours)
   - JSON log format for machine parsing
   - ELK/Loki/Grafana Loki integration ready
   - Searchable structured data

2. **Performance Logging** (30 minutes)
   - Timing decorators for slow operations
   - Automatic performance tracking
   - Database query logging

#### To Reach 10/10:
3. **Log Sanitization** (1 hour)
   - Prevent logging sensitive data
   - Automatic PII redaction
   - Security best practice

4. **Metrics Integration** (2-3 hours)
   - Prometheus metrics
   - Grafana dashboards
   - Alert rules

---

## Testing Logging

### Enable Debug Logging

```bash
# Set environment variable
export LOG_LEVEL=DEBUG

# Run application
python src/main.py
```

### Test Request Logging

```bash
# Make a request
curl -X POST http://localhost:8000/api/v1/clusters/generate \
  -H "Content-Type: application/json" \
  -d '{"cluster_name": "test", ...}'

# Check logs
tail -f logs/app.log
```

### Verify Correlation IDs

```bash
# Check response headers
curl -v http://localhost:8000/api/v1/clusters/vendors 2>&1 | grep X-Correlation-ID
```

---

## Troubleshooting

### No Logs Appearing

1. Check log level: `export LOG_LEVEL=DEBUG`
2. Check log file location: `ls -la logs/`
3. Check permissions: `chmod 755 logs/`

### Log File Too Large

```bash
# Manually rotate logs
cd logs/
mv app.log app.log.manual.$(date +%Y%m%d)
touch app.log
```

### Missing Context in Logs

Make sure to use `extra` parameter:
```python
logger.info("Message", extra={"key": "value"})
```

---

## Best Practices

### DO:
✅ Use correlation IDs for request tracking
✅ Include context in extra parameter
✅ Use appropriate log levels
✅ Log errors with exc_info=True
✅ Use get_logger(__name__)

### DON'T:
❌ Log sensitive data (passwords, tokens)
❌ Log in tight loops
❌ Use print() statements
❌ Ignore log rotation
❌ Log entire request/response bodies

---

## Summary

The logging system is now **production-ready** with:
- ✅ Consistent namespace hierarchy
- ✅ Automatic request/response logging
- ✅ Correlation IDs for distributed tracing
- ✅ Structured logging with context
- ✅ Rotating file handler
- ✅ Rich console output
- ✅ Error tracking with stack traces

**Rating: 8/10** - Excellent observability for debugging and monitoring!

For advanced features (JSON logging, metrics), see the roadmap section above.
