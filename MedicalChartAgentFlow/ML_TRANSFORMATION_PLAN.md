# ML Transformation Plan: Rule-Based to Deterministic ML Agents

## Executive Summary

This document outlines a strategy to transform the current rule-based Gap Match, Discrepancy, and Decision agents into **deterministic machine learning models** that maintain reproducibility while learning from historical data to improve accuracy.

**Key Principle**: Deterministic ML means same input → same output (no randomness in inference), achieved through:
- Fixed random seeds during training
- Deterministic algorithms (Decision Trees, Gradient Boosting)
- Model versioning and artifact management
- Reproducible feature engineering

---

## 1. Current State Analysis

### 1.1 Gap Match Agent (Rule-Based)
**Current Logic**: [`run_gap_match_agent()`](medchart_demo/agents.py:98)

**Hard-coded weights**:
- ICD Match: 0.5 weight (binary: 1.0 or 0.0)
- Date in Window: 0.4 weight (binary: 1.0 or 0.0)  
- Provider NPI: 0.1 weight (binary: 1.0 or 0.0)

**Limitations**:
- Fixed weights don't adapt to different gap types
- Binary scoring loses nuanced information
- No learning from historical match quality
- Cannot capture feature interactions

**ML Opportunity**: Learn optimal weights and feature interactions from historical data

---

### 1.2 Discrepancy Agent (Rule-Based)
**Current Logic**: [`run_discrepancy_agent()`](medchart_demo/agents.py:130)

**Hard-coded thresholds**:
- HbA1c range: 2-15 (high severity if outside)
- Lab date gap: >365 days (high), >180 days (medium)
- Unknown ICD codes: low severity
- Missing member ID: high severity

**Limitations**:
- Fixed thresholds don't adapt to context
- Cannot detect complex anomaly patterns
- No learning from false positives/negatives
- Limited to predefined checks

**ML Opportunity**: Learn anomaly patterns and severity levels from labeled data

---

### 1.3 Decision Agent (Rule-Based)
**Current Logic**: [`run_decision_agent()`](medchart_demo/agents.py:178)

**Hard-coded penalties and thresholds**:
- High flag: -0.20 penalty
- Medium flag: -0.10 penalty
- Low flag: -0.03 penalty
- Thresholds: ≥0.85 approve, ≤0.40 reject, else manual_review

**Limitations**:
- Fixed penalty weights
- Static thresholds don't adapt
- Cannot learn from reviewer feedback
- No context-aware routing

**ML Opportunity**: Learn optimal routing decisions from historical outcomes

---

## 2. Deterministic ML Architecture

### 2.1 Technology Stack

**Core Libraries**:
- **scikit-learn**: Decision Trees, Random Forests (deterministic with fixed seed)
- **XGBoost/LightGBM**: Gradient Boosting (deterministic mode available)
- **MLflow**: Model versioning, experiment tracking
- **DVC**: Data version control
- **joblib/pickle**: Model serialization

**Why These Are Deterministic**:
- Decision Trees: Deterministic splits based on feature thresholds
- Gradient Boosting: Deterministic with `random_state` and `deterministic_histogram=True`
- No neural networks (inherently less deterministic due to floating-point operations)

### 2.2 Determinism Configuration

```python
# Configuration for deterministic training
DETERMINISTIC_CONFIG = {
    "random_state": 42,  # Fixed seed
    "n_jobs": 1,  # Single thread (parallel can introduce non-determinism)
    "deterministic_histogram": True,  # XGBoost/LightGBM
    "feature_fraction_seed": 42,
    "bagging_seed": 42,
    "drop_seed": 42
}
```

---

## 3. Agent-Specific ML Designs

### 3.1 Gap Match Agent → ML Scorer

#### Feature Engineering

```python
FEATURES = {
    # Binary features (from current rules)
    "icd_exact_match": bool,           # Any required code present
    "date_in_window": bool,            # Visit in gap window
    "npi_present": bool,               # Provider NPI exists
    
    # Numeric features (new)
    "days_from_window_start": int,     # Temporal proximity
    "days_from_window_end": int,
    "num_matching_codes": int,         # Count of matches
    "num_total_codes": int,
    
    # Categorical features (new)
    "gap_type": str,                   # "wellness", "screening", "diabetes"
    "member_age_group": str,           # "18-35", "36-50", "51-65", "65+"
    
    # Interaction features
    "match_ratio": float,              # matching_codes / required_codes
}

TARGET = "gap_closure_score"  # 0.0 to 1.0 (from historical data)
```

