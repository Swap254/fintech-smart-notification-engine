package com.fintech.riskengine.service;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.fintech.riskengine.model.RiskFlag;
import com.fintech.riskengine.repository.RiskFlagRepository;
import io.awspring.cloud.sqs.annotation.SqsListener;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import software.amazon.awssdk.services.sns.SnsClient;
import software.amazon.awssdk.services.sns.model.PublishRequest;

@Service
public class SqsRiskAlertListener {

    @Autowired
    private RiskFlagRepository riskFlagRepository;

    private final ObjectMapper objectMapper = new ObjectMapper();

    // AWS SDK Core Client for broadcasting alerts
    private final SnsClient snsClient = SnsClient.create();

    // Replace with your exact SNS Topic ARN from your AWS console step
    private final String snsTopicArn = "arn:aws:sns:ap-south-1:078127713461:fintech-risk-notifications";

    @SqsListener("${aws.sqs.queue-url}")
    public void listenToRiskAlerts(String messageJson) {
        try {
            RiskFlag alert = objectMapper.readValue(messageJson, RiskFlag.class);
            riskFlagRepository.save(alert);

            System.out.println("📥 Background worker consumed anomaly from SQS: TxID -> " +
                    alert.getTransactionId() + " [Risk Score: " + alert.getCalculatedRiskScore() + "%]");

            // 🛑 CRITICAL ALARM ROUTING LAYER (Amazon SNS)
            // If the risk engine scores the threat at 75% or higher, fire an instant external broadcast alert
            if (alert.getCalculatedRiskScore() >= 75) {
                String alertMessage = String.format(
                        "🚨 CRITICAL FINTECH THREAT DETECTED\n" +
                                "-----------------------------------\n" +
                                "Transaction ID: %s\n" +
                                "Risk Score: %d%%\n" +
                                "Trigger Reason: %s\n",
                        alert.getTransactionId(), alert.getCalculatedRiskScore(), alert.getFlagReason()
                );

                PublishRequest publishRequest = PublishRequest.builder()
                        .topicArn(snsTopicArn)
                        .subject("⚠️ CRITICAL RISK ALERT: " + alert.getTransactionId())
                        .message(alertMessage)
                        .build();

                snsClient.publish(publishRequest);
                System.out.println("⚡ High-Priority alert broadcasted via Amazon SNS to operations email teams!");
            }

        } catch (Exception e) {
            System.err.println("⚠️ Listener processing breakdown: " + e.getMessage());
        }
    }
}
