import { getAuthToken, clearAuthToken } from '../utils/auth';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

export const fetchDashboardData = async () => {
  try {
    const token = getAuthToken();
    if (!token) {
      window.location.href = '/login';
      return;
    }

    const kpisResponse = await fetch(API_BASE_URL + '/dashboard/kpis', {
      headers: {
        'Authorization': 'Bearer ' + token,
        'Content-Type': 'application/json',
      },
    });
    
    const activitiesResponse = await fetch(API_BASE_URL + '/dashboard/recent-activities', {
      headers: {
        'Authorization': 'Bearer ' + token,
        'Content-Type': 'application/json',
      },
    });
    
    const taskStatusResponse = await fetch(API_BASE_URL + '/dashboard/charts/task-status', {
      headers: {
        'Authorization': 'Bearer ' + token,
        'Content-Type': 'application/json',
      },
    });

    if (kpisResponse.status === 401 || activitiesResponse.status === 401 || taskStatusResponse.status === 401) {
      clearAuthToken();
      window.location.href = '/login';
      return;
    }

    if (!kpisResponse.ok || !activitiesResponse.ok || !taskStatusResponse.ok) {
      throw new Error('Failed to fetch dashboard data');
    }

    const kpis = await kpisResponse.json();
    const activities = await activitiesResponse.json();
    const taskStatus = await taskStatusResponse.json();

    return {
      kpis: {
        ...kpis,
        taskStatus,
      },
      activities,
    };
  } catch (error) {
    console.error('Error fetching dashboard data:', error);
    throw error;
  }
};

export const updateKpi = async (kpiKey: string, value: number) => {
  try {
    const token = getAuthToken();
    if (!token) {
      window.location.href = '/login';
      return;
    }
    const response = await fetch(`${API_BASE_URL}/dashboard/kpis/${kpiKey}`, {
      method: 'PUT',
      headers: {
        'Authorization': 'Bearer ' + token,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ value }),
    });
    if (response.status === 401) {
      clearAuthToken();
      window.location.href = '/login';
      return;
    }
    if (!response.ok) {
      throw new Error('Failed to update KPI');
    }
    return true;
  } catch (error) {
    console.error('Error updating KPI:', error);
    throw error;
  }
};

export const getEmployees = async () => {
  try {
    const token = getAuthToken();
    if (!token) {
      window.location.href = '/login';
      return [];
    }
    const response = await fetch(API_BASE_URL + '/employees/', {
      headers: {
        'Authorization': 'Bearer ' + token,
        'Content-Type': 'application/json',
      },
    });
    if (response.status === 401) {
      clearAuthToken();
      window.location.href = '/login';
      return [];
    }
    if (!response.ok) {
      throw new Error('Failed to fetch employees');
    }
    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error fetching employees:', error);
    throw error;
  }
};

export const deleteEmployee = async (employeeId: string | number) => {
  try {
    const token = getAuthToken();
    if (!token) {
      window.location.href = '/login';
      return false;
    }
    const response = await fetch(API_BASE_URL + '/employees/' + employeeId, {
      method: 'DELETE',
      headers: {
        'Authorization': 'Bearer ' + token,
      },
    });
    if (response.status === 401) {
      clearAuthToken();
      window.location.href = '/login';
      return false;
    }
    if (!response.ok) {
      throw new Error('Failed to delete employee');
    }
    return true;
  } catch (error) {
    console.error('Error deleting employee:', error);
    throw error;
  }
};

