import { z } from 'zod'
import {
  requiredString,
  requiredNumberMin,
  requiredStringMax,
} from 'src/helpers/validators'

export const initiativeSchema = z.object({
  item: requiredString('Indicator is required'),

  description: requiredStringMax(
    'Description is required',
    500,
    'Description must be 500 characters or less'
  ),

  value: requiredNumberMin(
    'Accomplishment value is required',
    1,
    'Value must be 1 or greater'
  ),

  target_date: requiredString('Target date is required'),

  remarks: z
    .string()
    .max(1000, 'Remarks must be 1000 characters or less')
    .optional()
})
