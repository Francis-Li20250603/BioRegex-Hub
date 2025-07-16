export interface Rule {
  id: number;
  pattern: string;
  description: string;
  dataType: string;
  region: string;
  referenceUrl?: string;
  createdAt: string;
}

export interface RuleSubmission {
  pattern: string;
  description: string;
  dataType: string;
  region: string;
  reference?: File | null;
}

export interface ValidationResult {
  passed: boolean;
  pValue?: number;
  errorMessage?: string;
  reportUrl?: string;
}
