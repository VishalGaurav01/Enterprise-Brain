export interface BusinessRule {
  rule_id: string;
  rule_name: string;
  entity_type: string;
  condition: any;
  action: any;
  priority: number;
  enabled: boolean;
}

export interface EvaluationRequest {
  entity_type?: string;
  employee_id?: string;
  project_id?: string;
  department_id?: string;
  is_organization?: boolean;
  rule_name?: string;
}

export interface EvaluationResponse {
  result: any;
  details: Record<string, any>;
  triggered_rules: string[];
}
