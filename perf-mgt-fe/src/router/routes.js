import { PAGE_ACCESS } from './pageAccess'

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
        props: true,
        meta: PAGE_ACCESS.documents,
      },
      {
        path: '/admin/dashboard',
        name: 'dashboard',
        component: () => import('pages/DashboardPage.vue'),
        meta: PAGE_ACCESS.dashboard,
      },
      {
        path: '/admin/users',
        name: 'users',
        component: () => import('pages/UserPage.vue'),
        meta: PAGE_ACCESS.users,
      },
      {
        path: '/admin/roles',
        name: 'roles',
        component: () => import('pages/RolePage.vue'),
        meta: PAGE_ACCESS.roles,
      },
      {
        path: '/admin/permissions',
        name: 'permissions',
        component: () => import('pages/PermissionPage.vue'),
        meta: PAGE_ACCESS.permissions,
      },
      {
        path: '/admin/audit-logs',
        name: 'audit-logs',
        component: () => import('pages/AuditLogPage.vue'),
        meta: PAGE_ACCESS.auditLogs,
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
