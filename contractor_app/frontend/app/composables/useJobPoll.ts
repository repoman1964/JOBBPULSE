import type { Job } from '~/types/domain'

const IN_FLIGHT = new Set(['processing', 'publishing'])

/** Poll GET /jobs/{id} while the server reports processing or publishing. */
export function useJobPoll(job: Ref<Job | null>) {
  const api = useApi()
  let timer: ReturnType<typeof setInterval> | null = null

  const processing = computed(() => IN_FLIGHT.has(job.value?.publicStatus || ''))

  async function tick() {
    if (!job.value || !IN_FLIGHT.has(job.value.publicStatus)) return
    try {
      job.value = await api.getJob(job.value.id)
    } catch {
      /* keep last known job */
    }
  }

  function start() {
    if (timer) return
    void tick()
    timer = setInterval(() => {
      void tick()
    }, 1000)
  }

  function stop() {
    if (timer) {
      clearInterval(timer)
      timer = null
    }
  }

  watch(
    processing,
    (on) => {
      if (on) start()
      else stop()
    },
    { immediate: true },
  )

  onBeforeUnmount(stop)

  return { processing }
}
