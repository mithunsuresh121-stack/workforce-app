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
export declare const getLeaveRequests: () => Promise<LeaveRequest[]>;
export declare const createLeaveRequest: (data: {
    start_date: string;
    end_date: string;
    reason?: string;
}) => Promise<LeaveRequest>;
export declare const updateLeaveRequest: (id: number, data: Partial<LeaveRequest>) => Promise<LeaveRequest>;
export {};
//# sourceMappingURL=leaveApi.d.ts.map