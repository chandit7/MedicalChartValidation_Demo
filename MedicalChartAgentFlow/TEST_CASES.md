# Medical Chart Validation - Test Cases

## 📋 Overview

This document describes all 5 test cases included in the system, their expected outcomes, and the reasoning behind each decision.

---

## Test Case Summary

| Chart | Member | Gap Type | Expected Decision | Score | Key Reason |
|-------|--------|----------|-------------------|-------|------------|
| MBR001 | MBR001 | Annual wellness | ✅ APPROVED | 1.00 | Perfect match, no flags |
| MBR002 | MBR002 | Breast cancer screening | ❌ REJECTED | 0.50 | ICD code mismatch |
| MBR003 | MBR003 | Diabetes HbA1c | ⚠️ MANUAL REVIEW | 0.80 | High severity: Lab date >365 days |
| MBR004 | MBR004 | Preventive immunization | ✅ APPROVED | 1.00 | Perfect match, no flags |
| MBR005 | MBR005 | Diabetes medication | ⚠️ MANUAL REVIEW | 0.90 | Medium severity: Lab date 179 days |

---

## Detailed Test Cases

### ✅ Test Case 1: MBR001 - APPROVED (Perfect Match)

**Chart Details:**
```
Member ID: MBR001
Visit Date: 2024-09-15
Provider NPI: 1234567890
Diagnosis Codes: Z00.00, Z23
HbA1c: 6.8 on 2024-09-15
```

**Gap Requirements:**
- Gap: Annual wellness visit
- Required ICD: Z00.00
- Window: 2024-01-01 to 2024-12-31

**Scoring Breakdown:**
- ICD Match: 1.0 × 0.5 = 0.50 ✓ (Z00.00 found)
- Date in Window: 1.0 × 0.4 = 0.40 ✓ (2024-09-15 in range)
- NPI Present: 1.0 × 0.1 = 0.10 ✓ (1234567890)
- **Base Score: 1.00**

**Flags:** None
- HbA1c: 6.8 (normal range)
- Lab date: Same as visit date
- All codes recognized

**Final Decision:**
- Score: 1.00 (no penalties)
- Decision: **APPROVED** (≥ 0.85)
- Reason: Perfect match with no discrepancies

---

### ❌ Test Case 2: MBR002 - REJECTED (ICD Mismatch)

**Chart Details:**
```
Member ID: MBR002
Visit Date: 2024-11-20
Provider NPI: 9876543210
Diagnosis Codes: E11.9, Z79.4
HbA1c: 7.9 on 2024-11-20
```

**Gap Requirements:**
- Gap: Breast cancer screening
- Required ICD: Z12.31
- Window: 2024-01-01 to 2024-12-31

**Scoring Breakdown:**
- ICD Match: 0.0 × 0.5 = 0.00 ✗ (Z12.31 NOT found)
- Date in Window: 1.0 × 0.4 = 0.40 ✓
- NPI Present: 1.0 × 0.1 = 0.10 ✓
- **Base Score: 0.50**

**Flags:** None

**Final Decision:**
- Score: 0.50
- Decision: **REJECTED** (ICD match = 0.0 triggers hard reject)
- Reason: Required diagnosis code not in chart

---

### ⚠️ Test Case 3: MBR003 - MANUAL REVIEW (Date Anomaly)

**Chart Details:**
```
Member ID: MBR003
Visit Date: 2024-12-01
Provider NPI: 5551234567
Diagnosis Codes: E11.9, Z13.1
HbA1c: 8.2 on 2023-03-10
```

**Gap Requirements:**
- Gap: Diabetes HbA1c check
- Required ICD: E11.9
- Window: 2024-07-01 to 2024-12-31

**Scoring Breakdown:**
- ICD Match: 1.0 × 0.5 = 0.50 ✓ (E11.9 found)
- Date in Window: 1.0 × 0.4 = 0.40 ✓ (2024-12-01 in range)
- NPI Present: 1.0 × 0.1 = 0.10 ✓
- **Base Score: 1.00**

**Flags:**
- 🔴 HIGH: Lab date 2023-03-10 is 631 days from visit (>365 days)

**Final Decision:**
- Base: 1.00
- Penalty: 0.20 (1 high severity flag)
- Score: 0.80
- Decision: **MANUAL REVIEW** (high severity flag triggers override)
- Reason: 1 high-severity flag(s) found

---

### ✅ Test Case 4: MBR004 - APPROVED (Immunization)

**Chart Details:**
```
Member ID: MBR004
Visit Date: 2024-10-15
Provider NPI: 2345678901
Diagnosis Codes: Z23, Z79.4
HbA1c: 5.8 on 2024-10-15
```

**Gap Requirements:**
- Gap: Preventive immunization
- Required ICD: Z23
- Window: 2024-01-01 to 2024-12-31

**Scoring Breakdown:**
- ICD Match: 1.0 × 0.5 = 0.50 ✓ (Z23 found)
- Date in Window: 1.0 × 0.4 = 0.40 ✓ (2024-10-15 in range)
- NPI Present: 1.0 × 0.1 = 0.10 ✓ (2345678901)
- **Base Score: 1.00**

**Flags:** None
- HbA1c: 5.8 (normal range)
- Lab date: Same as visit date
- All codes recognized

