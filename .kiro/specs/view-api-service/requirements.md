# Requirements Document: View API Service

## Introduction

The View API Service is a production-grade HTTP service that implements the view-envelope@1 specification to provide stable, cacheable, and observable access to financial market data views. The service acts as a stable abstraction layer over unstable upstream data sources, providing Primitive Views (atomic, reusable data views) and Feature Views (aggregated dashboard views) to client applications.

The service addresses the core problem of upstream data source instability (frequent API changes, rate limiting, downtime) by centralizing data acquisition, caching, error handling, and observability in a single managed service. This allows client applications to consume data through a stable contract without worrying about upstream volatility.

## Glossary

- **View_API_Service**: The HTTP service that provides access to data views through RESTful endpoints
- **View**: A callable data endpoint that accepts JSON parameters and returns a JSON Envelope
- **Envelope**: The standardized response structure containing meta, data, warnings, and errors fields
- **Primitive_View**: A stable, single-purpose, cacheable data view (e.g., PV.HistOHLCV, PV.FundFlow)
- **Feature_View**: An aggregated dashboard view composed of multiple Primitive Views
- **Provider**: Internal component that interfaces with upstream data sources (e.g., EastMoney, Sina)
- **Cache**: Temporary storage of view results with TTL to reduce upstream load and improve response time
- **Refresh**: A parameter that forces cache bypass and triggers fresh data retrieval
- **TTL**: Time-to-live duration for cached results
- **Request_ID**: Unique identifier for each API request used for tracing and debugging
- **Bearer_Token**: Authentication token passed in Authorization header
- **API_Key**: Alternative authentication credential passed in X-API-Key header
- **Upstream**: External data sources that the service fetches data from
- **Stale_Cache**: Cached data that has exceeded its TTL but may be returned as fallback

## Requirements

### Requirement 1: HTTP API Endpoints

**User Story:** As a client application, I want to interact with the View API Service through standard HTTP endpoints, so that I can discover, inspect, and execute data views using any HTTP client.

#### Acceptance Criteria

1. THE View_API_Service SHALL expose a health check endpoint at GET /health
2. THE View_API_Service SHALL expose a view listing endpoint at GET /views
3. THE View_API_Service SHALL expose a view schema endpoint at GET /views/{name}
4. THE View_API_Service SHALL expose a view execution endpoint at POST /run
5. THE View_API_Service SHALL use Content-Type application/json with UTF-8 encoding for all requests and responses
6. THE View_API_Service SHALL support gzip compression for responses via Content-Encoding header

### Requirement 2: Health Check Endpoint

**User Story:** As a monitoring system, I want to check if the View API Service is operational, so that I can detect service outages and trigger alerts.

#### Acceptance Criteria

1. WHEN a GET request is made to /health, THE View_API_Service SHALL return HTTP status 200
2. WHEN a GET request is made to /health, THE View_API_Service SHALL return a JSON object with an "ok" field set to true
3. THE View_API_Service SHALL respond to /health requests within 1 second

### Requirement 3: View Listing Endpoint

**User Story:** As a client application, I want to discover all available views, so that I can understand what data the service provides.

#### Acceptance Criteria

1. WHEN a GET request is made to /views, THE View_API_Service SHALL return a JSON object containing a "views" array and a "count" field
2. WHERE a "contains" query parameter is provided, THE View_API_Service SHALL filter views by substring match
3. WHERE a "prefix" query parameter is provided, THE View_API_Service SHALL filter views by prefix match
4. WHERE a "kind" query parameter is provided with value "primitive", "feature", or "any", THE View_API_Service SHALL filter views by kind
5. THE View_API_Service SHALL return view names in snake_case format

### Requirement 4: View Schema Endpoint

**User Story:** As a client application, I want to inspect a view's parameter schema and output structure, so that I can validate my requests before execution.

#### Acceptance Criteria

1. WHEN a GET request is made to /views/{name} with a valid view name, THE View_API_Service SHALL return HTTP status 200 with view metadata
2. WHEN a GET request is made to /views/{name} with an invalid view name, THE View_API_Service SHALL return HTTP status 404
3. THE View_API_Service SHALL include a "params_schema" field conforming to JSON Schema specification
4. THE View_API_Service SHALL include a "name" field matching the requested view name
5. THE View_API_Service SHALL include a "kind" field indicating "primitive" or "feature"
6. THE View_API_Service SHALL include a "description" field explaining the view's purpose

### Requirement 5: View Execution Endpoint

**User Story:** As a client application, I want to execute views with parameters, so that I can retrieve the data I need for analysis.

#### Acceptance Criteria

