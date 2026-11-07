# Classifier comparison (decision D-018)

500 development tickets, 341 different questions. Main test: 5-fold group cross-validation, identical questions never split between training and testing. Stress test: rewordings kept together too (73 groups), so whole questions are unseen. Probabilities calibrated by temperature scaling learned inside each training fold. Seed 42.

| Features | C | Type accuracy | Type precision (weighted) [95% CI] | Type precision (macro) | Type recall (macro) | Urgency accuracy | Largest calibration gap | Stress test: type accuracy |
|---|---|---|---|---|---|---|---|---|
| tfidf | 1 | 99.2% | 99.3% [98.5%, 99.8%] | 99.3% | 98.7% | 49.6% | 26.7 points | 34.8% |
| tfidf | 10 | 99.6% | 99.6% [99.1%, 100.0%] | 99.6% | 99.4% | 48.0% | 0.0 points | 51.2% |
| embeddings | 1 | 96.4% | 97.0% [95.9%, 98.2%] | 97.2% | 95.6% | 51.8% | 12.9 points | 66.2% |
| embeddings | 10 | 99.0% | 99.1% [98.4%, 99.8%] | 99.2% | 99.0% | 49.6% | 0.6 points | 77.6% |

## Safety rules (FR-03), development tickets

- Person-only tickets (must-not labels, data location, leaked keys): 122
- Caught by the word rules alone: 107 (87.7%)
- Missed by the word rules but of a person-only type (caught if the classifier is right): 15
- Missed by both word rules and type: 0 []
- Safe tickets flagged by the word rules (false alarms, sent to a person unnecessarily): 12 of 378 (3.2%)

False alarms (first 10):

- DEV-0050 (billing_query): ['billing dispute'] - Question about this month's charges. invoice showing service we not use. can you check and tell?
- DEV-0073 (billing_query): ['billing dispute'] - Invoice higher than expected. There are charges on our invoice for a service I do not believe we use. Could you explain 
- DEV-0078 (billing_query): ['billing dispute'] - There are charges on our invoice for a service I do not believe we use. Could you explain what these relate to?
- DEV-0079 (billing_query): ['billing dispute'] - invoice showing service we not use. can you check and tell?
- DEV-0151 (billing_query): ['billing dispute'] - Invoice higher than expected. There are charges on our invoice for a service I do not believe we use. Could you explain 
- DEV-0189 (billing_query): ['billing dispute'] - There are charges on our invoice for a service I do not believe we use. Could you explain what these relate to?
- DEV-0228 (billing_query): ['billing dispute'] - Invoice higher than expected. invoice showing service we not use. can you check and tell?
- DEV-0284 (billing_query): ['billing dispute'] - Question about this month's charges. there charges on our invoice for a service i am not believe we use. Can you please 
- DEV-0411 (billing_query): ['billing dispute'] - Billing period dates unclear. There are charges on our invoice for a service I do not believe we use. Could you explain 
- DEV-0415 (billing_query): ['billing dispute'] - Question about this month's charges. There are charges on our invoice for a service I do not believe we use. Could you e

## tfidf, C = 1

Calibration (Evaluation Framework):

| Band | Tickets | Stated confidence | Observed accuracy | Gap |
|---|---|---|---|---|
| 0.0-0.2 | 1 | 16.4% | 0.0% | +16.4 points |
| 0.2-0.4 | 2 | 23.9% | 0.0% | +23.9 points |
| 0.4-0.6 | 4 | 48.0% | 75.0% | -27.0 points |
| 0.6-0.8 | 10 | 73.3% | 100.0% | -26.7 points |
| 0.8-1.0 | 483 | 99.7% | 100.0% | -0.3 points |

```
                         precision    recall  f1-score   support

         account_access      1.000     1.000     1.000        22
          api_key_issue      1.000     1.000     1.000        18
     api_usage_question      1.000     1.000     1.000        24
 authentication_failure      0.909     1.000     0.952        20
          billing_query      1.000     1.000     1.000        24
     compliance_request      1.000     1.000     1.000        26
     configuration_help      1.000     1.000     1.000        17
            data_export      1.000     1.000     1.000        29
         data_residency      1.000     1.000     1.000        29
         database_issue      0.963     1.000     0.981        26
     deployment_failure      1.000     1.000     1.000        27
        feature_request      1.000     1.000     1.000        20
       integration_help      1.000     1.000     1.000        21
             onboarding      1.000     1.000     1.000        22
performance_degradation      1.000     1.000     1.000        23
       quota_or_overage      1.000     1.000     1.000        23
             rate_limit      1.000     0.769     0.870        13
       rollback_request      1.000     1.000     1.000        28
      security_incident      1.000     1.000     1.000        26
      sso_configuration      0.963     1.000     0.981        26
        unclear_request      1.000     1.000     1.000        15
          webhook_issue      1.000     0.952     0.976        21

               accuracy                          0.992       500
              macro avg      0.993     0.987     0.989       500
           weighted avg      0.993     0.992     0.992       500

```

