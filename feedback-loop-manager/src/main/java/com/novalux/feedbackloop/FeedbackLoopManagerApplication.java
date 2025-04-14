package com.novalux.feedbackloop;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.scheduling.annotation.EnableScheduling;

@SpringBootApplication
@EnableScheduling
public class FeedbackLoopManagerApplication {

    public static void main(String[] args) {
        SpringApplication.run(FeedbackLoopManagerApplication.class, args);
    }
}
