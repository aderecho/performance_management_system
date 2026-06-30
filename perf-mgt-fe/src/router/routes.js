const routes = [
  {
    path: '/',
    redirect: '/admin/dashboard',
    component: () => import('layouts/MainLayout.vue'),
    meta: { requiresAuth: true },
    children: [
      {
        path: '/documents/:documentId',
        name: 'documents.show',
        component: () => import('pages/PmePage.vue'),
        props: true
      },
      {
        path: '/admin/dashboard',
        name: 'dashboard',
        component: () => import('pages/DashboardPage.vue')
      },
      {
        path: '/admin/users',
        name: 'users',
        component: () => import('pages/UserPage.vue'),
        meta: { requiredPermission: 'authentication.view_user' }
      },
      {
        path: '/admin/roles',
        name: 'roles',
        component: () => import('pages/RolePage.vue'),
        meta: { requiredPermission: 'auth.view_group' }
      },
      {
        path: '/admin/permissions',
        name: 'permissions',
        component: () => import('pages/PermissionPage.vue'),
        meta: {
          requiredPermissions: [
            'auth.view_permission',
            'authentication.view_user',
            'authentication.change_user'
          ]
        }
      },
      {
        path: '/admin/audit-logs',
        name: 'audit-logs',
        component: () => import('pages/AuditLogPage.vue'),
        meta: { requiresSuperAdmin: true }
      }
    ],
  },
  {
    path: '/login',
    component: () => import('pages/LoginPage.vue'),
  },

  // Always leave this as last one,
  // but you can also remove it
  {
    path: '/:catchAll(.*)*',
    component: () => import('pages/ErrorNotFound.vue'),
  },
]

export default routes
