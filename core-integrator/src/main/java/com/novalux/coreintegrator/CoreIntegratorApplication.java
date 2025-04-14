package com.novalux.coreintegrator;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.cloud.client.discovery.EnableDiscoveryClient;

@SpringBootApplication
@EnableDiscoveryClient
public class CoreIntegratorApplication {

    public static void main(String[] args) {
        SpringApplication.run(CoreIntegratorApplication.class, args);
    }
}
