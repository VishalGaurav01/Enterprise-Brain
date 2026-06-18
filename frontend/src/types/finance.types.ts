export interface Client {
  id: string;
  name: string;
  industry?: string;
  contact_person?: string;
  email?: string;
  status: string;
}

export interface Invoice {
  id: string;
  client_id: string;
  project_id?: string;
  amount: number;
  issue_date: string;
  due_date?: string;
  status: string;
}

export interface Revenue {
  id: string;
  project_id?: string;
  client_id?: string;
  amount: number;
  date: string;
  category: string;
  description?: string;
}

export interface Reimbursement {
  id: string;
  employee_id: string;
  amount: number;
  date: string;
  category: string;
  status: string;
  description?: string;
}
