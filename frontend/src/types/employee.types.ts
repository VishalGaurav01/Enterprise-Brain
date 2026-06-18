export interface Employee {
  id: string;
  user_code: string;
  first_name: string;
  last_name: string;
  email: string;
  contact_number: string;
  department_id?: string;
  designation_id?: string;
  manager_id?: string;
  status: string;
}

export interface Department {
  id: string;
  name: string;
  code: string;
  manager_id?: string;
}

export interface Designation {
  id: string;
  title: string;
  level: number;
}

export interface SoftwareTool {
  id: string;
  name: string;
  category?: string;
  license_type?: string;
}
