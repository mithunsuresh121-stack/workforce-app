import type { Page } from '@playwright/test';
export declare function loginUser(page: Page): Promise<void>;
export declare function getProfileInput(page: Page, field: string): import("@playwright/test").Locator;
export declare function getProfileButton(page: Page, button: string): import("@playwright/test").Locator;
export declare function getProfileMessage(page: Page, type: string): import("@playwright/test").Locator;
export declare function getDirectoryFilter(page: Page, filter: string): import("@playwright/test").Locator;
export declare function getDirectoryItem(page: Page, id: string): import("@playwright/test").Locator;
export declare function getDirectoryMessage(page: Page, type: string): import("@playwright/test").Locator;
export declare function getDirectoryList(page: Page): import("@playwright/test").Locator;
export declare function getDirectoryItems(page: Page): import("@playwright/test").Locator;
export declare function getDirectorySort(page: Page, type: string): import("@playwright/test").Locator;
export declare function getDirectorySortBy(page: Page): import("@playwright/test").Locator;
export declare function getDirectorySortOrder(page: Page): import("@playwright/test").Locator;
export declare function getPageTitle(page: Page, title: string): import("@playwright/test").Locator;
export declare function getSuccessMessage(page: Page): import("@playwright/test").Locator;
export declare function getTableHeader(page: Page, header: string): import("@playwright/test").Locator;
export declare function getStatusIndicator(page: Page, status: string): import("@playwright/test").Locator;
//# sourceMappingURL=test-utils.d.ts.map