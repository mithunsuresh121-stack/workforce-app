import { expect, afterEach, vi } from 'vitest';
import { cleanup } from '@testing-library/react';
import '@testing-library/jest-dom';

// Global mocks for consistent testing
global.fetch = vi.fn();
global.localStorage = {
  getItem: vi.fn(),
  setItem: vi.fn(),
  removeItem: vi.fn(),
  clear: vi.fn(),
};

// Mock WebSocket globally
class MockWebSocket {
  constructor() {
    // Keep reference to the last instance for testing
    global.lastMockWebSocket = this;
    // Do not auto-call onopen; let tests control it
  }

  send() {}
  close() {}
}

global.WebSocket = MockWebSocket;

// Extend Vitest's expect with jest-dom matchers
// Cleanup after each test case (e.g. clearing jsdom)
afterEach(() => {
  cleanup();
});
