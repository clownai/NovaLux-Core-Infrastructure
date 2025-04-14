package com.novalux.coreintegrator.filter;

import org.springframework.cloud.gateway.filter.GatewayFilterChain;
import org.springframework.cloud.gateway.filter.GlobalFilter;
import org.springframework.stereotype.Component;
import org.springframework.web.server.ServerWebExchange;
import reactor.core.publisher.Mono;
import lombok.extern.slf4j.Slf4j;

import java.util.UUID;

@Component
@Slf4j
public class RequestTracingFilter implements GlobalFilter {

    private static final String REQUEST_ID_HEADER = "X-Request-ID";
    private static final String TRACE_ID_HEADER = "X-Trace-ID";

    @Override
    public Mono<Void> filter(ServerWebExchange exchange, GatewayFilterChain chain) {
        // Generate or propagate request ID
        String requestId = exchange.getRequest().getHeaders().getFirst(REQUEST_ID_HEADER);
        if (requestId == null || requestId.isEmpty()) {
            requestId = UUID.randomUUID().toString();
        }
        
        // Generate trace ID
        String traceId = UUID.randomUUID().toString();
        
        // Add headers to the request
        exchange = exchange.mutate()
                .request(exchange.getRequest().mutate()
                        .header(REQUEST_ID_HEADER, requestId)
                        .header(TRACE_ID_HEADER, traceId)
                        .build())
                .build();
        
        // Add headers to the response
        return chain.filter(exchange)
                .then(Mono.fromRunnable(() -> {
                    exchange.getResponse().getHeaders().add(REQUEST_ID_HEADER, requestId);
                    exchange.getResponse().getHeaders().add(TRACE_ID_HEADER, traceId);
                }));
    }
}
