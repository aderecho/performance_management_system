export const PAGE_ACCESS = Object.freeze({
  documents: {},
  dashboard: {},
  users: {
    requiredPermission: 'authentication.view_user',
  },
  roles: {
    requiredPermission: 'auth.view_group',
  },
  permissions: {
    requiredPermissions: [
      'auth.view_permission',
      'authentication.view_user',
      'authentication.change_user',
    ],
  },
  auditLogs: {
    requiresSuperAdmin: true,
  },
  archivedInitiatives: {
    requiredPermission: 'pme.view_initiative',
  },
})
