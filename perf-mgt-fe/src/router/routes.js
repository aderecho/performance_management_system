const routes = [
  {
    path: '/',
    component: () => import('layouts/MainLayout.vue'),
    children: [
      // {
      //   path: '',
      //   component: () => import('pages/IndexPage.vue'),
      //   meta: { requiresAuth: true }
      // },
      {
        path: '/documents/:documentId',
        name: 'documents.show',
        component: () => import('pages/PmePage.vue'),
        props: true,
        meta: { requiresAuth: true }
      },
      {
        path: 'dashboard',
        name: 'dashboard',
        component: () => import('pages/DashboardPage.vue'),
        meta: { requiresAuth: true }
      },
      {
        path: '/admin/users',
        name: 'users',
        component: () => import('pages/UserPage.vue'),
        meta: { requiresAuth: true }
      },
      {
        path: '/admin/roles',
        name: 'roles',
        component: () => import('pages/RolePage.vue'),
        meta: { requiresAuth: true }
      },
      {
        path: '/admin/permissions',
        name: 'permissions',
        component: () => import('pages/PermissionPage.vue'),
        meta: { requiresAuth: true }
      },
       {
        path: '/admin/audit-logs',
        name: 'audit-logs',
        component: () => import('pages/AuditLogPage.vue'),
        meta: { requiresAuth: true }
      },
    ],
  },
  { path: '/login', component: () => import('pages/LoginPage.vue') },

  // Always leave this as last one,
  // but you can also remove it
  {
    path: '/:catchAll(.*)*',
    component: () => import('pages/ErrorNotFound.vue'),
  },
]

export default routes
