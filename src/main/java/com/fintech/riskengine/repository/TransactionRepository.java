package com.fintech.riskengine.repository;

import com.fintech.riskengine.model.Transaction;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

@Repository
public interface TransactionRepository extends JpaRepository<Transaction, String> {
    // By extending JpaRepository, Spring automatically gives us access to pre-built methods
    // like .save(), .findById(), .findAll(), and .delete() out of the box!
}