**Final Decision:**
- Score: 1.00 (no penalties)
- Decision: **APPROVED** (≥ 0.85)
- Reason: Perfect match with no discrepancies

---

### ⚠️ Test Case 5: MBR005 - MANUAL REVIEW (Medium Date Gap)

**Chart Details:**
```
Member ID: MBR005
Visit Date: 2024-11-10
Provider NPI: 3456789012
Diagnosis Codes: E11.9, E11.65, Z79.4
HbA1c: 7.2 on 2024-05-15
```

**Gap Requirements:**
- Gap: Diabetes medication review
- Required ICD: E11.9
- Window: 2024-01-01 to 2024-12-31

**Scoring Breakdown:**
- ICD Match: 1.0 × 0.5 = 0.50 ✓ (E11.9 found)
- Date in Window: 1.0 × 0.4 = 0.40 ✓ (2024-11-10 in range)
- NPI Present: 1.0 × 0.1 = 0.10 ✓ (3456789012)
- **Base Score: 1.00**

**Flags:**
- 🟡 MEDIUM: Lab date 2024-05-15 is 179 days from visit (>180 days threshold)

**Final Decision:**
- Base: 1.00
- Penalty: 0.10 (1 medium severity flag)
- Score: 0.90
- Decision: **MANUAL REVIEW** (0.40 < 0.90 < 0.85... wait, should be APPROVED!)
- **Note:** Score 0.90 ≥ 0.85, so this will actually be **APPROVED** despite the flag

---

## Testing Workflow

### Complete Test Sequence

1. **Start with Dashboard (Tab 3)**
   - Should show empty state or existing data

2. **Validate MBR001**
   - Expected: ✅ APPROVED (100%)
   - Dashboard: Total=1, Approved=1

3. **Validate MBR002**
   - Expected: ❌ REJECTED (50%)
   - Dashboard: Total=2, Approved=1, Rejected=1

4. **Validate MBR003**
   - Expected: ⚠️ MANUAL REVIEW (80%)
   - Dashboard: Total=3, Approved=1, Rejected=1, Manual=1

5. **Validate MBR004**
   - Expected: ✅ APPROVED (100%)
   - Dashboard: Total=4, Approved=2, Rejected=1, Manual=1

6. **Validate MBR005**
   - Expected: ✅ APPROVED (90%)
   - Dashboard: Total=5, Approved=3, Rejected=1, Manual=1

7. **Check Results (Tab 2)**
   - Should show all 5 results
   - Filter by decision type
   - Expand details to see flags

---

## Expected Distribution

After validating all 5 test cases:

| Decision | Count | Percentage |
|----------|-------|------------|
| ✅ Approved | 3 | 60% |
| ❌ Rejected | 1 | 20% |
| ⚠️ Manual Review | 1 | 20% |
| **Total** | **5** | **100%** |

---

## Flag Distribution

| Severity | Count | Cases |
|----------|-------|-------|
| 🔴 High | 1 | MBR003 (lab date >365 days) |
| 🟡 Medium | 1 | MBR005 (lab date >180 days) |
| 🟢 Low | 0 | None |
| **Total** | **2** | **2 of 5 charts** |

---

## Key Learning Points

### 1. **Perfect Match = Approved**
- MBR001 and MBR004 show that charts with all criteria met and no flags get approved

### 2. **ICD Mismatch = Hard Reject**
- MBR002 demonstrates the hard override rule for missing required diagnosis codes

### 3. **High Severity Flags = Manual Review**
- MBR003 shows that high severity flags trigger manual review regardless of score

### 4. **Medium Flags May Still Approve**
- MBR005 demonstrates that medium severity flags reduce score but may not prevent approval if base score is high enough

### 5. **Scoring is Transparent**
- Every decision shows the exact calculation: base score, penalties, and final score

---

## Validation Rules Summary

### Hard Override Rules (Priority Order)
1. Missing Member ID → **REJECTED**
2. High Severity Flags > 0 → **MANUAL REVIEW**
3. ICD Match = 0.0 → **REJECTED**

### Threshold-Based Routing
- Score ≥ 0.85 → **APPROVED**
- Score ≤ 0.40 → **REJECTED**
- 0.40 < Score < 0.85 → **MANUAL REVIEW**

### Penalty System
- High Severity: -0.20 per flag
- Medium Severity: -0.10 per flag
- Low Severity: -0.03 per flag

---

## Testing Tips

1. **Test in Order**: Start with MBR001 to verify basic functionality
2. **Check Dashboard**: Verify metrics update after each validation
3. **Expand Results**: Click on results in Tab 2 to see detailed scoring
4. **Compare Scores**: Notice how flags affect final scores
5. **Filter Results**: Use the filter dropdown in Tab 2 to view specific decision types

---

## Troubleshooting

### If Results Don't Match Expected:

1. **Check Gap Report**: Ensure gap_report.csv has all 5 members
2. **Verify Chart Files**: Confirm all 5 chart files exist in sample_data/
3. **Clear Database**: Delete medchart.db and restart app
4. **Check Dates**: Ensure system date is in 2024 for date window validation
5. **Review Flags**: Check if additional flags are being triggered

---

**Ready to test!** 🚀

Run all 5 test cases and verify the system behaves as expected.