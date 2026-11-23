export interface User {
  id: string;
  email: string;
  full_name: string;
  is_totp_enabled: boolean;
  role: 'SUPER_ADMIN' | 'ORG_ADMIN' | 'FINANCE_MANAGER' | 'FINANCIAL_ANALYST' | 'AUDITOR' | 'CUSTOMER';
  organization_id: string;
}

export interface AuthResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  mfa_required?: boolean;
  user: User;
}

export interface TransactionEvent {
  id: string;
  from_status: string | null;
  to_status: string;
  reason: string;
  created_at: string;
}

export interface Transaction {
  id: string;
  organization_id: string;
  reference_id: string;
  amount: number;
  currency: string;
  merchant_name: string;
  description?: string;
  category_id?: string;
  status: 'INITIATED' | 'VALIDATING' | 'RISK_ANALYSIS' | 'PENDING_APPROVAL' | 'PROCESSING' | 'SUCCESS' | 'FAILED' | 'FLAGGED' | 'REFUNDED';
  risk_score: number;
  risk_level: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  payment_method: string;
  created_at: string;
  events?: TransactionEvent[];
}

export interface FraudSignal {
  id: string;
  rule_code: string;
  signal_name: string;
  description: string;
  severity: string;
  weight: number;
}

export interface FraudCase {
  id: string;
  transaction_id: string;
  risk_score: number;
  risk_level: string;
  recommendation: string;
  status: 'OPEN' | 'INVESTIGATING' | 'RESOLVED_BENIGN' | 'CONFIRMED_FRAUD';
  investigator_notes?: string;
  created_at: string;
  signals: FraudSignal[];
}

export interface ReceiptLineItem {
  id: string;
  description: string;
  quantity: number;
  unit_price: number;
  total_price: number;
}

export interface Receipt {
  id: string;
  file_name: string;
  merchant_name: string;
  total_amount: number;
  currency: string;
  tax_amount?: number;
  invoice_number?: string;
  status: string;
  created_at: string;
  line_items: ReceiptLineItem[];
}

export interface Budget503020 {
  month: string;
  total_income: number;
  total_expenses: number;
  needs: {
    amount: number;
    actual_percentage: number;
    target_percentage: number;
    difference: number;
    status: string;
  };
  wants: {
    amount: number;
    actual_percentage: number;
    target_percentage: number;
    difference: number;
    status: string;
  };
  savings: {
    amount: number;
    actual_percentage: number;
    target_percentage: number;
    difference: number;
    status: string;
  };
  recommendations: string[];
}

export interface HealthScore {
  health_score: number;
  rating: string;
  month: string;
  pillars: Record<string, { score: number; max: number; details: string }>;
}

export interface Subscription {
  id: string;
  merchant_name: string;
  amount: number;
  currency: string;
  billing_cycle: string;
  next_renewal_date: string;
  status: string;
  is_auto_detected: boolean;
}

export interface DashboardMetrics {
  total_income: number;
  total_expenses: number;
  net_cashflow: number;
  savings_rate_percentage: number;
  total_transactions_count: number;
  failed_transactions_count: number;
  flagged_transactions_count: number;
  active_fraud_alerts: number;
  active_subscriptions: number;
  financial_health_score: number;
  financial_health_rating: string;
}

export interface AuditLog {
  id: string;
  actor_id: string;
  actor_email: string;
  action: string;
  resource_type: string;
  resource_id: string;
  ip_address: string;
  request_id: string;
  created_at: string;
}

export interface Notification {
  id: string;
  type: string;
  title: string;
  message: string;
  is_read: boolean;
  created_at: string;
}
