import axios from 'axios';
import { Rule, RuleSubmission } from '../types/types';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

const ruleCache = new Map<string, Rule[]>();

export const fetchRules = async (region?: string, dataType?: string): Promise<Rule[]> => {
  const cacheKey = `${region || 'all'}-${dataType || 'all'}`;
  
  if (ruleCache.has(cacheKey)) {
    return ruleCache.get(cacheKey)!;
  }

  const params = new URLSearchParams();
  if (region) params.append('region', region);
  if (dataType) params.append('data_type', dataType);
  
  const response = await axios.get(`${API_BASE_URL}/rules`, { params });
  ruleCache.set(cacheKey, response.data);
  return response.data;
};

export const submitRule = async (submission: RuleSubmission): Promise<void> => {
  const formData = new FormData();
  formData.append('pattern', submission.pattern);
  formData.append('description', submission.description);
  formData.append('data_type', submission.dataType);
  formData.append('region', submission.region);
  if (submission.reference) {
    formData.append('reference', submission.reference);
  }

  await axios.post(`${API_BASE_URL}/rule-submissions`, formData, {
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
