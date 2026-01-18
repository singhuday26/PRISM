# PRISM API Documentation

## Security Best Practices

### Environment Variables

- **Never commit `.env` files** to version control
- Store sensitive credentials in environment variables
- Use different credentials for development and production
- Rotate database credentials regularly

### MongoDB Security

1. **Authentication**: Always use authentication for MongoDB
2. **Connection String**: Use `mongodb+srv://` for Atlas or secure connection strings
3. **Network Security**: Restrict database access to specific IP addresses
4. **Minimal Privileges**: Grant only necessary permissions to database users

### API Security

- CORS is configurable via `CORS_ORIGINS` environment variable
- In production, set specific origins instead of `*`
- Consider adding rate limiting middleware for production use
- Use HTTPS in production

## Error Handling

### HTTP Status Codes

- `200 OK` - Successful request
- `422 Unprocessable Entity` - Validation error
- `500 Internal Server Error` - Unexpected server error
- `503 Service Unavailable` - Database unavailable

### Error Response Format

```json
{
  "error": "Error Type",
  "message": "Human-readable error message",
  "details": [] // Optional validation details
}
```

## Logging

### Log Levels

- `DEBUG` - Detailed diagnostic information
- `INFO` - General informational messages
- `WARNING` - Warning messages for potentially harmful situations
- `ERROR` - Error messages for serious problems
- `CRITICAL` - Critical messages for severe errors

### Log Files

- `logs/prism.log` - All application logs (rotated at 10MB)
- `logs/prism_errors.log` - Error and critical logs only

### Logging Configuration

Set log level via `LOG_LEVEL` environment variable.

## Database Indexes

### Automatic Indexes

The application automatically creates indexes on startup:

- `regions.region_id` (unique)
- `cases_daily.region_id + date` (unique compound)
- `forecasts_daily.region_id + date` (compound)
- `risk_scores.date + risk_score` (compound)
- `alerts.date + risk_score` (compound)

## API Endpoints

### Health Check

- `GET /health/ping` - Simple ping
- `GET /health/` - Comprehensive health check with database status

### Regions

- `GET /regions/` - List all regions

### Risk Assessment

- `POST /risk/compute?target_date=YYYY-MM-DD` - Compute risk scores
- `GET /risk/latest?region_id=xxx` - Get latest risk scores

### Alerts

- `POST /alerts/generate?date=YYYY-MM-DD` - Generate alerts
- `GET /alerts/latest?region_id=xxx&limit=20` - Get latest alerts

### Hotspots

- `GET /hotspots/?limit=5` - Get top hotspots

### Forecasts

- `POST /forecasts/generate?date=YYYY-MM-DD&horizon=7` - Generate forecasts
- `GET /forecasts/latest?region_id=xxx&horizon=7` - Get latest forecasts

## Configuration Reference

### Required Environment Variables

- `MONGO_URI` - MongoDB connection string

### Optional Environment Variables

- `DB_NAME` - Database name (default: prism_db)
- `API_HOST` - API host (default: 0.0.0.0)
- `API_PORT` - API port (default: 8000)
- `LOG_LEVEL` - Logging level (default: INFO)
- `RISK_HIGH_THRESHOLD` - Risk threshold for alerts (default: 0.7)
- `MONGO_CONNECT_TIMEOUT_MS` - MongoDB connection timeout (default: 5000)
- `MONGO_SERVER_SELECTION_TIMEOUT_MS` - Server selection timeout (default: 5000)
- `ENABLE_CORS` - Enable CORS (default: true)
- `CORS_ORIGINS` - Allowed origins (default: \*)

## Performance Considerations

### Database Queries

- All queries use indexes for optimal performance
- Aggregation pipelines are optimized with `$limit` and `$sort`
- Connection pooling (10-50 connections)

### Rate Limiting

Consider adding rate limiting middleware for production:

```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
```

## Monitoring

### Health Checks

Regular health checks should monitor:

- API responsiveness (`/health/ping`)
- Database connectivity (`/health/`)
- Collection document counts

### Metrics to Track

- Request latency
- Error rates by endpoint
- Database query performance
- Connection pool utilization
