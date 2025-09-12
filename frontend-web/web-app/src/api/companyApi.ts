const API_BASE_URL = (window as any).REACT_APP_API_URL || 'http://localhost:8000';

interface CompanyUser {
  id: number;
  email: string;
  full_name?: string;
  role: string;
  company_id?: number;
  is_active: boolean;
  created_at: string;
  updated_at: string;
  employee_profile?: {
    id: number;
    user_id: number;
    company_id: number;
    department?: string;
    position?: string;
    phone?: string;
    hire_date?: string;
    manager_id?: number;
    is_active: boolean;
    created_at: string;
    updated_at: string;
  };
}

interface CompanyUsersResponse {
  users: CompanyUser[];
  total: number;
  page: number;
  limit: number;
}

const getAuthHeaders = () => {
  const token = localStorage.getItem('auth_token');
  return {
    'Content-Type': 'application/json',
    'Authorization': token ? `Bearer ${token}` : '',
  };
};

export const getCompanyUsers = async (
  companyId: number,
  filters: {
    department?: string;
    position?: string;
    search?: string;
  } = {},
  sort: {
    sortBy?: string;
    sortOrder?: 'asc' | 'desc';
  } = {},
  pagination: {
    page?: number;
    limit?: number;
  } = {}
): Promise<CompanyUsersResponse> => {
  const params = new URLSearchParams();

  if (filters.department) params.append('department', filters.department);
  if (filters.position) params.append('position', filters.position);
  if (filters.search) params.append('search', filters.search);
  if (sort.sortBy) params.append('sort_by', sort.sortBy);
  if (sort.sortOrder) params.append('sort_order', sort.sortOrder);
  if (pagination.page) params.append('page', pagination.page.toString());
  if (pagination.limit) params.append('limit', pagination.limit.toString());

  const queryString = params.toString();
  const url = `${API_BASE_URL}/companies/${companyId}/users${queryString ? `?${queryString}` : ''}`;

  const response = await fetch(url, {
    method: 'GET',
    headers: getAuthHeaders(),
  });

  if (!response.ok) {
    throw new Error('Failed to fetch company users');
  }

  return response.json();
};

export const getCompanyDepartments = async (companyId: number): Promise<string[]> => {
  const response = await fetch(`${API_BASE_URL}/companies/${companyId}/departments`, {
    method: 'GET',
    headers: getAuthHeaders(),
  });

  if (!response.ok) {
    throw new Error('Failed to fetch departments');
  }

  const data = await response.json();
  return data.departments || [];
};

export const getCompanyPositions = async (companyId: number): Promise<string[]> => {
  const response = await fetch(`${API_BASE_URL}/companies/${companyId}/positions`, {
    method: 'GET',
    headers: getAuthHeaders(),
  });

  if (!response.ok) {
    throw new Error('Failed to fetch positions');
  }

  const data = await response.json();
  return data.positions || [];
};
