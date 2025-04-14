# Adaptive Core Engine

The Adaptive Core Engine is the central component of the NovaLux Forever Growth Loop architecture. It processes telemetry data from player actions, game events, and system metrics to generate optimization suggestions that continuously improve the gaming experience.

## Features

- Real-time telemetry processing via Kafka
- AI-driven optimization suggestions
- Feedback loop for continuous improvement
- Parameter adjustment application
- Elasticsearch integration for data storage and analytics
- Health and readiness endpoints for Kubernetes integration

## Architecture

The Adaptive Core Engine follows a microservice architecture with the following components:

- **Telemetry Consumer**: Consumes telemetry events from Kafka topics
- **AI Integration Service**: Sends telemetry data to the AI Model Server for analysis
- **Feedback Loop Service**: Processes optimization suggestions and applies parameter adjustments
- **Optimization Producer**: Publishes optimization events and parameter adjustments to Kafka
- **Telemetry Service**: Stores telemetry data, optimization events, and parameter adjustments in Elasticsearch
- **Batch Processing Scheduler**: Periodically processes batched telemetry data

## Configuration

The Adaptive Core Engine is configured via the following properties in `application.yml`:

- **Server**: HTTP port and shutdown behavior
- **Management**: Metrics and health endpoints
- **Telemetry**: Sampling rate and trace export settings
- **Feedback Loop**: Update interval and optimization thresholds
- **AI Integration**: Model server URL and inference settings
- **Data Pipeline**: Kafka and Elasticsearch configuration

## Building

To build the Adaptive Core Engine:

```bash
cd /path/to/NovaLux-Core-Infrastructure/adaptive-core-engine
mvn clean package
```

This will create a JAR file in the `target` directory.

## Running

To run the Adaptive Core Engine locally:

```bash
java -jar target/adaptive-core-engine-1.0.0.jar
```

## Deployment

The Adaptive Core Engine is deployed to Kubernetes using the configuration in `kubernetes/adaptive-core.yaml`. The deployment includes:

- Deployment with 3 replicas
- Service for HTTP and metrics endpoints
- ConfigMap for configuration
- PersistentVolumeClaim for data storage

## API Endpoints

- **GET /health**: Health check endpoint
- **GET /ready**: Readiness check endpoint
- **POST /api/v1/optimizations**: Submit an optimization event for processing

## Integration

The Adaptive Core Engine integrates with the following components:

- **Kafka**: For consuming telemetry events and publishing optimization events
- **Elasticsearch**: For storing telemetry data and optimization events
- **AI Model Server**: For generating optimization suggestions based on telemetry data

## Development

To set up the development environment:

1. Clone the NovaLux-Core-Infrastructure repository
2. Navigate to the adaptive-core-engine directory
3. Build the project using Maven
4. Run the application locally

## Testing

To run the tests:

```bash
mvn test
```

## Next Steps

Future enhancements to the Adaptive Core Engine include:

1. Implementing more sophisticated optimization algorithms
2. Adding support for A/B testing of parameter adjustments
3. Enhancing the telemetry processing pipeline
4. Implementing real-time analytics dashboards
5. Adding support for multi-tenant deployments
