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

  const res = await fetch(uploadUrl, {
    method: 'PUT',
    headers: { 'Content-Type': contentType },
    body,
  })

  if (!res.ok) {
    throw new Error('Could not upload the file. Check your connection and try again.')
  }
}
