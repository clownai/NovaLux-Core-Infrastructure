# Core Integrator

The Core Integrator is a central component of the NovaLux Forever Growth Loop architecture. It serves as an API gateway and integration layer that connects the Adaptive Core Engine, Feedback Loop Manager, and other services within the NovaLux ecosystem.

## Features

- **API Gateway**: Routes requests to appropriate microservices
- **Service Discovery**: Automatically discovers and registers services
- **Circuit Breaker**: Prevents cascading failures with fallback mechanisms
- **Rate Limiting**: Protects services from excessive traffic
- **CORS Support**: Enables cross-origin resource sharing
- **Request Tracing**: Adds tracing headers for distributed tracing
- **Logging**: Comprehensive request and response logging

## Architecture

The Core Integrator follows a microservice architecture with the following components:

- **Spring Cloud Gateway**: Routes API requests to appropriate services
- **Eureka Client**: Discovers and registers services
- **Resilience4j**: Implements circuit breaker patterns
- **Global Filters**: Adds cross-cutting concerns like logging and tracing

## Configuration

The Core Integrator is configured via the following properties in `application.yml`:

- **Server**: HTTP port and shutdown behavior
- **Management**: Metrics and health endpoints
- **Spring Cloud Gateway**: Route definitions and filters
- **Eureka**: Service discovery configuration
- **Resilience4j**: Circuit breaker configuration
- **API Gateway**: Rate limiting and CORS configuration

## Building

To build the Core Integrator:

```bash
cd /path/to/NovaLux-Core-Infrastructure/core-integrator
mvn clean package
```

This will create a JAR file in the `target` directory.

## Running

To run the Core Integrator locally:

```bash
java -jar target/core-integrator-1.0.0.jar
```

## Deployment

The Core Integrator is deployed to Kubernetes using the configuration in `kubernetes/core-integrator.yaml`. The deployment includes:

- Deployment with 3 replicas
- Service for HTTP and metrics endpoints
- ConfigMap for configuration

## API Endpoints

- **GET /health**: Health check endpoint
- **GET /ready**: Readiness check endpoint
- **GET /fallback/{service-name}**: Fallback endpoints for circuit breaker
- **All other paths**: Routed to appropriate microservices based on path

## Integration

The Core Integrator integrates with the following components:

- **Adaptive Core Engine**: For core game mechanics and optimization
- **Feedback Loop Manager**: For player behavior analysis and game balance
- **Game Service**: For game-specific functionality
- **Player Service**: For player management and profiles
- **Analytics Service**: For data analytics and reporting

## Development

To set up the development environment:

1. Clone the NovaLux-Core-Infrastructure repository
2. Navigate to the core-integrator directory
3. Build the project using Maven
4. Run the application locally

## Testing

To run the tests:

```bash
mvn test
```

## Next Steps

Future enhancements to the Core Integrator include:

1. Implementing authentication and authorization
2. Adding API documentation with Swagger
3. Enhancing monitoring and alerting
4. Implementing traffic shaping and throttling
5. Adding support for WebSocket routing
