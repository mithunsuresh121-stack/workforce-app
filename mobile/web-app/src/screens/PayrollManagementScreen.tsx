import React, { useState, useEffect } from 'react';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '../components/ui/table';
import Input from '../components/ui/Input';
import Button from '../components/ui/Button';
import Alert, { AlertDescription, AlertTitle } from '../components/ui/Alert';
import Skeleton from '../components/ui/skeleton';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/Card';
import {
  getPayrollEmployees,
  createPayrollEmployee,
  getPayrollEmployee,
  updatePayrollEmployee,
  deletePayrollEmployee,
  createSalary,
  getEmployeeSalaries,
  updateSalary,
  deleteSalary,
  createAllowance,
  getEmployeeAllowances,
  updateAllowance,
  deleteAllowance,
  createDeduction,
  getEmployeeDeductions,
  updateDeduction,
  deleteDeduction,
  createBonus,
  getEmployeeBonuses,
  updateBonus,
  deleteBonus,
  createPayrollRun,
  getPayrollRuns,
  getPayrollRun,
  updatePayrollRun,
  deletePayrollRun,
  createPayrollEntry,
  getPayrollEntriesByRun,
  getPayrollEntriesByEmployee,
  updatePayrollEntry,
  deletePayrollEntry
} from '../lib/api';

interface PayrollEmployee {
  id: number;
  user_id: number;
  employee_id: string;
  department: string;
  position: string;
  hire_date: string;
  base_salary: number;
  status: string;
  created_at: string;
  updated_at: string;
  user?: {
    id: number;
    email: string;
    full_name: string;
    role: string;
  };
}

interface Salary {
  id: number;
  employee_id: number;
  amount: number;
  effective_date: string;
  created_at: string;
  updated_at: string;
}

interface Allowance {
  id: number;
  employee_id: number;
  name: string;
  amount: number;
  type: string;
  is_taxable: string;
  effective_date: string;
  created_at: string;
  updated_at: string;
}

interface Deduction {
  id: number;
  employee_id: number;
  name: string;
  amount: number;
  type: string;
  is_mandatory: string;
  effective_date: string;
  created_at: string;
  updated_at: string;
}

interface Bonus {
  id: number;
  employee_id: number;
  name: string;
  amount: number;
  type: string;
  payment_date: string;
  created_at: string;
  updated_at: string;
}

interface PayrollRun {
  id: number;
  period_start: string;
  period_end: string;
  status: string;
  created_at: string;
  updated_at: string;
}

interface PayrollEntry {
  id: number;
  payroll_run_id: number;
  employee_id: number;
  base_salary: number;
  total_allowances: number;
  total_deductions: number;
  total_bonuses: number;
  gross_pay: number;
  net_pay: number;
  created_at: string;
  updated_at: string;
}