1. WHEN a POST request is made to /run with valid view name and parameters, THE View_API_Service SHALL return HTTP status 200 with an Envelope
2. WHEN a POST request is made to /run with an invalid view name, THE View_API_Service SHALL return an Envelope with VIEW_NOT_FOUND error
3. WHEN a POST request is made to /run with invalid parameters, THE View_API_Service SHALL return an Envelope with INVALID_PARAMS error
4. THE View_API_Service SHALL accept a JSON request body containing "name", "params", and optional "refresh" fields
5. WHERE the "refresh" field is true, THE View_API_Service SHALL bypass cache and fetch fresh data
6. WHERE the "refresh" field is false or omitted, THE View_API_Service SHALL attempt to serve from cache

### Requirement 6: Envelope Response Structure

**User Story:** As a client application, I want all view responses to follow a consistent structure, so that I can parse results reliably regardless of which view I call.

#### Acceptance Criteria

1. THE View_API_Service SHALL return responses conforming to the view-envelope@1 specification
2. THE View_API_Service SHALL include "meta", "data", "warnings", and "errors" fields in every Envelope
3. THE View_API_Service SHALL set meta.spec_version to "view-envelope@1"
4. THE View_API_Service SHALL include meta.provider identifying the service
5. THE View_API_Service SHALL include meta.view containing the view name
6. THE View_API_Service SHALL include meta.as_of with ISO 8601 timestamp
7. THE View_API_Service SHALL include meta.elapsed_seconds with execution duration
8. THE View_API_Service SHALL include meta.params echoing the effective parameters
9. THE View_API_Service SHALL return warnings as an array of strings
10. THE View_API_Service SHALL return errors as an array of strings

### Requirement 7: JSON Compatibility

**User Story:** As a client application in any programming language, I want responses to be valid JSON, so that I can parse them without special handling for edge cases.

#### Acceptance Criteria

1. THE View_API_Service SHALL NOT output NaN values in JSON responses
2. THE View_API_Service SHALL NOT output Infinity values in JSON responses
3. WHEN numeric values are NaN or Infinity, THE View_API_Service SHALL convert them to null and add a warning
4. THE View_API_Service SHALL encode datetime values as ISO 8601 strings
5. THE View_API_Service SHALL encode date values as YYYYMMDD strings or ISO 8601 strings
6. THE View_API_Service SHALL encode stock codes as strings to preserve leading zeros

### Requirement 8: Caching with TTL

**User Story:** As the View API Service operator, I want to cache view results with configurable TTL, so that I can reduce upstream load and improve response times.

#### Acceptance Criteria

1. THE View_API_Service SHALL cache view results with configurable TTL per view type
2. WHEN serving cached results, THE View_API_Service SHALL include meta.cache.hit set to true
3. WHEN serving cached results, THE View_API_Service SHALL include meta.cache.ttl_seconds
4. WHEN serving cached results, THE View_API_Service SHALL include meta.cache.age_seconds
5. WHEN cache age exceeds TTL, THE View_API_Service SHALL mark meta.cache.stale as true
6. WHERE refresh is false and cache is available, THE View_API_Service SHALL serve from cache
7. WHERE refresh is true, THE View_API_Service SHALL bypass cache and fetch fresh data

### Requirement 9: Stale Cache Fallback

**User Story:** As a client application, I want the service to return stale cached data when upstream fails, so that I can maintain partial functionality during outages.

#### Acceptance Criteria

1. WHEN upstream data fetch fails and stale cache exists, THE View_API_Service SHALL return the stale cache with a warning
2. WHEN returning stale cache, THE View_API_Service SHALL set meta.cache.stale to true
3. WHEN returning stale cache, THE View_API_Service SHALL add a STALE_CACHE warning
4. WHEN returning stale cache, THE View_API_Service SHALL include the upstream error in warnings

### Requirement 10: Error Code Standardization

**User Story:** As a client application, I want errors and warnings to use standardized codes, so that I can programmatically handle different failure scenarios.

#### Acceptance Criteria

1. WHEN parameters are invalid or missing, THE View_API_Service SHALL return INVALID_PARAMS error
2. WHEN a view name is not found, THE View_API_Service SHALL return VIEW_NOT_FOUND error
3. WHEN upstream times out, THE View_API_Service SHALL return UPSTREAM_TIMEOUT warning or error
4. WHEN upstream structure changes, THE View_API_Service SHALL return UPSTREAM_CHANGED warning
5. WHEN rate limited by upstream, THE View_API_Service SHALL return RATE_LIMITED warning or error
6. WHEN a view returns no data, THE View_API_Service SHALL return EMPTY_RESULT warning
7. WHEN partial data is available, THE View_API_Service SHALL return PARTIAL_RESULT warning
8. WHEN authentication fails, THE View_API_Service SHALL return AUTH_FAILED error
9. WHEN an internal error occurs, THE View_API_Service SHALL return INTERNAL_ERROR error
10. THE View_API_Service SHALL format error and warning strings as "[CODE] message"

