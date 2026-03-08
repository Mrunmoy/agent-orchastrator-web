import { Badge } from '@/components/ui/badge'
import { CheckCircle, XCircle, Clock, Warning, Circle } from '@phosphor-icons/react'
import type { TaskStatus as TaskStatusType } from '@/lib/types'

interface StatusBadgeProps {
  status: TaskStatusType
  className?: string
}

export function StatusBadge({ status, className }: StatusBadgeProps) {
  const config = {
    idle: {
      icon: Circle,
      label: 'Idle',
      variant: 'secondary' as const,
      className: 'bg-muted text-muted-foreground'
    },
    planning: {
      icon: Clock,
      label: 'Planning',
      variant: 'secondary' as const,
      className: 'bg-info/10 text-info border-info/20'
    },
    executing: {
      icon: Clock,
      label: 'Executing',
      variant: 'secondary' as const,
      className: 'bg-warning/10 text-warning border-warning/20 animate-pulse'
    },
    reviewing: {
      icon: Warning,
      label: 'In Review',
      variant: 'secondary' as const,
      className: 'bg-info/10 text-info border-info/20'
    },
    completed: {
      icon: CheckCircle,
      label: 'Completed',
      variant: 'secondary' as const,
      className: 'bg-success/10 text-success border-success/20'
    },
    failed: {
      icon: XCircle,
      label: 'Failed',
      variant: 'destructive' as const,
      className: 'bg-error/10 text-error border-error/20'
    },
    blocked: {
      icon: Warning,
      label: 'Blocked',
      variant: 'destructive' as const,
      className: 'bg-error/10 text-error border-error/20'
    }
  }

  const { icon: Icon, label, className: statusClassName } = config[status]

  return (
    <Badge variant="outline" className={`${statusClassName} ${className} flex items-center gap-1.5`}>
      <Icon size={14} weight="fill" />
      <span>{label}</span>
    </Badge>
  )
}
