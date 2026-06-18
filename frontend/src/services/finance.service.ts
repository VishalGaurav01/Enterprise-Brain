import api from '../lib/api';
import type { ApiResponse, Client, Invoice, Revenue, Reimbursement } from '../types';

export const FinanceService = {
  getClients: async (): Promise<Client[]> => {
    const response = await api.get<ApiResponse<Client[]>>('/clients/');
    return response.data.data;
  },

  getInvoices: async (): Promise<Invoice[]> => {
    const response = await api.get<ApiResponse<Invoice[]>>('/invoices/');
    return response.data.data;
  },

  getRevenues: async (): Promise<Revenue[]> => {
    const response = await api.get<ApiResponse<Revenue[]>>('/revenues/');
    return response.data.data;
  },

  getReimbursements: async (): Promise<Reimbursement[]> => {
    const response = await api.get<ApiResponse<Reimbursement[]>>('/reimbursements/');
    return response.data.data;
  }
};
