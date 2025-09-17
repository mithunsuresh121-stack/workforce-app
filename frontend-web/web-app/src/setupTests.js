import { expect, afterEach } from 'vitest';
import { cleanup } from '@testing-library/react';
import '@testing-library/jest-dom';

// Extend Vitest's expect with jest-dom matchers
// Cleanup after each test case (e.g. clearing jsdom)
afterEach(() => {
  cleanup();
});
