import { expect, afterEach, vi } from 'vitest';
import { cleanup } from '@testing-library/react';
import '@testing-library/jest-dom';

// Mock axios globally
vi.mock('axios', () => {
  const mockAxios = {
    create: vi.fn(() => ({
      interceptors: {
        request: { use: vi.fn() },
        response: { use: vi.fn() }
      },
      get: vi.fn(),
      post: vi.fn(),
      put: vi.fn(),
      delete: vi.fn()
    })),
    interceptors: {
      request: { use: vi.fn() },
      response: { use: vi.fn() }
    },
    get: vi.fn(),
    post: vi.fn(),
    put: vi.fn(),
    delete: vi.fn()
  };
  return {
    default: mockAxios,
    __esModule: true
  };
});

// Mock WebSocket globally
vi.mock('ws', () => {
  return {
    default: vi.fn().mockImplementation(() => ({
      on: vi.fn(),
      off: vi.fn(),
      send: vi.fn(),
      close: vi.fn(),
      readyState: 1 // OPEN
    })),
    __esModule: true
  };
});

// Extend Vitest's expect with jest-dom matchers
// Cleanup after each test case (e.g. clearing jsdom)
afterEach(() => {
  cleanup();
});
