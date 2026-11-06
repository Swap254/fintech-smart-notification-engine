package com.fintech.riskengine.controller;

import com.fintech.riskengine.model.Transaction;
import com.fintech.riskengine.repository.TransactionRepository;
import com.fintech.riskengine.service.S3StorageService;
import jakarta.persistence.EntityManager;
import jakarta.persistence.PersistenceContext;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.ArrayList;
import java.util.List;

@RestController
@RequestMapping("/api/transactions")
public class TransactionController {

    @Autowired
    private TransactionRepository transactionRepository;

    @Autowired
    private S3StorageService s3StorageService;

    @PersistenceContext
    private EntityManager entityManager;

    @PostMapping("/upload")
    @Transactional // Required to keep the batch transaction block open safely
    public ResponseEntity<String> uploadTransactionFile(@RequestParam("file") MultipartFile file) {
        if (file.isEmpty()) {
            return ResponseEntity.badRequest().body("Error: Please upload a valid transaction file.");
        }

        try {
            // 1. Asynchronously stream file copy to Amazon S3
            String uploadedName = s3StorageService.uploadTransactionFile(file);
            System.out.println("☁️ File successfully pushed to Amazon S3: " + uploadedName);

            // 2. Parse and save rows locally using optimized batch sizes
            try (BufferedReader fileReader = new BufferedReader(new InputStreamReader(file.getInputStream()))) {
                String line;
                boolean isHeader = true;
                int count = 0;
                int batchSize = 500;
                DateTimeFormatter formatter = DateTimeFormatter.ISO_LOCAL_DATE_TIME;

                while ((line = fileReader.readLine()) != null) {
                    if (isHeader) {
                        isHeader = false;
                        continue;
                    }

                    String[] data = line.split(",");
                    if (data.length < 7) continue;

                    Transaction txn = new Transaction();
                    txn.setTransactionId(data[0].trim());
                    txn.setUserId(Integer.parseInt(data[1].trim()));
                    txn.setAmount(new BigDecimal(data[2].trim()));
                    txn.setCurrency(data[3].trim());
                    txn.setReceiverAccount(data[4].trim());
                    txn.setLocationCountry(data[5].trim());
                    txn.setTimestamp(LocalDateTime.parse(data[6].trim(), formatter));
                    txn.setStatus("PENDING");

                    // Use persist to cleanly queue rows directly into the hibernate batch memory space
                    entityManager.persist(txn);
                    count++;

                    // Flush batch segments to the database network layer every 500 rows
                    if (count % batchSize == 0) {
                        entityManager.flush();
                        entityManager.clear();
                    }
                }

                // Flush any remaining trailing records
                entityManager.flush();
                entityManager.clear();

                return ResponseEntity.ok("Successfully batch-stored " + count +
                        " rows locally and triggered Cloud Pipeline! S3 Name: " + uploadedName);
            }

        } catch (Exception e) {
            return ResponseEntity.internalServerError().body("Pipeline Batch Error: " + e.getMessage());
        }
    }
}