export const createEmployee = async (employeeData: any) => {
  try {
    const token = getAuthToken();
    if (!token) {
      window.location.href = '/login';
      return null;
    }
    const response = await fetch(API_BASE_URL + '/employees/', {
      method: 'POST',
      headers: {
        'Authorization': 'Bearer ' + token,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(employeeData),
    });
    if (response.status === 401) {
      clearAuthToken();
      window.location.href = '/login';
      return null;
    }
    if (!response.ok) {
      throw new Error('Failed to create employee');
    }
    return await response.json();
  } catch (error) {
    console.error('Error creating employee:', error);
    throw error;
  }
};

export const updateEmployee = async (employeeId: string | number, employeeData: any) => {
  try {
    const token = getAuthToken();
    if (!token) {
      window.location.href = '/login';
      return null;
    }
    const response = await fetch(API_BASE_URL + '/employees/' + employeeId, {
      method: 'PUT',
      headers: {
        'Authorization': 'Bearer ' + token,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(employeeData),
    });
    if (response.status === 401) {
      clearAuthToken();
      window.location.href = '/login';
      return null;
    }
    if (!response.ok) {
      throw new Error('Failed to update employee');
    }
    return await response.json();
  } catch (error) {
    console.error('Error updating employee:', error);
    throw error;
  }
};

export const getEmployee = async (employeeId: string | number) => {
  try {
    const token = getAuthToken();
    if (!token) {
      window.location.href = '/login';
      return null;
    }
    const response = await fetch(API_BASE_URL + '/employees/' + employeeId, {
      headers: {
        'Authorization': 'Bearer ' + token,
        'Content-Type': 'application/json',
      },
    });
    if (response.status === 401) {
      clearAuthToken();
      window.location.href = '/login';
      return null;
    }
    if (!response.ok) {
      throw new Error('Failed to fetch employee');
    }
    return await response.json();
  } catch (error) {
    console.error('Error fetching employee:', error);
    throw error;
  }
};

export const getTasks = async () => {
  try {
    const token = getAuthToken();
    if (!token) {
      window.location.href = '/login';
      return [];
    }
    const response = await fetch(API_BASE_URL + '/tasks/', {
      headers: {
        'Authorization': 'Bearer ' + token,
        'Content-Type': 'application/json',
      },
    });
    if (response.status === 401) {
      clearAuthToken();
      window.location.href = '/login';
      return [];
    }
    if (!response.ok) {
      throw new Error('Failed to fetch tasks');
    }
    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error fetching tasks:', error);
    throw error;
  }
};

export const deleteTask = async (taskId: string | number) => {
  try {
    const token = getAuthToken();
    if (!token) {
      window.location.href = '/login';
      return false;
    }
    const response = await fetch(API_BASE_URL + '/tasks/' + taskId, {
      method: 'DELETE',
      headers: {
        'Authorization': 'Bearer ' + token,
      },
    });
    if (response.status === 401) {
      clearAuthToken();
      window.location.href = '/login';
      return false;
    }
    if (!response.ok) {
      throw new Error('Failed to delete task');
    }
    return true;
  } catch (error) {
    console.error('Error deleting task:', error);
    throw error;
  }
};

export const createTask = async (taskData: any) => {
  try {
    const token = getAuthToken();
    if (!token) {
      window.location.href = '/login';
      return null;
    }
    const response = await fetch(API_BASE_URL + '/tasks/', {
      method: 'POST',
      headers: {
        'Authorization': 'Bearer ' + token,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(taskData),
    });
    if (response.status === 401) {
      clearAuthToken();
      window.location.href = '/login';
      return null;
    }
    if (!response.ok) {
      throw new Error('Failed to create task');
    }
    return await response.json();
  } catch (error) {
    console.error('Error creating task:', error);
    throw error;
  }
};

export const updateTask = async (taskId: string | number, taskData: any) => {
  try {
    const token = getAuthToken();
    if (!token) {
      window.location.href = '/login';
      return null;
    }
    const response = await fetch(API_BASE_URL + '/tasks/' + taskId, {
      method: 'PUT',
      headers: {
        'Authorization': 'Bearer ' + token,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(taskData),
    });
    if (response.status === 401) {
      clearAuthToken();
      window.location.href = '/login';
      return null;
    }
    if (!response.ok) {
      throw new Error('Failed to update task');
    }
    return await response.json();
  } catch (error) {
    console.error('Error updating task:', error);
    throw error;
  }
};

export const signup = async (user: { full_name: string; email: string; password: string; role: string }) => {
  try {
    const response = await fetch(API_BASE_URL + '/auth/signup', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(user),
    });
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || 'Signup failed');
    }
    return await response.json();
  } catch (error) {
    console.error('Error during signup:', error);
    throw error;
  }
};

export const login = async (credentials: { email: string; password: string; company_id?: number }) => {
  try {
    const response = await fetch(API_BASE_URL + '/auth/login', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(credentials),
    });
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || 'Login failed');
    }
    return await response.json();
  } catch (error) {
    console.error('Error during login:', error);
    throw error;
  }
};

export const getCurrentUserProfile = async () => {
  try {
    const token = getAuthToken();
    if (!token) {
      window.location.href = '/login';
      return null;
    }
    const response = await fetch(API_BASE_URL + '/auth/me', {
      headers: {
        'Authorization': 'Bearer ' + token,
        'Content-Type': 'application/json',
      },
    });
    if (response.status === 401) {
      clearAuthToken();
      window.location.href = '/login';
      return null;
    }
    if (!response.ok) {
      throw new Error('Failed to fetch user profile');
    }
    return await response.json();
  } catch (error) {
    console.error('Error fetching user profile:', error);
    throw error;
  }
};

