/**
 * Directory instances are metro-scoped (e.g. JobPulse ATL).
 * Never surface state in the UI — city (or area name) only.
 */

/** Strip trailing ", GA" / ", Georgia" style suffixes from a display string. */
export function stripState(label?: string | null): string {
  if (!label) return ''
  return String(label)
    .replace(/,\s*[A-Z]{2}\s*$/i, '')
    .replace(/,\s*Georgia\s*$/i, '')
    .trim()
}

/**
 * Prefer an explicit city field; otherwise strip state from a composite name.
 * Pass candidates in priority order (first non-empty wins after stripping).
 */
export function cityOnly(...candidates: Array<string | null | undefined>): string {
  for (const c of candidates) {
    const cleaned = stripState(c)
    if (cleaned) return cleaned
  }
  return ''
}