Confusion matrix (rows = true type, columns = predicted, in sorted type order):

```
[[22  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0]
 [ 0 18  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0]
 [ 0  0 24  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0]
 [ 0  0  0 20  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0]
 [ 0  0  0  0 24  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0]
 [ 0  0  0  0  0 26  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0]
 [ 0  0  0  0  0  0 17  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0]
 [ 0  0  0  0  0  0  0 29  0  0  0  0  0  0  0  0  0  0  0  0  0  0]
 [ 0  0  0  0  0  0  0  0 29  0  0  0  0  0  0  0  0  0  0  0  0  0]
 [ 0  0  0  0  0  0  0  0  0 26  0  0  0  0  0  0  0  0  0  0  0  0]
 [ 0  0  0  0  0  0  0  0  0  0 27  0  0  0  0  0  0  0  0  0  0  0]
 [ 0  0  0  0  0  0  0  0  0  0  0 20  0  0  0  0  0  0  0  0  0  0]
 [ 0  0  0  0  0  0  0  0  0  0  0  0 21  0  0  0  0  0  0  0  0  0]
 [ 0  0  0  0  0  0  0  0  0  0  0  0  0 22  0  0  0  0  0  0  0  0]
 [ 0  0  0  0  0  0  0  0  0  0  0  0  0  0 23  0  0  0  0  0  0  0]
 [ 0  0  0  0  0  0  0  0  0  0  0  0  0  0  0 23  0  0  0  0  0  0]
 [ 0  0  0  2  0  0  0  0  0  0  0  0  0  0  0  0 10  0  0  1  0  0]
 [ 0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0 28  0  0  0  0]
 [ 0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0 26  0  0  0]
 [ 0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0 26  0  0]
 [ 0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0 15  0]
 [ 0  0  0  0  0  0  0  0  0  1  0  0  0  0  0  0  0  0  0  0  0 20]]
```

## tfidf, C = 10

Calibration (Evaluation Framework):

| Band | Tickets | Stated confidence | Observed accuracy | Gap |
|---|---|---|---|---|
| 0.0-0.2 | 1 | 14.6% | 0.0% | +14.6 points |
| 0.4-0.6 | 3 | 52.4% | 66.7% | -14.3 points |
| 0.8-1.0 | 496 | 100.0% | 100.0% | -0.0 points |

```
                         precision    recall  f1-score   support

         account_access      1.000     1.000     1.000        22
          api_key_issue      1.000     1.000     1.000        18
     api_usage_question      1.000     1.000     1.000        24
 authentication_failure      1.000     1.000     1.000        20
          billing_query      1.000     1.000     1.000        24
     compliance_request      1.000     1.000     1.000        26
     configuration_help      1.000     1.000     1.000        17
            data_export      1.000     1.000     1.000        29
         data_residency      1.000     1.000     1.000        29
         database_issue      0.963     1.000     0.981        26
     deployment_failure      1.000     1.000     1.000        27
        feature_request      1.000     1.000     1.000        20
       integration_help      1.000     1.000     1.000        21
             onboarding      1.000     1.000     1.000        22
performance_degradation      0.958     1.000     0.979        23
       quota_or_overage      1.000     1.000     1.000        23
             rate_limit      1.000     0.923     0.960        13
       rollback_request      1.000     1.000     1.000        28
      security_incident      1.000     1.000     1.000        26
      sso_configuration      1.000     1.000     1.000        26
        unclear_request      1.000     1.000     1.000        15
          webhook_issue      1.000     0.952     0.976        21

               accuracy                          0.996       500
              macro avg      0.996     0.994     0.995       500
           weighted avg      0.996     0.996     0.996       500

```

Confusion matrix (rows = true type, columns = predicted, in sorted type order):

