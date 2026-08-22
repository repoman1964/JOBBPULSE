export function useAskModal() {
  const open = useState('ask-modal-open', () => false)

  function show() {
    open.value = true
  }

  function hide() {
    open.value = false
  }

  return { open, show, hide }
}
