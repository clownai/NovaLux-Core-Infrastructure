package com.novalux.coreintegrator.filter;

import org.springframework.cloud.gateway.filter.GatewayFilterChain;
import org.springframework.cloud.gateway.filter.GlobalFilter;
import org.springframework.stereotype.Component;
import org.springframework.web.server.ServerWebExchange;
import reactor.core.publisher.Mono;
import lombok.extern.slf4j.Slf4j;

@Component
@Slf4j
public class LoggingFilter implements GlobalFilter {

    @Override
    public Mono<Void> filter(ServerWebExchange exchange, GatewayFilterChain chain) {
        // Log request details
        log.info("Request: {} {}", 
                exchange.getRequest().getMethod(), 
                exchange.getRequest().getURI());
        
        // Continue the filter chain
        return chain.filter(exchange)
                .then(Mono.fromRunnable(() -> {
                    // Log response details
                    log.info("Response: {} for {} {}", 
                            exchange.getResponse().getStatusCode(),
                            exchange.getRequest().getMethod(),
                            exchange.getRequest().getURI());
                }));
    }
}
