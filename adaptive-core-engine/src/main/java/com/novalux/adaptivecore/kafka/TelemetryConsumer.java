package com.novalux.adaptivecore.kafka;

import org.springframework.kafka.annotation.KafkaListener;
import org.springframework.kafka.support.KafkaHeaders;
import org.springframework.messaging.handler.annotation.Header;
import org.springframework.messaging.handler.annotation.Payload;
import org.springframework.stereotype.Component;
import org.springframework.beans.factory.annotation.Autowired;
import lombok.extern.slf4j.Slf4j;

import com.novalux.adaptivecore.model.TelemetryEvent;
import com.novalux.adaptivecore.service.AIIntegrationService;
import com.fasterxml.jackson.databind.ObjectMapper;

@Component
@Slf4j
public class TelemetryConsumer {

    private final AIIntegrationService aiIntegrationService;
    private final ObjectMapper objectMapper;

    @Autowired
    public TelemetryConsumer(AIIntegrationService aiIntegrationService, ObjectMapper objectMapper) {
        this.aiIntegrationService = aiIntegrationService;
        this.objectMapper = objectMapper;
    }

    @KafkaListener(
        topics = {"player-actions", "game-events", "system-metrics"},
        groupId = "${data-pipeline.kafka.consumer-group}",
        containerFactory = "kafkaListenerContainerFactory"
    )
    public void consume(@Payload String message,
                        @Header(KafkaHeaders.RECEIVED_TOPIC) String topic,
                        @Header(KafkaHeaders.RECEIVED_PARTITION_ID) int partition,
                        @Header(KafkaHeaders.OFFSET) long offset) {
        
        log.debug("Received message from topic {}, partition {}, offset {}", topic, partition, offset);
        
        try {
            TelemetryEvent event = objectMapper.readValue(message, TelemetryEvent.class);
            log.info("Processing telemetry event: {} of type {} from {}", 
                    event.getId(), event.getType(), event.getSource());
            
            // Queue the event for AI processing
            aiIntegrationService.queueForInference(event);
            
        } catch (Exception e) {
            log.error("Error processing message from topic {}: {}", topic, e.getMessage(), e);
        }
    }
}
