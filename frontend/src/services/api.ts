import axios from 'axios';

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
  referenceUrl?: string;
  file?: File;
}

// Default to /api (works with Nginx proxy in prod and Vite dev proxy)
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api';

const ruleCache = new Map<string, Rule[]>();

export const fetchRules = async (region?: string, dataType?: string): Promise<Rule[]> => {
  const cacheKey = `${region || 'all'}-${dataType || 'all'}`;
  if (ruleCache.has(cacheKey)) {
    return ruleCache.get(cacheKey)!;
  }

  const params: any = {};
  if (region) params.region = region;
  if (dataType) params.data_type = dataType;

  const response = await axios.get(`${API_BASE_URL}/rules`, { params });

  // Normalize snake_case from backend → camelCase expected by frontend
  const normalized: Rule[] = response.data.map((r: any) => ({
    id: r.id,
    pattern: r.pattern,
    description: r.description,
    dataType: r.data_type,
    region: r.region,
    referenceUrl: r.reference_url ?? undefined,
    createdAt: r.created_at ?? ''
  }));

  ruleCache.set(cacheKey, normalized);
  return normalized;
};

export const submitRule = async (submission: RuleSubmission): Promise<void> => {
  const formData = new FormData();
  formData.append('pattern', submission.pattern);
  formData.append('description', submission.description);
  formData.append('data_type', submission.dataType);
  formData.append('region', submission.region);
  if (submission.referenceUrl) formData.append('reference_url', submission.referenceUrl);
  if (submission.file) formData.append('file', submission.file);

  await axios.post(`${API_BASE_URL}/submissions`, formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
};

export const validateData = async (file: File, ruleId: number): Promise<any> => {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('rule_id', ruleId.toString());

  const response = await axios.post(`${API_BASE_URL}/validate`, formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
  return response.data;
};
