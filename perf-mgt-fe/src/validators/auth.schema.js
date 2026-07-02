import { z } from 'zod'
import { requiredString } from 'src/helpers/validators'

export const loginSchema = z.object({
  email: requiredString('Email is required'),

  password: requiredString('Password is required'),
})
