export function instagramHandle(companyName: string): string {
  const slug = companyName.toLowerCase().replace(/[^a-z0-9]+/g, '')
  return slug || 'company'
}

export function companyInitials(companyName: string): string {
  const parts = companyName.trim().split(/\s+/).filter(Boolean)
  if (parts.length === 0) return '?'
  if (parts.length === 1) return parts[0].slice(0, 2).toUpperCase()
  return (parts[0][0] + parts[parts.length - 1][0]).toUpperCase()
}

export type CaptionPart = { type: 'text' | 'tag'; value: string }

export function captionParts(body: string): CaptionPart[] {
  const re = /(#[A-Za-z0-9_]+)/g
  const parts: CaptionPart[] = []
  let last = 0
  let match: RegExpExecArray | null
  while ((match = re.exec(body))) {
    if (match.index > last) {
      parts.push({ type: 'text', value: body.slice(last, match.index) })
    }
    parts.push({ type: 'tag', value: match[1] })
    last = match.index + match[1].length
  }
  if (last < body.length) parts.push({ type: 'text', value: body.slice(last) })
  return parts.length ? parts : [{ type: 'text', value: body }]
}
