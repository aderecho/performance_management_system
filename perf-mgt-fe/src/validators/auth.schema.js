import { z } from 'zod'
import { requiredString } from 'src/helpers/validators'

export const loginSchema = z.object({
  username: requiredString('Username is required'),

  password: requiredString('Password is required'),
})