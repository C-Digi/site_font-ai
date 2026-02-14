/**
 * Retrieval Strategy Configuration
 *
 * Controls which retrieval intervention strategy is active at runtime.
 * Default is 'v3' (champion path) for safe default-off behavior.
 *
 * P5-07D-A: Runtime strategy toggle wiring for staged rollout.
 */

export type RetrievalStrategy = 'v3' | 'p5_07a';

/**
 * Get the active retrieval strategy from environment configuration.
 *
 * @returns The configured strategy, defaulting to 'v3' if unset or invalid.
 */
export function getRetrievalStrategy(): RetrievalStrategy {
  const envValue = process.env.RETRIEVAL_STRATEGY;

  if (envValue === 'p5_07a') {
    return 'p5_07a';
  }

  // Default to champion path for safe default-off behavior
  return 'v3';
}

/**
 * Check if the P5-07A intervention strategy is active.
 *
 * @returns True if p5_07a strategy is enabled via config.
 */
export function isP507AActive(): boolean {
  return getRetrievalStrategy() === 'p5_07a';
}
