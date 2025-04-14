package com.novalux.feedbackloop.config;

import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.context.annotation.Configuration;
import lombok.Data;

@Configuration
@ConfigurationProperties(prefix = "adaptive-core")
@Data
public class AdaptiveCoreConfig {
    private String url;
    private String connectionTimeout;
    private String readTimeout;
}
