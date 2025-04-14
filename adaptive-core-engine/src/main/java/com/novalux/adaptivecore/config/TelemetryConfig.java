package com.novalux.adaptivecore.config;

import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.context.annotation.Configuration;
import lombok.Data;

@Configuration
@ConfigurationProperties(prefix = "telemetry")
@Data
public class TelemetryConfig {
    private boolean enabled;
    private double samplingRate;
    private String traceExportInterval;
}
