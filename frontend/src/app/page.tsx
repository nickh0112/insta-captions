"use client"

import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Textarea } from '@/components/ui/textarea'
import { Progress } from '@/components/ui/progress'
import { Badge } from '@/components/ui/badge'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Download, Plus, Trash2, AlertCircle, CheckCircle, Clock, Loader2 } from 'lucide-react'

interface Job {
  job_id: string
  state: 'pending' | 'running' | 'completed' | 'failed'
  progress: number
  message: string
  created_at: string
  completed_at?: string
}

interface JobResponse {
  job_id: string
  message: string
}

const API_BASE = 'http://localhost:8000'

export default function Home() {
  const [urls, setUrls] = useState('')
  const queryClient = useQueryClient()

  // Fetch all jobs
  const { data: jobsData } = useQuery({
    queryKey: ['jobs'],
    queryFn: async () => {
      const response = await fetch(`${API_BASE}/jobs`)
      if (!response.ok) throw new Error('Failed to fetch jobs')
      return response.json()
    },
    refetchInterval: 2000, // Poll every 2 seconds
  })

  // Submit URLs mutation
  const submitMutation = useMutation({
    mutationFn: async (urls: string[]) => {
      const response = await fetch(`${API_BASE}/submit`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ urls }),
      })
      if (!response.ok) throw new Error('Failed to submit URLs')
      return response.json() as Promise<JobResponse>
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['jobs'] })
      setUrls('')
    },
  })

  // Delete job mutation
  const deleteMutation = useMutation({
    mutationFn: async (jobId: string) => {
      const response = await fetch(`${API_BASE}/jobs/${jobId}`, {
        method: 'DELETE',
      })
      if (!response.ok) throw new Error('Failed to delete job')
      return response.json()
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['jobs'] })
    },
  })

  const handleSubmit = () => {
    const urlList = urls
      .split('\n')
      .map(url => url.trim())
      .filter(url => url && url.startsWith('https://www.instagram.com/'))
    
    if (urlList.length === 0) {
      alert('Please enter valid Instagram URLs')
      return
    }

    submitMutation.mutate(urlList)
  }

  const handleDownload = (jobId: string) => {
    const link = document.createElement('a')
    link.href = `${API_BASE}/result/${jobId}`
    link.download = `transcripts_${jobId}.zip`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
  }

  const getStatusIcon = (state: string) => {
    switch (state) {
      case 'pending':
        return <Clock className="h-4 w-4" />
      case 'running':
        return <Loader2 className="h-4 w-4 animate-spin" />
      case 'completed':
        return <CheckCircle className="h-4 w-4" />
      case 'failed':
        return <AlertCircle className="h-4 w-4" />
      default:
        return <Clock className="h-4 w-4" />
    }
  }

  const getStatusColor = (state: string) => {
    switch (state) {
      case 'pending':
        return 'default'
      case 'running':
        return 'default'
      case 'completed':
        return 'default'
      case 'failed':
        return 'destructive'
      default:
        return 'default'
    }
  }

  const jobs: Job[] = jobsData?.jobs || []

  return (
    <div className="container mx-auto p-6 max-w-4xl">
      <div className="space-y-6">
        {/* Header */}
        <div className="text-center space-y-2">
          <h1 className="text-3xl font-bold">Instagram Reels Transcript Extractor</h1>
          <p className="text-muted-foreground">
            Extract transcripts from Instagram reels and posts for content analysis
          </p>
        </div>

        {/* URL Submission Form */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Plus className="h-5 w-5" />
              Submit Instagram URLs
            </CardTitle>
            <CardDescription>
              Enter Instagram reel or post URLs, one per line
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <Textarea
              placeholder="https://www.instagram.com/p/ABC123/
https://www.instagram.com/reels/DEF456/
https://www.instagram.com/p/GHI789/"
              value={urls}
              onChange={(e) => setUrls(e.target.value)}
              rows={6}
              className="font-mono text-sm"
            />
            <Button 
              onClick={handleSubmit}
              disabled={!urls.trim() || submitMutation.isPending}
              className="w-full"
            >
              {submitMutation.isPending ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Submitting...
                </>
              ) : (
                <>
                  <Plus className="mr-2 h-4 w-4" />
                  Submit URLs
                </>
              )}
            </Button>
            {submitMutation.error && (
              <Alert variant="destructive">
                <AlertCircle className="h-4 w-4" />
                <AlertDescription>
                  {submitMutation.error.message}
                </AlertDescription>
              </Alert>
            )}
          </CardContent>
        </Card>

        {/* Jobs List */}
        <Card>
          <CardHeader>
            <CardTitle>Processing Jobs</CardTitle>
            <CardDescription>
              Track the status of your transcript extraction jobs
            </CardDescription>
          </CardHeader>
          <CardContent>
            {jobs.length === 0 ? (
              <p className="text-center text-muted-foreground py-8">
                No jobs yet. Submit some Instagram URLs to get started!
              </p>
            ) : (
              <div className="space-y-4">
                {jobs.map((job) => (
                  <div key={job.job_id} className="border rounded-lg p-4 space-y-3">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        {getStatusIcon(job.state)}
                        <Badge variant={getStatusColor(job.state) as any}>
                          {job.state.toUpperCase()}
                        </Badge>
                        <span className="text-sm text-muted-foreground">
                          {job.job_id.slice(0, 8)}...
                        </span>
                      </div>
                      <div className="flex items-center gap-2">
                        {job.state === 'completed' && (
                          <Button
                            size="sm"
                            onClick={() => handleDownload(job.job_id)}
                            variant="outline"
                          >
                            <Download className="mr-2 h-4 w-4" />
                            Download
                          </Button>
                        )}
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => deleteMutation.mutate(job.job_id)}
                          disabled={deleteMutation.isPending}
                        >
                          <Trash2 className="h-4 w-4" />
                        </Button>
                      </div>
                    </div>
                    
                    {job.state === 'running' && (
                      <div className="space-y-2">
                        <Progress value={job.progress * 100} className="w-full" />
                        <p className="text-sm text-muted-foreground">
                          {Math.round(job.progress * 100)}% - {job.message}
                        </p>
                      </div>
                    )}
                    
                    <div className="text-xs text-muted-foreground">
                      Created: {new Date(job.created_at).toLocaleString()}
                      {job.completed_at && (
                        <> • Completed: {new Date(job.completed_at).toLocaleString()}</>
                      )}
                    </div>
                    
                    {job.message && job.state !== 'running' && (
                      <p className="text-sm">{job.message}</p>
                    )}
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
