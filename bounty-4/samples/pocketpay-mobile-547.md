# Example review: Axionvera/pocketpay-mobile#547

Source PR: https://github.com/Axionvera/pocketpay-mobile/pull/547

## Summary
This PR adds transaction-hash status resolution through Horizon, reconciles optimistic wallet entries only after a definitive result, and exposes an explicit refresh flow for pending or unknown transaction details. It also distinguishes confirmed, failed, pending, and unresolved UI states instead of treating every non-failure as success.

## Identified Risks
- `isNotFoundError()` treats any error message containing `not found` as an authoritative Horizon 404. A lower-level SDK/network error with that phrase could be downgraded to `unknown` instead of surfacing as a retryable transport failure.
- Pending reconciliation deletes `pendingTransactions[transactionHash]` by exact key while transaction matching accepts `id`, `hash`, or `transaction_hash`. If the pending map can be keyed by an alternate transaction identifier, a definitive status may update the history row but leave a stale pending entry.

## Improvement Suggestions
- Prefer the SDK/HTTP status shape for 404 detection and use message matching only as a narrowly documented compatibility fallback.
- Centralize transaction-hash normalization and use the same identity function both for pending-map eviction and history-row matching so definitive Horizon results cannot leave duplicate optimistic state behind.
- Consider carrying the authoritative Horizon transaction fields into the refreshed detail record, not only the boolean/status fields, when the UI later needs ledger/time metadata.

## Confidence
Medium
