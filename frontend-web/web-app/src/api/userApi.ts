const API_BASE_URL = (window as any).REACT_APP_API_URL || 'http://localhost:8000';

interface UserProfile {
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

interface UpdateProfileData {
  user: {
    full_name: string;
  };
  employee_profile: {
    department?: string | null;
    position?: string | null;
    phone?: string | null;
    hire_date?: string | null;
  };
}

const getAuthHeaders = () => {
  const token = localStorage.getItem('auth_token');
  return {
    'Content-Type': 'application/json',
    'Authorization': token ? `Bearer ${token}` : '',
  };
};

export const getCurrentUserProfile = async (): Promise<UserProfile> => {
  const response = await fetch(`${API_BASE_URL}/auth/me/profile`, {
    method: 'GET',
    headers: getAuthHeaders(),
  });

  if (!response.ok) {
    throw new Error('Failed to fetch user profile');
  }

  return response.json();
};

export const updateCurrentUserProfile = async (data: UpdateProfileData): Promise<UserProfile> => {
  const response = await fetch(`${API_BASE_URL}/auth/me/profile`, {
    method: 'PUT',
    headers: getAuthHeaders(),
    body: JSON.stringify(data),
  });

  if (!response.ok) {
    const errorData = await response.json();
    throw new Error(errorData.detail || 'Failed to update profile');
  }

  return response.json();
};
