const nextJest = require('next/jest')

const createJestConfig = nextJest({
    dir: './',
})

const customJestConfig = {
    setupFilesAfterEnv: ['<rootDir>/jest.setup.js'],
    testEnvironment: 'jest-environment-jsdom',
    collectCoverage: true,
    collectCoverageFrom: [
        "src/app/results/**/*.tsx",
        "src/app/page.tsx",
    ],
    coverageDirectory: 'coverage',
    coverageReporters: ['text', 'lcov'],
}

module.exports = createJestConfig(customJestConfig)
