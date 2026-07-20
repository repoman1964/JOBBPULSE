/**
 * Browser MediaRecorder for job voice summaries.
 * Prefers WebM Opus; falls back to MP4 / plain WebM.
 */

export type RecorderState = 'idle' | 'recording' | 'paused' | 'stopped' | 'unsupported'

function pickMimeType(): string | undefined {
  if (typeof MediaRecorder === 'undefined') return undefined
  const candidates = [
    'audio/webm;codecs=opus',
    'audio/webm',
    'audio/mp4',
    'audio/ogg;codecs=opus',
  ]
  for (const t of candidates) {
    if (MediaRecorder.isTypeSupported(t)) return t
  }
  return undefined
}

function extForMime(mime: string): string {
  if (mime.includes('mp4')) return 'm4a'
  if (mime.includes('ogg')) return 'ogg'
  return 'webm'
}

export const useVoiceRecorder = () => {
  const state = ref<RecorderState>('idle')
  const error = ref<string | null>(null)
  const durationMs = ref(0)
  const blob = ref<Blob | null>(null)
  const playbackUrl = ref<string | null>(null)
  const mimeType = ref<string>('audio/webm')

  let mediaRecorder: MediaRecorder | null = null
  let stream: MediaStream | null = null
  let chunks: BlobPart[] = []
  let tickTimer: ReturnType<typeof setInterval> | null = null
  let startedAt = 0
  let accumulatedMs = 0

  function clearTick() {
    if (tickTimer) {
      clearInterval(tickTimer)
      tickTimer = null
    }
  }

  function revokePlayback() {
    if (playbackUrl.value) {
      URL.revokeObjectURL(playbackUrl.value)
      playbackUrl.value = null
    }
  }

  function stopTracks() {
    if (stream) {
      stream.getTracks().forEach((t) => t.stop())
      stream = null
    }
  }

  function resetBlob() {
    revokePlayback()
    blob.value = null
    durationMs.value = 0
    accumulatedMs = 0
  }

  async function start() {
    error.value = null
    if (typeof window === 'undefined' || typeof navigator === 'undefined') {
      state.value = 'unsupported'
      error.value = 'Recording is only available in the browser.'
      return
    }
    if (!navigator.mediaDevices?.getUserMedia || typeof MediaRecorder === 'undefined') {
      state.value = 'unsupported'
      error.value = 'This browser does not support voice recording.'
      return
    }

    resetBlob()
    chunks = []

    try {
      stream = await navigator.mediaDevices.getUserMedia({ audio: true })
    } catch {
      error.value = 'Microphone permission denied. Allow mic access and try again.'
      state.value = 'idle'
      return
    }

    const mime = pickMimeType()
    try {
      mediaRecorder = mime
        ? new MediaRecorder(stream, { mimeType: mime })
        : new MediaRecorder(stream)
    } catch {
      stopTracks()
      error.value = 'Could not start the recorder on this device.'
      state.value = 'idle'
      return
    }

    mimeType.value = mediaRecorder.mimeType || mime || 'audio/webm'
    mediaRecorder.ondataavailable = (ev) => {
      if (ev.data && ev.data.size > 0) chunks.push(ev.data)
    }
    mediaRecorder.onstop = () => {
      clearTick()
      const type = mimeType.value || 'audio/webm'
      const result = new Blob(chunks, { type })
      blob.value = result
      revokePlayback()
      if (result.size > 0) {
        playbackUrl.value = URL.createObjectURL(result)
      }
      stopTracks()
      state.value = 'stopped'
    }
    mediaRecorder.onerror = () => {
      error.value = 'Recording failed.'
      clearTick()
      stopTracks()
      state.value = 'idle'
    }

    mediaRecorder.start(250)
    startedAt = Date.now()
    accumulatedMs = 0
    state.value = 'recording'
    tickTimer = setInterval(() => {
      if (state.value === 'recording') {
        durationMs.value = accumulatedMs + (Date.now() - startedAt)
      }
    }, 200)
  }

  function pause() {
    if (!mediaRecorder || state.value !== 'recording') return
    if (mediaRecorder.state === 'recording' && typeof mediaRecorder.pause === 'function') {
      mediaRecorder.pause()
      accumulatedMs += Date.now() - startedAt
      durationMs.value = accumulatedMs
      state.value = 'paused'
    }
  }

  function resume() {
    if (!mediaRecorder || state.value !== 'paused') return
    if (mediaRecorder.state === 'paused' && typeof mediaRecorder.resume === 'function') {
      mediaRecorder.resume()
      startedAt = Date.now()
      state.value = 'recording'
    }
  }

  function stop() {
    if (!mediaRecorder) return
    if (state.value === 'recording') {
      accumulatedMs += Date.now() - startedAt
      durationMs.value = accumulatedMs
    }
    if (mediaRecorder.state !== 'inactive') {
      mediaRecorder.stop()
    }
  }

  function discard() {
    clearTick()
    if (mediaRecorder && mediaRecorder.state !== 'inactive') {
      try {
        mediaRecorder.stop()
      } catch {
        /* ignore */
      }
    }
    mediaRecorder = null
    stopTracks()
    resetBlob()
    chunks = []
    state.value = 'idle'
    error.value = null
  }

  function asFile(name?: string): File | null {
    if (!blob.value) return null
    const ext = extForMime(mimeType.value)
    const filename = name || `voice.${ext}`
    return new File([blob.value], filename, { type: blob.value.type || mimeType.value })
  }

  function formatDuration(ms: number): string {
    const total = Math.floor(ms / 1000)
    const m = Math.floor(total / 60)
    const s = total % 60
    return `${m}:${s.toString().padStart(2, '0')}`
  }

  onBeforeUnmount(() => {
    discard()
  })

  return {
    state,
    error,
    durationMs,
    blob,
    playbackUrl,
    mimeType,
    start,
    pause,
    resume,
    stop,
    discard,
    asFile,
    formatDuration,
  }
}
