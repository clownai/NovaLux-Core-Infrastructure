#!/bin/bash

# NovaLux Core Infrastructure Test Script
# This script tests the NovaLux Core Infrastructure components in a Kubernetes cluster

set -e

echo "===== NovaLux Core Infrastructure Testing ====="
echo "Starting tests at $(date)"

# Create directories for test logs
mkdir -p test-logs

# Function to test component health
test_component_health() {
    local component=$1
    local namespace=$2
    local endpoint=$3
    
    echo "Testing health of $component in namespace $namespace..."
    
    # Get the service IP
    local service_ip=$(kubectl get service $component -n $namespace -o jsonpath='{.spec.clusterIP}')
    
    if [ -z "$service_ip" ]; then
        echo "❌ Failed to get service IP for $component"
        return 1
    fi
    
    # Test the health endpoint
    kubectl run curl-test-$component --image=curlimages/curl --restart=Never -n $namespace -- \
        curl -s -o /dev/null -w "%{http_code}" http://$service_ip:8080$endpoint > test-logs/$component-health.log 2>&1
    
    # Wait for the pod to complete
    kubectl wait --for=condition=complete job/curl-test-$component -n $namespace --timeout=60s > /dev/null 2>&1
    
    # Get the result
    local result=$(kubectl logs curl-test-$component -n $namespace)
    
    # Clean up the test pod
    kubectl delete pod curl-test-$component -n $namespace > /dev/null 2>&1
    
    if [ "$result" == "200" ]; then
        echo "✅ $component health check passed"
        return 0
    else
        echo "❌ $component health check failed with status $result"
        return 1
    fi
}

# Function to test Kafka connectivity
test_kafka_connectivity() {
    echo "Testing Kafka connectivity..."
    
    # Create a test topic
    kubectl exec -it kafka-0 -n novalux-data -- \
        kafka-topics --create --topic test-topic --bootstrap-server kafka-headless.novalux-data.svc.cluster.local:9092 \
        --partitions 1 --replication-factor 1 > test-logs/kafka-create-topic.log 2>&1
    
    if [ $? -eq 0 ]; then
        echo "✅ Successfully created Kafka test topic"
    else
        echo "❌ Failed to create Kafka test topic. Check test-logs/kafka-create-topic.log for details"
        return 1
    fi
    
    # Produce a test message
    kubectl exec -it kafka-0 -n novalux-data -- \
        echo "test message" | kafka-console-producer --topic test-topic --bootstrap-server kafka-headless.novalux-data.svc.cluster.local:9092 \
        > test-logs/kafka-produce.log 2>&1
    
    if [ $? -eq 0 ]; then
        echo "✅ Successfully produced test message to Kafka"
    else
        echo "❌ Failed to produce test message to Kafka. Check test-logs/kafka-produce.log for details"
        return 1
    fi
    
    # Consume the test message
    kubectl exec -it kafka-0 -n novalux-data -- \
        kafka-console-consumer --topic test-topic --bootstrap-server kafka-headless.novalux-data.svc.cluster.local:9092 \
        --from-beginning --max-messages 1 > test-logs/kafka-consume.log 2>&1
    
    if [ $? -eq 0 ]; then
        echo "✅ Successfully consumed test message from Kafka"
    else
        echo "❌ Failed to consume test message from Kafka. Check test-logs/kafka-consume.log for details"
        return 1
    fi
    
    return 0
}

# Function to test Elasticsearch connectivity
test_elasticsearch_connectivity() {
    echo "Testing Elasticsearch connectivity..."
    
    # Check cluster health
    kubectl exec -it elasticsearch-master-0 -n novalux-data -- \
        curl -s http://localhost:9200/_cluster/health > test-logs/elasticsearch-health.log 2>&1
    
    if [ $? -eq 0 ]; then
        echo "✅ Successfully connected to Elasticsearch"
    else
        echo "❌ Failed to connect to Elasticsearch. Check test-logs/elasticsearch-health.log for details"
        return 1
    fi
    
    return 0
}

# Function to test integration between components
test_integration() {
    echo "Testing integration between components..."
    
    # Test adaptive core to feedback loop manager integration
    kubectl exec -it $(kubectl get pod -l app=novalux-core-integrator -n novalux-system -o jsonpath='{.items[0].metadata.name}') -n novalux-system -- \
        curl -s http://localhost:8080/integration/test?source=adaptive-core&target=feedback-loop-manager > test-logs/integration-test.log 2>&1
    
    if [ $? -eq 0 ]; then
        echo "✅ Successfully tested integration between components"
    else
        echo "❌ Failed to test integration between components. Check test-logs/integration-test.log for details"
        return 1
    fi
    
    return 0
}

# Run the tests
echo "Step 1: Testing component health"
test_component_health "novalux-adaptive-core" "novalux-system" "/health" || echo "Continuing despite failure..."
test_component_health "novalux-feedback-loop-manager" "novalux-system" "/health" || echo "Continuing despite failure..."
test_component_health "novalux-data-ingestion" "novalux-data" "/health" || echo "Continuing despite failure..."
test_component_health "novalux-stream-processor" "novalux-data" "/health" || echo "Continuing despite failure..."
test_component_health "novalux-core-integrator" "novalux-system" "/health" || echo "Continuing despite failure..."

echo "Step 2: Testing Kafka connectivity"
test_kafka_connectivity || echo "Continuing despite failure..."

echo "Step 3: Testing Elasticsearch connectivity"
test_elasticsearch_connectivity || echo "Continuing despite failure..."

echo "Step 4: Testing integration between components"
test_integration || echo "Continuing despite failure..."

echo "===== Testing Complete ====="
echo "Test results summary:"
echo "Component health tests: $(grep -c "health check passed" test-logs/*) passed, $(grep -c "health check failed" test-logs/*) failed"
echo "Kafka connectivity tests: $(grep -c "Successfully" test-logs/kafka-*.log) passed, $(grep -c "Failed" test-logs/kafka-*.log) failed"
echo "Elasticsearch connectivity tests: $(grep -c "Successfully" test-logs/elasticsearch-*.log) passed, $(grep -c "Failed" test-logs/elasticsearch-*.log) failed"
echo "Integration tests: $(grep -c "Successfully" test-logs/integration-*.log) passed, $(grep -c "Failed" test-logs/integration-*.log) failed"

echo "===== NovaLux Core Infrastructure Testing Completed at $(date) ====="
