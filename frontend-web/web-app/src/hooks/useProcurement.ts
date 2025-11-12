import { useState, useEffect, useCallback } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useAuth } from '../contexts/AuthContext';

interface Vendor {
  id: string;
  name: string;
  contact_email: string;
  contact_phone: string;
  address: string;
  status: 'ACTIVE' | 'INACTIVE';
  created_at: string;
}

interface PurchaseOrder {
  id: string;
  vendor_id: string;
  vendor_name: string;
  items: Array<{
    item_id: string;
    item_name: string;
    quantity: number;
    unit_price: number;
    total_price: number;
  }>;
  total_amount: number;
  status: 'DRAFT' | 'PENDING_APPROVAL' | 'APPROVED' | 'REJECTED' | 'COMPLETED';
  created_at: string;
  approved_at?: string;
}

interface InventoryItem {
  id: string;
  name: string;
  description: string;
  category: string;
  current_stock: number;
  min_stock_level: number;
  unit_price: number;
  supplier_id: string;
}

interface ProcurementStats {
  total_vendors: number;
  active_vendors: number;
  total_pos: number;
  pending_approvals: number;
  low_stock_items: number;
}

interface UseProcurementReturn {
  // Vendors
  vendors: Vendor[];
  vendorsLoading: boolean;
  vendorsError: string | null;
  createVendor: (vendor: Omit<Vendor, 'id' | 'created_at'>) => Promise<void>;
  updateVendor: (id: string, vendor: Partial<Vendor>) => Promise<void>;
  deleteVendor: (id: string) => Promise<void>;

  // Purchase Orders
  purchaseOrders: PurchaseOrder[];
  posLoading: boolean;
  posError: string | null;
  createPO: (po: Omit<PurchaseOrder, 'id' | 'created_at'>) => Promise<void>;
  updatePO: (id: string, po: Partial<PurchaseOrder>) => Promise<void>;
  approvePO: (id: string) => Promise<void>;

  // Inventory
  inventory: InventoryItem[];
  inventoryLoading: boolean;
  inventoryError: string | null;

  // Stats
  stats: ProcurementStats | null;
  statsLoading: boolean;

  // WebSocket
  connected: boolean;
  notifications: Array<{
    id: string;
    type: string;
    message: string;
    timestamp: string;
  }>;
}

