import { z } from 'zod'

export const userSchema = z.object({
  email: z.string().email('Invalid email').min(1, 'Email is required'),

  is_active: z.boolean(),
  is_superuser: z.boolean(),

  profile: z.object({
    first_name: z.string().min(1, 'First name is required'),
    middle_name: z.string().optional().nullable(),
    last_name: z.string().min(1, 'Last name is required'),
    suffix: z.string().optional().nullable()
  }),

  units: z.array(z.string()).min(1, 'At least one unit is required'),

  primary_unit: z.string().min(1, 'Primary unit is required')
})