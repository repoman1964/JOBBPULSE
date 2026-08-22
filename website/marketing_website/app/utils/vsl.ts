export function vslEmbedSrc(raw: string): string {
  const url = raw.trim()
  if (!url) return ''

  try {
    const parsed = new URL(url)
    const host = parsed.hostname.replace(/^www\./, '')

    if (host === 'youtu.be') {
      const id = parsed.pathname.split('/').filter(Boolean)[0]
      return id ? `https://www.youtube.com/embed/${id}` : ''
    }

    if (host === 'youtube.com' || host === 'youtube-nocookie.com') {
      const id = parsed.searchParams.get('v') || parsed.pathname.split('/').filter(Boolean).pop()
      return id ? `https://www.youtube.com/embed/${id}` : ''
    }

    if (host === 'vimeo.com' || host === 'player.vimeo.com') {
      const id = parsed.pathname.split('/').filter(Boolean).pop()
      return id ? `https://player.vimeo.com/video/${id}` : ''
    }
  } catch {
    return ''
  }

  return url
}

export function isFileVideo(url: string): boolean {
  return /\.(mp4|webm|ogg)(\?|$)/i.test(url.trim())
}
