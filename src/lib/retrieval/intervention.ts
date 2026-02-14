/**
 * Retrieval Intervention Module
 *
 * TypeScript port of validated P5-07A intervention primitives.
 * Implements deterministic motif detection and rank-aware penalty scaling.
 *
 * P5-07D-A: Runtime strategy toggle wiring for staged rollout.
 * Reference: research/ab-eval/py/run_p5_04a_hardneg_trial.py
 */

// Penalty constants (validated in P5-06B-R2)
export const DEFAULT_VINTAGE_PENALTY = 0.20;
export const DEFAULT_STRICT_PENALTY = 0.18;
export const RANK_SCALING_FACTOR = 0.15;

// Motif detection terms
const VINTAGE_TERMS = ['vintage', 'retro', 'classic', 'old-school', 'art deco', '70s', '80s'];
const STRICT_TERMS = ['exact', 'literally', 'strictly', 'must', 'only', 'precise'];

// Strict cue patterns (deterministic regex, no model calls)
const STRICT_USE_CASE_PATTERN = /\bfor\s+(?:a|an|the\s+)?(?:[a-z0-9-]+\s+){0,4}(?:firm|brand|company|startup)\b/i;
const STRICT_CONSTRAINT_PATTERN = /\b(?:tight|specific|particular|certain)\b/i;
const STRICT_DOMAIN_PATTERN = /\b(?:industrial|professional|authoritative|stern)\b/i;

// Standard English stopword set
const STOPWORDS = new Set([
  'a', 'about', 'above', 'after', 'again', 'against', 'all', 'am', 'an', 'and', 'any', 'are', 'as', 'at',
  'be', 'because', 'been', 'before', 'being', 'below', 'between', 'both', 'but', 'by',
  'can', 'could',
  'did', 'do', 'does', 'doing', 'down', 'during',
  'each',
  'few', 'for', 'from', 'further',
  'had', 'has', 'have', 'having', 'he', 'her', 'here', 'hers', 'herself', 'him', 'himself', 'his', 'how',
  'i', 'if', 'in', 'into', 'is', 'it', 'its', 'itself',
  'just',
  'me', 'more', 'most', 'my', 'myself',
  'no', 'nor', 'not', 'now',
  'of', 'off', 'on', 'once', 'only', 'or', 'other', 'our', 'ours', 'ourselves', 'out', 'over', 'own',
  'same', 'she', 'should', 'so', 'some', 'such',
  'than', 'that', 'the', 'their', 'theirs', 'them', 'themselves', 'then', 'there', 'these', 'they', 'this',
  'those', 'through', 'to', 'too',
  'under', 'until', 'up',
  'very',
  'was', 'we', 'were', 'what', 'when', 'where', 'which', 'while', 'who', 'whom', 'why', 'will', 'with', 'would',
  'you', 'your', 'yours', 'yourself', 'yourselves',
]);

/**
 * Retrieval result item from vector search.
 */
export interface RetrievalResult {
  name: string;
  category?: string;
  description?: string;
  tags?: string[];
  source?: string;
  files?: Record<string, string>;
  confidence?: number;
  [key: string]: unknown;
}

/**
 * Result item with intervention metadata.
 */
export interface InterventionResult extends RetrievalResult {
  originalConfidence: number;
  adjustedConfidence: number;
  penaltyApplied: number;
  penaltyReason: string;
  motif: string | null;
}

/**
 * Motif types for intervention.
 */
export type Motif = 'vintage_era' | 'over_strict_semantic' | null;

/**
 * Tokenize text into lowercase alphanumeric tokens.
 */
function tokenize(text: string): string[] {
  return (text || '').toLowerCase().match(/[a-z0-9]+(?:-[a-z0-9]+)?/g) || [];
}

/**
 * Check if text contains any of the specified terms.
 */
function containsAnyTerm(text: string, terms: string[]): boolean {
  const lowered = (text || '').toLowerCase();
  return terms.some(term => lowered.includes(term));
}

/**
 * Get non-stopword tokens from query text.
 */
function nonStopwordQueryTokens(queryText: string): string[] {
  return tokenize(queryText).filter(t => !STOPWORDS.has(t));
}

/**
 * Build searchable text from font metadata.
 */
function buildFontText(font: RetrievalResult): string {
  const parts = [
    font.name || '',
    font.category || '',
    Array.isArray(font.tags) ? font.tags.join(' ') : '',
    font.description || '',
  ];
  return parts.join(' ').trim();
}

