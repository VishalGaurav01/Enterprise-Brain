import api from '../lib/api';
import type { BusinessRule, EvaluationRequest, EvaluationResponse } from '../types';

export const AnalyticsService = {
  getRules: async (): Promise<BusinessRule[]> => {
    const response = await api.get<BusinessRule[]>('/analytics/rules');
    return response.data;
  },

  createRule: async (rule: Partial<BusinessRule>): Promise<BusinessRule> => {
    const response = await api.post<BusinessRule>('/analytics/rules', rule);
    return response.data;
  },

  evaluate: async (payload: EvaluationRequest): Promise<EvaluationResponse> => {
    const response = await api.post<EvaluationResponse>('/analytics/evaluate', payload);
    return response.data;
  }
};
