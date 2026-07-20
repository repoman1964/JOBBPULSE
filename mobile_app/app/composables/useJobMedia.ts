/**
 * Photo upload helpers: prefer signed URL → object storage, fall back to multipart.
 * Phase 2 stages: before | after only.
 */

export type StageLabel = 'before' | 'after'

function mimeFromFile(file: File): string {
  if (file.type) return file.type
  const name = file.name.toLowerCase()
  if (name.endsWith('.png')) return 'image/png'
  if (name.endsWith('.webp')) return 'image/webp'
  if (name.endsWith('.heic') || name.endsWith('.heif')) return 'image/heic'
  return 'image/jpeg'
}

export const useJobMedia = () => {
  const api = useApi()
  const uploading = ref(false)
  const progressLabel = ref('')
  const uploadError = ref<string | null>(null)

  async function uploadPhoto(
    jobId: string,
    file: File,
    stageLabel: StageLabel,
  ): Promise<unknown> {
    uploading.value = true
    uploadError.value = null
    progressLabel.value = 'Preparing upload…'

    const mime = mimeFromFile(file)

    try {
      const signed = (await api.requestMediaUploadUrl(jobId, {
        filename: file.name || 'photo.jpg',
        mime_type: mime,
        stage_label: stageLabel,
        file_size_bytes: file.size,
      })) as {
        media_id: string
        upload_url: string
        upload_method: string
        headers: Record<string, string>
      }

      progressLabel.value = 'Uploading photo…'
      try {
        const putRes = await fetch(signed.upload_url, {
          method: signed.upload_method || 'PUT',
          headers: signed.headers || { 'Content-Type': mime },
          body: file,
        })
        if (!putRes.ok) {
          throw new Error(`Direct upload failed (${putRes.status})`)
        }

        progressLabel.value = 'Finalizing…'
        return await api.completeMediaUpload(jobId, {
          media_id: signed.media_id,
          file_size_bytes: file.size,
        })
      } catch {
        progressLabel.value = 'Uploading via server…'
        return await api.uploadMediaDirect(jobId, file, stageLabel)
      }
    } catch (e: any) {
      uploadError.value = e?.message || 'Upload failed'
      throw e
    } finally {
      uploading.value = false
      progressLabel.value = ''
    }
  }

  async function uploadMany(
    jobId: string,
    files: FileList | File[],
    stageLabel: StageLabel,
  ) {
    const list = Array.from(files)
    let last: unknown = null
    for (const file of list) {
      last = await uploadPhoto(jobId, file, stageLabel)
    }
    return last
  }

  async function reorder(jobId: string, mediaIds: string[]) {
    return api.reorderMedia(jobId, mediaIds)
  }

  return {
    uploading,
    progressLabel,
    uploadError,
    uploadPhoto,
    uploadMany,
    reorder,
  }
}