#### Model Architecture

```python
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.pipeline import Pipeline

gap_match_model = Pipeline([
    ("preprocessor", preprocessor),
    ("regressor", GradientBoostingRegressor(
        n_estimators=100,
        max_depth=5,
        learning_rate=0.1,
        random_state=42,
        loss="squared_error"
    ))
])
```

---

### 3.2 Discrepancy Agent → ML Anomaly Detector

#### Feature Engineering

```python
ANOMALY_FEATURES = {
    # Lab value features
    "hba1c_value": float,
    "hba1c_zscore": float,              # Standardized value
    "hba1c_missing": bool,
    
    # Temporal features
    "lab_visit_gap_days": int,
    "visit_date_month": int,
    
    # Code features
    "num_icd_codes": int,
    "num_unknown_codes": int,
    
    # Completeness features
    "member_id_present": bool,
    "npi_present": bool,
    "num_missing_fields": int,
}

TARGETS = {
    "has_anomaly": bool,                # Binary: any anomaly?
    "severity": str,                    # "none", "low", "medium", "high"
}
```

#### Model Architecture

```python
from sklearn.ensemble import RandomForestClassifier

# Binary anomaly detection
anomaly_detector = RandomForestClassifier(
    n_estimators=200,
    max_depth=10,
    min_samples_split=20,
    random_state=42,
    class_weight="balanced"
)

# Severity classification
severity_classifier = GradientBoostingClassifier(
    n_estimators=100,
    max_depth=5,
    random_state=42
)
```

---

### 3.3 Decision Agent → ML Router

#### Feature Engineering

```python
ROUTING_FEATURES = {
    # From Gap Match Agent
    "gap_match_score": float,
    "icd_match": bool,
    "date_match": bool,
    
    # From Discrepancy Agent
    "has_anomaly": bool,
    "anomaly_severity": str,
    "num_high_flags": int,
    "num_medium_flags": int,
    "num_low_flags": int,
    
    # Contextual features
    "gap_type": str,
    "chart_complexity": float,
}

TARGET = "routing_decision"  # "approved", "rejected", "manual_review"
```

#### Model Architecture

```python
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.calibration import CalibratedClassifierCV

# Base classifier with calibration for reliable probabilities
decision_router = CalibratedClassifierCV(
    GradientBoostingClassifier(
        n_estimators=150,
        max_depth=6,
        learning_rate=0.05,
        random_state=42
    ),
    method="isotonic",
    cv=5
)
```

---

## 4. Training Data Requirements

### 4.1 Data Collection Strategy

```python
# Historical data extraction
DATA_SOURCES = {
    "production_logs": {
        "location": "database.validation_results",
        "fields": ["chart_id", "extracted_data", "gap_result", "flags", "decision"],
        "date_range": "last_12_months"
    },
    
    "manual_reviews": {
        "location": "database.manual_reviews",
        "fields": ["chart_id", "reviewer_id", "final_decision", "notes"],
        "date_range": "last_12_months"
    }
}

# Minimum data requirements
MIN_SAMPLES = 1000  # Per gap type
MIN_POSITIVE_SAMPLES = 100  # Approved cases
MIN_NEGATIVE_SAMPLES = 100  # Rejected cases
```

### 4.2 Active Learning for Efficient Labeling

```python
class ActiveLearningLabeler:
    def select_for_labeling(self, unlabeled_data, n_samples=100):
        """Select most informative samples for labeling"""
        predictions = self.model.predict_proba(unlabeled_data)
        
        # Uncertainty sampling: select cases with low confidence
        max_proba = predictions.max(axis=1)
        uncertainty = 1 - max_proba
        
        # Select top uncertain cases
        uncertain_indices = uncertainty.argsort()[-n_samples:]
        return unlabeled_data.iloc[uncertain_indices]
```

---

## 5. Model Training Pipeline

### 5.1 Deterministic Training

