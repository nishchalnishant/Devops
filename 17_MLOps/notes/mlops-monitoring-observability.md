# MLOps Monitoring & Observability — Deep Dive

## Table of Contents

1. [The Four Layers of ML Observability](#1-the-four-layers-of-ml-observability)
2. [Infrastructure Monitoring](#2-infrastructure-monitoring)
3. [Model Performance Monitoring](#3-model-performance-monitoring)
4. [Data Drift Detection](#4-data-drift-detection)
5. [Concept Drift & Delayed Labels](#5-concept-drift--delayed-labels)
6. [Evidently AI — Drift Analysis](#6-evidently-ai--drift-analysis)
7. [WhyLabs & whylogs](#7-whylabs--whylogs)
8. [Arize AI](#8-arize-ai)
9. [Alerting Strategies](#9-alerting-strategies)
10. [Monitoring Runbooks](#10-monitoring-runbooks)

***

## 1. The Four Layers of ML Observability

ML observability extends beyond traditional application monitoring. You need visibility at four distinct layers:

```
┌─────────────────────────────────────────────────────────────┐
│                    ML OBSERVABILITY STACK                   │
├─────────────────────────────────────────────────────────────┤
│  Layer 4: Business Impact                                   │
│  - Revenue impact, conversion rate, customer churn          │
│  - False positive/negative cost analysis                    │
├─────────────────────────────────────────────────────────────┤
│  Layer 3: Model Performance                                 │
│  - Accuracy, precision, recall, AUC (when labels available) │
│  - Drift scores, confidence distribution                    │
│  - Fairness metrics across demographic groups               │
├─────────────────────────────────────────────────────────────┤
│  Layer 2: Data Quality                                      │
│  - Feature null rates, type violations                      │
│  - Feature freshness (staleness lag)                        │
│  - Schema changes, cardinality shifts                       │
├─────────────────────────────────────────────────────────────┤
│  Layer 1: Infrastructure Health                             │
│  - Endpoint latency (p50, p95, p99)                         │
│  - Error rate (4xx, 5xx)                                    │
│  - Throughput (requests/second)                             │
│  - GPU utilization, memory pressure                         │
└─────────────────────────────────────────────────────────────┘
```

**Key insight:** Infrastructure can be 100% healthy while the model silently degrades. Traditional APM tools (Datadog, New Relic) only cover Layer 1. ML-specific monitoring covers Layers 2-4.

***

## 2. Infrastructure Monitoring

### Critical SLOs for Model Serving

| Metric | Target | Alert Threshold | Why It Matters |
|--------|--------|-----------------|----------------|
| **Latency p99** | < 100ms | > 200ms | User experience, SLA compliance |
| **Error rate** | < 0.1% | > 1% | Service reliability |
| **Throughput** | Baseline + 20% headroom | < 50% baseline | Capacity planning |
| **GPU utilization** | 60-80% (training), 30-50% (inference) | > 90% sustained | Resource saturation |
| **GPU memory** | < 80% | > 90% | OOM risk |
| **Request queue depth** | < 10 | > 50 | Backlog indicator |

### Prometheus Metrics for Model Serving

```yaml
# Custom metrics exposed by model serving endpoint
# Example: KServe /v2/metrics endpoint

# HELP inference_request_duration_seconds Request latency histogram
# TYPE inference_request_duration_seconds histogram
inference_request_duration_seconds_bucket{model="fraud-detector",le="0.05"} 1500
inference_request_duration_seconds_bucket{model="fraud-detector",le="0.1"} 1800
inference_request_duration_seconds_bucket{model="fraud-detector",le="0.5"} 1950
inference_request_duration_seconds_bucket{model="fraud-detector",le="1.0"} 1990
inference_request_duration_seconds_bucket{model="fraud-detector",le="+Inf"} 2000

# HELP inference_predictions_total Total predictions made
# TYPE inference_predictions_total counter
inference_predictions_total{model="fraud-detector",status="success"} 1995
inference_predictions_total{model="fraud-detector",status="error"} 5

# HELP model_prediction_confidence_distribution Model confidence histogram
# TYPE model_prediction_confidence_distribution histogram
model_prediction_confidence_distribution_bucket{model="fraud-detector",le="0.3"} 500
model_prediction_confidence_distribution_bucket{model="fraud-detector",le="0.5"} 800
model_prediction_confidence_distribution_bucket{model="fraud-detector",le="0.7"} 1200
model_prediction_confidence_distribution_bucket{model="fraud-detector",le="1.0"} 2000

# HELP model_input_feature_null_count Null count per feature
# TYPE model_input_feature_null_count gauge
model_input_feature_null_count{model="fraud-detector",feature="user_age"} 0
model_input_feature_null_count{model="fraud-detector",feature="transaction_amount"} 3
```

### Grafana Dashboard Panels

```json
{
  "dashboard": {
    "title": "ML Model Serving — Fraud Detector",
    "panels": [
      {
        "title": "Request Latency (p50, p95, p99)",
        "targets": [
          {
            "expr": "histogram_quantile(0.50, rate(inference_request_duration_seconds_bucket[5m]))",
            "legendFormat": "p50"
          },
          {
            "expr": "histogram_quantile(0.95, rate(inference_request_duration_seconds_bucket[5m]))",
            "legendFormat": "p95"
          },
          {
            "expr": "histogram_quantile(0.99, rate(inference_request_duration_seconds_bucket[5m]))",
            "legendFormat": "p99"
          }
        ]
      },
      {
        "title": "Prediction Confidence Distribution",
        "targets": [
          {
            "expr": "rate(model_prediction_confidence_distribution_bucket[1h])",
            "legendFormat": "{{le}}"
          }
        ]
      },
      {
        "title": "Error Rate by Error Type",
        "targets": [
          {
            "expr": "rate(inference_predictions_total{status=\"error\"}[5m])",
            "legendFormat": "Errors"
          }
        ]
      }
    ]
  }
}
```

***

## 3. Model Performance Monitoring

### Monitoring When Labels Are Available (Real-time)

For use cases with immediate feedback (click prediction, ad CTR, spam detection):

```python
# Real-time accuracy tracking
from collections import deque
import numpy as np

class ModelPerformanceTracker:
    def __init__(self, window_size=1000):
        self.predictions = deque(maxlen=window_size)
        self.labels = deque(maxlen=window_size)
        self.window_size = window_size
    
    def record(self, prediction, label):
        self.predictions.append(prediction)
        self.labels.append(label)
    
    def get_metrics(self):
        if len(self.predictions) < 100:
            return None
        
        y_pred = np.array(self.predictions)
        y_true = np.array(self.labels)
        
        return {
            "accuracy": (y_pred == y_true).mean(),
            "precision": (y_pred[y_true == 1] == 1).mean() if (y_true == 1).sum() > 0 else 0,
            "recall": (y_pred[y_true == 1] == 1).mean() if (y_true == 1).sum() > 0 else 0,
            "sample_count": len(self.predictions),
        }

# Usage in serving code
tracker = ModelPerformanceTracker(window_size=1000)

def predict_and_track(features):
    prediction = model.predict(features)
    # Label arrives asynchronously — record when available
    # tracker.record(prediction, actual_label)
    return prediction
```

### Monitoring with Delayed Labels (Most Common)

For fraud detection (30-day label delay), loan default (90-day), churn (variable):

```python
# Cohort-based tracking
from datetime import datetime, timedelta
import pandas as pd

class CohortTracker:
    def __init__(self):
        self.cohorts = {}  # date → list of (prediction, label, days_since_prediction)
    
    def record_prediction(self, prediction_id, prediction, features, timestamp):
        """Store prediction for later evaluation."""
        cohort_date = timestamp.date()
        if cohort_date not in self.cohorts:
            self.cohorts[cohort_date] = []
        
        self.cohorts[cohort_date].append({
            "prediction_id": prediction_id,
            "prediction": prediction,
            "features": features,
            "timestamp": timestamp,
            "label": None,  # Will be filled when label arrives
        })
    
    def update_labels(self, labeled_data):
        """Update cohort with arrived labels."""
        for row in labeled_data:
            prediction_id = row["prediction_id"]
            label = row["label"]
            
            # Find and update the prediction
            for cohort_date, predictions in self.cohorts.items():
                for pred in predictions:
                    if pred["prediction_id"] == prediction_id:
                        pred["label"] = label
                        break
    
    def get_cohort_metrics(self, cohort_date):
        """Calculate metrics for a specific cohort."""
        cohort = self.cohorts.get(cohort_date, [])
        labeled = [p for p in cohort if p["label"] is not None]
        
        if len(labeled) < 100:
            return None
        
        y_pred = [p["prediction"] for p in labeled]
        y_true = [p["label"] for p in labeled]
        
        return {
            "cohort_date": cohort_date,
            "labeled_count": len(labeled),
            "total_count": len(cohort),
            "label_rate": len(labeled) / len(cohort),
            "accuracy": (np.array(y_pred) == np.array(y_true)).mean(),
        }
    
    def get_trend(self, metric="accuracy", days=30):
        """Get metric trend over last N days."""
        trends = []
        for i in range(days):
            date = datetime.now().date() - timedelta(days=i)
            metrics = self.get_cohort_metrics(date)
            if metrics and metrics.get(metric):
                trends.append({
                    "date": date,
                    metric: metrics[metric],
                })
        return trends
```

***

## 4. Data Drift Detection

### Drift Detection Algorithms

| Algorithm | Best For | Computational Cost | Interpretability |
|-----------|----------|-------------------|------------------|
| **PSI (Population Stability Index)** | Categorical features, binned continuous | Low | High — single score per feature |
| **KS Test (Kolmogorov-Smirnov)** | Continuous features | Low | Medium — test statistic + p-value |
| **Jensen-Shannon Divergence** | Probability distributions | Medium | Medium — 0 to 1 score |
| **Chi-Square Test** | Categorical features | Low | High — p-value |
| **Wasserstein Distance (Earth Mover's)** | Continuous features | Medium | Low — distance in original units |
| **MMD (Maximum Mean Discrepancy)** | High-dimensional features | High | Low — kernel-based |

### PSI Implementation

```python
import numpy as np
import pandas as pd

def calculate_psi(expected, actual, bucket_type="quantile", buckets=10):
    """
    Calculate PSI for a single feature.
    
    expected: array of values from reference (training) distribution
    actual: array of values from current (production) distribution
    bucket_type: "quantile" or "uniform"
    buckets: number of buckets
    """
    if bucket_type == "quantile":
        breakpoints = np.quantile(expected, np.linspace(0, 1, buckets + 1))
    else:
        min_val = min(expected.min(), actual.min())
        max_val = max(expected.max(), actual.max())
        breakpoints = np.linspace(min_val, max_val, buckets + 1)
    
    # Remove duplicate breakpoints
    breakpoints = np.unique(breakpoints)
    
    # Calculate percentages in each bucket
    expected_percents = np.digitize(expected, breakpoints, right=True)
    actual_percents = np.digitize(actual, breakpoints, right=True)
    
    expected_pct = np.bincount(expected_percents, minlength=len(breakpoints)) / len(expected)
    actual_pct = np.bincount(actual_percents, minlength=len(breakpoints)) / len(actual)
    
    # PSI formula: sum((actual - expected) * ln(actual / expected))
    # Add small epsilon to avoid log(0)
    epsilon = 0.0001
    psi = np.sum((actual_pct + epsilon) / (expected_pct + epsilon))
    psi = np.sum((actual_pct - expected_pct) * np.log((actual_pct + epsilon) / (expected_pct + epsilon)))
    
    return psi, expected_pct, actual_pct


def interpret_psi(psi):
    """Interpret PSI score."""
    if psi < 0.1:
        return "Negligible drift"
    elif psi < 0.2:
        return "Moderate drift — investigate"
    else:
        return "Significant drift — consider retraining"


# Example usage
reference_data = pd.read_parquet("s3://data/training/baseline.parquet")
current_data = pd.read_parquet("s3://data/production/last_7_days.parquet")

for feature in ["user_age", "transaction_amount", "merchant_risk_score"]:
    psi, _, _ = calculate_psi(
        reference_data[feature].dropna(),
        current_data[feature].dropna(),
        bucket_type="quantile",
        buckets=10,
    )
    print(f"{feature}: PSI = {psi:.4f} — {interpret_psi(psi)}")
```

### Multi-Feature Drift Dashboard

```python
def calculate_drift_summary(reference_df, current_df, features=None):
    """Calculate drift for all features."""
    if features is None:
        features = reference_df.select_dtypes(include=[np.number]).columns.tolist()
    
    results = []
    for feature in features:
        try:
            psi, _, _ = calculate_psi(
                reference_df[feature].dropna(),
                current_df[feature].dropna(),
            )
            results.append({
                "feature": feature,
                "psi": psi,
                "interpretation": interpret_psi(psi),
            })
        except Exception as e:
            results.append({
                "feature": feature,
                "psi": None,
                "error": str(e),
            })
    
    return pd.DataFrame(results)


# Generate drift report
drift_df = calculate_drift_summary(reference_data, current_data)
print(drift_df.sort_values("psi", ascending=False))
```

***

## 5. Concept Drift & Delayed Labels

### The Delayed Label Problem

This is the core tension in ML monitoring:

```
Timeline:
Day 0: Model makes prediction (fraud/not fraud)
Day 1-29: Waiting for label (investigation, chargeback process)
Day 30: Label arrives (confirmed fraud or not)

Problem: You cannot calculate accuracy on Day 0-29.
         By Day 30, you've made 30 days of potentially bad predictions.
```

### Proxy Metrics (Leading Indicators)

Use these as early warning signals while waiting for true labels:

| Proxy Metric | What It Detects | Implementation |
|--------------|-----------------|----------------|
| **Confidence distribution shift** | Model becoming more/less certain | Track histogram of prediction probabilities |
| **Output entropy** | Model becoming confused | Calculate entropy of prediction distribution |
| **Feature drift** | Input data changing | PSI, KS test on input features |
| **Business KPI movement** | Downstream impact | Chargeback rate, dispute rate, manual review rate |
| **Prediction rate change** | Model behavior shift | % of predictions above threshold |

### Confidence Distribution Monitoring

```python
import numpy as np
from scipy import stats

class ConfidenceMonitor:
    def __init__(self, reference_confidence, window_size=1000):
        self.reference_confidence = reference_confidence  # Array of confidence scores from validation
        self.current_confidence = []
        self.window_size = window_size
    
    def record(self, confidence_score):
        self.current_confidence.append(confidence_score)
        if len(self.current_confidence) > self.window_size:
            self.current_confidence.pop(0)
    
    def get_drift_score(self):
        """KS test between reference and current confidence distribution."""
        if len(self.current_confidence) < 100:
            return None
        
        statistic, pvalue = stats.ks_2samp(self.reference_confidence, self.current_confidence)
        
        return {
            "ks_statistic": statistic,
            "p_value": pvalue,
            "drift_detected": pvalue < 0.05,
            "current_mean_confidence": np.mean(self.current_confidence),
            "reference_mean_confidence": np.mean(self.reference_confidence),
        }
    
    def get_confidence_buckets(self):
        """Bucket predictions by confidence level."""
        if not self.current_confidence:
            return {}
        
        arr = np.array(self.current_confidence)
        return {
            "very_low (< 0.3)": (arr < 0.3).sum(),
            "low (0.3-0.5)": ((arr >= 0.3) & (arr < 0.5)).sum(),
            "medium (0.5-0.7)": ((arr >= 0.5) & (arr < 0.7)).sum(),
            "high (0.7-0.9)": ((arr >= 0.7) & (arr < 0.9)).sum(),
            "very_high (> 0.9)": (arr >= 0.9).sum(),
        }


# Usage
reference_confidence = model.predict_proba(X_val)[:, 1]  # Validation set confidence
monitor = ConfidenceMonitor(reference_confidence)

# In serving code
prediction = model.predict_proba(features)[0]
monitor.record(prediction)

# Check drift every hour
drift_status = monitor.get_drift_score()
if drift_status and drift_status["drift_detected"]:
    alert_team("Confidence distribution drift detected!")
```

### Output Entropy Monitoring

```python
import numpy as np

def calculate_entropy(probabilities):
    """Calculate Shannon entropy of probability distribution."""
    # Avoid log(0)
    probabilities = np.clip(probabilities, 1e-10, 1.0)
    return -np.sum(probabilities * np.log(probabilities))


class EntropyMonitor:
    def __init__(self, reference_entropy_mean, reference_entropy_std):
        self.reference_mean = reference_entropy_mean
        self.reference_std = reference_entropy_std
        self.current_entropies = []
    
    def record(self, probabilities):
        entropy = calculate_entropy(probabilities)
        self.current_entropies.append(entropy)
        
        # Z-score: how many std devs from reference
        z_score = (entropy - self.reference_mean) / self.reference_std
        
        return {
            "entropy": entropy,
            "z_score": z_score,
            "anomaly": abs(z_score) > 3,  # 3 sigma rule
        }


# For binary classification, entropy is highest at 0.5 (maximum uncertainty)
# Low entropy = model is confident (predictions near 0 or 1)
# High entropy = model is uncertain (predictions near 0.5)
```

***

## 6. Evidently AI — Drift Analysis

Evidently AI is the most popular open-source Python library for ML monitoring and drift detection.

### Installation & Setup

```bash
pip install evidently
```

### Data Drift Report

```python
import pandas as pd
from evidently.report import Report
from evidently.metric_preset import DataDriftPreset, DataQualityPreset
from evidently.metrics import ColumnDriftMetric, ColumnQualityMetric

# Load reference (training) and current (production) data
reference_data = pd.read_parquet("s3://data/training/baseline.parquet")
current_data = pd.read_parquet("s3://data/production/last_7_days.parquet")

# Create report with multiple metrics
report = Report(metrics=[
    DataDriftPreset(),  # Drift for all numeric features
    DataQualityPreset(),  # Null rates, type violations, range violations
    ColumnDriftMetric(column_name="user_age"),  # Specific feature drift
    ColumnDriftMetric(column_name="transaction_amount"),
    ColumnQualityMetric(column_name="merchant_category"),  # Categorical quality
])

# Generate report
report.run(reference_data=reference_data, current_data=current_data)

# Save as HTML dashboard
report.save_html("drift_report.html")

# Get programmatic results
result = report.as_dict()

# Extract drift share
drift_share = result["metrics"][0]["result"]["share_of_drifted_columns"]
print(f"Drift share: {drift_share:.2%}")

if drift_share > 0.3:
    print("ALERT: More than 30% of features have drifted!")
```

### Test Suite (for CI/CD gates)

```python
from evidently.test_suite import TestSuite
from evidently.tests import (
    TestColumnDrift,
    TestNumberOfDriftedColumns,
    TestNumberOfDuplicatedColumns,
    TestNumberOfMissingValues,
    TestValueList,
)

# Create test suite for CI/CD gate
suite = TestSuite(tests=[
    TestColumnDrift(column_name="user_age", drift_threshold=0.1),
    TestColumnDrift(column_name="transaction_amount", drift_threshold=0.1),
    TestNumberOfDriftedColumns(num_columns=2),  # Fail if > 2 columns drift
    TestNumberOfMissingValues(),  # Fail if any missing values
])

suite.run(reference_data=reference_data, current_data=current_data)

# Get results
results = suite.as_dict()
for test_result in results["tests"]:
    print(f"{test_result['name']}: {test_result['result']}")

# Exit with error code if tests failed
if any(r["result"] == "fail" for r in results["tests"]):
    exit(1)
```

### Target Drift (Label Drift)

```python
from evidently.metric_preset import TargetDriftPreset

# Detect if prediction distribution is drifting
target_drift_report = Report(metrics=[
    TargetDriftPreset(),
])

target_drift_report.run(
    reference_data=reference_data.assign(prediction=model.predict(reference_data)),
    current_data=current_data.assign(prediction=model.predict(current_data)),
    target_column="prediction",
)

target_drift_report.save_html("target_drift_report.html")
```

***

## 7. WhyLabs & whylogs

whylogs is an open-source library for logging data statistics. WhyLabs is the managed platform for storing and analyzing those logs.

### whylogs Basic Usage

```python
import whylogs as why
import pandas as pd

# Log a dataframe
profile = why.log(df)

# Save profile to file
profile.view().write(path="profile.bin")

# Compare two profiles
reference_profile = why.log(reference_data)
current_profile = why.log(current_data)

# Detect drift
drift_check = current_profile.view().compare(reference_profile.view())
print(drift_check)
```

### WhyLabs Platform Integration

```python
import whylogs as why
from whylogs.api.writer import WhyLabsWriter

# Configure WhyLabs writer
writer = WhyLabsWriter(
    api_key="YOUR_API_KEY",
    organization_id="org-xxx",
    default_dataset_id="model-123",
)

# Log and send to WhyLabs
profile = why.log(df)
profile.writer("whylabs").write()

# Set dataset name and tags
profile.writer("whylabs").option(
    dataset_name="fraud-detector-inputs",
    tags=["production", "v3"],
).write()
```

### WhyLabs Drift Detection

```python
from whylogs.core.constraints import Constraints, MetricsSelector, MetricConstraint

# Define constraints
constraints = Constraints(
    name="Fraud Detector Input Validation",
    constraints=[
        MetricConstraint(
            name="user_age no nulls",
            selector=MetricsSelector(column_name="user_age"),
            metric_name="null_count",
            value=0,
        ),
        MetricConstraint(
            name="transaction_amount range",
            selector=MetricsSelector(column_name="transaction_amount"),
            metric_name="distribution",
            value={"min": 0, "max": 100000},
        ),
    ],
)

# Validate data
profile = why.log(df)
results = constraints.validate(profile.view())
print(results)
```

***

## 8. Arize AI

Arize is a commercial ML observability platform with strong support for deep learning and NLP use cases.

### Arize Key Features

| Feature | Description |
|---------|-------------|
| **Model Performance** | Accuracy, precision, recall, AUC with cohort slicing |
| **Drift Detection** | Automatic drift detection with alerts |
| **Data Quality** | Schema validation, null detection, cardinality monitoring |
| **Root Cause Analysis** | Slice-based debugging to find problem cohorts |
| **LLM Observability** | Token usage, latency, hallucination detection for LLMs |
| **Embedding Analysis** | t-SNE/UMAP visualization of embedding clusters |

### Arize SDK Integration

```python
from arize import phoenix
import pandas as pd

# Log inference data
phoenix.log_inferences(
    dataframe=inference_df,
    model_name="fraud-detector",
    model_version="v3",
    prediction_id_column="prediction_id",
    timestamp_column="timestamp",
    feature_column_names=["user_age", "transaction_amount", "merchant_category"],
    prediction_label_column="prediction",
    actual_label_column="label",  # Optional, for when labels arrive
)

# Create embedding dataset for visualization
phoenix.log_dataset(
    dataframe=embedding_df,
    name="user-embeddings",
    timestamp_column="timestamp",
    embedding_feature_column_names=["embedding_vector"],
    excluded_feature_column_names=["embedding_vector"],
)
```

***

## 9. Alerting Strategies

### Alert Severity Levels

| Severity | Trigger | Response Time | Action |
|----------|---------|---------------|--------|
| **P0 (Critical)** | Model returning errors, latency > 1s, 50%+ drift | Immediate (page) | Rollback to previous model, incident response |
| **P1 (High)** | Drift > 30%, accuracy drop > 10%, feature staleness > 2h | < 4 hours | Investigate, prepare retrain, notify stakeholders |
| **P2 (Medium)** | Drift > 15%, latency p99 > 200ms | < 24 hours | Schedule investigation, monitor trend |
| **P3 (Low)** | Minor metric deviation, single feature drift | Next business day | Add to backlog, review in weekly ML ops meeting |

### Alert Routing

```yaml
# Alertmanager configuration for ML monitoring
groups:
  - name: ml-model-alerts
    rules:
      - alert: HighModelLatency
        expr: histogram_quantile(0.99, rate(inference_request_duration_seconds_bucket[5m])) > 0.5
        for: 5m
        labels:
          severity: P1
          team: ml-platform
        annotations:
          summary: "Model {{ $labels.model }} latency p99 > 500ms"
          description: "Current p99 latency: {{ $value }}s"
      
      - alert: SignificantDataDrift
        expr: drift_score > 0.3
        for: 1h
        labels:
          severity: P1
          team: ml-data-science
        annotations:
          summary: "Data drift detected for model {{ $labels.model }}"
          description: "Drift score: {{ $value }}"
      
      - alert: FeatureStaleness
        expr: time() - feature_last_updated_timestamp > 7200
        for: 15m
        labels:
          severity: P2
          team: ml-data-engineering
        annotations:
          summary: "Feature {{ $labels.feature }} is stale (> 2 hours)"
      
      - alert: ModelAccuracyDrop
        expr: model_accuracy < 0.80
        for: 1h
        labels:
          severity: P1
          team: ml-data-science
        annotations:
          summary: "Model {{ $labels.model }} accuracy dropped below 80%"
          description: "Current accuracy: {{ $value }}"
```

### Runbook Integration

Every alert should link to a runbook:

```yaml
# In alert annotations
annotations:
  summary: "Data drift detected for model {{ $labels.model }}"
  runbook_url: "https://wiki.internal/ml/runbooks/data-drift-response"
  escalation_policy: "ml-oncall-escalation"
```

***

## 10. Monitoring Runbooks

### Runbook: Data Drift Detected

**Trigger:** PSI > 0.2 for any feature, or drift share > 30%

**Step 1: Triage (15 minutes)**
```bash
# Check which features drifted
python -c "
import pandas as pd
from evidently.report import Report
from evidently.metric_preset import DataDriftPreset

ref = pd.read_parquet('s3://data/training/baseline.parquet')
curr = pd.read_parquet('s3://data/production/last_7_days.parquet')

report = Report(metrics=[DataDriftPreset()])
report.run(ref, curr)
result = report.as_dict()

for col, drift in result['metrics'][0]['result']['drift_by_columns'].items():
    print(f'{col}: PSI = {drift[\"psi\"]:.4f}')
"
```

**Step 2: Check upstream data pipelines (30 minutes)**
- Verify no schema changes in upstream data sources
- Check for ETL job failures or data quality issues
- Confirm no recent code deployments changed feature engineering

**Step 3: Assess business impact (30 minutes)**
- Compare prediction distribution before/after drift
- Check business KPIs (conversion rate, chargeback rate) for anomalies
- Sample recent predictions for manual review

**Step 4: Decide response (1 hour)**
| Drift Type | Response |
|------------|----------|
| Upstream data bug | Fix data pipeline, reprocess affected data |
| Genuine distribution shift | Trigger retraining pipeline |
| Seasonal/expected drift | Document, adjust drift thresholds |
| Single outlier feature | Investigate feature specifically, consider removal |

**Step 5: Communicate**
- Update incident ticket
- Notify data science team
- Schedule post-mortem if P0/P1

### Runbook: Model Accuracy Degradation

**Trigger:** Accuracy drops > 10% from baseline

**Step 1: Verify the signal (15 minutes)**
- Confirm labels have arrived (not just delayed labeling)
- Check sample size (need > 100 labeled predictions for statistical significance)
- Rule out data quality issues in label source

**Step 2: Check for training-serving skew (30 minutes)**
```bash
# Compare feature distributions between training and serving
python -c "
import pandas as pd

train = pd.read_parquet('s3://data/training/v3.parquet')
serve = pd.read_parquet('s3://data/production/serving_features.parquet')

for col in train.columns:
    train_mean = train[col].mean()
    serve_mean = serve[col].mean()
    diff = abs(train_mean - serve_mean) / abs(train_mean) * 100
    if diff > 10:
        print(f'{col}: {diff:.1f}% difference (train={train_mean:.2f}, serve={serve_mean:.2f})')
"
```

**Step 3: Analyze by cohort (1 hour)**
- Slice accuracy by demographic groups, geographies, time of day
- Identify if degradation is concentrated in specific segments
- Check for new user segments not represented in training data

**Step 4: Decide response**
| Scenario | Response |
|----------|----------|
| Skew detected | Fix feature engineering, retrain |
| Cohort-specific | Add cohort to training data, retrain with oversampling |
| Global degradation | Concept drift — full retrain with recent data |
| Label quality issue | Work with labeling team to fix label source |

### Runbook: High Inference Latency

**Trigger:** p99 latency > 500ms for 5+ minutes

**Step 1: Check infrastructure (5 minutes)**
```bash
# Check pod status
kubectl get pods -n inference
kubectl describe pod <pod-name> -n inference

# Check GPU utilization
nvidia-smi

# Check request queue
kubectl logs <pod-name> -n inference | grep "queue_depth"
```

**Step 2: Identify bottleneck (10 minutes)**
| Metric | Check |
|--------|-------|
| CPU > 90% | Scale horizontally or increase CPU limits |
| GPU > 90% | Scale horizontally, optimize model |
| Memory > 90% | Increase memory limits, check for memory leak |
| Network I/O saturated | Check VPC bandwidth, consider regional distribution |

**Step 3: Immediate mitigation (15 minutes)**
- Scale up replicas: `kubectl scale deployment fraud-detector --replicas=10`
- Reduce model complexity if possible (smaller model, quantization)
- Enable request batching if not already

**Step 4: Long-term fix**
- Profile model inference to identify slowest operations
- Consider model optimization (pruning, quantization, distillation)
- Implement request prioritization for high-value traffic

***

## Key Gotchas

| Gotcha | Detail |
|--------|--------|
| Monitoring healthy, model wrong | Infrastructure metrics (200 OK, low latency) don't measure prediction correctness |
| Drift detection without baseline | Need to save reference distributions at training time |
| Alert fatigue from noisy drift | Use rolling windows and hysteresis — don't alert on every fluctuation |
| Delayed labels masking problems | Proxy metrics (confidence, entropy) are essential while waiting for labels |
| Feature store staleness | Online store lag causes drift even with Feature Store — monitor freshness |
| Cohort slicing blind spots | Overall accuracy can hide degradation in specific user segments |
| P99 latency spikes | Short windows (1m) can miss — use 5m+ windows for alerting |
