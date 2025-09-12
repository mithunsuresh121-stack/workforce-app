const API_BASE_URL = (window as any).REACT_APP_API_URL || 'http://localhost:8000';

interface LeaveRequest {
  id: number;
  user_id: number;
  start_date: string;
  end_date: string;
  reason?: string;
  status: string;
  created_at: string;
  updated_at: string;
}

const getAuthHeaders = () => {
  const token = localStorage.getItem('auth_token');
  return {
    'Content-Type': 'application/json',
    'Authorization': token ? `Bearer ${token}` : '',
  };
};

export const getLeaveRequests = async (): Promise<LeaveRequest[]> => {
  const response = await fetch(`${API_BASE_URL}/leaves`, {
    method: 'GET',
    headers: getAuthHeaders(),
  });

  if (!response.ok) {
    throw new Error('Failed to fetch leave requests');
  }

  return response.json();
};

export const createLeaveRequest = async (data: { start_date: string; end_date: string; reason?: string }): Promise<LeaveRequest> => {
  const response = await fetch(`${API_BASE_URL}/leaves`, {
    method: 'POST',
    headers: getAuthHeaders(),
    body: JSON.stringify(data),
  });

  if (!response.ok) {
    throw new Error('Failed to create leave request');
  }

  return response.json();
};

export const updateLeaveRequest = async (id: number, data: Partial<LeaveRequest>): Promise<LeaveRequest> => {
  const response = await fetch(`${API_BASE_URL}/leaves/${id}`, {
    method: 'PUT',
    headers: getAuthHeaders(),
    body: JSON.stringify(data),
  });

  if (!response.ok) {
    throw new Error('Failed to update leave request');
  }

  return response.json();
};
