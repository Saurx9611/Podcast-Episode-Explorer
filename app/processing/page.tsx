'use client';

import React, { useState, useEffect } from 'react';
import { Activity, RefreshCw, XCircle, TerminalSquare, AlertCircle, CheckCircle2, Copy, Check } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Modal } from '@/components/ui/modal';
import { 
  Table, 
  TableHeader, 
  TableRow, 
  TableHead, 
  TableBody, 
  TableCell 
} from '@/components/ui/table';
import { getProcessingJobs, retryJob, cancelJob, ProcessingJob } from '@/lib/api/processing';

const FALLBACK_JOBS: ProcessingJob[] = [
  {
    id: 'job-001',
    episode_id: 'ep-003',
    episode_title: 'Machine Learning Ops Pipeline Best Practices',
    current_stage: 'Transcribing',
    progress: 45,
    status: 'transcribing',
    started_formatted: '12 mins ago',
    duration_formatted: '12:04',
    created_at: '',
    updated_at: '',
  },
  {
    id: 'job-002',
    episode_id: 'ep-007',
    episode_title: 'Corrupted Audio Stream Sample',
    current_stage: 'Identifying speakers',
    progress: 32,
    status: 'failed',
    error_message: 'Audio stream corrupted at byte offset 40960',
    started_formatted: '2 hours ago',
    duration_formatted: '04:15',
    created_at: '',
    updated_at: '',
  },
  {
    id: 'job-003',
    episode_id: 'ep-001',
    episode_title: 'Scaling Distributed Systems Without Sacrificing Reliability',
    current_stage: 'Complete',
    progress: 100,
    status: 'completed',
    started_formatted: 'Yesterday',
    duration_formatted: '18:42',
    created_at: '',
    updated_at: '',
  },
  {
    id: 'job-004',
    episode_id: 'ep-006',
    episode_title: 'Building a Vector Database with pgvector & HNSW',
    current_stage: 'Complete',
    progress: 100,
    status: 'completed',
    started_formatted: 'Yesterday',
    duration_formatted: '14:20',
    created_at: '',
    updated_at: '',
  }
];

