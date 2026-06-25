# Rationale Template Audit

Date: 2026-06-24
Scope: 15 sample requests in mock_data/requests.json
Criteria:
- Names specific driving check(s)
- Includes relevant amount, vendor name, or policy ID context
- Uses complete sentences (no bullet points)
- Uses 2 to 4 sentences

## Iteration 1 (before refinement)
- Total evaluated: 15
- Pass: 7
- Fail: 8
- Failed request IDs: REQ-004, REQ-005, REQ-006, REQ-007, REQ-009, REQ-011, REQ-012, REQ-014

Observed issues in failed cases:
- Rationale text embedded verbose policy detail blocks, causing sentence-count violations.
- Some fallback rationales included multiple policy-description fragments with extra punctuation, reducing clarity.
- Sentence counting logic incorrectly treated decimal points in currency values as sentence boundaries.

## Refinements applied
- Added explicit rationale template rules to the system prompt.
- Added rationale compliance checks in agent post-processing.
- Added deterministic rationale rewrite fallback when output is non-compliant.
- Fixed sentence counting to split only on punctuation followed by whitespace.
- Sanitized fallback key findings to concise single-sentence fragments.

## Iteration 2 (after refinement)
- Total evaluated: 15
- Pass: 15
- Fail: 0

Result:
- All 15 rationales meet template criteria after prompt and post-processing refinement.
