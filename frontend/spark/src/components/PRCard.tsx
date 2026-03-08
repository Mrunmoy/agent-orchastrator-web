import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { GitBranch, GitMerge, GitPullRequest, ArrowSquareOut, CheckCircle, XCircle, Clock } from '@phosphor-icons/react'
import type { PullRequest } from '@/lib/types'
import { motion } from 'framer-motion'

interface PRCardProps {
  pr: PullRequest
}

export function PRCard({ pr }: PRCardProps) {
  const statusConfig = {
    open: { color: 'bg-info/10 text-info border-info/20', icon: GitPullRequest, label: 'Open' },
    draft: { color: 'bg-muted text-muted-foreground border-border', icon: GitPullRequest, label: 'Draft' },
    merged: { color: 'bg-success/10 text-success border-success/20', icon: GitMerge, label: 'Merged' },
    closed: { color: 'bg-error/10 text-error border-error/20', icon: XCircle, label: 'Closed' }
  }

  const config = statusConfig[pr.status]
  const StatusIcon = config.icon

  const allChecksPassed = pr.checks.every(c => c.status === 'success')
  const hasFailedChecks = pr.checks.some(c => c.status === 'failure')
  const pendingChecks = pr.checks.filter(c => c.status === 'pending' || c.status === 'queued').length

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.2 }}
    >
      <Card className="hover:shadow-md transition-shadow">
        <CardHeader className="pb-3">
          <div className="flex items-start justify-between gap-2">
            <div className="flex-1 space-y-1">
              <CardTitle className="text-base leading-tight">{pr.title}</CardTitle>
              <div className="flex items-center gap-2 text-xs text-muted-foreground">
                <code className="font-mono">#{pr.number}</code>
                <span>•</span>
                <span>by {pr.author}</span>
              </div>
            </div>
            <Badge variant="outline" className={`${config.color} flex items-center gap-1.5 shrink-0`}>
              <StatusIcon size={14} weight="fill" />
              {config.label}
            </Badge>
          </div>
        </CardHeader>
        <CardContent className="space-y-3">
          <div className="flex items-center gap-2 text-xs">
            <GitBranch size={14} className="text-muted-foreground" />
            <code className="font-mono text-muted-foreground">{pr.branch}</code>
          </div>

          {pr.checks.length > 0 && (
            <div className="space-y-2">
              <div className="flex items-center justify-between text-xs">
                <span className="text-muted-foreground font-medium">Checks</span>
                {allChecksPassed && (
                  <span className="flex items-center gap-1 text-success">
                    <CheckCircle size={14} weight="fill" />
                    All passed
                  </span>
                )}
                {hasFailedChecks && (
                  <span className="flex items-center gap-1 text-error">
                    <XCircle size={14} weight="fill" />
                    Failed
                  </span>
                )}
                {pendingChecks > 0 && !hasFailedChecks && (
                  <span className="flex items-center gap-1 text-warning">
                    <Clock size={14} weight="fill" />
                    {pendingChecks} pending
                  </span>
                )}
              </div>
              <div className="space-y-1">
                {pr.checks.slice(0, 3).map((check, idx) => (
                  <div key={idx} className="flex items-center justify-between text-xs">
                    <span className="text-muted-foreground truncate">{check.name}</span>
                    <div className="flex items-center gap-1">
                      {check.status === 'success' && <CheckCircle size={12} className="text-success" weight="fill" />}
                      {check.status === 'failure' && <XCircle size={12} className="text-error" weight="fill" />}
                      {(check.status === 'pending' || check.status === 'queued') && <Clock size={12} className="text-warning" weight="fill" />}
                    </div>
                  </div>
                ))}
                {pr.checks.length > 3 && (
                  <p className="text-xs text-muted-foreground">+{pr.checks.length - 3} more</p>
                )}
              </div>
            </div>
          )}

          {pr.hasConflicts && (
            <div className="flex items-center gap-2 text-xs text-error bg-error/5 p-2 rounded border border-error/20">
              <XCircle size={14} weight="fill" />
              <span className="font-medium">Has merge conflicts</span>
            </div>
          )}

          <div className="flex items-center justify-between pt-2 border-t">
            <div className="flex items-center gap-3 text-xs text-muted-foreground">
              <span className="text-success">+{pr.additions}</span>
              <span className="text-error">-{pr.deletions}</span>
            </div>
            <Button variant="ghost" size="sm" asChild>
              <a href={pr.url} target="_blank" rel="noopener noreferrer" className="flex items-center gap-1">
                View PR
                <ArrowSquareOut size={14} />
              </a>
            </Button>
          </div>
        </CardContent>
      </Card>
    </motion.div>
  )
}
