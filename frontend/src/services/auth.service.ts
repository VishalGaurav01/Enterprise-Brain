import api from '../lib/api';
import type { TokenResponse, ApiResponse } from '../types';

export const AuthService = {
  login: async (payload: any): Promise<TokenResponse> => {
    const response = await api.post<ApiResponse<TokenResponse>>('/auth/login', payload);
    return response.data.data;
  },

  logout: () => {
    localStorage.removeItem('token');
  }
};