```python
import mlflow
import joblib
import hashlib

class DeterministicTrainingPipeline:
    def train(self, X, y, model, hyperparameters):
        """Deterministic training with full reproducibility"""
        
        with mlflow.start_run():
            # Log parameters
            mlflow.log_params(hyperparameters)
            mlflow.log_param("random_state", 42)
            
            # Split data (deterministic)
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42, stratify=y
            )
            
            # Train model
            model.fit(X_train, y_train)
            
            # Evaluate
            train_score = model.score(X_train, y_train)
            test_score = model.score(X_test, y_test)
            
            # Log metrics
            mlflow.log_metric("train_score", train_score)
            mlflow.log_metric("test_score", test_score)
            
            # Save model with hash
            model_path = f"models/{self.model_name}_v{version}.pkl"
            joblib.dump(model, model_path)
            model_hash = self.compute_hash(model_path)
            mlflow.log_param("model_hash", model_hash)
            
            return model, model_hash
```

---

## 6. Model Versioning & Reproducibility

### 6.1 Model Registry

```python
class ModelRegistry:
    """Centralized model version management"""
    
    def register_model(self, model_name, version, metadata):
        """Register a new model version"""
        entry = {
            "model_name": model_name,
            "version": version,
            "timestamp": datetime.now().isoformat(),
            "model_hash": metadata["model_hash"],
            "training_data_hash": metadata["data_hash"],
            "hyperparameters": metadata["hyperparameters"],
            "metrics": metadata["metrics"],
            "random_state": metadata["random_state"]
        }
        
        self.registry[f"{model_name}_{version}"] = entry
        return entry
    
    def get_model(self, model_name, version="latest"):
        """Retrieve model by name and version"""
        entry = self.registry[f"{model_name}_{version}"]
        model_path = f"models/{model_name}_v{version}.pkl"
        
        # Verify hash
        current_hash = self.compute_hash(model_path)
        if current_hash != entry["model_hash"]:
            raise ValueError("Model hash mismatch! File may be corrupted.")
        
        return joblib.load(model_path), entry
```

---

## 7. Inference Pipeline

### 7.1 ML-Based Agents

```python
class MLGapMatchAgent:
    """ML-based Gap Match Agent"""
    
    def __init__(self, model_version):
        self.model, self.metadata = ModelRegistry().get_model(
            "gap_match_agent", model_version
        )
    
    def predict(self, extracted_data, gap_row):
        """Deterministic prediction"""
        features = self.extract_features(extracted_data, gap_row)
        score = self.model.predict([features])[0]
        
        return {
            "composite": round(float(score), 2),
            "model_version": self.metadata["version"],
            "prediction_timestamp": datetime.now().isoformat()
        }


class MLDecisionAgent:
    """ML-based Decision Agent"""
    
    def decide(self, gap_result, flags, extracted_data):
        """Deterministic routing decision"""
        features = self.extract_features(gap_result, flags, extracted_data)
        
        decision = self.model.predict([features])[0]
        probabilities = self.model.predict_proba([features])[0]
        confidence = probabilities.max()
        
        return {
            "decision": decision,
            "confidence": round(float(confidence), 2),
            "probabilities": {
                "approved": round(float(probabilities[0]), 2),
                "rejected": round(float(probabilities[1]), 2),
                "manual_review": round(float(probabilities[2]), 2)
            },
            "model_version": self.metadata["version"]
        }
```

### 7.2 Hybrid Agent with Fallback

```python
class HybridAgent:
    """Hybrid agent with ML primary and rule-based fallback"""
    
    def __init__(self, ml_agent, rule_agent, confidence_threshold=0.7):
        self.ml_agent = ml_agent
        self.rule_agent = rule_agent
        self.threshold = confidence_threshold
    
    def predict(self, *args, **kwargs):
        """Use ML if confident, otherwise fallback to rules"""
        try:
            ml_result = self.ml_agent.predict(*args, **kwargs)
            
            if ml_result.get("confidence", 1.0) >= self.threshold:
                ml_result["method"] = "ml"
                return ml_result
            else:
                rule_result = self.rule_agent.predict(*args, **kwargs)
                rule_result["method"] = "rule_fallback"
                return rule_result
                
        except Exception as e:
            rule_result = self.rule_agent.predict(*args, **kwargs)
            rule_result["method"] = "rule_error_fallback"
            return rule_result
```

---

## 8. Model Evaluation

### 8.1 Evaluation Metrics

