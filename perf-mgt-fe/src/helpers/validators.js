import { z } from 'zod'

export const requiredString = (message) =>
    z.preprocess(
        (val) => (val === null || val === '' ? undefined : val),
        z.string({
            required_error: message,
            invalid_type_error: message,
        })
    )

export const requiredNumberMin = (message, min, minMessage) =>
    z.preprocess(
        (val) =>
            val === null || val === '' || Number.isNaN(val)
                ? undefined
                : val,
        z.number({
            required_error: message,
            invalid_type_error: message,
        }).min(min, minMessage)
    )

export const requiredStringMax = (message, max, maxMessage) =>
    z.preprocess(
        (val) =>
            val === null || val === ''
                ? undefined
                : val,
        z.string({
            required_error: message,
            invalid_type_error: message,
        }).max(max, maxMessage)
    )