const PayrollManagementScreen: React.FC = () => {
  const [employees, setEmployees] = useState<PayrollEmployee[]>([]);
  const [selectedEmployee, setSelectedEmployee] = useState<PayrollEmployee | null>(null);
  const [salaries, setSalaries] = useState<Salary[]>([]);
  const [allowances, setAllowances] = useState<Allowance[]>([]);
  const [deductions, setDeductions] = useState<Deduction[]>([]);
  const [bonuses, setBonuses] = useState<Bonus[]>([]);
  const [payrollRuns, setPayrollRuns] = useState<PayrollRun[]>([]);
  const [payrollEntries, setPayrollEntries] = useState<PayrollEntry[]>([]);

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [operationLoading, setOperationLoading] = useState(false);

  // Form states
  const [newSalary, setNewSalary] = useState({ amount: '', effective_date: '' });
  const [newAllowance, setNewAllowance] = useState({
    name: '',
    amount: '',
    type: 'Monthly',
    is_taxable: 'Yes',
    effective_date: ''
  });
  const [newDeduction, setNewDeduction] = useState({
    name: '',
    amount: '',
    type: 'Monthly',
    is_mandatory: 'Yes',
    effective_date: ''
  });
  const [newBonus, setNewBonus] = useState({
    name: '',
    amount: '',
    type: 'Annual',
    payment_date: ''
  });
  const [newPayrollRun, setNewPayrollRun] = useState({
    period_start: '',
    period_end: ''
  });

  // Tab state
  const [activeTab, setActiveTab] = useState('overview');

  useEffect(() => {
    fetchEmployees();
    fetchPayrollRuns();
  }, []);

  useEffect(() => {
    if (selectedEmployee) {
      fetchEmployeeData(selectedEmployee.id);
    }
  }, [selectedEmployee]);

  const fetchEmployees = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await getPayrollEmployees();
      setEmployees(data);
    } catch (err) {
      setError('Failed to load employees. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const fetchPayrollRuns = async () => {
    try {
      const data = await getPayrollRuns();
      setPayrollRuns(data);
    } catch (err) {
      console.error('Failed to fetch payroll runs:', err);
    }
  };

  const fetchEmployeeData = async (employeeId: number) => {
    try {
      const [salariesData, allowancesData, deductionsData, bonusesData, entriesData] = await Promise.all([
        getEmployeeSalaries(employeeId),
        getEmployeeAllowances(employeeId),
        getEmployeeDeductions(employeeId),
        getEmployeeBonuses(employeeId),
        getPayrollEntriesByEmployee(employeeId)
      ]);

      setSalaries(salariesData);
      setAllowances(allowancesData);
      setDeductions(deductionsData);
      setBonuses(bonusesData);
      setPayrollEntries(entriesData);
    } catch (err) {
      console.error('Failed to fetch employee data:', err);
    }
  };

  const handleCreateSalary = async () => {
    if (!selectedEmployee || !newSalary.amount || !newSalary.effective_date) return;

    try {
      setOperationLoading(true);
      await createSalary({
        employee_id: selectedEmployee.id,
        amount: parseFloat(newSalary.amount),
        effective_date: new Date(newSalary.effective_date).toISOString()
      });

      setNewSalary({ amount: '', effective_date: '' });
      fetchEmployeeData(selectedEmployee.id);
    } catch (err) {
      setError('Failed to create salary. Please try again.');
    } finally {
      setOperationLoading(false);
    }
  };

  const handleCreateAllowance = async () => {
    if (!selectedEmployee || !newAllowance.name || !newAllowance.amount || !newAllowance.effective_date) return;

    try {
      setOperationLoading(true);
      await createAllowance({
        employee_id: selectedEmployee.id,
        name: newAllowance.name,
        amount: parseFloat(newAllowance.amount),
        type: newAllowance.type,
        is_taxable: newAllowance.is_taxable,
        effective_date: new Date(newAllowance.effective_date).toISOString()
      });

      setNewAllowance({
        name: '',
        amount: '',
        type: 'Monthly',
        is_taxable: 'Yes',
        effective_date: ''
      });
      fetchEmployeeData(selectedEmployee.id);
    } catch (err) {
      setError('Failed to create allowance. Please try again.');
    } finally {
      setOperationLoading(false);
    }
  };

  const handleCreateDeduction = async () => {
    if (!selectedEmployee || !newDeduction.name || !newDeduction.amount || !newDeduction.effective_date) return;

    try {
      setOperationLoading(true);
      await createDeduction({
        employee_id: selectedEmployee.id,
        name: newDeduction.name,
        amount: parseFloat(newDeduction.amount),
        type: newDeduction.type,
        is_mandatory: newDeduction.is_mandatory,
        effective_date: new Date(newDeduction.effective_date).toISOString()
      });

      setNewDeduction({
        name: '',
        amount: '',
        type: 'Monthly',
        is_mandatory: 'Yes',
        effective_date: ''
      });
      fetchEmployeeData(selectedEmployee.id);
    } catch (err) {
      setError('Failed to create deduction. Please try again.');
    } finally {
      setOperationLoading(false);
    }
  };

  const handleCreateBonus = async () => {
    if (!selectedEmployee || !newBonus.name || !newBonus.amount || !newBonus.payment_date) return;

    try {
      setOperationLoading(true);
      await createBonus({
        employee_id: selectedEmployee.id,
        name: newBonus.name,
        amount: parseFloat(newBonus.amount),
        type: newBonus.type,
        payment_date: new Date(newBonus.payment_date).toISOString()
      });

      setNewBonus({
        name: '',
        amount: '',
        type: 'Annual',
        payment_date: ''
      });
      fetchEmployeeData(selectedEmployee.id);
    } catch (err) {
      setError('Failed to create bonus. Please try again.');
    } finally {
      setOperationLoading(false);
    }
  };

  const handleCreatePayrollRun = async () => {
    if (!newPayrollRun.period_start || !newPayrollRun.period_end) return;

    try {
      setOperationLoading(true);
      await createPayrollRun({
        period_start: new Date(newPayrollRun.period_start).toISOString(),
        period_end: new Date(newPayrollRun.period_end).toISOString()
      });

      setNewPayrollRun({ period_start: '', period_end: '' });
      fetchPayrollRuns();
    } catch (err) {
      setError('Failed to create payroll run. Please try again.');
    } finally {
      setOperationLoading(false);
    }
  };

  const calculateSalaryBreakdown = () => {
    if (!selectedEmployee) return null;

    const currentSalary = salaries.find(s => new Date(s.effective_date) <= new Date()) || { amount: selectedEmployee.base_salary };
    const totalAllowances = allowances.reduce((sum, a) => sum + a.amount, 0);
    const totalDeductions = deductions.reduce((sum, d) => sum + d.amount, 0);
    const totalBonuses = bonuses.reduce((sum, b) => sum + b.amount, 0);

    const grossPay = currentSalary.amount + totalAllowances + totalBonuses;
    const netPay = grossPay - totalDeductions;

    return {
      baseSalary: currentSalary.amount,
      totalAllowances,
      totalDeductions,
      totalBonuses,
      grossPay,
      netPay
    };
  };

  const salaryBreakdown = calculateSalaryBreakdown();

  if (loading) {
    return (
      <div className="p-6">
        <h1 className="text-2xl font-bold mb-6">Payroll Management</h1>
        <Skeleton className="h-64 w-full" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-6">
        <h1 className="text-2xl font-bold mb-6">Payroll Management</h1>
        <Alert variant="destructive">
          <AlertTitle>Error</AlertTitle>
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      </div>
    );
  }

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold mb-6">Payroll Management</h1>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* Employee Selection */}
        <div className="lg:col-span-1">
          <Card>
            <CardHeader>
              <CardTitle>Select Employee</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                {employees.map((employee) => (
                  <div
                    key={employee.id}
                    className={`p-3 border rounded-lg cursor-pointer hover:bg-gray-50 ${
                      selectedEmployee?.id === employee.id ? 'border-blue-500 bg-blue-50' : ''
                    }`}
                    onClick={() => setSelectedEmployee(employee)}
                  >
                    <div className="font-medium">{employee.user?.full_name || 'N/A'}</div>
                    <div className="text-sm text-gray-500">{employee.employee_id}</div>
                    <div className="text-sm text-gray-500">{employee.position}</div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Main Content */}
        <div className="lg:col-span-3">
          {selectedEmployee ? (
            <div className="w-full">
              {/* Tab Navigation */}
              <div className="flex border-b mb-6">
                {[
                  { id: 'overview', label: 'Overview' },
                  { id: 'salary', label: 'Salary' },
                  { id: 'allowances', label: 'Allowances' },
                  { id: 'deductions', label: 'Deductions' },
                  { id: 'bonuses', label: 'Bonuses' },
                  { id: 'history', label: 'History' }
                ].map((tab) => (
                  <button
                    key={tab.id}
                    onClick={() => setActiveTab(tab.id)}
                    className={`px-4 py-2 border-b-2 font-medium text-sm ${
                      activeTab === tab.id
                        ? 'border-blue-500 text-blue-600'
                        : 'border-transparent text-gray-500 hover:text-gray-700'
                    }`}
                  >
                    {tab.label}
                  </button>
                ))}
              </div>

              {/* Tab Content */}
              {activeTab === 'overview' && (
                <div className="space-y-4">
                  <Card>
                    <CardHeader>
                      <CardTitle>Employee Information</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="grid grid-cols-2 gap-4">
                        <div>
                          <label className="text-sm font-medium">Name</label>
                          <p>{selectedEmployee.user?.full_name || 'N/A'}</p>
                        </div>
                        <div>
                          <label className="text-sm font-medium">Employee ID</label>
                          <p>{selectedEmployee.employee_id}</p>
                        </div>
                        <div>
                          <label className="text-sm font-medium">Position</label>
                          <p>{selectedEmployee.position}</p>
                        </div>
                        <div>
                          <label className="text-sm font-medium">Department</label>
                          <p>{selectedEmployee.department}</p>
                        </div>
                      </div>
                    </CardContent>
                  </Card>

                  {salaryBreakdown && (
                    <Card>
                      <CardHeader>
                        <CardTitle>Salary Breakdown</CardTitle>
                      </CardHeader>
                      <CardContent>
                        <div className="grid grid-cols-2 gap-4">
                          <div>
                            <label className="text-sm font-medium">Base Salary</label>
                            <p className="text-lg font-semibold">${salaryBreakdown.baseSalary.toLocaleString()}</p>
                          </div>
                          <div>
                            <label className="text-sm font-medium">Total Allowances</label>
                            <p className="text-lg font-semibold text-green-600">+${salaryBreakdown.totalAllowances.toLocaleString()}</p>
                          </div>
                          <div>
                            <label className="text-sm font-medium">Total Deductions</label>
                            <p className="text-lg font-semibold text-red-600">-${salaryBreakdown.totalDeductions.toLocaleString()}</p>
                          </div>
                          <div>
                            <label className="text-sm font-medium">Total Bonuses</label>
                            <p className="text-lg font-semibold text-green-600">+${salaryBreakdown.totalBonuses.toLocaleString()}</p>
                          </div>
                          <div className="col-span-2 border-t pt-4">
                            <label className="text-sm font-medium">Gross Pay</label>
                            <p className="text-xl font-bold">${salaryBreakdown.grossPay.toLocaleString()}</p>
                          </div>
                          <div className="col-span-2">
                            <label className="text-sm font-medium">Net Pay</label>
                            <p className="text-2xl font-bold text-blue-600">${salaryBreakdown.netPay.toLocaleString()}</p>
                          </div>
                        </div>
                      </CardContent>
                    </Card>
                  )}
                </div>
              )}

              {activeTab === 'salary' && (
                <div className="space-y-4">
                  <Card>
                    <CardHeader>
                      <CardTitle>Add New Salary</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="grid grid-cols-2 gap-4">
                        <Input
                          type="number"
                          placeholder="Amount"
                          value={newSalary.amount}
                          onChange={(e) => setNewSalary({ ...newSalary, amount: e.target.value })}
                        />
                        <Input
                          type="date"
                          value={newSalary.effective_date}
                          onChange={(e) => setNewSalary({ ...newSalary, effective_date: e.target.value })}
                        />
                        <Button
                          onClick={handleCreateSalary}
                          disabled={operationLoading}
                          className="col-span-2"
                        >
                          {operationLoading ? 'Adding...' : 'Add Salary'}
                        </Button>
                      </div>
                    </CardContent>
                  </Card>

                  <Card>
                    <CardHeader>
                      <CardTitle>Salary History</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <Table>
                        <TableHeader>
                          <TableRow>
                            <TableHead>Amount</TableHead>
                            <TableHead>Effective Date</TableHead>
                            <TableHead>Actions</TableHead>
                          </TableRow>
                        </TableHeader>
                        <TableBody>
                          {salaries.map((salary) => (
                            <TableRow key={salary.id}>
                              <TableCell>${salary.amount.toLocaleString()}</TableCell>
                              <TableCell>{new Date(salary.effective_date).toLocaleDateString()}</TableCell>
                              <TableCell>
                                <Button variant="outline" size="sm">Edit</Button>
                              </TableCell>
                            </TableRow>
                          ))}
                        </TableBody>
                      </Table>
                    </CardContent>
                  </Card>
                </div>
              )}

              {activeTab === 'allowances' && (
                <div className="space-y-4">
                  <Card>
                    <CardHeader>
                      <CardTitle>Add New Allowance</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="grid grid-cols-2 gap-4">
                        <Input
                          placeholder="Allowance Name"
                          value={newAllowance.name}
                          onChange={(e) => setNewAllowance({ ...newAllowance, name: e.target.value })}
                        />
                        <Input
                          type="number"
                          placeholder="Amount"
                          value={newAllowance.amount}
                          onChange={(e) => setNewAllowance({ ...newAllowance, amount: e.target.value })}
                        />
                        <select
                          className="border rounded px-3 py-2"
                          value={newAllowance.type}
                          onChange={(e) => setNewAllowance({ ...newAllowance, type: e.target.value })}
                        >
                          <option value="Monthly">Monthly</option>
                          <option value="Annual">Annual</option>
                          <option value="One-time">One-time</option>
                        </select>
                        <select
                          className="border rounded px-3 py-2"
                          value={newAllowance.is_taxable}
                          onChange={(e) => setNewAllowance({ ...newAllowance, is_taxable: e.target.value })}
                        >
                          <option value="Yes">Taxable</option>
                          <option value="No">Non-taxable</option>
                        </select>
                        <Input
                          type="date"
                          value={newAllowance.effective_date}
                          onChange={(e) => setNewAllowance({ ...newAllowance, effective_date: e.target.value })}
                          className="col-span-2"
                        />
                        <Button
                          onClick={handleCreateAllowance}
                          disabled={operationLoading}
                          className="col-span-2"
                        >
                          {operationLoading ? 'Adding...' : 'Add Allowance'}
                        </Button>
                      </div>
                    </CardContent>
                  </Card>

                  <Card>
                    <CardHeader>
                      <CardTitle>Allowances</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <Table>
                        <TableHeader>
                          <TableRow>
                            <TableHead>Name</TableHead>
                            <TableHead>Amount</TableHead>
                            <TableHead>Type</TableHead>
                            <TableHead>Taxable</TableHead>
                            <TableHead>Actions</TableHead>
                          </TableRow>
                        </TableHeader>
                        <TableBody>
                          {allowances.map((allowance) => (
                            <TableRow key={allowance.id}>
                              <TableCell>{allowance.name}</TableCell>
                              <TableCell>${allowance.amount.toLocaleString()}</TableCell>
                              <TableCell>{allowance.type}</TableCell>
                              <TableCell>
                                <span className={`px-2 py-1 rounded-full text-xs ${
                                  allowance.is_taxable === 'Yes'
                                    ? 'bg-blue-100 text-blue-800'
                                    : 'bg-gray-100 text-gray-800'
                                }`}>
                                  {allowance.is_taxable}
                                </span>
                              </TableCell>
                              <TableCell>
                                <Button variant="outline" size="sm">Edit</Button>
                              </TableCell>
                            </TableRow>
                          ))}
                        </TableBody>
                      </Table>
                    </CardContent>
                  </Card>
                </div>
              )}

              {activeTab === 'deductions' && (
                <div className="space-y-4">
                  <Card>
                    <CardHeader>
                      <CardTitle>Add New Deduction</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="grid grid-cols-2 gap-4">
                        <Input
                          placeholder="Deduction Name"
                          value={newDeduction.name}
                          onChange={(e) => setNewDeduction({ ...newDeduction, name: e.target.value })}
                        />
                        <Input
                          type="number"
                          placeholder="Amount"
                          value={newDeduction.amount}
                          onChange={(e) => setNewDeduction({ ...newDeduction, amount: e.target.value })}
                        />
                        <select
                          className="border rounded px-3 py-2"
                          value={newDeduction.type}
                          onChange={(e) => setNewDeduction({ ...newDeduction, type: e.target.value })}
                        >
                          <option value="Monthly">Monthly</option>
                          <option value="Annual">Annual</option>
                          <option value="One-time">One-time</option>
                        </select>
                        <select
                          className="border rounded px-3 py-2"
                          value={newDeduction.is_mandatory}
                          onChange={(e) => setNewDeduction({ ...newDeduction, is_mandatory: e.target.value })}
                        >
                          <option value="Yes">Mandatory</option>
                          <option value="No">Optional</option>
                        </select>
                        <Input
                          type="date"
                          value={newDeduction.effective_date}
                          onChange={(e) => setNewDeduction({ ...newDeduction, effective_date: e.target.value })}
                          className="col-span-2"
                        />
                        <Button
                          onClick={handleCreateDeduction}
                          disabled={operationLoading}
                          className="col-span-2"
                        >
                          {operationLoading ? 'Adding...' : 'Add Deduction'}
                        </Button>
                      </div>
                    </CardContent>
                  </Card>

                  <Card>
                    <CardHeader>
                      <CardTitle>Deductions</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <Table>
                        <TableHeader>
                          <TableRow>
                            <TableHead>Name</TableHead>
                            <TableHead>Amount</TableHead>
                            <TableHead>Type</TableHead>
                            <TableHead>Mandatory</TableHead>
                            <TableHead>Actions</TableHead>
                          </TableRow>
                        </TableHeader>
                        <TableBody>
                          {deductions.map((deduction) => (
                            <TableRow key={deduction.id}>
                              <TableCell>{deduction.name}</TableCell>
                              <TableCell>${deduction.amount.toLocaleString()}</TableCell>
                              <TableCell>{deduction.type}</TableCell>
                              <TableCell>
                                <span className={`px-2 py-1 rounded-full text-xs ${
                                  deduction.is_mandatory === 'Yes'
                                    ? 'bg-red-100 text-red-800'
                                    : 'bg-gray-100 text-gray-800'
                                }`}>
                                  {deduction.is_mandatory}
                                </span>
                              </TableCell>
                              <TableCell>
                                <Button variant="outline" size="sm">Edit</Button>
                              </TableCell>
                            </TableRow>
                          ))}
                        </TableBody>
                      </Table>
                    </CardContent>
                  </Card>
                </div>
              )}

              {activeTab === 'bonuses' && (
                <div className="space-y-4">
                  <Card>
                    <CardHeader>
                      <CardTitle>Add New Bonus</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="grid grid-cols-2 gap-4">
                        <Input
                          placeholder="Bonus Name"
                          value={newBonus.name}
                          onChange={(e) => setNewBonus({ ...newBonus, name: e.target.value })}
                        />
                        <Input
                          type="number"
                          placeholder="Amount"
                          value={newBonus.amount}
                          onChange={(e) => setNewBonus({ ...newBonus, amount: e.target.value })}
                        />
                        <select
                          className="border rounded px-3 py-2"
                          value={newBonus.type}
                          onChange={(e) => setNewBonus({ ...newBonus, type: e.target.value })}
                        >
                          <option value="Annual">Annual</option>
                          <option value="Performance">Performance</option>
                          <option value="One-time">One-time</option>
                        </select>
                        <Input
                          type="date"
                          placeholder="Payment Date"
                          value={newBonus.payment_date}
                          onChange={(e) => setNewBonus({ ...newBonus, payment_date: e.target.value })}
                        />
                        <Button
                          onClick={handleCreateBonus}
                          disabled={operationLoading}
                          className="col-span-2"
                        >
                          {operationLoading ? 'Adding...' : 'Add Bonus'}
                        </Button>
                      </div>
                    </CardContent>
                  </Card>

                  <Card>
                    <CardHeader>
                      <CardTitle>Bonuses</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <Table>
                        <TableHeader>
                          <TableRow>
                            <TableHead>Name</TableHead>
                            <TableHead>Amount</TableHead>
                            <TableHead>Type</TableHead>
                            <TableHead>Payment Date</TableHead>
                            <TableHead>Actions</TableHead>
                          </TableRow>
                        </TableHeader>
                        <TableBody>
                          {bonuses.map((bonus) => (
                            <TableRow key={bonus.id}>
                              <TableCell>{bonus.name}</TableCell>
                              <TableCell>${bonus.amount.toLocaleString()}</TableCell>
                              <TableCell>{bonus.type}</TableCell>
                              <TableCell>{new Date(bonus.payment_date).toLocaleDateString()}</TableCell>
                              <TableCell>
                                <Button variant="outline" size="sm">Edit</Button>
                              </TableCell>
                            </TableRow>
                          ))}
                        </TableBody>
                      </Table>
                    </CardContent>
                  </Card>
                </div>
              )}

              {activeTab === 'history' && (
                <div className="space-y-4">
                  <Card>
                    <CardHeader>
                      <CardTitle>Payroll History</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <Table>
                        <TableHeader>
                          <TableRow>
                            <TableHead>Period</TableHead>
                            <TableHead>Base Salary</TableHead>
                            <TableHead>Allowances</TableHead>
                            <TableHead>Deductions</TableHead>
                            <TableHead>Bonuses</TableHead>
                            <TableHead>Gross Pay</TableHead>
                            <TableHead>Net Pay</TableHead>
                          </TableRow>
                        </TableHeader>
                        <TableBody>
                          {payrollEntries.map((entry) => (
                            <TableRow key={entry.id}>
                              <TableCell>
                                {new Date(entry.created_at).toLocaleDateString()}
                              </TableCell>
                              <TableCell>${entry.base_salary.toLocaleString()}</TableCell>
                              <TableCell>${entry.total_allowances.toLocaleString()}</TableCell>
                              <TableCell>${entry.total_deductions.toLocaleString()}</TableCell>
                              <TableCell>${entry.total_bonuses.toLocaleString()}</TableCell>
                              <TableCell className="font-semibold">${entry.gross_pay.toLocaleString()}</TableCell>
                              <TableCell className="font-bold text-blue-600">${entry.net_pay.toLocaleString()}</TableCell>
                            </TableRow>
                          ))}
                        </TableBody>
                      </Table>
                    </CardContent>
                  </Card>
                </div>
              )}
            </div>
          ) : (
            <Card>
              <CardContent className="flex items-center justify-center h-64">
                <p className="text-gray-500">Select an employee to view payroll information</p>
              </CardContent>
            </Card>
          )}
        </div>
      </div>

      {/* Payroll Runs Management */}
      <Card className="mt-6">
        <CardHeader>
          <CardTitle>Payroll Runs</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
            <Input
              type="date"
              placeholder="Period Start"
              value={newPayrollRun.period_start}
              onChange={(e) => setNewPayrollRun({ ...newPayrollRun, period_start: e.target.value })}
            />
            <Input
              type="date"
              placeholder="Period End"
              value={newPayrollRun.period_end}
              onChange={(e) => setNewPayrollRun({ ...newPayrollRun, period_end: e.target.value })}
            />
            <Button
              onClick={handleCreatePayrollRun}
              disabled={operationLoading}
            >
              {operationLoading ? 'Creating...' : 'Create Payroll Run'}
            </Button>
          </div>

          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Period Start</TableHead>
                <TableHead>Period End</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Created</TableHead>
                <TableHead>Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {payrollRuns.map((run) => (
                <TableRow key={run.id}>
                  <TableCell>{new Date(run.period_start).toLocaleDateString()}</TableCell>
                  <TableCell>{new Date(run.period_end).toLocaleDateString()}</TableCell>
                  <TableCell>
                    <span className={`px-2 py-1 rounded-full text-xs ${
                      run.status === 'Completed' ? 'bg-green-100 text-green-800' :
                      run.status === 'Processing' ? 'bg-yellow-100 text-yellow-800' :
                      'bg-gray-100 text-gray-800'
                    }`}>
                      {run.status}
                    </span>
                  </TableCell>
                  <TableCell>{new Date(run.created_at).toLocaleDateString()}</TableCell>
                  <TableCell>
                    <div className="flex space-x-2">
                      <Button variant="outline" size="sm">View</Button>
                      <Button variant="outline" size="sm">Process</Button>
                    </div>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </div>
  );
};

export default PayrollManagementScreen;
