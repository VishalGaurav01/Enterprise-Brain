import api from '../lib/api';
import type { ApiResponse, Project, Assignment, Vendor, Cost } from '../types';

export const ProjectService = {
  getProjects: async (): Promise<Project[]> => {
    const response = await api.get<ApiResponse<Project[]>>('/projects/');
    return response.data.data;
  },

  getAssignments: async (): Promise<Assignment[]> => {
    const response = await api.get<ApiResponse<Assignment[]>>('/assignments/');
    return response.data.data;
  },

  getAssignmentsByEmployee: async (employeeId: string): Promise<Assignment[]> => {
    const response = await api.get<ApiResponse<Assignment[]>>(`/assignments/employee/${employeeId}`);
    return response.data.data;
  },

  getVendors: async (): Promise<Vendor[]> => {
    const response = await api.get<ApiResponse<Vendor[]>>('/vendors/');
    return response.data.data;
  },

  getCosts: async (): Promise<Cost[]> => {
    const response = await api.get<ApiResponse<Cost[]>>('/costs/');
    return response.data.data;
  }
};