```python
class ModelEvaluator:
    def evaluate_gap_match_agent(self, y_true, y_pred):
        """Evaluate regression model"""
        return {
            "mse": mean_squared_error(y_true, y_pred),
            "rmse": mean_squared_error(y_true, y_pred, squared=False),
            "mae": mean_absolute_error(y_true, y_pred),
            "r2": r2_score(y_true, y_pred)
        }
    
    def evaluate_decision_agent(self, y_true, y_pred):
        """Evaluate classification model"""
        return {
            "accuracy": accuracy_score(y_true, y_pred),
            "precision": precision_score(y_true, y_pred, average="weighted"),
            "recall": recall_score(y_true, y_pred, average="weighted"),
            "f1": f1_score(y_true, y_pred, average="weighted"),
            "confusion_matrix": confusion_matrix(y_true, y_pred).tolist()
        }
```

### 8.2 A/B Testing

```python
class ABTestFramework:
    """A/B test ML vs rule-based agents"""
    
    def route_request(self, request_id, split_ratio=0.5):
        """Deterministically route to A or B based on ID"""
        hash_value = int(hashlib.md5(request_id.encode()).hexdigest(), 16)
        return "ml" if (hash_value % 100) < (split_ratio * 100) else "rule"
    
    def analyze_results(self, results_df):
        """Compare ML vs rule-based performance"""
        ml_results = results_df[results_df["ab_group"] == "ml"]
        rule_results = results_df[results_df["ab_group"] == "rule"]
        
        return {
            "ml_accuracy": ml_results["correct"].mean(),
            "rule_accuracy": rule_results["correct"].mean(),
            "ml_review_rate": (ml_results["decision"] == "manual_review").mean(),
            "rule_review_rate": (rule_results["decision"] == "manual_review").mean()
        }
```

---

## 9. Migration Path

### 9.1 Phased Rollout

**Phase 1: Data Collection (Weeks 1-4)**
- Deploy logging infrastructure
- Collect 1000+ labeled samples per agent
- Implement active learning labeling queue
- Validate data quality

**Phase 2: Model Training (Weeks 5-8)**
- Train initial models
- Hyperparameter tuning
- Cross-validation
- Model versioning setup

**Phase 3: Shadow Mode (Weeks 9-12)**
- Run ML models in parallel with rules
- Compare predictions (no production impact)
- Collect performance metrics
- Identify edge cases

**Phase 4: A/B Testing (Weeks 13-16)**
- Route 10% traffic to ML models
- Monitor metrics closely
- Gradually increase to 50%
- Collect user feedback

**Phase 5: Full Deployment (Week 17+)**
- Switch to ML as primary
- Keep rules as fallback
- Continuous monitoring
- Regular retraining

### 9.2 Implementation Checklist

**Infrastructure**:
- ✅ Set up MLflow tracking server
- ✅ Configure model registry
- ✅ Set up DVC for data versioning
- ✅ Create training pipeline
- ✅ Set up monitoring dashboards

**Data**:
- ✅ Extract historical data
- ✅ Label training samples
- ✅ Validate data quality
- ✅ Create train/test splits
- ✅ Version control datasets

**Models**:
- ✅ Train Gap Match Agent
- ✅ Train Discrepancy Agent
- ✅ Train Decision Agent
- ✅ Validate model performance
- ✅ Register model versions

**Deployment**:
- ✅ Implement inference pipeline
- ✅ Add fallback logic
- ✅ Set up A/B testing
- ✅ Configure monitoring
- ✅ Document API changes

---

## 10. Monitoring & Maintenance

### 10.1 Model Monitoring

```python
class ModelMonitor:
    """Monitor ML model performance in production"""
    
    def detect_drift(self, window_size=1000):
        """Detect feature or prediction drift"""
        recent_data = self.metrics_store.get_recent(window_size)
        baseline_data = self.metrics_store.get_baseline()
        
        # Feature drift (KS test)
        feature_drift = self.compute_feature_drift(recent_data, baseline_data)
        
        # Prediction drift
        prediction_drift = self.compute_prediction_drift(recent_data, baseline_data)
        
        if feature_drift > 0.1 or prediction_drift > 0.1:
            self.trigger_retraining_alert()
        
        return {
            "feature_drift": feature_drift,
            "prediction_drift": prediction_drift,
            "requires_retraining": feature_drift > 0.1 or prediction_drift > 0.1
        }
```

