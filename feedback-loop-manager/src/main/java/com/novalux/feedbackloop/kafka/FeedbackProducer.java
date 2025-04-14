package com.novalux.feedbackloop.kafka;

import org.springframework.kafka.core.KafkaTemplate;
import org.springframework.stereotype.Component;
import org.springframework.beans.factory.annotation.Autowired;
import lombok.extern.slf4j.Slf4j;

import com.novalux.feedbackloop.model.PlayerInsight;
import com.novalux.feedbackloop.model.BalanceAdjustment;
import com.novalux.feedbackloop.model.ContentRecommendation;
import com.novalux.feedbackloop.model.ResponsibleGamingAlert;
import com.novalux.feedbackloop.config.KafkaConfig;

@Component
@Slf4j
public class FeedbackProducer {

    private final KafkaTemplate<String, Object> kafkaTemplate;
    private final KafkaConfig kafkaConfig;

    @Autowired
    public FeedbackProducer(KafkaTemplate<String, Object> kafkaTemplate, KafkaConfig kafkaConfig) {
        this.kafkaTemplate = kafkaTemplate;
        this.kafkaConfig = kafkaConfig;
    }

    public void publishPlayerInsight(PlayerInsight insight) {
        try {
            String topic = kafkaConfig.getTopics().getOutput().getPlayerInsights();
            log.debug("Publishing player insight to topic {}: {}", topic, insight.getId());
            kafkaTemplate.send(topic, insight.getPlayerId(), insight);
            log.debug("Published player insight: {}", insight.getId());
        } catch (Exception e) {
            log.error("Error publishing player insight: {}", insight.getId(), e);
        }
    }

    public void publishBalanceAdjustment(BalanceAdjustment adjustment) {
        try {
            String topic = kafkaConfig.getTopics().getOutput().getBalanceAdjustments();
            log.debug("Publishing balance adjustment to topic {}: {}", topic, adjustment.getId());
            kafkaTemplate.send(topic, adjustment.getGameId(), adjustment);
            log.debug("Published balance adjustment: {}", adjustment.getId());
        } catch (Exception e) {
            log.error("Error publishing balance adjustment: {}", adjustment.getId(), e);
        }
    }

    public void publishContentRecommendation(ContentRecommendation recommendation) {
        try {
            String topic = kafkaConfig.getTopics().getOutput().getContentRecommendations();
            log.debug("Publishing content recommendation to topic {}: {}", topic, recommendation.getId());
            kafkaTemplate.send(topic, recommendation.getPlayerId(), recommendation);
            log.debug("Published content recommendation: {}", recommendation.getId());
        } catch (Exception e) {
            log.error("Error publishing content recommendation: {}", recommendation.getId(), e);
        }
    }

    public void publishResponsibleGamingAlert(ResponsibleGamingAlert alert) {
        try {
            String topic = kafkaConfig.getTopics().getOutput().getResponsibleGamingAlerts();
            log.debug("Publishing responsible gaming alert to topic {}: {}", topic, alert.getId());
            kafkaTemplate.send(topic, alert.getPlayerId(), alert);
            log.debug("Published responsible gaming alert: {}", alert.getId());
        } catch (Exception e) {
            log.error("Error publishing responsible gaming alert: {}", alert.getId(), e);
        }
    }
}
