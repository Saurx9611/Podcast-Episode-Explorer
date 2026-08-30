'use client';

import React, { useState, useEffect, useMemo, useRef } from 'react';
import Link from 'next/link';
import { 
  Upload, 
  Search, 
  Filter, 
  MoreHorizontal,
  Clock,
  CheckCircle2,
  AlertCircle,
  FileAudio,
  Trash2,
  Loader2,
  Check,
  Sparkles,
  Play,
  Layers,
  Rss,
  RefreshCw
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
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
import { getEpisodes, uploadEpisode, deleteEpisode, Episode } from '@/lib/api/episodes';
import { importPodcast } from '@/lib/api/podcasts';
import { getProjects, Project } from '@/lib/api/projects';
import { EpisodeInsightModal } from '@/components/episodes/EpisodeInsightModal';

export default function EpisodesPage() {
  const [episodes, setEpisodes] = useState<Episode[]>([]);
  const [projects, setProjects] = useState<Project[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [activeFilter, setActiveFilter] = useState<'All' | 'Processing' | 'Indexed' | 'Failed'>('All');

  // Upload Modal State
  const [isUploadOpen, setIsUploadOpen] = useState(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [uploadTitle, setUploadTitle] = useState('');
  const [selectedProjectId, setSelectedProjectId] = useState<string>('none');
  const [uploadDescription, setUploadDescription] = useState('');
  const [isUploading, setIsUploading] = useState(false);
  const [uploadError, setUploadError] = useState<string | null>(null);
  const [uploadSuccess, setUploadSuccess] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // RSS Import Modal State
  const [isImportOpen, setIsImportOpen] = useState(false);
  const [importFeedUrl, setImportFeedUrl] = useState('');
  const [importAutoProcess, setImportAutoProcess] = useState(true);
  const [isImporting, setIsImporting] = useState(false);
  const [importError, setImportError] = useState<string | null>(null);
  const [importSuccess, setImportSuccess] = useState<string | null>(null);

  // Active action menu state
  const [actionMenuEpisodeId, setActionMenuEpisodeId] = useState<string | null>(null);

  // Insight Modal State
  const [insightEpisode, setInsightEpisode] = useState<Episode | null>(null);
  const [isInsightModalOpen, setIsInsightModalOpen] = useState(false);

  const fetchEpisodeData = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await getEpisodes();
      setEpisodes(data || []);
    } catch (err: any) {
      console.error('Backend episodes error:', err);
      setError(err.message || 'Unable to connect to backend.');
    } finally {
      setLoading(false);
    }
  };

  const fetchProjectData = async () => {
    try {
      const projs = await getProjects();
      setProjects(projs || []);
    } catch {
      // Ignored
    }
  };

  useEffect(() => {
    fetchEpisodeData();
    fetchProjectData();
  }, []);

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
      setSelectedFile(file);
      setUploadError(null);
      if (!uploadTitle) {
        const cleanName = file.name.replace(/\.[^/.]+$/, '').replace(/[-_]/g, ' ');
        setUploadTitle(cleanName.charAt(0).toUpperCase() + cleanName.slice(1));
      }
    }
  };

  const handleUploadSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedFile) {
      setUploadError('Please select an audio file to upload.');
      return;
    }

    try {
      setIsUploading(true);
      setUploadError(null);
      setUploadSuccess(null);

      const res = await uploadEpisode(selectedFile, {
        title: uploadTitle.trim() || undefined,
        project_id: selectedProjectId !== 'none' ? selectedProjectId : undefined,
        description: uploadDescription.trim() || undefined,
      });

      setUploadSuccess(`"${res.title}" uploaded successfully and queued for processing!`);
      await fetchEpisodeData();

      setTimeout(() => {
        setIsUploadOpen(false);
        setSelectedFile(null);
        setUploadTitle('');
        setUploadDescription('');
        setSelectedProjectId('none');
        setUploadSuccess(null);
      }, 1200);

    } catch (err: any) {
      setUploadError(err.message || 'Failed to upload episode. Please check file format and try again.');
    } finally {
      setIsUploading(false);
    }
  };

  const handleImportSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!importFeedUrl.trim()) {
      setImportError('Please enter a valid podcast RSS feed URL.');
      return;
    }

    try {
      setIsImporting(true);
      setImportError(null);
      setImportSuccess(null);

      const res = await importPodcast({
        feed_url: importFeedUrl.trim(),
        auto_download_latest: importAutoProcess,
        auto_process_latest: importAutoProcess,
      });

      setImportSuccess(`Imported "${res.podcast.title}" with ${res.imported_episodes_count} episodes!`);
      await fetchEpisodeData();

      setTimeout(() => {
        setIsImportOpen(false);
        setImportFeedUrl('');
        setImportSuccess(null);
      }, 1500);
    } catch (err: any) {
      setImportError(err.message || 'Failed to import podcast RSS feed. Please check URL.');
    } finally {
      setIsImporting(false);
    }
  };

  const handleDelete = async (id: string, e: React.MouseEvent) => {
    e.stopPropagation();
    if (!confirm('Are you sure you want to delete this episode?')) return;

    try {
      await deleteEpisode(id);
      setEpisodes(prev => prev.filter(ep => ep.id !== id));
      setActionMenuEpisodeId(null);
    } catch (err: any) {
      alert(err.message || 'Failed to delete episode.');
    }
  };

  const handleOpenInsight = (ep: Episode) => {
    setInsightEpisode(ep);
    setIsInsightModalOpen(true);
    setActionMenuEpisodeId(null);
  };

  // Filter and search
  const filteredEpisodes = useMemo(() => {
    return episodes.filter(ep => {
      const matchesSearch = 
        !searchQuery ||
        ep.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
        (ep.project_name && ep.project_name.toLowerCase().includes(searchQuery.toLowerCase()));

      if (!matchesSearch) return false;
      if (activeFilter === 'All') return true;

      const normStatus = (ep.status || '').toLowerCase();
      if (activeFilter === 'Indexed') return normStatus === 'indexed' || normStatus === 'completed';
      if (activeFilter === 'Processing') return normStatus === 'processing' || normStatus === 'queued' || normStatus === 'transcribing' || normStatus === 'chunking' || normStatus === 'embedding' || normStatus === 'indexing';
      if (activeFilter === 'Failed') return normStatus === 'failed';

      return true;
    });
  }, [episodes, searchQuery, activeFilter]);

  const counts = useMemo(() => {
    return {
      all: episodes.length,
      indexed: episodes.filter(e => ['indexed', 'completed'].includes((e.status || '').toLowerCase())).length,
      processing: episodes.filter(e => ['processing', 'queued', 'transcribing', 'chunking', 'embedding', 'indexing'].includes((e.status || '').toLowerCase())).length,
      failed: episodes.filter(e => (e.status || '').toLowerCase() === 'failed').length,
    };
  }, [episodes]);

  return (
    <div className="space-y-6 max-w-7xl mx-auto pb-16">
      {/* Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div className="space-y-1">
          <h1 className="text-2xl font-semibold text-[var(--color-primary)] tracking-tight">Episode Library</h1>
          <p className="text-xs sm:text-sm text-[var(--color-secondary)]">Search, playback, and extract intelligence from recorded conversations.</p>
        </div>
        <div className="flex items-center gap-2.5">
          <Button onClick={() => setIsImportOpen(true)} variant="secondary" className="gap-2 text-xs">
            <Rss className="w-3.5 h-3.5 text-amber-400" />
            Import RSS Feed
          </Button>
          <Button onClick={() => setIsUploadOpen(true)} variant="accent" className="gap-2 text-xs">
            <Upload className="w-3.5 h-3.5" />
            Upload Episode
          </Button>
        </div>
      </div>

      {/* Toolbar */}
      <div className="flex flex-col sm:flex-row gap-3 justify-between items-stretch sm:items-center">
        <div className="w-full sm:max-w-xs">
          <Input 
            icon={<Search className="w-3.5 h-3.5" />} 
            placeholder="Filter episodes by title or project..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="h-8 text-xs"
          />
        </div>

        {/* Filter Badges */}
        <div className="flex items-center gap-1.5 overflow-x-auto pb-1 sm:pb-0">
          <FilterChip label="All" count={counts.all} active={activeFilter === 'All'} onClick={() => setActiveFilter('All')} />
          <FilterChip label="Indexed" count={counts.indexed} active={activeFilter === 'Indexed'} onClick={() => setActiveFilter('Indexed')} />
          <FilterChip label="Processing" count={counts.processing} active={activeFilter === 'Processing'} onClick={() => setActiveFilter('Processing')} />
          <FilterChip label="Failed" count={counts.failed} active={activeFilter === 'Failed'} onClick={() => setActiveFilter('Failed')} />
        </div>
      </div>

      {/* Error state */}
      {error && (
        <div className="p-4 bg-rose-500/10 border border-rose-500/20 rounded-lg flex items-center justify-between gap-3 text-xs text-rose-400">
          <div className="flex items-center gap-2">
            <AlertCircle className="w-4 h-4 shrink-0" />
            <span>{error}</span>
          </div>
          <Button variant="outline" size="sm" onClick={fetchEpisodeData} className="h-7 text-xs gap-1.5">
            <RefreshCw className="w-3 h-3" /> Retry
          </Button>
        </div>
      )}

      {/* Table */}
      <div className="border border-[var(--color-border)] rounded-lg overflow-hidden bg-[var(--color-surface)]">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Episode Title</TableHead>
              <TableHead>Duration</TableHead>
              <TableHead>Status</TableHead>
              <TableHead>Indexed</TableHead>
              <TableHead className="w-[100px] text-right">Actions</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {loading ? (
              <TableRow>
                <TableCell colSpan={5} className="text-center py-12 text-[var(--color-muted)]">
                  <div className="flex flex-col items-center justify-center space-y-2">
                    <Loader2 className="w-6 h-6 animate-spin text-[var(--color-accent)]" />
                    <p className="text-xs font-mono text-[var(--color-muted)]">Loading episodes from database...</p>
                  </div>
                </TableCell>
              </TableRow>
            ) : filteredEpisodes.length === 0 ? (
              <TableRow>
                <TableCell colSpan={5} className="text-center py-12 text-[var(--color-muted)]">
                  <div className="flex flex-col items-center justify-center space-y-2">
                    <FileAudio className="w-7 h-7 opacity-40 text-[var(--color-muted)]" />
                    <p className="text-xs font-medium text-[var(--color-primary)]">
                      {searchQuery ? "No episodes match your search criteria" : "No episodes in database"}
                    </p>
                    <p className="text-[11px] text-[var(--color-muted)]">
                      {searchQuery ? "Try clearing your filters" : "Upload an audio file or import an RSS feed to begin."}
                    </p>
                    {searchQuery ? (
                      <Button variant="outline" size="sm" onClick={() => { setSearchQuery(''); setActiveFilter('All'); }} className="text-xs h-7">
                        Clear filters
                      </Button>
                    ) : (
                      <div className="flex items-center gap-2 pt-2">
                        <Button variant="secondary" size="sm" onClick={() => setIsImportOpen(true)} className="text-xs h-7 gap-1.5">
                          <Rss className="w-3 h-3 text-amber-400" /> Import RSS
                        </Button>
                        <Button variant="accent" size="sm" onClick={() => setIsUploadOpen(true)} className="text-xs h-7 gap-1.5">
                          <Upload className="w-3 h-3" /> Upload File
                        </Button>
                      </div>
                    )}
                  </div>
                </TableCell>
              </TableRow>
            ) : (
              filteredEpisodes.map((ep) => (
                <TableRow key={ep.id} className="group hover:bg-[var(--color-surface-hover)] transition-colors">
                  <TableCell>
                    <div className="font-medium text-xs sm:text-sm text-[var(--color-primary)]">
                      <Link href={`/episodes/${ep.id}`} className="hover:text-[var(--color-accent)] transition-colors line-clamp-1">
                        {ep.title}
                      </Link>
                    </div>
                    <div className="text-[11px] text-[var(--color-muted)] font-mono mt-0.5">{ep.project_name || 'General'}</div>
                  </TableCell>
                  <TableCell className="text-[var(--color-muted)] font-mono text-xs">
                    {ep.duration_formatted || '00:00'}
                  </TableCell>
                  <TableCell>
                    <StatusBadge status={ep.status} />
                  </TableCell>
                  <TableCell className="text-[var(--color-muted)] text-xs font-mono">{ep.date_formatted || 'Recently'}</TableCell>
                  <TableCell className="text-right">
                    <div className="flex items-center justify-end gap-1.5 opacity-80 group-hover:opacity-100 transition-opacity">
                      <Link href={`/episodes/${ep.id}/player`}>
                        <Button variant="ghost" size="icon" className="h-7 w-7 text-[var(--color-muted)] hover:text-[var(--color-primary)]">
                          <Play className="w-3.5 h-3.5 fill-current" />
                        </Button>
                      </Link>
                      <Button 
                        variant="ghost" 
                        size="icon" 
                        onClick={() => handleOpenInsight(ep)}
                        className="h-7 w-7 text-[var(--color-muted)] hover:text-[var(--color-accent)]"
                        title="AI Intelligence Insights"
                      >
                        <Sparkles className="w-3.5 h-3.5" />
                      </Button>
                      <Button 
                        variant="ghost" 
                        size="icon" 
                        onClick={(e) => handleDelete(ep.id, e)}
                        className="h-7 w-7 text-[var(--color-muted)] hover:text-rose-400"
                        title="Delete Episode"
                      >
                        <Trash2 className="w-3.5 h-3.5" />
                      </Button>
                    </div>
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </div>

      {/* Upload Modal */}
      <Modal
        isOpen={isUploadOpen}
        onClose={() => setIsUploadOpen(false)}
        title="Upload Episode"
        description="Upload an MP3, WAV, M4A, or AAC file to transcribe, detect speakers, and generate semantic embeddings."
        footer={
          <div className="flex items-center gap-2">
            <Button 
              variant="secondary" 
              onClick={() => setIsUploadOpen(false)}
              disabled={isUploading}
              size="sm"
            >
              Cancel
            </Button>
            <Button 
              onClick={handleUploadSubmit}
              disabled={isUploading || !selectedFile}
              variant="accent"
              size="sm"
              className="gap-2"
            >
              {isUploading ? (
                <>
                  <Loader2 className="w-3.5 h-3.5 animate-spin" />
                  Uploading...
                </>
              ) : (
                <>
                  <Upload className="w-3.5 h-3.5" />
                  Queue Upload
                </>
              )}
            </Button>
          </div>
        }
      >
        <form onSubmit={handleUploadSubmit} className="space-y-4">
          <div 
            onClick={() => fileInputRef.current?.click()}
            className={`border border-dashed rounded-lg p-6 flex flex-col items-center justify-center text-center cursor-pointer transition-all duration-150 ${
              selectedFile 
                ? 'border-[var(--color-accent)] bg-[var(--color-accent-subtle)]/20' 
                : 'border-[var(--color-border-subtle)] hover:border-[var(--color-border-hover)] bg-[var(--color-surface-elevated)]/40'
            }`}
          >
            <input 
              ref={fileInputRef}
              type="file" 
              accept=".mp3,.wav,.m4a,.aac,.flac,.ogg,.mp4" 
              className="hidden" 
              onChange={handleFileSelect}
            />
            <div className="w-9 h-9 rounded-md bg-[var(--color-surface-elevated)] flex items-center justify-center mb-2.5 border border-[var(--color-border)]">
              <FileAudio className={`w-4 h-4 ${selectedFile ? 'text-[var(--color-accent)]' : 'text-[var(--color-muted)]'}`} />
            </div>
            {selectedFile ? (
              <div className="space-y-0.5">
                <p className="text-xs font-semibold text-[var(--color-primary)] truncate max-w-[280px]">
                  {selectedFile.name}
                </p>
                <p className="text-[11px] font-mono text-[var(--color-muted)]">
                  {(selectedFile.size / (1024 * 1024)).toFixed(1)} MB • Click to change
                </p>
              </div>
            ) : (
              <div className="space-y-0.5">
                <p className="text-xs font-medium text-[var(--color-primary)]">
                  Select or drag &amp; drop audio file
                </p>
                <p className="text-[10px] text-[var(--color-muted)] font-mono">
                  MP3, WAV, M4A, AAC, FLAC (up to 250MB)
                </p>
              </div>
            )}
          </div>

          <div className="space-y-1">
            <label className="text-xs font-medium text-[var(--color-muted)]">Episode Title</label>
            <Input 
              placeholder="e.g. Scaling Distributed Systems" 
              value={uploadTitle}
              onChange={(e) => setUploadTitle(e.target.value)}
              disabled={isUploading}
              className="h-8 text-xs"
            />
          </div>

          <div className="space-y-1">
            <label className="text-xs font-medium text-[var(--color-muted)]">Project Association</label>
            <select
              value={selectedProjectId}
              onChange={(e) => setSelectedProjectId(e.target.value)}
              disabled={isUploading}
              className="flex h-8 w-full rounded-md border border-[var(--color-border)] bg-[var(--color-surface-elevated)] px-3 text-xs text-[var(--color-primary)] outline-none focus:border-[var(--color-accent)]"
            >
              <option value="none">General / Unassigned</option>
              {projects.map(p => (
                <option key={p.id} value={p.id}>{p.name}</option>
              ))}
            </select>
          </div>

          {uploadError && (
            <div className="p-2.5 bg-rose-500/10 border border-rose-500/20 rounded-md flex items-center gap-2 text-xs text-rose-400">
              <AlertCircle className="w-3.5 h-3.5 shrink-0" />
              <span>{uploadError}</span>
            </div>
          )}

          {uploadSuccess && (
            <div className="p-2.5 bg-emerald-500/10 border border-emerald-500/20 rounded-md flex items-center gap-2 text-xs text-emerald-400">
              <Check className="w-3.5 h-3.5 shrink-0" />
              <span>{uploadSuccess}</span>
            </div>
          )}
        </form>
      </Modal>

      {/* RSS Import Modal */}
      <Modal
        isOpen={isImportOpen}
        onClose={() => setIsImportOpen(false)}
        title="Import Podcast from RSS Feed"
        description="Ingest podcast show metadata and episodes directly from an active RSS/Atom or Apple Podcasts XML feed."
        footer={
          <div className="flex items-center gap-2">
            <Button 
              variant="secondary" 
              onClick={() => setIsImportOpen(false)}
              disabled={isImporting}
              size="sm"
            >
              Cancel
            </Button>
            <Button 
              onClick={handleImportSubmit}
              disabled={isImporting || !importFeedUrl.trim()}
              variant="accent"
              size="sm"
              className="gap-2"
            >
              {isImporting ? (
                <>
                  <Loader2 className="w-3.5 h-3.5 animate-spin" />
                  Importing Feed...
                </>
              ) : (
                <>
                  <Rss className="w-3.5 h-3.5" />
                  Import Feed
                </>
              )}
            </Button>
          </div>
        }
      >
        <form onSubmit={handleImportSubmit} className="space-y-4">
          <div className="space-y-1">
            <label className="text-xs font-medium text-[var(--color-muted)]">Podcast RSS Feed URL</label>
            <Input 
              placeholder="https://example.com/podcast/feed.xml" 
              value={importFeedUrl}
              onChange={(e) => setImportFeedUrl(e.target.value)}
              disabled={isImporting}
              className="h-8 text-xs font-mono"
            />
          </div>

          <div className="flex items-center gap-2 pt-1">
            <input 
              type="checkbox"
              id="autoProcessCheck"
              checked={importAutoProcess}
              onChange={(e) => setImportAutoProcess(e.target.checked)}
              className="rounded border-[var(--color-border)] bg-[var(--color-surface-elevated)]"
            />
            <label htmlFor="autoProcessCheck" className="text-xs text-[var(--color-secondary)] cursor-pointer">
              Automatically download and queue latest episode for processing
            </label>
          </div>

          {importError && (
            <div className="p-2.5 bg-rose-500/10 border border-rose-500/20 rounded-md flex items-center gap-2 text-xs text-rose-400">
              <AlertCircle className="w-3.5 h-3.5 shrink-0" />
              <span>{importError}</span>
            </div>
          )}

          {importSuccess && (
            <div className="p-2.5 bg-emerald-500/10 border border-emerald-500/20 rounded-md flex items-center gap-2 text-xs text-emerald-400">
              <Check className="w-3.5 h-3.5 shrink-0" />
              <span>{importSuccess}</span>
            </div>
          )}
        </form>
      </Modal>

      {/* Episode Insight Modal */}
      <EpisodeInsightModal
        isOpen={isInsightModalOpen}
        onClose={() => {
          setIsInsightModalOpen(false);
          setInsightEpisode(null);
        }}
        episodeId={insightEpisode?.id || null}
        episodeTitle={insightEpisode?.title}
      />
    </div>
  );
}

function FilterChip({ label, count, active, onClick }: {
  label: string;
  count: number;
  active: boolean;
  onClick: () => void;
}) {
  return (
    <button
      onClick={onClick}
      className={`px-2.5 py-1 rounded-md text-xs font-medium flex items-center gap-1.5 transition-all duration-150 cursor-pointer ${
        active 
          ? 'bg-[var(--color-surface-elevated)] text-[var(--color-primary)] border border-[var(--color-border-subtle)] shadow-xs' 
          : 'text-[var(--color-muted)] hover:text-[var(--color-primary)] hover:bg-[var(--color-surface)] border border-transparent'
      }`}
    >
      <span>{label}</span>
      <span className="text-[10px] font-mono opacity-60">({count})</span>
    </button>
  );
}

function StatusBadge({ status }: { status: string }) {
  const norm = (status || '').toLowerCase();
  if (norm === 'indexed' || norm === 'completed') {
    return <Badge variant="success" dot>Indexed</Badge>;
  }
  if (norm === 'processing' || norm === 'queued' || norm === 'transcribing' || norm === 'chunking' || norm === 'embedding' || norm === 'indexing') {
    return <Badge variant="accent" dot>Processing</Badge>;
  }
  return <Badge variant="error" dot>Failed</Badge>;
}
