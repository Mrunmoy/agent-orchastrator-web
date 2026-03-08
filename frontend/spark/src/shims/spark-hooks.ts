/**
 * Shim for @github/spark/hooks — replaces Spark's KV store with local React state.
 *
 * In production, replace this with calls to our FastAPI REST API:
 *   - GET /api/conversations → useConversations() hook
 *   - GET /api/agents → useAgents() hook
 *   - etc.
 *
 * This shim exists so the Spark prototype code can be read and understood
 * without access to the private @github/spark package.
 */
import { useState, useCallback } from 'react'

type SetterFn<T> = (prev: T) => T

/**
 * Local-state replacement for Spark's useKV hook.
 * NOT connected to any backend — data lives only in component state.
 */
export function useKV<T>(key: string, defaultValue: T): [T, (updater: T | SetterFn<T>) => void] {
  const [value, setValue] = useState<T>(defaultValue)

  const setter = useCallback((updater: T | SetterFn<T>) => {
    if (typeof updater === 'function') {
      setValue(updater as SetterFn<T>)
    } else {
      setValue(updater)
    }
  }, [])

  return [value, setter]
}