```
[[22  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0]
 [ 0 18  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0]
 [ 0  0 24  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0]
 [ 0  0  0 20  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0]
 [ 0  0  0  0 24  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0]
 [ 0  0  0  0  0 26  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0]
 [ 0  0  0  0  0  0 17  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0]
 [ 0  0  0  0  0  0  0 29  0  0  0  0  0  0  0  0  0  0  0  0  0  0]
 [ 0  0  0  0  0  0  0  0 29  0  0  0  0  0  0  0  0  0  0  0  0  0]
 [ 0  0  0  0  0  0  0  0  0 26  0  0  0  0  0  0  0  0  0  0  0  0]
 [ 0  0  0  0  0  0  0  0  0  0 27  0  0  0  0  0  0  0  0  0  0  0]
 [ 0  0  0  0  0  0  0  0  0  0  0 20  0  0  0  0  0  0  0  0  0  0]
 [ 0  0  0  0  0  0  0  0  0  0  0  0 21  0  0  0  0  0  0  0  0  0]
 [ 0  0  0  0  0  0  0  0  0  0  0  0  0 22  0  0  0  0  0  0  0  0]
 [ 0  0  0  0  0  0  0  0  0  0  0  0  0  0 23  0  0  0  0  0  0  0]
 [ 0  0  0  0  0  0  0  0  0  0  0  0  0  0  0 23  0  0  0  0  0  0]
 [ 0  0  0  0  0  0  0  0  0  0  0  0  0  0  1  0 12  0  0  0  0  0]
 [ 0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0 28  0  0  0  0]
 [ 0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0 26  0  0  0]
 [ 0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0 26  0  0]
 [ 0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0 15  0]
 [ 0  0  0  0  0  0  0  0  0  1  0  0  0  0  0  0  0  0  0  0  0 20]]
```

## embeddings, C = 1

Calibration (Evaluation Framework):

| Band | Tickets | Stated confidence | Observed accuracy | Gap |
|---|---|---|---|---|
| 0.2-0.4 | 2 | 36.3% | 0.0% | +36.3 points |
| 0.4-0.6 | 8 | 47.1% | 62.5% | -15.4 points |
| 0.6-0.8 | 17 | 71.7% | 58.8% | +12.9 points |
| 0.8-1.0 | 473 | 98.9% | 98.7% | +0.2 points |

```
                         precision    recall  f1-score   support

         account_access      0.880     1.000     0.936        22
          api_key_issue      1.000     0.833     0.909        18
     api_usage_question      1.000     0.875     0.933        24
 authentication_failure      1.000     1.000     1.000        20
          billing_query      0.923     1.000     0.960        24
     compliance_request      0.929     1.000     0.963        26
     configuration_help      1.000     1.000     1.000        17
            data_export      0.906     1.000     0.951        29
         data_residency      1.000     1.000     1.000        29
         database_issue      1.000     0.885     0.939        26
     deployment_failure      1.000     1.000     1.000        27
        feature_request      1.000     0.900     0.947        20
       integration_help      1.000     1.000     1.000        21
             onboarding      1.000     1.000     1.000        22
performance_degradation      0.742     1.000     0.852        23
       quota_or_overage      1.000     0.913     0.955        23
             rate_limit      1.000     0.615     0.762        13
       rollback_request      1.000     1.000     1.000        28
      security_incident      1.000     1.000     1.000        26
      sso_configuration      1.000     1.000     1.000        26
        unclear_request      1.000     1.000     1.000        15
          webhook_issue      1.000     1.000     1.000        21

               accuracy                          0.964       500
              macro avg      0.972     0.956     0.959       500
           weighted avg      0.970     0.964     0.964       500

```

Confusion matrix (rows = true type, columns = predicted, in sorted type order):

```
[[22  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0]
 [ 3 15  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0]
 [ 0  0 21  0  0  0  0  3  0  0  0  0  0  0  0  0  0  0  0  0  0  0]
 [ 0  0  0 20  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0]
 [ 0  0  0  0 24  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0]
 [ 0  0  0  0  0 26  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0]
 [ 0  0  0  0  0  0 17  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0]
 [ 0  0  0  0  0  0  0 29  0  0  0  0  0  0  0  0  0  0  0  0  0  0]
 [ 0  0  0  0  0  0  0  0 29  0  0  0  0  0  0  0  0  0  0  0  0  0]
 [ 0  0  0  0  0  0  0  0  0 23  0  0  0  0  3  0  0  0  0  0  0  0]
 [ 0  0  0  0  0  0  0  0  0  0 27  0  0  0  0  0  0  0  0  0  0  0]
 [ 0  0  0  0  0  2  0  0  0  0  0 18  0  0  0  0  0  0  0  0  0  0]
 [ 0  0  0  0  0  0  0  0  0  0  0  0 21  0  0  0  0  0  0  0  0  0]
 [ 0  0  0  0  0  0  0  0  0  0  0  0  0 22  0  0  0  0  0  0  0  0]
 [ 0  0  0  0  0  0  0  0  0  0  0  0  0  0 23  0  0  0  0  0  0  0]
 [ 0  0  0  0  2  0  0  0  0  0  0  0  0  0  0 21  0  0  0  0  0  0]
 [ 0  0  0  0  0  0  0  0  0  0  0  0  0  0  5  0  8  0  0  0  0  0]
 [ 0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0 28  0  0  0  0]
 [ 0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0 26  0  0  0]
 [ 0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0 26  0  0]
 [ 0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0 15  0]
 [ 0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0 21]]
```