### 10.2 Retraining Strategy

```python
class AutoRetrainingPipeline:
    """Automated model retraining"""
    
    def should_retrain(self):
        """Determine if retraining is needed"""
        drift_metrics = self.monitor.detect_drift()
        recent_accuracy = self.monitor.get_recent_accuracy()
        baseline_accuracy = self.monitor.get_baseline_accuracy()
        new_samples = self.monitor.count_new_labeled_samples()
        
        return (
            drift_metrics["requires_retraining"] or
            recent_accuracy < baseline_accuracy - 0.05 or
            new_samples > 1000
        )
```

---

## 11. Cost-Benefit Analysis

### 11.1 Development Costs

| Phase | Effort (weeks) | Cost Estimate |
|-------|---------------|---------------|
| Data Collection | 4 | $20,000 |
| Model Development | 4 | $30,000 |
| Testing & Validation | 4 | $35,000 |
| Deployment | 2 | $15,000 |
| **Total** | **14 weeks** | **$100,000** |

### 11.2 Expected Benefits

| Benefit | Current | ML-Based | Improvement |
|---------|---------|----------|-------------|
| Accuracy | 85% | 92% | +7% |
| Manual Review Rate | 25% | 15% | -10% |
| Processing Time | 2 min/chart | 1.5 min/chart | -25% |
| False Approvals | 5% | 2% | -60% |

### 11.3 ROI Calculation

Assuming 10,000 charts/month:
- **Monthly time savings**: $4,167
- **Reduced manual reviews**: $10,000
- **Total monthly savings**: $14,167
- **Payback period**: 7.1 months
- **Annual ROI**: 70%

---

## 12. Success Criteria

### Technical Metrics
- **Determinism**: 100% reproducible predictions
- **Accuracy**: >90% on test set
- **Latency**: <100ms per prediction
- **Model size**: <50MB per model

### Business Metrics
- **Manual review reduction**: >10%
- **False approval reduction**: >50%
- **User satisfaction**: >4.0/5.0
- **ROI**: >200% in first year

### Operational Metrics
- **Uptime**: >99.9%
- **Fallback rate**: <1%
- **Retraining frequency**: Monthly
- **Monitoring coverage**: 100%

---

## 13. Conclusion

This plan provides a comprehensive roadmap for transforming your rule-based agents into **deterministic ML models** that:

✅ **Maintain reproducibility** through fixed seeds and versioning  
✅ **Learn from data** to improve accuracy over time  
✅ **Preserve explainability** with feature importance and confidence scores  
✅ **Enable gradual migration** through shadow mode and A/B testing  
✅ **Support continuous improvement** with monitoring and retraining  

**Key Advantages of ML Approach**:
- Adaptive to changing patterns
- Better handling of edge cases
- Reduced manual review burden
- Continuous learning from feedback
- Quantifiable confidence scores

**Recommended Starting Point**: Begin with the **Gap Match Agent** as it has the clearest success metrics and simplest feature engineering requirements.

---

## Appendix: Quick Start Guide

### Step 1: Set Up Environment

```bash
# Install dependencies
pip install scikit-learn==1.3.2 xgboost==2.0.3 mlflow==2.9.2 joblib==1.3.2

# Initialize MLflow
mlflow server --backend-store-uri sqlite:///mlflow.db --default-artifact-root ./mlruns
```

### Step 2: Extract Training Data

```python
# Extract historical data
from db import get_db_connection

conn = get_db_connection()
training_data = pd.read_sql("""
    SELECT * FROM validation_results 
    WHERE created_at >= DATE('now', '-12 months')
""", conn)
```

### Step 3: Train First Model

```python
# Train Gap Match Agent
from sklearn.ensemble import GradientBoostingRegressor

model = GradientBoostingRegressor(
    n_estimators=100,
    max_depth=5,
    random_state=42
)

model.fit(X_train, y_train)
joblib.dump(model, 'models/gap_match_v1.0.0.pkl')
```

### Step 4: Deploy in Shadow Mode

```python
# Run both models in parallel
ml_result = ml_agent.predict(data)
rule_result = rule_agent.predict(data)

# Log comparison
log_comparison(ml_result, rule_result, ground_truth)
```

---

**Document Version**: 1.0  
**Last Updated**: 2026-04-10  
**Author**: Bob (Plan Mode)