/**
 * Upload job voice audio: signed URL preferred, multipart fallback.
 */

export const useJobVoice = () => {
  const api = useApi()
  const uploading = ref(false)
  const progressLabel = ref('')
  const uploadError = ref<string | null>(null)

  async function uploadVoice(
    jobId: string,
    file: File | Blob,
    filename = 'voice.webm',
  ): Promise<{ voice: unknown; job: unknown }> {
    uploading.value = true
    uploadError.value = null
    progressLabel.value = 'Preparing upload…'

    const mime =
      (file instanceof File ? file.type : file.type) ||
      (filename.endsWith('.m4a') || filename.endsWith('.mp4')
        ? 'audio/mp4'
        : 'audio/webm')
    const size = file.size

    try {
      const signed = (await api.requestVoiceUploadUrl(jobId, {
        filename,
        mime_type: mime,
        file_size_bytes: size,
      })) as {
        media_id: string
        upload_url: string
        upload_method: string
        headers: Record<string, string>
      }

      progressLabel.value = 'Uploading voice…'
      try {
        const putRes = await fetch(signed.upload_url, {
          method: signed.upload_method || 'PUT',
          headers: signed.headers || { 'Content-Type': mime },
          body: file,
        })
        if (!putRes.ok) {
          throw new Error(`Direct upload failed (${putRes.status})`)
        }

        progressLabel.value = 'Transcribing…'
        return (await api.completeVoiceUpload(jobId, {
          media_id: signed.media_id,
          file_size_bytes: size,
        })) as { voice: unknown; job: unknown }
      } catch {
        progressLabel.value = 'Uploading via server…'
        return (await api.uploadVoiceDirect(jobId, file, filename)) as {
          voice: unknown
          job: unknown
        }
      }
    } catch (e: any) {
      uploadError.value = e?.message || 'Voice upload failed'
      throw e
    } finally {
      uploading.value = false
      progressLabel.value = ''
    }
  }

  async function pollUntilReady(
    jobId: string,
    {
      intervalMs = 1500,
      maxAttempts = 20,
    }: { intervalMs?: number; maxAttempts?: number } = {},
  ) {
    for (let i = 0; i < maxAttempts; i++) {
      const voice = (await api.getVoice(jobId)) as {
        transcription_status: string
      }
      if (
        voice.transcription_status === 'completed' ||
        voice.transcription_status === 'failed'
      ) {
        return voice
      }
      await new Promise((r) => setTimeout(r, intervalMs))
    }
    throw new Error('Transcription is taking longer than expected. Pull to refresh.')
  }

  return {
    uploading,
    progressLabel,
    uploadError,
    uploadVoice,
    pollUntilReady,
  }
}
