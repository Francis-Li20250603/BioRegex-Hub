# BioRegex-Hub: Biomedical & Regulatory Knowledge Graph

## Overview

The BioRegex-Hub is a unified knowledge graph designed to support the automatic desensitization of biomedical and regulatory data. It integrates multiple high-value regulatory datasets and converts them into regular expression–based entities for direct use in clinical and public health (PH) data pipelines.

## Data Sources

- **🇺🇸 FDA (Food & Drug Administration)**
  - OpenFDA drug database.
  - Extracted drug names and product terms for de-identification.

- **🇪🇺 EMA (European Medicines Agency)**
  - Human medicines dataset (Excel format).
  - Provides international drug identifiers to complement FDA scope.

- **🇺🇸 CMS (Centers for Medicare & Medicaid Services)**
  - Hospital and provider datasets.
  - Used to generate regex rules for institution names and linked identifiers.

- **🇺🇸 HIPAA Breach Reports**
  - Public OCR breach disclosures.
  - Inform regex rules around breach types and compliance categories.

## Methodology

### Crawling / Data Ingestion
- FDA data ingested via API (CSV format).
- EMA data obtained via official XLSX download.
- CMS & HIPAA data prepared from public CSV files.

### Regex-Based Normalization
- Convert terms (drug names, hospital names, breach types) into case-insensitive regex rules.
- Example:
  ```regex
  (?i)\bPOVIDONE\-IODINE\b
  ```

### Knowledge Graph Construction
- **Nodes**: Extracted biomedical and regulatory terms.
- **Edges**: Relationships between datasets (e.g., “Drug — approved by → FDA”, “Hospital — regulated by → CMS”).
- **Outputs**:
  - `nodes.csv`
  - `edges.csv`
  - `graph.json` (API-ready)

## Outputs

- **Regex-Enabled Knowledge Graph**:
  - FDA and EMA drug terms.
  - CMS hospitals and providers.
  - HIPAA breach categories.
  - Format: CSV + JSON for flexible integration.

- **Direct API Utility**:  
  Graph data can be queried to automatically apply desensitization to incoming clinical text or PHI.

## Applications

- **Automatic De-Identification**:  
  Redact or replace sensitive terms in clinical and public health data.

- **Regulatory Compliance**:  
  Aligns with HIPAA (U.S.) and is relevant for GDPR (EU) compliance.

- **ML Preprocessing**:  
  Provides clean, de-identified corpora for biomedical NLP pipelines.

## Contribution

This system demonstrates:
- Integration of multi-jurisdictional regulatory data.
- Transformation into regex-ready rules.
- Graph-based representation enabling API-based desensitization.

The BioRegex-Hub acts as a desensitization warehouse that can be extended to new biomedical sources and scaled into production pipelines.
