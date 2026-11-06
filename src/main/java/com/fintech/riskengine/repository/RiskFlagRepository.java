package com.fintech.riskengine.repository;

import com.fintech.riskengine.model.RiskFlag;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

@Repository
public interface RiskFlagRepository extends JpaRepository<RiskFlag, Long> {
}
