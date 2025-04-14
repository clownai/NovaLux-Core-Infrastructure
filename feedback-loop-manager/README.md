# Feedback Loop Manager

The Feedback Loop Manager is a critical component of the NovaLux Forever Growth Loop architecture. It analyzes player behavior, optimizes game balance, generates content recommendations, and monitors responsible gaming patterns to continuously improve the gaming experience.

## Features

- **Player Behavior Analysis**: Analyzes telemetry data to generate insights about player preferences, skill levels, and engagement patterns
- **Game Balance Optimization**: Monitors game metrics and suggests parameter adjustments to maintain optimal player experience
- **Content Recommendation**: Generates personalized content recommendations based on player behavior and preferences
- **Responsible Gaming Monitoring**: Identifies potentially problematic gaming patterns and generates alerts for intervention

## Architecture

The Feedback Loop Manager follows a microservice architecture with the following components:

- **Telemetry Consumer**: Consumes telemetry events from Kafka topics
- **Feedback Producer**: Publishes insights, adjustments, recommendations, and alerts to Kafka topics
- **Service Layer**: Processes telemetry data through specialized services for each feature area
- **REST API**: Provides endpoints for direct interaction with the feedback loop system

## Configuration

The Feedback Loop Manager is configured via the following properties in `application.yml`:

- **Server**: HTTP port and shutdown behavior
- **Management**: Metrics and health endpoints
- **Player Behavior Analysis**: Configuration for player behavior analysis
- **Game Balance Optimization**: Configuration for game balance optimization
- **Content Recommendation**: Configuration for content recommendation
- **Responsible Gaming Monitoring**: Configuration for responsible gaming monitoring
- **Data Pipeline**: Kafka and Elasticsearch configuration

## Building

To build the Feedback Loop Manager:

```bash
cd /path/to/NovaLux-Core-Infrastructure/feedback-loop-manager
mvn clean package
```

This will create a JAR file in the `target` directory.

## Running

To run the Feedback Loop Manager locally:

```bash
java -jar target/feedback-loop-manager-1.0.0.jar
```

## Deployment

The Feedback Loop Manager is deployed to Kubernetes using the configuration in `kubernetes/feedback-loop-manager.yaml`. The deployment includes:

- Deployment with 3 replicas
- Service for HTTP and metrics endpoints
- ConfigMap for configuration
- PersistentVolumeClaim for data storage

## API Endpoints

- **GET /health**: Health check endpoint
- **GET /ready**: Readiness check endpoint
- **GET /api/v1/status**: Service status endpoint
- **POST /api/v1/telemetry**: Submit a telemetry event for processing

## Integration

The Feedback Loop Manager integrates with the following components:

- **Kafka**: For consuming telemetry events and publishing feedback events
- **Elasticsearch**: For storing telemetry data and feedback events
- **Adaptive Core Engine**: For coordinating optimization strategies

## Development

To set up the development environment:

1. Clone the NovaLux-Core-Infrastructure repository
2. Navigate to the feedback-loop-manager directory
3. Build the project using Maven
4. Run the application locally

## Testing

To run the tests:

```bash
mvn test
```

## Next Steps

Future enhancements to the Feedback Loop Manager include:

1. Implementing more sophisticated player behavior analysis algorithms
2. Enhancing game balance optimization with machine learning
3. Improving content recommendation personalization
4. Expanding responsible gaming monitoring capabilities
5. Adding support for A/B testing of recommendations and adjustments
