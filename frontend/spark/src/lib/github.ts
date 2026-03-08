import type { PullRequest, Check } from './types'

interface GitHubPR {
  id: number
  number: number
  title: string
  state: 'open' | 'closed'
  draft: boolean
  html_url: string
  head: {
    ref: string
  }
  user: {
    login: string
  }
  created_at: string
  updated_at: string
  additions: number
  deletions: number
  mergeable_state?: string
  merged: boolean
}

interface GitHubCheck {
  name: string
  status: 'queued' | 'in_progress' | 'completed'
  conclusion: 'success' | 'failure' | 'neutral' | 'cancelled' | 'skipped' | 'timed_out' | null
}

export function parseGitHubURL(url: string): { owner: string; repo: string } | null {
  try {
    const match = url.match(/github\.com[:/]([^/]+)\/([^/.]+)(\.git)?$/)
    if (match) {
      return { owner: match[1], repo: match[2] }
    }
    return null
  } catch (error) {
    console.error('Failed to parse GitHub URL:', error)
    return null
  }
}

export async function fetchGitHubPRs(owner: string, repo: string): Promise<PullRequest[]> {
  try {
    const url = `https://api.github.com/repos/${owner}/${repo}/pulls?state=all&per_page=20`
    
    const response = await fetch(url, {
      headers: {
        'Accept': 'application/vnd.github.v3+json'
      }
    })
    
    if (!response.ok) {
      throw new Error(`GitHub API error: ${response.status}`)
    }
    
    const prs: GitHubPR[] = await response.json()
    
    const pullRequests: PullRequest[] = await Promise.all(
      prs.map(async (pr) => {
        const checks = await fetchPRChecks(owner, repo, pr.number)
        
        let status: 'open' | 'merged' | 'closed' | 'draft' = 'open'
        if (pr.merged) {
          status = 'merged'
        } else if (pr.draft) {
          status = 'draft'
        } else if (pr.state === 'closed') {
          status = 'closed'
        }
        
        const hasConflicts = pr.mergeable_state === 'dirty' || pr.mergeable_state === 'unstable'
        
        return {
          id: `pr-${pr.id}`,
          number: pr.number,
          title: pr.title,
          status,
          url: pr.html_url,
          branch: pr.head.ref,
          author: pr.user.login,
          createdAt: new Date(pr.created_at),
          updatedAt: new Date(pr.updated_at),
          checks,
          reviewers: [],
          hasConflicts,
          additions: pr.additions,
          deletions: pr.deletions
        }
      })
    )
    
    return pullRequests
  } catch (error) {
    console.error('Failed to fetch GitHub PRs:', error)
    return []
  }
}

async function fetchPRChecks(owner: string, repo: string, prNumber: number): Promise<Check[]> {
  try {
    const url = `https://api.github.com/repos/${owner}/${repo}/pulls/${prNumber}`
    
    const response = await fetch(url, {
      headers: {
        'Accept': 'application/vnd.github.v3+json'
      }
    })
    
    if (!response.ok) {
      return []
    }
    
    const pr = await response.json()
    const sha = pr.head.sha
    
    const checksUrl = `https://api.github.com/repos/${owner}/${repo}/commits/${sha}/check-runs`
    const checksResponse = await fetch(checksUrl, {
      headers: {
        'Accept': 'application/vnd.github.v3+json'
      }
    })
    
    if (!checksResponse.ok) {
      return []
    }
    
    const checksData = await checksResponse.json()
    const checkRuns: GitHubCheck[] = checksData.check_runs || []
    
    return checkRuns.map(check => ({
      name: check.name,
      status: mapCheckStatus(check.status, check.conclusion)
    }))
  } catch (error) {
    return []
  }
}

function mapCheckStatus(
  status: 'queued' | 'in_progress' | 'completed',
  conclusion: 'success' | 'failure' | 'neutral' | 'cancelled' | 'skipped' | 'timed_out' | null
): 'pending' | 'success' | 'failure' | 'queued' {
  if (status === 'queued') return 'queued'
  if (status === 'in_progress') return 'pending'
  if (conclusion === 'success') return 'success'
  if (conclusion === 'failure' || conclusion === 'timed_out' || conclusion === 'cancelled') return 'failure'
  return 'pending'
}