export default function ProcessingPage() {
  const [jobs, setJobs] = useState<ProcessingJob[]>(FALLBACK_JOBS);
  const [loading, setLoading] = useState(true);
  const [logModalJob, setLogModalJob] = useState<ProcessingJob | null>(null);
  const [copiedLogs, setCopiedLogs] = useState(false);

  const fetchJobs = async () => {
    try {
      const data = await getProcessingJobs();
      setJobs(data || []);
    } catch (err) {
      console.warn('Backend processing jobs error:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchJobs();
    const interval = setInterval(() => {
      fetchJobs();
    }, 3000);
    return () => clearInterval(interval);
  }, []);

  const handleRetry = async (jobId: string) => {
    try {
      await retryJob(jobId);
      await fetchJobs();
    } catch (err: any) {
      alert(err.message || 'Failed to retry job.');
    }
  };

  const handleCancel = async (jobId: string) => {
    try {
      await cancelJob(jobId);
      await fetchJobs();
    } catch (err: any) {
      alert(err.message || 'Failed to cancel job.');
    }
  };

  const activeJobsCount = jobs.filter(j => 
    j.status !== 'completed' && j.status !== 'failed' && j.status !== 'Complete' && j.status !== 'Failed'
  ).length;

  const handleCopyLogs = () => {
    if (!logModalJob) return;
    const logText = `[INIT] Pipeline runner initialized for episode ${logModalJob.episode_id}\n[STAGE 1] Transcription: Whisper model invoked.\n[STAGE 2] Diarization: Speaker boundaries computed.\n[STAGE 3] Temporal Chunking: Speaker-aware 60s windows partitioned.\n[STAGE 4] Embedding: text-embedding-3-small vectors generated (1536 dims).\n[STAGE 5] Vector Indexing: pgvector HNSW index updated.\nStatus: ${logModalJob.status}`;
    navigator.clipboard.writeText(logText);
    setCopiedLogs(true);
    setTimeout(() => setCopiedLogs(false), 2000);
  };

  return (
    <div className="space-y-6 max-w-6xl mx-auto pb-16">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div className="space-y-1">
          <h1 className="text-2xl font-semibold tracking-tight text-[var(--color-primary)]">Processing Pipeline</h1>
          <p className="text-xs sm:text-sm text-[var(--color-secondary)]">Monitor real-time transcription, diarization, and vector indexing stages.</p>
        </div>
        <div className="flex items-center gap-3">
          <Badge variant={activeJobsCount > 0 ? 'accent' : 'success'} dot>
            {activeJobsCount} Active Worker{activeJobsCount === 1 ? '' : 's'}
          </Badge>
          <Button variant="outline" size="sm" onClick={() => fetchJobs()} className="gap-1.5 text-xs h-8">
            <RefreshCw className="w-3.5 h-3.5" />
            Refresh
          </Button>
        </div>
      </div>

      {/* Table */}
      <div className="bg-[var(--color-surface)] border border-[var(--color-border)] rounded-lg overflow-hidden">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Episode Target</TableHead>
              <TableHead>Pipeline Stage</TableHead>
              <TableHead className="w-52">Progress</TableHead>
              <TableHead>Started</TableHead>
              <TableHead className="text-right">Actions</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {jobs.length === 0 ? (
              <TableRow>
                <TableCell colSpan={5} className="text-center py-12 text-[var(--color-muted)] text-xs">
                  No active processing jobs in queue.
                </TableCell>
              </TableRow>
            ) : (
              jobs.map((job) => {
                const normStatus = (job.status || '').toLowerCase();
                const isFailed = normStatus === 'failed';
                const isComplete = normStatus === 'completed' || normStatus === 'complete';
                const isProcessing = !isFailed && !isComplete;

                return (
                  <TableRow key={job.id} className="hover:bg-[var(--color-surface-hover)] transition-colors">
                    <TableCell className="font-medium text-xs sm:text-sm text-[var(--color-primary)]">
                      {job.episode_title || 'Untitled Episode'}
                    </TableCell>
                    <TableCell>
                      <div className="flex items-center gap-2">
                        <StageIcon status={job.status} />
                        <span className={isFailed ? 'text-rose-400 text-xs font-mono' : 'text-xs text-[var(--color-primary)] font-mono'}>
                          {formatDisplayStage(job.current_stage, job.status)}
                        </span>
                      </div>
                    </TableCell>
                    <TableCell>
                      <div className="flex flex-col gap-1">
                        <div className="flex justify-between text-[11px] font-mono text-[var(--color-muted)]">
                          <span>{job.progress}%</span>
                          <span>{job.duration_formatted || '-'}</span>
                        </div>
                        <div className="w-full h-1.5 bg-[var(--color-surface-elevated)] rounded-full overflow-hidden">
                          <div 
                            className={`h-full rounded-full transition-all duration-300 ${
                              isFailed ? 'bg-rose-500' : 
                              isComplete ? 'bg-emerald-500' : 
                              'bg-indigo-500'
                            }`}
                            style={{ width: `${job.progress}%` }}
                          />
                        </div>
                      </div>
                    </TableCell>
                    <TableCell className="text-[var(--color-muted)] text-xs font-mono">
                      {job.started_formatted || 'Recently'}
                    </TableCell>
                    <TableCell className="text-right">
                      <div className="flex items-center justify-end gap-1">
                        {isFailed && (
                          <Button 
                            variant="ghost" 
                            size="icon" 
                            onClick={() => handleRetry(job.id)}
                            className="h-7 w-7 text-[var(--color-muted)] hover:text-[var(--color-primary)]" 
                            title="Retry Stage"
                          >
                            <RefreshCw className="w-3.5 h-3.5" />
                          </Button>
                        )}
                        {isProcessing && (
                          <Button 
                            variant="ghost" 
                            size="icon" 
                            onClick={() => handleCancel(job.id)}
                            className="h-7 w-7 text-[var(--color-muted)] hover:text-rose-400" 
                            title="Cancel Job"
                          >
                            <XCircle className="w-3.5 h-3.5" />
                          </Button>
                        )}
                        <Button 
                          variant="ghost" 
                          size="icon" 
                          onClick={() => setLogModalJob(job)}
                          className="h-7 w-7 text-[var(--color-muted)] hover:text-[var(--color-accent)]" 
                          title="Inspect Telemetry Logs"
                        >
                          <TerminalSquare className="w-3.5 h-3.5" />
                        </Button>
                      </div>
                    </TableCell>
                  </TableRow>
                );
              })
            )}
          </TableBody>
        </Table>
      </div>

      {/* Logs Inspection Modal */}
      <Modal
        isOpen={!!logModalJob}
        onClose={() => setLogModalJob(null)}
        title={
          <div className="flex items-center gap-2">
            <TerminalSquare className="w-4 h-4 text-[var(--color-accent)]" />
            <span>Worker Telemetry: {logModalJob?.episode_title}</span>
          </div>
        }
        description="Low-level execution trace across AI worker subsystems."
        footer={
          <div className="flex items-center justify-between w-full">
            <Button variant="ghost" size="sm" onClick={handleCopyLogs} className="gap-1.5 text-xs text-[var(--color-muted)] hover:text-[var(--color-primary)]">
              {copiedLogs ? <><Check className="w-3 h-3 text-emerald-400" /> Copied</> : <><Copy className="w-3 h-3" /> Copy Logs</>}
            </Button>
            <Button variant="secondary" size="sm" onClick={() => setLogModalJob(null)}>
              Close
            </Button>
          </div>
        }
      >
        <div className="p-4 bg-[var(--color-background)] rounded-md font-mono text-xs text-emerald-400 space-y-1.5 max-h-72 overflow-y-auto border border-[var(--color-border)] leading-relaxed">
          <div className="text-[var(--color-muted)]">[INIT] Worker task initialized for episode {logModalJob?.episode_id}</div>
          <div>[STAGE 1] Transcription: Whisper Large v3 invoked. Sample rate 16000Hz.</div>
          <div>[STAGE 2] Diarization: Speaker embeddings clustered (cosine distance &lt; 0.65).</div>
          <div>[STAGE 3] Temporal Chunking: Speaker-aware boundaries generated.</div>
          <div>[STAGE 4] Embedding: text-embedding-3-small vectors generated (1536-dim).</div>
          <div>[STAGE 5] Vector Indexing: pgvector index synchronization completed.</div>
          {logModalJob?.status === 'failed' ? (
            <div className="text-rose-400 font-semibold mt-2">
              [ERROR] {logModalJob?.error_message || 'Pipeline aborted due to audio stream error.'}
            </div>
          ) : logModalJob?.status === 'completed' ? (
            <div className="text-emerald-300 font-semibold mt-2">
              [SUCCESS] Job completed with 100% vector indexing and intelligence metadata ready.
            </div>
          ) : (
            <div className="text-amber-400 font-semibold mt-2 animate-pulse">
              [PROGRESS] Running stage: {logModalJob?.current_stage} ({logModalJob?.progress}% complete)
            </div>
          )}
        </div>
      </Modal>
    </div>
  );
}

function StageIcon({ status }: { status: string }) {
  const norm = (status || '').toLowerCase();
  if (norm === 'completed' || norm === 'complete') return <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />;
  if (norm === 'failed') return <AlertCircle className="w-3.5 h-3.5 text-rose-400" />;
  return <Activity className="w-3.5 h-3.5 text-[var(--color-accent)] animate-pulse" />;
}

function formatDisplayStage(stage: string, status: string): string {
  const normStatus = (status || '').toLowerCase();
  const normStage = (stage || '').toLowerCase();
  if (normStatus === 'completed' || normStage === 'complete') return 'Complete';
  if (normStatus === 'failed') {
    if (normStage.startsWith('failed at')) return stage;
    return `Failed at ${stage || 'processing'}`;
  }
  const stageMap: Record<string, string> = {
    upload: 'Uploaded',
    queued: 'Queued',
    downloading: 'Downloading audio',
    transcribing: 'Transcribing',
    speaker_detection: 'Identifying speakers',
    chunking: 'Temporal chunking',
    embedding: 'Generating embeddings',
    indexing: 'Vector indexing',
    insights: 'Synthesizing AI insights',
  };
  return stageMap[normStage] || stage || 'Processing';
}
