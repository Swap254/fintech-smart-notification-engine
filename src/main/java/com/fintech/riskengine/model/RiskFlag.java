package com.fintech.riskengine.model;

import com.fasterxml.jackson.annotation.JsonProperty;
import jakarta.persistence.*;
import lombok.Data;
import java.time.LocalDateTime;

@Entity
@Table(name = "risk_flags")
@Data
public class RiskFlag {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "flag_id")
    private Integer flagId;

    @JsonProperty("transaction_id")
    @Column(name = "transaction_id", nullable = false)
    private String transactionId;

    @JsonProperty("calculated_risk_score")
    @Column(name = "calculated_risk_score", nullable = false)
    private Integer calculatedRiskScore;

    @JsonProperty("flag_reason")
    @Column(name = "flag_reason", nullable = false)
    private String flagReason;

    @Column(name = "flagged_at")
    private LocalDateTime flaggedAt = LocalDateTime.now();
}