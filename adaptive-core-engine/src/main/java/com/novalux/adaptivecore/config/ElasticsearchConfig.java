package com.novalux.adaptivecore.config;

import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.context.annotation.Configuration;
import lombok.Data;

@Configuration
@ConfigurationProperties(prefix = "data-pipeline.elasticsearch")
@Data
public class ElasticsearchConfig {
    private String hosts;
    private String indexPrefix;
    private int bulkActions;
    private String bulkSize;
    private String flushInterval;
    private int concurrency;
}
