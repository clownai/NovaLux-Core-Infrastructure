package com.novalux.adaptivecore.kafka;

import org.springframework.kafka.core.KafkaTemplate;
import org.springframework.stereotype.Component;
import org.springframework.beans.factory.annotation.Autowired;
import lombok.extern.slf4j.Slf4j;

import com.novalux.adaptivecore.config.KafkaConfig;
import com.novalux.adaptivecore.model.OptimizationEvent;
import com.novalux.adaptivecore.model.ParameterAdjustment;
import com.fasterxml.jackson.databind.ObjectMapper;

@Component
@Slf4j
public class OptimizationProducer {

    private final KafkaTemplate<String, String> kafkaTemplate;
    private final KafkaConfig kafkaConfig;
    private final ObjectMapper objectMapper;

    @Autowired
    public OptimizationProducer(KafkaTemplate<String, String> kafkaTemplate, 
                               KafkaConfig kafkaConfig,
                               ObjectMapper objectMapper) {
        this.kafkaTemplate = kafkaTemplate;
        this.kafkaConfig = kafkaConfig;
        this.objectMapper = objectMapper;
    }

    public void sendOptimizationEvent(OptimizationEvent event) {
        try {
            String topic = kafkaConfig.getTopics().getOutput().getOptimizationEvents();
            String message = objectMapper.writeValueAsString(event);
            
            log.info("Sending optimization event to topic {}: {}", topic, event.getId());
            kafkaTemplate.send(topic, event.getId(), message);
            
        } catch (Exception e) {
            log.error("Error sending optimization event: {}", e.getMessage(), e);
        }
    }

    public void sendParameterAdjustment(ParameterAdjustment adjustment) {
        try {
            String topic = kafkaConfig.getTopics().getOutput().getParameterAdjustments();
            String message = objectMapper.writeValueAsString(adjustment);
            
            log.info("Sending parameter adjustment to topic {}: {}", topic, adjustment.getId());
            kafkaTemplate.send(topic, adjustment.getId(), message);
            
        } catch (Exception e) {
            log.error("Error sending parameter adjustment: {}", e.getMessage(), e);
        }
    }
}
