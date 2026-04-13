export function resolveFieldValue(data, path) {
  if (!data || !path) return null

  return path.split('.').reduce((obj, key) => {
    return obj?.[key]
  }, data)
}

export function formatFieldValue(field, value, data) {
  if (field.format) {
    return field.format(value, data)
  }
  return value ?? '-'
}

export function getBadgeConfig(field, data) {
  const rawValue = resolveFieldValue(data, field.key)

  if (field.badge) {
    return field.badge(rawValue, data)
  }

  return {
    label: rawValue ?? '-',
    color: 'grey'
  }
}