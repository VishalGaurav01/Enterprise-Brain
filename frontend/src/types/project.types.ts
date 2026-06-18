export interface Project {
  id: string;
  name: string;
  project_type?: string;
  department_id?: string;
  owner_employee_id?: string;
  budget_allocated?: number;
  status: string;
  start_date?: string;
  end_date?: string;
}

export interface Assignment {
  id: string;
  employee_id: string;
  project_id: string;
  role: string;
  allocation_percentage: number;
  start_date: string;
  end_date?: string;
  status: string;
}

export interface Vendor {
  id: string;
  name: string;
  contact_person?: string;
  email?: string;
  status: string;
}

export interface Cost {
  id: string;
  project_id?: string;
  vendor_id?: string;
  amount: number;
  date: string;
  category: string;
  description?: string;
}
