package com.novalux.coreintegrator.config;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.cloud.client.loadbalancer.LoadBalanced;
import org.springframework.web.reactive.function.client.WebClient;
import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.boot.context.properties.EnableConfigurationProperties;
import lombok.Data;

@Configuration
@EnableConfigurationProperties
public class ServiceDiscoveryConfig {

    private final ServiceDiscoveryProperties serviceDiscoveryProperties;

    public ServiceDiscoveryConfig(ServiceDiscoveryProperties serviceDiscoveryProperties) {
        this.serviceDiscoveryProperties = serviceDiscoveryProperties;
    }

    @Bean
    @LoadBalanced
    public WebClient.Builder loadBalancedWebClientBuilder() {
        return WebClient.builder();
    }
    
    @Configuration
    @ConfigurationProperties(prefix = "service-discovery")
    @Data
    public static class ServiceDiscoveryProperties {
        private boolean enabled;
        private String refreshInterval;
        private String healthCheckInterval;
    }
}