### Requirement 11: Request Tracing

**User Story:** As a service operator, I want each request to have a unique identifier, so that I can trace requests through logs for debugging.

#### Acceptance Criteria

1. THE View_API_Service SHALL generate a unique request_id for each /run request
2. THE View_API_Service SHALL include meta.request_id in the response Envelope
3. THE View_API_Service SHALL log the request_id with request details
4. WHERE a client provides a trace_id in the request, THE View_API_Service SHALL include it in meta.trace_id

### Requirement 12: Authentication

**User Story:** As a service operator, I want to authenticate API requests, so that I can control access and prevent abuse.

#### Acceptance Criteria

1. THE View_API_Service SHALL support Bearer token authentication via Authorization header
2. THE View_API_Service SHALL support API key authentication via X-API-Key header
3. WHEN authentication fails, THE View_API_Service SHALL return HTTP status 401
4. WHEN authentication fails, THE View_API_Service SHALL return an Envelope with AUTH_FAILED error
5. THE View_API_Service SHALL validate authentication tokens before processing requests

### Requirement 13: Parameter Validation

**User Story:** As a client application, I want clear validation errors when I provide invalid parameters, so that I can correct my requests quickly.

#### Acceptance Criteria

1. THE View_API_Service SHALL validate request parameters against the view's params_schema
2. WHEN required parameters are missing, THE View_API_Service SHALL return INVALID_PARAMS error with details
3. WHEN parameter types are incorrect, THE View_API_Service SHALL return INVALID_PARAMS error with details
4. WHEN parameter values are out of range, THE View_API_Service SHALL return INVALID_PARAMS error with details
5. THE View_API_Service SHALL normalize and echo validated parameters in meta.params

### Requirement 14: Feature View Composition

**User Story:** As a client application, I want Feature Views to return structured sub-views, so that I can identify which components succeeded or failed independently.

#### Acceptance Criteria

1. WHEN a Feature View is executed, THE View_API_Service SHALL return data as a dictionary of component Envelopes
2. WHEN a Feature View component fails, THE View_API_Service SHALL include that component's errors in its sub-Envelope
3. WHEN a Feature View has partial failures, THE View_API_Service SHALL add PARTIAL_RESULT warning to the top-level Envelope
4. THE View_API_Service SHALL include meta.kind set to "feature" for Feature Views
5. THE View_API_Service SHALL include meta.deps listing dependent Primitive Views

### Requirement 15: Primitive View Implementation

**User Story:** As a client application, I want to call Primitive Views directly, so that I can access atomic data without unnecessary aggregation overhead.

#### Acceptance Criteria

1. THE View_API_Service SHALL expose Primitive Views as callable views
2. THE View_API_Service SHALL set meta.kind to "primitive" for Primitive Views
3. THE View_API_Service SHALL cache Primitive View results independently
4. THE View_API_Service SHALL include meta.source indicating data providers used

### Requirement 16: Observability Metadata

**User Story:** As a service operator, I want detailed metadata in responses, so that I can monitor performance and diagnose issues.

#### Acceptance Criteria

1. THE View_API_Service SHALL include meta.result.type indicating data structure type
2. WHERE data is tabular, THE View_API_Service SHALL include meta.result.rows with row count
3. WHERE data is tabular, THE View_API_Service SHALL include meta.result.columns with column names
4. WHERE data is a dictionary, THE View_API_Service SHALL include meta.result.keys with key count
5. THE View_API_Service SHALL measure and report elapsed_seconds with millisecond precision

### Requirement 17: Rate Limiting

**User Story:** As a service operator, I want to rate limit requests per client, so that I can prevent abuse and protect upstream data sources.

#### Acceptance Criteria

1. THE View_API_Service SHALL enforce rate limits per authentication token
2. WHEN rate limit is exceeded, THE View_API_Service SHALL return HTTP status 429
3. WHEN rate limit is exceeded, THE View_API_Service SHALL return an Envelope with RATE_LIMITED error
4. THE View_API_Service SHALL include rate limit information in response headers

### Requirement 18: Upstream Retry Logic

**User Story:** As a service operator, I want automatic retries for transient upstream failures, so that temporary issues don't cause request failures.

#### Acceptance Criteria

