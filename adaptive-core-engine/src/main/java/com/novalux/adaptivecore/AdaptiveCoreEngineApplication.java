package com.novalux.adaptivecore;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.scheduling.annotation.EnableScheduling;

@SpringBootApplication
@EnableScheduling
public class AdaptiveCoreEngineApplication {

    public static void main(String[] args) {
        SpringApplication.run(AdaptiveCoreEngineApplication.class, args);
    }
}
