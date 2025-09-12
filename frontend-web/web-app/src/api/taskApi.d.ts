interface Task {
    id: number;
    title: string;
    description?: string;
    status: string;
    assigned_to: number;
    created_by: number;
    created_at: string;
    updated_at: string;
}
export declare const getTasks: () => Promise<Task[]>;
export declare const createTask: (data: {
    title: string;
    description?: string;
    assigned_to: number;
}) => Promise<Task>;
export declare const updateTask: (id: number, data: Partial<Task>) => Promise<Task>;
export {};
//# sourceMappingURL=taskApi.d.ts.map