## embeddings, C = 10

Calibration (Evaluation Framework):

| Band | Tickets | Stated confidence | Observed accuracy | Gap |
|---|---|---|---|---|
| 0.4-0.6 | 6 | 49.6% | 66.7% | -17.1 points |
| 0.6-0.8 | 8 | 71.1% | 62.5% | +8.6 points |
| 0.8-1.0 | 486 | 99.4% | 100.0% | -0.6 points |

```
                         precision    recall  f1-score   support

         account_access      1.000     1.000     1.000        22
          api_key_issue      1.000     1.000     1.000        18
     api_usage_question      1.000     0.875     0.933        24
 authentication_failure      1.000     1.000     1.000        20
          billing_query      1.000     1.000     1.000        24
     compliance_request      0.929     1.000     0.963        26
     configuration_help      1.000     1.000     1.000        17
            data_export      0.906     1.000     0.951        29
         data_residency      1.000     1.000     1.000        29
         database_issue      1.000     1.000     1.000        26
     deployment_failure      1.000     1.000     1.000        27
        feature_request      1.000     0.900     0.947        20
       integration_help      1.000     1.000     1.000        21
             onboarding      1.000     1.000     1.000        22
performance_degradation      1.000     1.000     1.000        23
       quota_or_overage      1.000     1.000     1.000        23
             rate_limit      1.000     1.000     1.000        13
       rollback_request      1.000     1.000     1.000        28
      security_incident      1.000     1.000     1.000        26
      sso_configuration      1.000     1.000     1.000        26
        unclear_request      1.000     1.000     1.000        15
          webhook_issue      1.000     1.000     1.000        21

               accuracy                          0.990       500
              macro avg      0.992     0.990     0.991       500
           weighted avg      0.991     0.990     0.990       500

```

Confusion matrix (rows = true type, columns = predicted, in sorted type order):

```
[[22  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0]
 [ 0 18  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0]
 [ 0  0 21  0  0  0  0  3  0  0  0  0  0  0  0  0  0  0  0  0  0  0]
 [ 0  0  0 20  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0]
 [ 0  0  0  0 24  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0]
 [ 0  0  0  0  0 26  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0]
 [ 0  0  0  0  0  0 17  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0]
 [ 0  0  0  0  0  0  0 29  0  0  0  0  0  0  0  0  0  0  0  0  0  0]
 [ 0  0  0  0  0  0  0  0 29  0  0  0  0  0  0  0  0  0  0  0  0  0]
 [ 0  0  0  0  0  0  0  0  0 26  0  0  0  0  0  0  0  0  0  0  0  0]
 [ 0  0  0  0  0  0  0  0  0  0 27  0  0  0  0  0  0  0  0  0  0  0]
 [ 0  0  0  0  0  2  0  0  0  0  0 18  0  0  0  0  0  0  0  0  0  0]
 [ 0  0  0  0  0  0  0  0  0  0  0  0 21  0  0  0  0  0  0  0  0  0]
 [ 0  0  0  0  0  0  0  0  0  0  0  0  0 22  0  0  0  0  0  0  0  0]
 [ 0  0  0  0  0  0  0  0  0  0  0  0  0  0 23  0  0  0  0  0  0  0]
 [ 0  0  0  0  0  0  0  0  0  0  0  0  0  0  0 23  0  0  0  0  0  0]
 [ 0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0 13  0  0  0  0  0]
 [ 0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0 28  0  0  0  0]
 [ 0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0 26  0  0  0]
 [ 0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0 26  0  0]
 [ 0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0 15  0]
 [ 0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0 21]]
```