export default function useProcurement(): UseProcurementReturn {
  const { user } = useAuth();
  const queryClient = useQueryClient();
  const [ws, setWs] = useState<WebSocket | null>(null);
  const [connected, setConnected] = useState(false);
  const [notifications, setNotifications] = useState<Array<{
    id: string;
    type: string;
    message: string;
    timestamp: string;
  }>>([]);

  // API base URL
  const apiBase = import.meta.env.VITE_API_URL || (process.env.NODE_ENV === 'production'
    ? 'https://api.workforce-app.com'
    : 'http://localhost:8000');

  // Vendors Query
  const {
    data: vendors = [],
    isLoading: vendorsLoading,
    error: vendorsError
  } = useQuery({
    queryKey: ['vendors'],
    queryFn: async () => {
      const response = await fetch(`${apiBase}/api/procurement/vendors`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
        },
      });
      if (!response.ok) throw new Error('Failed to fetch vendors');
      return response.json();
    },
    enabled: !!user,
  });

  // Purchase Orders Query
  const {
    data: purchaseOrders = [],
    isLoading: posLoading,
    error: posError
  } = useQuery({
    queryKey: ['purchase-orders'],
    queryFn: async () => {
      const response = await fetch(`${apiBase}/api/procurement/purchase-orders`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
        },
      });
      if (!response.ok) throw new Error('Failed to fetch purchase orders');
      return response.json();
    },
    enabled: !!user,
  });

  // Inventory Query
  const {
    data: inventory = [],
    isLoading: inventoryLoading,
    error: inventoryError
  } = useQuery({
    queryKey: ['inventory'],
    queryFn: async () => {
      const response = await fetch(`${apiBase}/api/procurement/inventory`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
        },
      });
      if (!response.ok) throw new Error('Failed to fetch inventory');
      return response.json();
    },
    enabled: !!user,
  });

  // Stats Query
  const {
    data: stats = null,
    isLoading: statsLoading
  } = useQuery({
    queryKey: ['procurement-stats'],
    queryFn: async () => {
      const response = await fetch(`${apiBase}/api/procurement/stats`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
        },
      });
      if (!response.ok) throw new Error('Failed to fetch stats');
      return response.json();
    },
    enabled: !!user,
  });

  // Mutations
  const createVendorMutation = useMutation({
    mutationFn: async (vendor: Omit<Vendor, 'id' | 'created_at'>) => {
      const response = await fetch(`${apiBase}/api/procurement/vendors`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
        },
        body: JSON.stringify(vendor),
      });
      if (!response.ok) throw new Error('Failed to create vendor');
      return response.json();
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['vendors'] });
      queryClient.invalidateQueries({ queryKey: ['procurement-stats'] });
    },
  });

  const updateVendorMutation = useMutation({
    mutationFn: async ({ id, vendor }: { id: string; vendor: Partial<Vendor> }) => {
      const response = await fetch(`${apiBase}/api/procurement/vendors/${id}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
        },
        body: JSON.stringify(vendor),
      });
      if (!response.ok) throw new Error('Failed to update vendor');
      return response.json();
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['vendors'] });
    },
  });

  const deleteVendorMutation = useMutation({
    mutationFn: async (id: string) => {
      const response = await fetch(`${apiBase}/api/procurement/vendors/${id}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
        },
      });
      if (!response.ok) throw new Error('Failed to delete vendor');
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['vendors'] });
      queryClient.invalidateQueries({ queryKey: ['procurement-stats'] });
    },
  });

  const createPOMutation = useMutation({
    mutationFn: async (po: Omit<PurchaseOrder, 'id' | 'created_at'>) => {
      const response = await fetch(`${apiBase}/api/procurement/purchase-orders`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
        },
        body: JSON.stringify(po),
      });
      if (!response.ok) throw new Error('Failed to create purchase order');
      return response.json();
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['purchase-orders'] });
      queryClient.invalidateQueries({ queryKey: ['procurement-stats'] });
    },
  });

  const updatePOMutation = useMutation({
    mutationFn: async ({ id, po }: { id: string; po: Partial<PurchaseOrder> }) => {
      const response = await fetch(`${apiBase}/api/procurement/purchase-orders/${id}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
        },
        body: JSON.stringify(po),
      });
      if (!response.ok) throw new Error('Failed to update purchase order');
      return response.json();
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['purchase-orders'] });
      queryClient.invalidateQueries({ queryKey: ['procurement-stats'] });
    },
  });

  const approvePOMutation = useMutation({
    mutationFn: async (id: string) => {
      const response = await fetch(`${apiBase}/api/procurement/purchase-orders/${id}/approve`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
        },
      });
      if (!response.ok) throw new Error('Failed to approve purchase order');
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['purchase-orders'] });
      queryClient.invalidateQueries({ queryKey: ['procurement-stats'] });
    },
  });

  // WebSocket connection for notifications
  useEffect(() => {
    if (!user) return;

    const token = localStorage.getItem('token');
    if (!token) return;

    const companyId = user.company_id;
    const wsUrl = `wss://${apiBase.replace('https://', '').replace('http://', '')}/ws/procurement/${companyId}?token=${token}`;

    const websocket = new WebSocket(wsUrl);

    websocket.onopen = () => {
      setConnected(true);
    };

    websocket.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        if (data.type === 'procurement_notification') {
          setNotifications(prev => [{
            id: Date.now().toString(),
            type: data.notification_type,
            message: data.message,
            timestamp: new Date().toISOString(),
          }, ...prev.slice(0, 9)]); // Keep last 10 notifications
        }
      } catch (err) {
        console.error('Failed to parse WebSocket message:', err);
      }
    };

    websocket.onclose = () => {
      setConnected(false);
    };

    websocket.onerror = (error) => {
      console.error('WebSocket error:', error);
    };

    setWs(websocket);

    return () => {
      websocket.close();
    };
  }, [user, apiBase]);

  // Callback functions
  const createVendor = useCallback(async (vendor: Omit<Vendor, 'id' | 'created_at'>) => {
    await createVendorMutation.mutateAsync(vendor);
  }, [createVendorMutation]);

  const updateVendor = useCallback(async (id: string, vendor: Partial<Vendor>) => {
    await updateVendorMutation.mutateAsync({ id, vendor });
  }, [updateVendorMutation]);

  const deleteVendor = useCallback(async (id: string) => {
    await deleteVendorMutation.mutateAsync(id);
  }, [deleteVendorMutation]);

  const createPO = useCallback(async (po: Omit<PurchaseOrder, 'id' | 'created_at'>) => {
    await createPOMutation.mutateAsync(po);
  }, [createPOMutation]);

  const updatePO = useCallback(async (id: string, po: Partial<PurchaseOrder>) => {
    await updatePOMutation.mutateAsync({ id, po });
  }, [updatePOMutation]);

  const approvePO = useCallback(async (id: string) => {
    await approvePOMutation.mutateAsync(id);
  }, [approvePOMutation]);

  return {
    // Vendors
    vendors,
    vendorsLoading,
    vendorsError: vendorsError?.message || null,
    createVendor,
    updateVendor,
    deleteVendor,

    // Purchase Orders
    purchaseOrders,
    posLoading,
    posError: posError?.message || null,
    createPO,
    updatePO,
    approvePO,

    // Inventory
    inventory,
    inventoryLoading,
    inventoryError: inventoryError?.message || null,

    // Stats
    stats,
    statsLoading,

    // WebSocket
    connected,
    notifications,
  };
}
