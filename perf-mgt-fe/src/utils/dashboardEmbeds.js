export const dashboardSandbox =
  'allow-storage-access-by-user-activation allow-scripts allow-same-origin allow-popups allow-popups-to-escape-sandbox'

function isLookerStudioEmbedUrl(value) {
  try {
    const parsedUrl = new URL(value)

    return (
      parsedUrl.protocol === 'https:' &&
      parsedUrl.hostname === 'lookerstudio.google.com' &&
      parsedUrl.pathname.startsWith('/embed/reporting/')
    )
  } catch {
    return false
  }
}

export function extractDashboardSrc(value) {
  const trimmedValue = value.trim()
  const iframeMatch = trimmedValue.match(/src=["']([^"']+)["']/i)
  const src = iframeMatch ? iframeMatch[1] : trimmedValue

  if (!isLookerStudioEmbedUrl(src)) {
    return ''
  }

  return src
}
