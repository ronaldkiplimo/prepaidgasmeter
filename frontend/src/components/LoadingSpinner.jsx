export default function LoadingSpinner({ fullScreen = false }) {
  const wrapper = fullScreen
    ? 'min-h-screen flex items-center justify-center'
    : 'flex items-center justify-center py-12'

  return (
    <div className={wrapper}>
      <div className="animate-spin rounded-full h-10 w-10 border-4 border-primary-200 border-t-primary-600" />
    </div>
  )
}