/**
 * Assign motif based on query text (deterministic).
 *
 * @param queryText - The user's search query
 * @returns The detected motif or null
 */
export function assignMotif(queryText: string): Motif {
  const q = (queryText || '').toLowerCase();

  if (containsAnyTerm(q, VINTAGE_TERMS)) {
    return 'vintage_era';
  }

  if (containsAnyTerm(q, STRICT_TERMS)) {
    return 'over_strict_semantic';
  }

  if (STRICT_USE_CASE_PATTERN.test(q)) {
    return 'over_strict_semantic';
  }

  if (STRICT_CONSTRAINT_PATTERN.test(q)) {
    return 'over_strict_semantic';
  }

  if (STRICT_DOMAIN_PATTERN.test(q)) {
    return 'over_strict_semantic';
  }

  return null;
}

/**
 * Compute rank-boundary-aware penalty scaling.
 *
 * Formula: scaled_penalty = base_penalty * (1 + (10 - baseline_rank) * RANK_SCALING_FACTOR)
 *
 * Higher-ranked items (closer to rank 1) get larger penalties because:
 * - They have more influence on top-10 membership
 * - Demoting them has more impact on precision metrics
 *
 * @param basePenalty - The base penalty amount
 * @param baselineRank - The item's rank in baseline results (1-indexed)
 * @returns The scaled penalty
 */
export function computeScaledPenalty(basePenalty: number, baselineRank: number): number {
  if (baselineRank < 1 || baselineRank > 10) {
    return basePenalty; // No scaling for out-of-range ranks
  }
  const scalingMultiplier = 1 + (10 - baselineRank) * RANK_SCALING_FACTOR;
  return basePenalty * scalingMultiplier;
}

/**
 * Apply intervention to retrieval results.
 *
 * Non-mutating: returns a new array with adjusted confidence scores.
 *
 * @param results - The retrieval results from vector search
 * @param queryText - The user's search query
 * @param options - Optional penalty overrides
 * @returns New array with intervention metadata
 */
export function applyIntervention(
  results: RetrievalResult[],
  queryText: string,
  options?: {
    vintagePenalty?: number;
    strictPenalty?: number;
  }
): InterventionResult[] {
  const vintagePenalty = options?.vintagePenalty ?? DEFAULT_VINTAGE_PENALTY;
  const strictPenalty = options?.strictPenalty ?? DEFAULT_STRICT_PENALTY;

  const motif = assignMotif(queryText);
  const queryTokens = new Set(nonStopwordQueryTokens(queryText));

  // Create adjusted results with penalty application
  const adjusted = results.map((result, index) => {
    const baselineRank = index + 1;
    const baseScore = result.confidence ?? 0;
    const fontText = buildFontText(result);

    let basePenalty = 0;
    let penaltyReason = 'none';

    if (motif === 'vintage_era') {
      if (!containsAnyTerm(fontText, VINTAGE_TERMS)) {
        basePenalty = vintagePenalty;
        penaltyReason = 'vintage_term_absent';
      }
    } else if (motif === 'over_strict_semantic') {
      const candidateTokens = new Set(tokenize(fontText));
      if (queryTokens.size > 0 && candidateTokens.size > 0) {
        const overlap = Array.from(queryTokens).filter(t => candidateTokens.has(t)).length;
        if (overlap === 0) {
          basePenalty = strictPenalty;
          penaltyReason = 'strict_query_token_miss';
        }
      }
    }

    // Apply rank-boundary-aware scaling
    const penalty = basePenalty > 0 && baselineRank <= 10
      ? computeScaledPenalty(basePenalty, baselineRank)
      : basePenalty;

    const adjustedScore = Math.max(0, baseScore - penalty);

    return {
      ...result,
      originalConfidence: baseScore,
      adjustedConfidence: adjustedScore,
      penaltyApplied: penalty,
      penaltyReason,
      motif,
    } as InterventionResult;
  });

  // Sort by adjusted confidence (descending), then by original confidence as tie-breaker
  adjusted.sort((a, b) => {
    const scoreDiff = b.adjustedConfidence - a.adjustedConfidence;
    if (scoreDiff !== 0) return scoreDiff;
    const origDiff = (b.originalConfidence) - (a.originalConfidence);
    if (origDiff !== 0) return origDiff;
    return (a.name || '').localeCompare(b.name || '');
  });

  return adjusted;
}
