/**
 * Strip codec/params so the PUT Content-Type matches the signed S3/MinIO header.
 * MediaRecorder reports e.g. `audio/webm;codecs=opus`; the signed URL uses `audio/webm`.
 */
export function normalizeUploadContentType(contentType: string | undefined | null): string {
  return (contentType || '').split(';')[0].trim()
}

/**
 * PUT bytes to a browser-facing S3/R2 presigned URL.
 * Mock sessions (mock://) are a no-op — the mock client stores a local preview URL on complete.
 */
export async function putToPresignedUrl(
  uploadUrl: string,
  body: Blob,
  contentType: string,
): Promise<void> {
  if (!uploadUrl || uploadUrl.startsWith('mock:')) return

  const mime = normalizeUploadContentType(contentType)
  const res = await fetch(uploadUrl, {
    method: 'PUT',
    headers: mime ? { 'Content-Type': mime } : {},
    body,
  })

  if (!res.ok) {
    throw new Error('Could not upload the file. Check your connection and try again.')
  }
}
