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
export declare const getCurrentUserProfile: () => Promise<UserProfile>;
export declare const updateCurrentUserProfile: (data: UpdateProfileData) => Promise<UserProfile>;
export {};
//# sourceMappingURL=userApi.d.ts.map