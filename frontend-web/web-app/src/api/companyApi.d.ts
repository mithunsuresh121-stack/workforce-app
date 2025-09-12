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
export declare const getCompanyUsers: (companyId: number, filters?: {
    department?: string;
    position?: string;
    search?: string;
}, sort?: {
    sortBy?: string;
    sortOrder?: "asc" | "desc";
}, pagination?: {
    page?: number;
    limit?: number;
}) => Promise<CompanyUsersResponse>;
export declare const getCompanyDepartments: (companyId: number) => Promise<string[]>;
export declare const getCompanyPositions: (companyId: number) => Promise<string[]>;
export {};
//# sourceMappingURL=companyApi.d.ts.map