export const getNotifications = async () => {
  try {
    const token = getAuthToken();
    if (!token) {
      window.location.href = '/login';
      return [];
    }
    const response = await fetch(API_BASE_URL + '/notifications/', {
      headers: {
        'Authorization': 'Bearer ' + token,
        'Content-Type': 'application/json',
      },
    });
    if (response.status === 401) {
      clearAuthToken();
      window.location.href = '/login';
      return [];
    }
    if (!response.ok) {
      throw new Error('Failed to fetch notifications');
    }
    return await response.json();
  } catch (error) {
    console.error('Error fetching notifications:', error);
    throw error;
  }
};

export const markNotificationAsRead = async (notificationId: number) => {
  try {
    const token = getAuthToken();
    if (!token) {
      window.location.href = '/login';
      return false;
    }
    const response = await fetch(API_BASE_URL + `/notifications/mark-read/${notificationId}`, {
      method: 'POST',
      headers: {
        'Authorization': 'Bearer ' + token,
        'Content-Type': 'application/json',
      },
    });
    if (response.status === 401) {
      clearAuthToken();
      window.location.href = '/login';
      return false;
    }
    if (!response.ok) {
      throw new Error('Failed to mark notification as read');
    }
    return true;
  } catch (error) {
    console.error('Error marking notification as read:', error);
    throw error;
  }
};

// Notification Preferences API functions
export const getNotificationPreferences = async () => {
  try {
    const token = getAuthToken();
    if (!token) {
      window.location.href = '/login';
      return null;
    }
    const response = await fetch(API_BASE_URL + '/notification-preferences/', {
      headers: {
        'Authorization': 'Bearer ' + token,
        'Content-Type': 'application/json',
      },
    });
    if (response.status === 401) {
      clearAuthToken();
      window.location.href = '/login';
      return null;
    }
    if (!response.ok) {
      throw new Error('Failed to fetch notification preferences');
    }
    return await response.json();
  } catch (error) {
    console.error('Error fetching notification preferences:', error);
    throw error;
  }
};