1. WHEN upstream requests fail with transient errors, THE View_API_Service SHALL retry with exponential backoff
2. THE View_API_Service SHALL limit retry attempts to prevent cascading failures
3. WHEN all retries are exhausted, THE View_API_Service SHALL return UPSTREAM_TIMEOUT error
4. THE View_API_Service SHALL add jitter to retry delays to prevent thundering herd

### Requirement 19: Upstream Contract Validation

**User Story:** As a service operator, I want to detect when upstream data structures change, so that I can fix adapters before clients are affected.

#### Acceptance Criteria

1. THE View_API_Service SHALL validate upstream response structures against expected schemas
2. WHEN upstream structure changes, THE View_API_Service SHALL add UPSTREAM_CHANGED warning
3. WHEN upstream structure changes, THE View_API_Service SHALL log the change for operator review
4. THE View_API_Service SHALL attempt to return partial data when structure changes are non-breaking

### Requirement 20: Empty Result Handling

**User Story:** As a client application, I want explicit warnings when results are empty, so that I don't mistake empty data for "no events" or "no risk".

#### Acceptance Criteria

1. WHEN a view returns zero rows or empty data, THE View_API_Service SHALL add EMPTY_RESULT warning
2. THE View_API_Service SHALL distinguish between "no data available" and "query returned no matches"
3. THE View_API_Service SHALL include context in EMPTY_RESULT warnings to aid interpretation

### Requirement 21: View Name Compatibility

**User Story:** As a client application, I want the service to accept both snake_case and kebab-case view names, so that I can migrate smoothly from legacy systems.

#### Acceptance Criteria

1. THE View_API_Service SHALL accept view names with underscores or hyphens interchangeably
2. WHEN a view name with hyphens is requested, THE View_API_Service SHALL attempt to match the underscore equivalent
3. WHEN a view name with underscores is requested, THE View_API_Service SHALL attempt to match the hyphen equivalent
4. THE View_API_Service SHALL return the canonical view name in meta.view

### Requirement 22: Timeout Configuration

**User Story:** As a service operator, I want configurable timeouts for upstream requests, so that I can balance responsiveness with success rate.

#### Acceptance Criteria

1. THE View_API_Service SHALL enforce configurable timeouts for upstream data fetches
2. WHEN upstream timeout is reached, THE View_API_Service SHALL cancel the request
3. WHEN upstream timeout is reached, THE View_API_Service SHALL attempt stale cache fallback
4. THE View_API_Service SHALL allow different timeout values per view type

### Requirement 23: Logging and Audit Trail

**User Story:** As a service operator, I want comprehensive logs of all requests, so that I can audit usage and troubleshoot issues.

#### Acceptance Criteria

1. THE View_API_Service SHALL log each request with timestamp, request_id, view name, and parameters
2. THE View_API_Service SHALL log authentication information for audit purposes
3. THE View_API_Service SHALL log cache hit/miss status
4. THE View_API_Service SHALL log upstream errors and retry attempts
5. THE View_API_Service SHALL log response status and elapsed time

### Requirement 24: Metrics Exposure

**User Story:** As a service operator, I want to monitor service health through metrics, so that I can detect and respond to issues proactively.

#### Acceptance Criteria

1. THE View_API_Service SHALL expose a /metrics endpoint for Prometheus scraping
2. THE View_API_Service SHALL track request count per view
3. THE View_API_Service SHALL track request latency percentiles (p50, p95, p99)
4. THE View_API_Service SHALL track cache hit rate per view
5. THE View_API_Service SHALL track upstream error rate per provider
6. THE View_API_Service SHALL track authentication failure rate

### Requirement 25: Graceful Degradation

**User Story:** As a client application, I want the service to degrade gracefully during partial outages, so that I can continue operating with reduced functionality.

#### Acceptance Criteria

1. WHEN some upstream providers fail, THE View_API_Service SHALL attempt alternative providers
2. WHEN all providers fail, THE View_API_Service SHALL return stale cache if available
3. WHEN Feature View components fail partially, THE View_API_Service SHALL return successful components with PARTIAL_RESULT warning
4. THE View_API_Service SHALL never return HTTP 5xx errors when partial data is available

### Requirement 26: Configuration Management

**User Story:** As a service operator, I want to configure cache TTLs, timeouts, and rate limits without code changes, so that I can tune the service for different deployment environments.

#### Acceptance Criteria

1. THE View_API_Service SHALL load configuration from environment variables or configuration files
2. THE View_API_Service SHALL support per-view TTL configuration
3. THE View_API_Service SHALL support per-view timeout configuration
4. THE View_API_Service SHALL support per-token rate limit configuration
5. THE View_API_Service SHALL validate configuration on startup and fail fast if invalid
