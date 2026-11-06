package com.fintech.riskengine.model;

import jakarta.persistence.*;
import lombok.Data;
import java.math.BigDecimal;
import java.time.LocalDateTime;

@Entity
@Table(name = "transactions")
@Data // Lombok automatically creates all getters, setters, and toString methods behind the scenes!
public class Transaction {

    @Id
    @Column(name = "transaction_id")
    private String transactionId;

    @Column(name = "user_id")
    private Integer userId;

    @Column(name = "amount", nullable = false)
    private BigDecimal amount;

    @Column(name = "currency")
    private String currency = "INR";

    @Column(name = "receiver_account", nullable = false)
    private String receiverAccount;

    @Column(name = "location_country", nullable = false)
    private String locationCountry;

    @Column(name = "timestamp", nullable = false)
    private LocalDateTime timestamp;

    @Column(name = "status")
    private String status = "PENDING";
}