export const createNotificationPreferences = async (preferences: any) => {
  try {
    const token = getAuthToken();
    if (!token) {
      window.location.href = '/login';
      return null;
    }
    const response = await fetch(API_BASE_URL + '/notification-preferences/', {
      method: 'POST',
      headers: {
        'Authorization': 'Bearer ' + token,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(preferences),
    });
    if (response.status === 401) {
      clearAuthToken();
      window.location.href = '/login';
      return null;
    }
    if (!response.ok) {
      throw new Error('Failed to create notification preferences');
    }
    return await response.json();
  } catch (error) {
    console.error('Error creating notification preferences:', error);
    throw error;
  }
};

export const updateNotificationPreferences = async (preferences: any) => {
  try {
    const token = getAuthToken();
    if (!token) {
      window.location.href = '/login';
      return null;
    }
    const response = await fetch(API_BASE_URL + '/notification-preferences/', {
      method: 'PUT',
      headers: {
        'Authorization': 'Bearer ' + token,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(preferences),
    });
    if (response.status === 401) {
      clearAuthToken();
      window.location.href = '/login';
      return null;
    }
    if (!response.ok) {
      throw new Error('Failed to update notification preferences');
    }
    return await response.json();
  } catch (error) {
    console.error('Error updating notification preferences:', error);
    throw error;
  }
};

export const deleteNotificationPreferences = async () => {
  try {
    const token = getAuthToken();
    if (!token) {
      window.location.href = '/login';
      return false;
    }
    const response = await fetch(API_BASE_URL + '/notification-preferences/', {
      method: 'DELETE',
      headers: {
        'Authorization': 'Bearer ' + token,
      },
    });
    if (response.status === 401) {
      clearAuthToken();
      window.location.href = '/login';
      return false;
    }
    if (!response.ok) {
      throw new Error('Failed to delete notification preferences');
    }
    return true;
  } catch (error) {
    console.error('Error deleting notification preferences:', error);
    throw error;
  }
};

export const getLeaves = async () => {
  try {
    const token = getAuthToken();
    if (!token) {
      window.location.href = '/login';
      return [];
    }
    const response = await fetch(API_BASE_URL + '/leaves/', {
      headers: {
        'Authorization': 'Bearer ' + token,
        'Content-Type': 'application/json',
      },
    });
    if (response.status === 401) {
      clearAuthToken();
      window.location.href = '/login';
      return [];
    }
    if (!response.ok) {
      throw new Error('Failed to fetch leaves');
    }
    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error fetching leaves:', error);
    throw error;
  }
};

export const createLeave = async (leaveData: any) => {
  try {
    const token = getAuthToken();
    if (!token) {
      window.location.href = '/login';
      return null;
    }
    const response = await fetch(API_BASE_URL + '/leaves/', {
      method: 'POST',
      headers: {
        'Authorization': 'Bearer ' + token,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(leaveData),
    });
    if (response.status === 401) {
      clearAuthToken();
      window.location.href = '/login';
      return null;
    }
    if (!response.ok) {
      throw new Error('Failed to create leave');
    }
    return await response.json();
  } catch (error) {
    console.error('Error creating leave:', error);
    throw error;
  }
};

export const getMyLeaves = async () => {
  try {
    const token = getAuthToken();
    if (!token) {
      window.location.href = '/login';
      return [];
    }
    const response = await fetch(API_BASE_URL + '/leaves/my-leaves/', {
      headers: {
        'Authorization': 'Bearer ' + token,
        'Content-Type': 'application/json',
      },
    });
    if (response.status === 401) {
      clearAuthToken();
      window.location.href = '/login';
      return [];
    }
    if (!response.ok) {
      throw new Error('Failed to fetch my leaves');
    }
    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error fetching my leaves:', error);
    throw error;
  }
};

export const getShifts = async () => {
  try {
    const token = getAuthToken();
    if (!token) {
      window.location.href = '/login';
      return [];
    }
    const response = await fetch(API_BASE_URL + '/shifts/', {
      headers: {
        'Authorization': 'Bearer ' + token,
        'Content-Type': 'application/json',
      },
    });
    if (response.status === 401) {
      clearAuthToken();
      window.location.href = '/login';
      return [];
    }
    if (!response.ok) {
      throw new Error('Failed to fetch shifts');
    }
    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error fetching shifts:', error);
    throw error;
  }
};

export const createShift = async (shiftData: any) => {
  try {
    const token = getAuthToken();
    if (!token) {
      window.location.href = '/login';
      return null;
    }
    const response = await fetch(API_BASE_URL + '/shifts/', {
      method: 'POST',
      headers: {
        'Authorization': 'Bearer ' + token,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(shiftData),
    });
    if (response.status === 401) {
      clearAuthToken();
      window.location.href = '/login';
      return null;
    }
    if (!response.ok) {
      throw new Error('Failed to create shift');
    }
    return await response.json();
  } catch (error) {
    console.error('Error creating shift:', error);
    throw error;
  }
};

export const getMyShifts = async () => {
  try {
    const token = getAuthToken();
    if (!token) {
      window.location.href = '/login';
      return [];
    }
    const response = await fetch(API_BASE_URL + '/shifts/my-shifts/', {
      headers: {
        'Authorization': 'Bearer ' + token,
        'Content-Type': 'application/json',
      },
    });
    if (response.status === 401) {
      clearAuthToken();
      window.location.href = '/login';
      return [];
    }
    if (!response.ok) {
      throw new Error('Failed to fetch my shifts');
    }
    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error fetching my shifts:', error);
    throw error;
  }
};

// Payroll API functions
export const getPayrollEmployees = async () => {
  try {
    const token = getAuthToken();
    if (!token) {
      window.location.href = '/login';
      return [];
    }
    const response = await fetch(API_BASE_URL + '/payroll/employees/', {
      headers: {
        'Authorization': 'Bearer ' + token,
        'Content-Type': 'application/json',
      },
    });
    if (response.status === 401) {
      clearAuthToken();
      window.location.href = '/login';
      return [];
    }
    if (!response.ok) {
      throw new Error('Failed to fetch payroll employees');
    }
    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error fetching payroll employees:', error);
    throw error;
  }
};

export const createPayrollEmployee = async (employeeData: any) => {
  try {
    const token = getAuthToken();
    if (!token) {
      window.location.href = '/login';
      return null;
    }
    const response = await fetch(API_BASE_URL + '/payroll/employees/', {
      method: 'POST',
      headers: {
        'Authorization': 'Bearer ' + token,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(employeeData),
    });
    if (response.status === 401) {
      clearAuthToken();
      window.location.href = '/login';
      return null;
    }
    if (!response.ok) {
      throw new Error('Failed to create payroll employee');
    }
    return await response.json();
  } catch (error) {
    console.error('Error creating payroll employee:', error);
    throw error;
  }
};

export const getPayrollEmployee = async (employeeId: number) => {
  try {
    const token = getAuthToken();
    if (!token) {
      window.location.href = '/login';
      return null;
    }
    const response = await fetch(API_BASE_URL + `/payroll/employees/${employeeId}`, {
      headers: {
        'Authorization': 'Bearer ' + token,
        'Content-Type': 'application/json',
      },
    });
    if (response.status === 401) {
      clearAuthToken();
      window.location.href = '/login';
      return null;
    }
    if (!response.ok) {
      throw new Error('Failed to fetch payroll employee');
    }
    return await response.json();
  } catch (error) {
    console.error('Error fetching payroll employee:', error);
    throw error;
  }
};

export const updatePayrollEmployee = async (employeeId: number, employeeData: any) => {
  try {
    const token = getAuthToken();
    if (!token) {
      window.location.href = '/login';
      return null;
    }
    const response = await fetch(API_BASE_URL + `/payroll/employees/${employeeId}`, {
      method: 'PUT',
      headers: {
        'Authorization': 'Bearer ' + token,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(employeeData),
    });
    if (response.status === 401) {
      clearAuthToken();
      window.location.href = '/login';
      return null;
    }
    if (!response.ok) {
      throw new Error('Failed to update payroll employee');
    }
    return await response.json();
  } catch (error) {
    console.error('Error updating payroll employee:', error);
    throw error;
  }
};

export const deletePayrollEmployee = async (employeeId: number) => {
  try {
    const token = getAuthToken();
    if (!token) {
      window.location.href = '/login';
      return false;
    }
    const response = await fetch(API_BASE_URL + `/payroll/employees/${employeeId}`, {
      method: 'DELETE',
      headers: {
        'Authorization': 'Bearer ' + token,
      },
    });
    if (response.status === 401) {
      clearAuthToken();
      window.location.href = '/login';
      return false;
    }
    if (!response.ok) {
      throw new Error('Failed to delete payroll employee');
    }
    return true;
  } catch (error) {
    console.error('Error deleting payroll employee:', error);
    throw error;
  }
};

// Salary API functions
export const createSalary = async (salaryData: any) => {
  try {
    const token = getAuthToken();
    if (!token) {
      window.location.href = '/login';
      return null;
    }
    const response = await fetch(API_BASE_URL + '/payroll/salaries/', {
      method: 'POST',
      headers: {
        'Authorization': 'Bearer ' + token,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(salaryData),
    });
    if (response.status === 401) {
      clearAuthToken();
      window.location.href = '/login';
      return null;
    }
    if (!response.ok) {
      throw new Error('Failed to create salary');
    }
    return await response.json();
  } catch (error) {
    console.error('Error creating salary:', error);
    throw error;
  }
};

export const getEmployeeSalaries = async (employeeId: number) => {
  try {
    const token = getAuthToken();
    if (!token) {
      window.location.href = '/login';
      return [];
    }
    const response = await fetch(API_BASE_URL + `/payroll/salaries/employee/${employeeId}`, {
      headers: {
        'Authorization': 'Bearer ' + token,
        'Content-Type': 'application/json',
      },
    });
    if (response.status === 401) {
      clearAuthToken();
      window.location.href = '/login';
      return [];
    }
    if (!response.ok) {
      throw new Error('Failed to fetch employee salaries');
    }
    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error fetching employee salaries:', error);
    throw error;
  }
};

export const updateSalary = async (salaryId: number, salaryData: any) => {
  try {
    const token = getAuthToken();
    if (!token) {
      window.location.href = '/login';
      return null;
    }
    const response = await fetch(API_BASE_URL + `/payroll/salaries/${salaryId}`, {
      method: 'PUT',
      headers: {
        'Authorization': 'Bearer ' + token,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(salaryData),
    });
    if (response.status === 401) {
      clearAuthToken();
      window.location.href = '/login';
      return null;
    }
    if (!response.ok) {
      throw new Error('Failed to update salary');
    }
    return await response.json();
  } catch (error) {
    console.error('Error updating salary:', error);
    throw error;
  }
};

export const deleteSalary = async (salaryId: number) => {
  try {
    const token = getAuthToken();
    if (!token) {
      window.location.href = '/login';
      return false;
    }
    const response = await fetch(API_BASE_URL + `/payroll/salaries/${salaryId}`, {
      method: 'DELETE',
      headers: {
        'Authorization': 'Bearer ' + token,
      },
    });
    if (response.status === 401) {
      clearAuthToken();
      window.location.href = '/login';
      return false;
    }
    if (!response.ok) {
      throw new Error('Failed to delete salary');
    }
    return true;
  } catch (error) {
    console.error('Error deleting salary:', error);
    throw error;
  }
};

// Allowance API functions
export const createAllowance = async (allowanceData: any) => {
  try {
    const token = getAuthToken();
    if (!token) {
      window.location.href = '/login';
      return null;
    }
    const response = await fetch(API_BASE_URL + '/payroll/allowances/', {
      method: 'POST',
      headers: {
        'Authorization': 'Bearer ' + token,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(allowanceData),
    });
    if (response.status === 401) {
      clearAuthToken();
      window.location.href = '/login';
      return null;
    }
    if (!response.ok) {
      throw new Error('Failed to create allowance');
    }
    return await response.json();
  } catch (error) {
    console.error('Error creating allowance:', error);
    throw error;
  }
};

export const getEmployeeAllowances = async (employeeId: number) => {
  try {
    const token = getAuthToken();
    if (!token) {
      window.location.href = '/login';
      return [];
    }
    const response = await fetch(API_BASE_URL + `/payroll/allowances/employee/${employeeId}`, {
      headers: {
        'Authorization': 'Bearer ' + token,
        'Content-Type': 'application/json',
      },
    });
    if (response.status === 401) {
      clearAuthToken();
      window.location.href = '/login';
      return [];
    }
    if (!response.ok) {
      throw new Error('Failed to fetch employee allowances');
    }
    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error fetching employee allowances:', error);
    throw error;
  }
};

export const updateAllowance = async (allowanceId: number, allowanceData: any) => {
  try {
    const token = getAuthToken();
    if (!token) {
      window.location.href = '/login';
      return null;
    }
    const response = await fetch(API_BASE_URL + `/payroll/allowances/${allowanceId}`, {
      method: 'PUT',
      headers: {
        'Authorization': 'Bearer ' + token,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(allowanceData),
    });
    if (response.status === 401) {
      clearAuthToken();
      window.location.href = '/login';
      return null;
    }
    if (!response.ok) {
      throw new Error('Failed to update allowance');
    }
    return await response.json();
  } catch (error) {
    console.error('Error updating allowance:', error);
    throw error;
  }
};

export const deleteAllowance = async (allowanceId: number) => {
  try {
    const token = getAuthToken();
    if (!token) {
      window.location.href = '/login';
      return false;
    }
    const response = await fetch(API_BASE_URL + `/payroll/allowances/${allowanceId}`, {
      method: 'DELETE',
      headers: {
        'Authorization': 'Bearer ' + token,
      },
    });
    if (response.status === 401) {
      clearAuthToken();
      window.location.href = '/login';
      return false;
    }
    if (!response.ok) {
      throw new Error('Failed to delete allowance');
    }
    return true;
  } catch (error) {
    console.error('Error deleting allowance:', error);
    throw error;
  }
};

// Deduction API functions
export const createDeduction = async (deductionData: any) => {
  try {
    const token = getAuthToken();
    if (!token) {
      window.location.href = '/login';
      return null;
    }
    const response = await fetch(API_BASE_URL + '/payroll/deductions/', {
      method: 'POST',
      headers: {
        'Authorization': 'Bearer ' + token,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(deductionData),
    });
    if (response.status === 401) {
      clearAuthToken();
      window.location.href = '/login';
      return null;
    }
    if (!response.ok) {
      throw new Error('Failed to create deduction');
    }
    return await response.json();
  } catch (error) {
    console.error('Error creating deduction:', error);
    throw error;
  }
};

export const getEmployeeDeductions = async (employeeId: number) => {
  try {
    const token = getAuthToken();
    if (!token) {
      window.location.href = '/login';
      return [];
    }
    const response = await fetch(API_BASE_URL + `/payroll/deductions/employee/${employeeId}`, {
      headers: {
        'Authorization': 'Bearer ' + token,
        'Content-Type': 'application/json',
      },
    });
    if (response.status === 401) {
      clearAuthToken();
      window.location.href = '/login';
      return [];
    }
    if (!response.ok) {
      throw new Error('Failed to fetch employee deductions');
    }
    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error fetching employee deductions:', error);
    throw error;
  }
};

export const updateDeduction = async (deductionId: number, deductionData: any) => {
  try {
    const token = getAuthToken();
    if (!token) {
      window.location.href = '/login';
      return null;
    }
    const response = await fetch(API_BASE_URL + `/payroll/deductions/${deductionId}`, {
      method: 'PUT',
      headers: {
        'Authorization': 'Bearer ' + token,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(deductionData),
    });
    if (response.status === 401) {
      clearAuthToken();
      window.location.href = '/login';
      return null;
    }
    if (!response.ok) {
      throw new Error('Failed to update deduction');
    }
    return await response.json();
  } catch (error) {
    console.error('Error updating deduction:', error);
    throw error;
  }
};

export const deleteDeduction = async (deductionId: number) => {
  try {
    const token = getAuthToken();
    if (!token) {
      window.location.href = '/login';
      return false;
    }
    const response = await fetch(API_BASE_URL + `/payroll/deductions/${deductionId}`, {
      method: 'DELETE',
      headers: {
        'Authorization': 'Bearer ' + token,
      },
    });
    if (response.status === 401) {
      clearAuthToken();
      window.location.href = '/login';
      return false;
    }
    if (!response.ok) {
      throw new Error('Failed to delete deduction');
    }
    return true;
  } catch (error) {
    console.error('Error deleting deduction:', error);
    throw error;
  }
};

// Bonus API functions
export const createBonus = async (bonusData: any) => {
  try {
    const token = getAuthToken();
    if (!token) {
      window.location.href = '/login';
      return null;
    }
    const response = await fetch(API_BASE_URL + '/payroll/bonuses/', {
      method: 'POST',
      headers: {
        'Authorization': 'Bearer ' + token,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(bonusData),
    });
    if (response.status === 401) {
      clearAuthToken();
      window.location.href = '/login';
      return null;
    }
    if (!response.ok) {
      throw new Error('Failed to create bonus');
    }
    return await response.json();
  } catch (error) {
    console.error('Error creating bonus:', error);
    throw error;
  }
};

export const getEmployeeBonuses = async (employeeId: number) => {
  try {
    const token = getAuthToken();
    if (!token) {
      window.location.href = '/login';
      return [];
    }
    const response = await fetch(API_BASE_URL + `/payroll/bonuses/employee/${employeeId}`, {
      headers: {
        'Authorization': 'Bearer ' + token,
        'Content-Type': 'application/json',
      },
    });
    if (response.status === 401) {
      clearAuthToken();
      window.location.href = '/login';
      return [];
    }
    if (!response.ok) {
      throw new Error('Failed to fetch employee bonuses');
    }
    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error fetching employee bonuses:', error);
    throw error;
  }
};

export const updateBonus = async (bonusId: number, bonusData: any) => {
  try {
    const token = getAuthToken();
    if (!token) {
      window.location.href = '/login';
      return null;
    }
    const response = await fetch(API_BASE_URL + `/payroll/bonuses/${bonusId}`, {
      method: 'PUT',
      headers: {
        'Authorization': 'Bearer ' + token,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(bonusData),
    });
    if (response.status === 401) {
      clearAuthToken();
      window.location.href = '/login';
      return null;
    }
    if (!response.ok) {
      throw new Error('Failed to update bonus');
    }
    return await response.json();
  } catch (error) {
    console.error('Error updating bonus:', error);
    throw error;
  }
};

export const deleteBonus = async (bonusId: number) => {
  try {
    const token = getAuthToken();
    if (!token) {
      window.location.href = '/login';
      return false;
    }
    const response = await fetch(API_BASE_URL + `/payroll/bonuses/${bonusId}`, {
      method: 'DELETE',
      headers: {
        'Authorization': 'Bearer ' + token,
      },
    });
    if (response.status === 401) {
      clearAuthToken();
      window.location.href = '/login';
      return false;
    }
    if (!response.ok) {
      throw new Error('Failed to delete bonus');
    }
    return true;
  } catch (error) {
    console.error('Error deleting bonus:', error);
    throw error;
  }
};

// Payroll Run API functions
export const createPayrollRun = async (payrollRunData: any) => {
  try {
    const token = getAuthToken();
    if (!token) {
      window.location.href = '/login';
      return null;
    }
    const response = await fetch(API_BASE_URL + '/payroll/payroll-runs/', {
      method: 'POST',
      headers: {
        'Authorization': 'Bearer ' + token,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(payrollRunData),
    });
    if (response.status === 401) {
      clearAuthToken();
      window.location.href = '/login';
      return null;
    }
    if (!response.ok) {
      throw new Error('Failed to create payroll run');
    }
    return await response.json();
  } catch (error) {
    console.error('Error creating payroll run:', error);
    throw error;
  }
};

export const getPayrollRuns = async () => {
  try {
    const token = getAuthToken();
    if (!token) {
      window.location.href = '/login';
      return [];
    }
    const response = await fetch(API_BASE_URL + '/payroll/payroll-runs/', {
      headers: {
        'Authorization': 'Bearer ' + token,
        'Content-Type': 'application/json',
      },
    });
    if (response.status === 401) {
      clearAuthToken();
      window.location.href = '/login';
      return [];
    }
    if (!response.ok) {
      throw new Error('Failed to fetch payroll runs');
    }
    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error fetching payroll runs:', error);
    throw error;
  }
};

export const getPayrollRun = async (payrollRunId: number) => {
  try {
    const token = getAuthToken();
    if (!token) {
      window.location.href = '/login';
      return null;
    }
    const response = await fetch(API_BASE_URL + `/payroll/payroll-runs/${payrollRunId}`, {
      headers: {
        'Authorization': 'Bearer ' + token,
        'Content-Type': 'application/json',
      },
    });
    if (response.status === 401) {
      clearAuthToken();
      window.location.href = '/login';
      return null;
    }
    if (!response.ok) {
      throw new Error('Failed to fetch payroll run');
    }
    return await response.json();
  } catch (error) {
    console.error('Error fetching payroll run:', error);
    throw error;
  }
};

export const updatePayrollRun = async (payrollRunId: number, payrollRunData: any) => {
  try {
    const token = getAuthToken();
    if (!token) {
      window.location.href = '/login';
      return null;
    }
    const response = await fetch(API_BASE_URL + `/payroll/payroll-runs/${payrollRunId}`, {
      method: 'PUT',
      headers: {
        'Authorization': 'Bearer ' + token,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(payrollRunData),
    });
    if (response.status === 401) {
      clearAuthToken();
      window.location.href = '/login';
      return null;
    }
    if (!response.ok) {
      throw new Error('Failed to update payroll run');
    }
    return await response.json();
  } catch (error) {
    console.error('Error updating payroll run:', error);
    throw error;
  }
};

export const deletePayrollRun = async (payrollRunId: number) => {
  try {
    const token = getAuthToken();
    if (!token) {
      window.location.href = '/login';
      return false;
    }
    const response = await fetch(API_BASE_URL + `/payroll/payroll-runs/${payrollRunId}`, {
      method: 'DELETE',
      headers: {
        'Authorization': 'Bearer ' + token,
      },
    });
    if (response.status === 401) {
      clearAuthToken();
      window.location.href = '/login';
      return false;
    }
    if (!response.ok) {
      throw new Error('Failed to delete payroll run');
    }
    return true;
  } catch (error) {
    console.error('Error deleting payroll run:', error);
    throw error;
  }
};

// Payroll Entry API functions
export const createPayrollEntry = async (payrollEntryData: any) => {
  try {
    const token = getAuthToken();
    if (!token) {
      window.location.href = '/login';
      return null;
    }
    const response = await fetch(API_BASE_URL + '/payroll/payroll-entries/', {
      method: 'POST',
      headers: {
        'Authorization': 'Bearer ' + token,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(payrollEntryData),
    });
    if (response.status === 401) {
      clearAuthToken();
      window.location.href = '/login';
      return null;
    }
    if (!response.ok) {
      throw new Error('Failed to create payroll entry');
    }
    return await response.json();
  } catch (error) {
    console.error('Error creating payroll entry:', error);
    throw error;
  }
};

export const getPayrollEntriesByRun = async (payrollRunId: number) => {
  try {
    const token = getAuthToken();
    if (!token) {
      window.location.href = '/login';
      return [];
    }
    const response = await fetch(API_BASE_URL + `/payroll/payroll-entries/run/${payrollRunId}`, {
      headers: {
        'Authorization': 'Bearer ' + token,
        'Content-Type': 'application/json',
      },
    });
    if (response.status === 401) {
      clearAuthToken();
      window.location.href = '/login';
      return [];
    }
    if (!response.ok) {
      throw new Error('Failed to fetch payroll entries by run');
    }
    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error fetching payroll entries by run:', error);
    throw error;
  }
};

export const getPayrollEntriesByEmployee = async (employeeId: number) => {
  try {
    const token = getAuthToken();
    if (!token) {
      window.location.href = '/login';
      return [];
    }
    const response = await fetch(API_BASE_URL + `/payroll/payroll-entries/employee/${employeeId}`, {
      headers: {
        'Authorization': 'Bearer ' + token,
        'Content-Type': 'application/json',
      },
    });
    if (response.status === 401) {
      clearAuthToken();
      window.location.href = '/login';
      return [];
    }
    if (!response.ok) {
      throw new Error('Failed to fetch payroll entries by employee');
    }
    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error fetching payroll entries by employee:', error);
    throw error;
  }
};

export const updatePayrollEntry = async (payrollEntryId: number, payrollEntryData: any) => {
  try {
    const token = getAuthToken();
    if (!token) {
      window.location.href = '/login';
      return null;
    }
    const response = await fetch(API_BASE_URL + `/payroll/payroll-entries/${payrollEntryId}`, {
      method: 'PUT',
      headers: {
        'Authorization': 'Bearer ' + token,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(payrollEntryData),
    });
    if (response.status === 401) {
      clearAuthToken();
      window.location.href = '/login';
      return null;
    }
    if (!response.ok) {
      throw new Error('Failed to update payroll entry');
    }
    return await response.json();
  } catch (error) {
    console.error('Error updating payroll entry:', error);
    throw error;
  }
};

export const deletePayrollEntry = async (payrollEntryId: number) => {
  try {
    const token = getAuthToken();
    if (!token) {
      window.location.href = '/login';
      return false;
    }
    const response = await fetch(API_BASE_URL + `/payroll/payroll-entries/${payrollEntryId}`, {
      method: 'DELETE',
      headers: {
        'Authorization': 'Bearer ' + token,
      },
    });
    if (response.status === 401) {
      clearAuthToken();
      window.location.href = '/login';
      return false;
    }
    if (!response.ok) {
      throw new Error('Failed to delete payroll entry');
    }
    return true;
  } catch (error) {
    console.error('Error deleting payroll entry:', error);
    throw error;
  }
};
