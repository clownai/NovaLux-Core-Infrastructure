package com.novalux.adaptivecore.config;

import java.util.List;
import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.context.annotation.Configuration;
import lombok.Data;

@Configuration
@ConfigurationProperties(prefix = "data-pipeline.kafka")
@Data
public class KafkaConfig {
    private String bootstrapServers;
    private String consumerGroup;
    private Topics topics;
    private String autoOffsetReset;
    private int maxPollRecords;
    private String pollTimeout;
    
    @Data
    public static class Topics {
        private List<String> input;
        private Output output;
    }
    
    @Data
    public static class Output {
        private String optimizationEvents;
        private String parameterAdjustments;
    }
}
