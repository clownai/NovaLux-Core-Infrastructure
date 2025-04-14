#!/bin/bash

# NovaLux Core Infrastructure Deployment Script
# This script deploys the NovaLux Core Infrastructure components to a Kubernetes cluster

set -e

echo "===== NovaLux Core Infrastructure Deployment ====="
echo "Starting deployment at $(date)"

# Create directories for logs
mkdir -p logs

# Function to apply Kubernetes manifests with error handling
apply_manifest() {
    local file=$1
    local component=$2
    
    echo "Deploying $component from $file..."
    kubectl apply -f "$file" > "logs/${component}-deploy.log" 2>&1
    
    if [ $? -eq 0 ]; then
        echo "✅ Successfully deployed $component"
    else
        echo "❌ Failed to deploy $component. Check logs//${component}-deploy.log for details"
        exit 1
    fi
}

# Deploy components in the correct order
echo "Step 1: Creating namespaces and cluster configuration"
apply_manifest "/home/ubuntu/NovaLux-Core-Infrastructure/kubernetes/cluster-config.yaml" "cluster-config"

echo "Step 2: Deploying Zookeeper and Kafka"
apply_manifest "/home/ubuntu/NovaLux-Core-Infrastructure/kafka/kafka-zookeeper.yaml" "kafka-zookeeper"

echo "Step 3: Deploying Schema Registry and Kafka Connect"
apply_manifest "/home/ubuntu/NovaLux-Core-Infrastructure/kafka/schema-registry-connect.yaml" "schema-registry-connect"

echo "Step 4: Deploying Elasticsearch and Kibana"
apply_manifest "/home/ubuntu/NovaLux-Core-Infrastructure/elasticsearch/elasticsearch-kibana.yaml" "elasticsearch-kibana"

echo "Step 5: Deploying Data Ingestion Service"
apply_manifest "/home/ubuntu/NovaLux-Core-Infrastructure/kafka/data-ingestion.yaml" "data-ingestion"

echo "Step 6: Deploying Stream Processor"
apply_manifest "/home/ubuntu/NovaLux-Core-Infrastructure/kafka/stream-processor.yaml" "stream-processor"

echo "Step 7: Deploying Adaptive Core Engine"
apply_manifest "/home/ubuntu/NovaLux-Core-Infrastructure/kubernetes/adaptive-core.yaml" "adaptive-core"

echo "Step 8: Deploying Feedback Loop Manager"
apply_manifest "/home/ubuntu/NovaLux-Core-Infrastructure/elasticsearch/feedback-loop-manager.yaml" "feedback-loop-manager"

echo "Step 9: Deploying Core Integrator"
apply_manifest "/home/ubuntu/NovaLux-Core-Infrastructure/kubernetes/core-integrator.yaml" "core-integrator"

echo "Step 10: Deploying Deployment Manager"
apply_manifest "/home/ubuntu/NovaLux-Core-Infrastructure/kubernetes/deployment-manager.yaml" "deployment-manager"

echo "===== Deployment Complete ====="
echo "Verifying deployments..."

# Wait for all pods to be ready
echo "Waiting for all pods to be ready..."
kubectl wait --for=condition=ready pod --all --all-namespaces --timeout=300s > logs/pod-ready.log 2>&1

if [ $? -eq 0 ]; then
    echo "✅ All pods are ready"
else
    echo "⚠️ Not all pods are ready within timeout. Check logs/pod-ready.log for details"
fi

# Display deployment status
echo "===== Deployment Status ====="
echo "Namespaces:"
kubectl get namespaces | grep novalux

echo "Pods in novalux-system namespace:"
kubectl get pods -n novalux-system

echo "Pods in novalux-data namespace:"
kubectl get pods -n novalux-data

echo "Services in novalux-system namespace:"
kubectl get services -n novalux-system

echo "Services in novalux-data namespace:"
kubectl get services -n novalux-data

echo "===== NovaLux Core Infrastructure Deployment Completed at $(date) ====="
