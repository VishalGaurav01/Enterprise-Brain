import api from '../lib/api';
import type { ApiResponse, Employee, Department, Designation, SoftwareTool } from '../types';

export const EmployeeService = {
  getEmployees: async (): Promise<Employee[]> => {
    const response = await api.get<ApiResponse<Employee[]>>('/employees/');
    return response.data.data;
  },

  getDepartments: async (): Promise<Department[]> => {
    const response = await api.get<ApiResponse<Department[]>>('/departments/');
    return response.data.data;
  },

  getDesignations: async (): Promise<Designation[]> => {
    const response = await api.get<ApiResponse<Designation[]>>('/designations/');
    return response.data.data;
  },

  getSoftwareTools: async (): Promise<SoftwareTool[]> => {
    const response = await api.get<ApiResponse<SoftwareTool[]>>('/software-tools/');
    return response.data.data;
  }
};
