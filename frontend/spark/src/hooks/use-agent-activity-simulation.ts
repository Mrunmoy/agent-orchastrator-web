import { useEffect, useRef } from 'react'
import { useKV } from '@github/spark/hooks'
import type { Task, TaskStatus } from '@/lib/types'

export function useAgentActivitySimulation(enabled: boolean = true) {
  const [tasks, setTasks] = useKV<Task[]>('tasks', [])
  const intervalRef = useRef<number | null>(null)

  useEffect(() => {
    if (!enabled) {
      if (intervalRef.current) {
        clearInterval(intervalRef.current)
        intervalRef.current = null
      }
      return
    }

    intervalRef.current = window.setInterval(() => {
      setTasks((currentTasks) => {
        if (!currentTasks || currentTasks.length === 0) return currentTasks || []

        return currentTasks.map(task => {
          if (task.status === 'executing' || task.status === 'planning') {
            const progressIncrement = Math.floor(Math.random() * 5) + 1
            const newProgress = Math.min(100, task.progress + progressIncrement)
            
            let newStatus: TaskStatus = task.status
            let newPhase = task.phase
            
            if (task.status === 'planning' && newProgress >= 30) {
              newStatus = 'executing'
              newPhase = 'Implementation'
            } else if (task.status === 'executing' && newProgress >= 85) {
              newStatus = 'reviewing'
              newPhase = 'Code Review'
            } else if (newProgress >= 100) {
              newStatus = 'completed'
              newPhase = 'Done'
            }
            
            const completedSubtasks = task.subtasks.map((subtask, idx) => {
              if (subtask.completed) return subtask
              
              const shouldComplete = newProgress > ((idx + 1) / task.subtasks.length) * 100
              return {
                ...subtask,
                completed: shouldComplete
              }
            })
            
            return {
              ...task,
              progress: newProgress,
              status: newStatus,
              phase: newPhase,
              subtasks: completedSubtasks
            }
          }
          
          return task
        })
      })
    }, 3000)

    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current)
      }
    }
  }, [enabled, setTasks])

  return tasks
}
