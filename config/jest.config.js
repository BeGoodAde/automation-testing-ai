module.exports = {
  testEnvironment: 'node',
  roots: ['<rootDir>/tests/javascript', '<rootDir>/src/javascript'],
  testMatch: ['**/__tests__/**/*.js', '**/?(*.)+(spec|test).js'],
  collectCoverageFrom: [
    'src/javascript/**/*.js',
    '!src/javascript/**/*.test.js',
    '!**/node_modules/**'
  ],
  coverageDirectory: 'reports/test-coverage',
  coverageReporters: ['text', 'lcov', 'html'],
  verbose: true
};