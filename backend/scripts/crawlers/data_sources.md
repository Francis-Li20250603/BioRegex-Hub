# Data Sources for BioRegex-Hub

This program aims to build a **desensitization warehouse** for biomedical and regulatory data.  
Below are the core data sources and their importance:

## 🇺🇸 U.S. Sources

### FDA (Food and Drug Administration)
- Provides drug, supplement, and device information.
- Essential for identifying sensitive identifiers in clinical and biomedical records.
- Access: [OpenFDA API](https://open.fda.gov/apis/).

### HIPAA (Health Insurance Portability and Accountability Act)
- Defines privacy & security rules for health data.
- OCR breach portal reveals common compliance issues.
- Critical for rule-building in our knowledge graph.

### CMS (Centers for Medicare & Medicaid Services)
- Offers provider, hospital, and cost-report data.
- High-value for linking de-identification rules with real-world healthcare delivery datasets.
- Access: [CMS Data Portal](https://data.cms.gov/).

## 🇪🇺 European Sources

### EMA (European Medicines Agency)
- Maintains authoritative data on approved medicines.
- Supports supplement/medicine overlap checks in EU.
- Data: [EMA Medicine Data Download](https://www.ema.europa.eu/en/medicines/download-medicine-data).

### EFSA (European Food Safety Authority)
- Provides toxicological and safety assessments for food and supplements.
- Strengthens supplement-focused desensitization rules.
- Data: [EFSA OpenFoodTox](https://www.efsa.europa.eu/en/data/chemical-hazards-data).

---

## Why These Matter

- **Coverage**: Combining U.S. and EU sources ensures broad regulatory scope.
- **Compliance**: HIPAA + NIST + CMS ground our rules in privacy & security standards.
- **Application**: FDA/EMA/EFSA provide biomedical data directly relevant for ML pipelines.
- **Transparency**: All crawled data stored as CSV in `data/` folder for reproducibility.
