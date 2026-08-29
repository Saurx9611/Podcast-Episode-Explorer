"use client";

import React, { useState, useEffect, useCallback } from 'react';
import { Button } from '@/components/ui/button';
import { Check, Loader2 } from 'lucide-react';
import { getSettings, updateSettings, UserSettings } from '@/lib/api/settings';

export default function SettingsPage() {
  const [activeTab, setActiveTab] = useState('Search');
  const [toastMessage, setToastMessage] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [showDeleteModal, setShowDeleteModal] = useState(false);

  // General Settings
  const [workspaceName, setWorkspaceName] = useState('Engineering Podcast Library');
  const [defaultPlaybackSpeed, setDefaultPlaybackSpeed] = useState('1.0x');

  // Processing Settings
  const [transcriptionModel, setTranscriptionModel] = useState('Whisper Large v3');
  const [transcriptionLanguage, setTranscriptionLanguage] = useState('Auto-detect');
  const [translateToEnglish, setTranslateToEnglish] = useState(false);
  const [speakerDetection, setSpeakerDetection] = useState(true);
  const [maxSpeakers, setMaxSpeakers] = useState('Auto');
  const [speakerLabels, setSpeakerLabels] = useState('Speaker 1 / Speaker 2');
  const [chunkingStrategy, setChunkingStrategy] = useState('Speaker-aware temporal chunking');
  const [chunkDuration, setChunkDuration] = useState('45');
  const [overlap, setOverlap] = useState('10');
  const [procEmbeddingModel, setProcEmbeddingModel] = useState('text-embedding-3-small');
  const [vectorIndex, setVectorIndex] = useState('Local Vector Index');
  const [procSimilarityMetric, setProcSimilarityMetric] = useState('Cosine Similarity');
  const [procTopResults, setProcTopResults] = useState('10');
  const [autoProcess, setAutoProcess] = useState(true);
  const [generateEmbeddings, setGenerateEmbeddings] = useState(true);
  const [retryFailedJobs, setRetryFailedJobs] = useState(true);
  const [maxRetries, setMaxRetries] = useState('3');

  // Search Settings
  const [searchEmbeddingModel, setSearchEmbeddingModel] = useState('text-embedding-3-small');
  const [searchSimilarityMetric, setSearchSimilarityMetric] = useState('Cosine Similarity');
  const [searchMode, setSearchMode] = useState('Semantic');
  const [defaultResults, setDefaultResults] = useState('10');
  const [minSimilarity, setMinSimilarity] = useState('0.70');
  const [showSimilarityScore, setShowSimilarityScore] = useState(true);
  const [includeContext, setIncludeContext] = useState(true);
  const [contextWindow, setContextWindow] = useState('30 sec');
  const [includeAllEpisodes, setIncludeAllEpisodes] = useState(true);
  const [searchSpeakers, setSearchSpeakers] = useState(true);
  const [searchTopics, setSearchTopics] = useState(true);
  const [searchProjects, setSearchProjects] = useState(true);
  const [defaultDateRange, setDefaultDateRange] = useState('All time');
  const [openResultIn, setOpenResultIn] = useState('Transcript');
  const [autoPlay, setAutoPlay] = useState(false);
  const [preserveFilters, setPreserveFilters] = useState(true);
  const [transcriptPreviewLength, setTranscriptPreviewLength] = useState('2 lines');
  const [highlightText, setHighlightText] = useState(true);
  const [showSpeaker, setShowSpeaker] = useState(true);
  const [showTimestamp, setShowTimestamp] = useState(true);
  const [showEpisodeMetadata, setShowEpisodeMetadata] = useState(true);

  // Account Settings
  const [fullName, setFullName] = useState('Jane Doe');
  const [email, setEmail] = useState('jane@example.com');
  const [role, setRole] = useState('Developer');
  const [accountLanguage, setAccountLanguage] = useState('English');
  const [timeZone, setTimeZone] = useState('Asia/Kolkata (GMT+5:30)');
  const [dateFormat, setDateFormat] = useState('MMM DD, YYYY');
  const [notifEpisodeProcessed, setNotifEpisodeProcessed] = useState(true);
  const [notifSearchResults, setNotifSearchResults] = useState(true);
  const [notifSystemUpdates, setNotifSystemUpdates] = useState(false);
  const [notifEmail, setNotifEmail] = useState(true);
  const [themeMode, setThemeMode] = useState('Dark');
  const [accentColor, setAccentColor] = useState('Indigo');

  // Load Settings from Backend
  const loadSettings = useCallback(async () => {
    try {
      setLoading(true);
      const user = await getSettings();
      if (user) {
        if (user.name) setFullName(user.name);
        if (user.email) setEmail(user.email);
        if (user.role) setRole(user.role);

        const prefs = user.preferences || {};

        if (prefs.general) {
          if (prefs.general.workspace_name) setWorkspaceName(prefs.general.workspace_name);
          if (prefs.general.default_playback_speed) setDefaultPlaybackSpeed(prefs.general.default_playback_speed);
        }

        if (prefs.processing) {
          const p = prefs.processing;
          if (p.transcription_model) setTranscriptionModel(p.transcription_model);
          if (p.language) setTranscriptionLanguage(p.language);
          if (p.translate_to_english !== undefined) setTranslateToEnglish(p.translate_to_english);
          if (p.speaker_detection !== undefined) setSpeakerDetection(p.speaker_detection);
          if (p.max_speakers) setMaxSpeakers(p.max_speakers);
          if (p.speaker_labels) setSpeakerLabels(p.speaker_labels);
          if (p.chunking_strategy) setChunkingStrategy(p.chunking_strategy);
          if (p.chunk_duration) setChunkDuration(p.chunk_duration);
          if (p.overlap) setOverlap(p.overlap);
          if (p.embedding_model) setProcEmbeddingModel(p.embedding_model);
          if (p.vector_index) setVectorIndex(p.vector_index);
          if (p.similarity_metric) setProcSimilarityMetric(p.similarity_metric);
          if (p.top_results) setProcTopResults(p.top_results);
          if (p.auto_process !== undefined) setAutoProcess(p.auto_process);
          if (p.generate_embeddings !== undefined) setGenerateEmbeddings(p.generate_embeddings);
          if (p.retry_failed_jobs !== undefined) setRetryFailedJobs(p.retry_failed_jobs);
          if (p.max_retries) setMaxRetries(p.max_retries);
        }

        if (prefs.search) {
          const s = prefs.search;
          if (s.embedding_model) setSearchEmbeddingModel(s.embedding_model);
          if (s.similarity_metric) setSearchSimilarityMetric(s.similarity_metric);
          if (s.search_mode) setSearchMode(s.search_mode);
          if (s.default_results) setDefaultResults(s.default_results);
          if (s.min_similarity) setMinSimilarity(s.min_similarity);
          if (s.show_similarity_score !== undefined) setShowSimilarityScore(s.show_similarity_score);
          if (s.include_context !== undefined) setIncludeContext(s.include_context);
          if (s.context_window) setContextWindow(s.context_window);
          if (s.include_all_episodes !== undefined) setIncludeAllEpisodes(s.include_all_episodes);
          if (s.search_speakers !== undefined) setSearchSpeakers(s.search_speakers);
          if (s.search_topics !== undefined) setSearchTopics(s.search_topics);
          if (s.search_projects !== undefined) setSearchProjects(s.search_projects);
          if (s.default_date_range) setDefaultDateRange(s.default_date_range);
          if (s.open_result_in) setOpenResultIn(s.open_result_in);
          if (s.auto_play !== undefined) setAutoPlay(s.auto_play);
          if (s.preserve_filters !== undefined) setPreserveFilters(s.preserve_filters);
          if (s.transcript_preview_length) setTranscriptPreviewLength(s.transcript_preview_length);
          if (s.highlight_text !== undefined) setHighlightText(s.highlight_text);
          if (s.show_speaker !== undefined) setShowSpeaker(s.show_speaker);
          if (s.show_timestamp !== undefined) setShowTimestamp(s.show_timestamp);
          if (s.show_episode_metadata !== undefined) setShowEpisodeMetadata(s.show_episode_metadata);
        }

        if (prefs.account) {
          const a = prefs.account;
          if (a.language) setAccountLanguage(a.language);
          if (a.time_zone) setTimeZone(a.time_zone);
          if (a.date_format) setDateFormat(a.date_format);
          if (a.notif_episode_processed !== undefined) setNotifEpisodeProcessed(a.notif_episode_processed);
          if (a.notif_search_results !== undefined) setNotifSearchResults(a.notif_search_results);
          if (a.notif_system_updates !== undefined) setNotifSystemUpdates(a.notif_system_updates);
          if (a.notif_email !== undefined) setNotifEmail(a.notif_email);
          if (a.theme_mode) setThemeMode(a.theme_mode);
          if (a.accent_color) setAccentColor(a.accent_color);
        }
      }
    } catch (err) {
      console.warn('Backend settings endpoint unavailable, using defaults:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadSettings();
  }, [loadSettings]);

  const handleSave = async () => {
    try {
      setSaving(true);
      await updateSettings({
        name: fullName,
        role: role,
        preferences: {
          general: {
            workspace_name: workspaceName,
            default_playback_speed: defaultPlaybackSpeed,
          },
          processing: {
            transcription_model: transcriptionModel,
            language: transcriptionLanguage,
            translate_to_english: translateToEnglish,
            speaker_detection: speakerDetection,
            max_speakers: maxSpeakers,
            speaker_labels: speakerLabels,
            chunking_strategy: chunkingStrategy,
            chunk_duration: chunkDuration,
            overlap: overlap,
            embedding_model: procEmbeddingModel,
            vector_index: vectorIndex,
            similarity_metric: procSimilarityMetric,
            top_results: procTopResults,
            auto_process: autoProcess,
            generate_embeddings: generateEmbeddings,
            retry_failed_jobs: retryFailedJobs,
            max_retries: maxRetries,
          },
          search: {
            embedding_model: searchEmbeddingModel,
            similarity_metric: searchSimilarityMetric,
            search_mode: searchMode,
            default_results: defaultResults,
            min_similarity: minSimilarity,
            show_similarity_score: showSimilarityScore,
            include_context: includeContext,
            context_window: contextWindow,
            include_all_episodes: includeAllEpisodes,
            search_speakers: searchSpeakers,
            search_topics: searchTopics,
            search_projects: searchProjects,
            default_date_range: defaultDateRange,
            open_result_in: openResultIn,
            auto_play: autoPlay,
            preserve_filters: preserveFilters,
            transcript_preview_length: transcriptPreviewLength,
            highlight_text: highlightText,
            show_speaker: showSpeaker,
            show_timestamp: showTimestamp,
            show_episode_metadata: showEpisodeMetadata,
          },
          account: {
            language: accountLanguage,
            time_zone: timeZone,
            date_format: dateFormat,
            notif_episode_processed: notifEpisodeProcessed,
            notif_search_results: notifSearchResults,
            notif_system_updates: notifSystemUpdates,
            notif_email: notifEmail,
            theme_mode: themeMode,
            accent_color: accentColor,
          },
        },
      });
      setToastMessage(`${activeTab} settings saved.`);
      setTimeout(() => setToastMessage(null), 3000);
    } catch (err: any) {
      alert(err.message || 'Failed to save settings.');
    } finally {
      setSaving(false);
    }
  };

  const handleReset = () => {
    if (activeTab === 'General') {
      setWorkspaceName('Engineering Podcast Library');
      setDefaultPlaybackSpeed('1.0x');
    } else if (activeTab === 'Processing') {
      setChunkDuration('45');
      setOverlap('10');
      setTranscriptionModel('Whisper Large v3');
    } else if (activeTab === 'Search') {
      setMinSimilarity('0.70');
      setDefaultResults('10');
      setSearchMode('Semantic');
    } else if (activeTab === 'Account') {
      setThemeMode('Dark');
      setAccentColor('Indigo');
    }
    setToastMessage(`${activeTab} settings reset to defaults.`);
    setTimeout(() => setToastMessage(null), 3000);
  };

  return (
    <div className="max-w-4xl space-y-8 relative">
      {/* Toast Notification */}
      {toastMessage && (
        <div className="fixed bottom-6 right-6 z-50 bg-[var(--color-surface)] border border-[var(--color-border)] shadow-lg rounded-md px-4 py-3 flex items-center gap-2 animate-in slide-in-from-bottom-5">
          <Check className="w-4 h-4 text-emerald-400" />
          <span className="text-sm text-[var(--color-primary)]">{toastMessage}</span>
        </div>
      )}

      {/* Delete Account Modal */}
      {showDeleteModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm">
          <div className="bg-[#121214] border border-[var(--color-border)] rounded-xl w-full max-w-md overflow-hidden shadow-2xl animate-in fade-in zoom-in-95 duration-200">
            <div className="p-6">
              <h3 className="text-lg font-semibold text-[var(--color-primary)] mb-2">Delete account?</h3>
              <p className="text-sm text-[var(--color-secondary)]">This action cannot be undone. Your workspace data and indexed episodes will be permanently removed.</p>
            </div>
            <div className="p-4 bg-[#161618] border-t border-[var(--color-border)] flex justify-end gap-3">
              <Button variant="secondary" onClick={() => setShowDeleteModal(false)}>Cancel</Button>
              <Button variant="danger" className="bg-red-900/60 hover:bg-red-900/80 text-red-200 border border-red-900" onClick={() => {
                setShowDeleteModal(false);
                setToastMessage("Account deleted.");
                setTimeout(() => setToastMessage(null), 3000);
              }}>
                Delete Account
              </Button>
            </div>
          </div>
        </div>
      )}

      {/* Page Header */}
      <div>
        <h1 className="text-2xl font-semibold tracking-tight text-[var(--color-primary)]">Settings</h1>
        <p className="text-sm text-[var(--color-secondary)] mt-1">Manage your workspace preferences and processing configuration.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
        
        {/* Settings Navigation */}
        <div className="md:col-span-1 border-b border-[var(--color-border-subtle)] md:border-b-0 pb-4 md:pb-0 mb-6 md:mb-0">
          <nav className="flex flex-row md:flex-col space-x-2 md:space-x-0 md:space-y-1 overflow-x-auto scrollbar-hide pb-1 md:pb-0">
            <button 
              onClick={() => setActiveTab('General')}
              className={`whitespace-nowrap text-left px-3 py-2 rounded-md text-sm font-medium transition-colors ${activeTab === 'General' ? 'bg-[var(--color-accent-subtle)] text-[var(--color-accent)]' : 'text-[var(--color-secondary)] hover:bg-[var(--color-border-subtle)] hover:text-[var(--color-primary)]'}`}
            >
              General
            </button>
            <button 
              onClick={() => setActiveTab('Processing')}
              className={`whitespace-nowrap text-left px-3 py-2 rounded-md text-sm font-medium transition-colors ${activeTab === 'Processing' ? 'bg-[var(--color-accent-subtle)] text-[var(--color-accent)]' : 'text-[var(--color-secondary)] hover:bg-[var(--color-border-subtle)] hover:text-[var(--color-primary)]'}`}
            >
              Processing
            </button>
            <button 
              onClick={() => setActiveTab('Search')}
              className={`whitespace-nowrap text-left px-3 py-2 rounded-md text-sm font-medium transition-colors ${activeTab === 'Search' ? 'bg-[var(--color-accent-subtle)] text-[var(--color-accent)]' : 'text-[var(--color-secondary)] hover:bg-[var(--color-border-subtle)] hover:text-[var(--color-primary)]'}`}
            >
              Search
            </button>
            <button 
              onClick={() => setActiveTab('Account')}
              className={`whitespace-nowrap text-left px-3 py-2 rounded-md text-sm font-medium transition-colors ${activeTab === 'Account' ? 'bg-[var(--color-accent-subtle)] text-[var(--color-accent)]' : 'text-[var(--color-secondary)] hover:bg-[var(--color-border-subtle)] hover:text-[var(--color-primary)]'}`}
            >
              Account
            </button>
          </nav>
        </div>

        {/* Settings Content */}
        <div className="md:col-span-3 space-y-8">
          
          {activeTab === 'General' && (
            <div className="space-y-8">
              <div className="mb-2">
                <h2 className="text-xl font-semibold text-[var(--color-primary)]">General</h2>
                <p className="text-sm text-[var(--color-secondary)] mt-1">Basic configuration for your workspace.</p>
              </div>
              <section className="bg-[var(--color-surface)] border border-[var(--color-border)] rounded-lg">
                <div className="px-6 py-5 border-b border-[var(--color-border)]">
                  <h3 className="text-base font-semibold text-[var(--color-primary)]">Workspace Details</h3>
                  <p className="text-sm text-[var(--color-secondary)] mt-1">Basic configuration for your workspace.</p>
                </div>
                <div className="p-6 space-y-6">
                  <div className="grid gap-2">
                    <label className="text-sm font-medium text-[var(--color-primary)]">Workspace Name</label>
                    <input 
                      type="text" 
                      value={workspaceName}
                      onChange={e => setWorkspaceName(e.target.value)}
                      className="max-w-md px-3 py-2 bg-[#161618] border border-[var(--color-border)] rounded-md text-sm outline-none focus:border-[var(--color-accent)] focus:ring-1 focus:ring-[var(--color-accent)] text-[var(--color-primary)]" 
                    />
                  </div>
                  <div className="grid gap-2">
                    <label className="text-sm font-medium text-[var(--color-primary)]">Default Playback Speed</label>
                    <select 
                      value={defaultPlaybackSpeed}
                      onChange={e => setDefaultPlaybackSpeed(e.target.value)}
                      className="max-w-xs px-3 py-2 bg-[#161618] border border-[var(--color-border)] rounded-md text-sm outline-none focus:border-[var(--color-accent)] focus:ring-1 focus:ring-[var(--color-accent)] text-[var(--color-primary)]"
                    >
                      <option>1.0x</option>
                      <option>1.2x</option>
                      <option>1.5x</option>
                      <option>2.0x</option>
                    </select>
                  </div>
                </div>
              </section>
              <div className="flex justify-end gap-3 pt-4">
                <Button variant="secondary" onClick={handleReset}>Reset to Defaults</Button>
                <Button onClick={handleSave} disabled={saving}>
                  {saving ? "Saving..." : "Save Changes"}
                </Button>
              </div>
            </div>
          )}

          {activeTab === 'Processing' && (
            <div className="space-y-8">
              <div className="mb-2">
                <h2 className="text-xl font-semibold text-[var(--color-primary)]">Processing</h2>
                <p className="text-sm text-[var(--color-secondary)] mt-1">Configure how uploaded audio is transcribed, segmented, and indexed.</p>
              </div>

              {/* Transcription */}
              <section className="bg-[var(--color-surface)] border border-[var(--color-border)] rounded-lg">
                <div className="px-6 py-5 border-b border-[var(--color-border)]">
                  <h3 className="text-base font-semibold text-[var(--color-primary)]">Transcription</h3>
                  <p className="text-sm text-[var(--color-secondary)] mt-1">Configure the speech-to-text model used for uploaded episodes.</p>
                </div>
                <div className="p-6 space-y-6">
                  <div className="grid gap-2">
                    <label className="text-sm font-medium text-[var(--color-primary)]">Transcription Model</label>
                    <select 
                      value={transcriptionModel}
                      onChange={e => setTranscriptionModel(e.target.value)}
                      className="max-w-md px-3 py-2 bg-[#161618] border border-[var(--color-border)] rounded-md text-sm outline-none focus:border-[var(--color-accent)] focus:ring-1 focus:ring-[var(--color-accent)] text-[var(--color-primary)]"
                    >
                      <option>Whisper Large v3</option>
                      <option>Whisper Medium</option>
                      <option>Whisper Small</option>
                    </select>
                    <p className="text-xs text-[var(--color-secondary)]">Whisper Large v3 provides the highest transcription accuracy for long-form conversations.</p>
                  </div>
                  <div className="grid gap-2">
                    <label className="text-sm font-medium text-[var(--color-primary)]">Language</label>
                    <select 
                      value={transcriptionLanguage}
                      onChange={e => setTranscriptionLanguage(e.target.value)}
                      className="max-w-md px-3 py-2 bg-[#161618] border border-[var(--color-border)] rounded-md text-sm outline-none focus:border-[var(--color-accent)] focus:ring-1 focus:ring-[var(--color-accent)] text-[var(--color-primary)]"
                    >
                      <option>Auto-detect</option>
                      <option>English</option>
                      <option>Hindi</option>
                      <option>Spanish</option>
                      <option>French</option>
                      <option>German</option>
                    </select>
                  </div>
                  <div className="flex items-start gap-3">
                    <input 
                      type="checkbox" 
                      id="translate" 
                      checked={translateToEnglish}
                      onChange={e => setTranslateToEnglish(e.target.checked)}
                      className="mt-1 w-4 h-4 rounded bg-[#161618] border-[var(--color-border-subtle)] text-[var(--color-accent)] focus:ring-[var(--color-accent)]" 
                    />
                    <div>
                      <label htmlFor="translate" className="text-sm font-medium text-[var(--color-primary)] cursor-pointer">Translate to English</label>
                      <p className="text-xs text-[var(--color-secondary)] mt-0.5">Translate non-English speech into English during transcription.</p>
                    </div>
                  </div>
                </div>
              </section>

              {/* Speaker Detection */}
              <section className="bg-[var(--color-surface)] border border-[var(--color-border)] rounded-lg">
                <div className="px-6 py-5 border-b border-[var(--color-border)]">
                  <h3 className="text-base font-semibold text-[var(--color-primary)]">Speaker Detection</h3>
                  <p className="text-sm text-[var(--color-secondary)] mt-1">Identify and separate individual speakers in each episode.</p>
                </div>
                <div className="p-6 space-y-6">
                  <div className="flex items-start gap-3">
                    <input 
                      type="checkbox" 
                      id="speaker-detection-new" 
                      checked={speakerDetection}
                      onChange={e => setSpeakerDetection(e.target.checked)}
                      className="mt-1 w-4 h-4 rounded bg-[#161618] border-[var(--color-border-subtle)] text-[var(--color-accent)] focus:ring-[var(--color-accent)]" 
                    />
                    <div>
                      <label htmlFor="speaker-detection-new" className="text-sm font-medium text-[var(--color-primary)] cursor-pointer">Speaker Detection</label>
                      <p className="text-xs text-[var(--color-secondary)] mt-0.5">Automatically identify speaker turns during transcription.</p>
                    </div>
                  </div>
                  <div className="grid gap-2">
                    <label className="text-sm font-medium text-[var(--color-primary)]">Maximum Speakers</label>
                    <select 
                      value={maxSpeakers}
                      onChange={e => setMaxSpeakers(e.target.value)}
                      className="max-w-xs px-3 py-2 bg-[#161618] border border-[var(--color-border)] rounded-md text-sm outline-none focus:border-[var(--color-accent)] focus:ring-1 focus:ring-[var(--color-accent)] text-[var(--color-primary)]"
                    >
                      <option>Auto</option>
                      <option>2</option>
                      <option>3</option>
                      <option>4</option>
                      <option>5</option>
                      <option>6</option>
                      <option>8</option>
                    </select>
                    <p className="text-xs text-[var(--color-secondary)]">Limit the maximum number of speakers detected in an episode.</p>
                  </div>
                  <div className="grid gap-2">
                    <label className="text-sm font-medium text-[var(--color-primary)]">Speaker Labels</label>
                    <select 
                      value={speakerLabels}
                      onChange={e => setSpeakerLabels(e.target.value)}
                      className="max-w-md px-3 py-2 bg-[#161618] border border-[var(--color-border)] rounded-md text-sm outline-none focus:border-[var(--color-accent)] focus:ring-1 focus:ring-[var(--color-accent)] text-[var(--color-primary)]"
                    >
                      <option>Speaker 1 / Speaker 2</option>
                      <option>Named speakers when available</option>
                    </select>
                  </div>
                </div>
              </section>

              {/* Temporal Segmentation */}
              <section className="bg-[var(--color-surface)] border border-[var(--color-border)] rounded-lg">
                <div className="px-6 py-5 border-b border-[var(--color-border)]">
                  <h3 className="text-base font-semibold text-[var(--color-primary)]">Temporal Segmentation</h3>
                  <p className="text-sm text-[var(--color-secondary)] mt-1">Control how transcripts are divided into searchable segments.</p>
                </div>
                <div className="p-6 space-y-6">
                  <div className="grid gap-2">
                    <label className="text-sm font-medium text-[var(--color-primary)]">Chunking Strategy</label>
                    <select 
                      value={chunkingStrategy}
                      onChange={e => setChunkingStrategy(e.target.value)}
                      className="max-w-md px-3 py-2 bg-[#161618] border border-[var(--color-border)] rounded-md text-sm outline-none focus:border-[var(--color-accent)] focus:ring-1 focus:ring-[var(--color-accent)] text-[var(--color-primary)]"
                    >
                      <option>Speaker-aware temporal chunking</option>
                      <option>Fixed duration</option>
                      <option>Paragraph-based</option>
                      <option>Hybrid</option>
                    </select>
                  </div>
                  
                  <div className="grid gap-3">
                    <div className="flex justify-between items-center max-w-md">
                      <label className="text-sm font-medium text-[var(--color-primary)]">Chunk Duration</label>
                      <span className="text-sm font-medium text-[var(--color-accent)]">{chunkDuration} sec</span>
                    </div>
                    <div className="max-w-md relative flex items-center h-5">
                      <input 
                        type="range" 
                        min="15" max="120" step="15" 
                        value={chunkDuration} 
                        onChange={e => setChunkDuration(e.target.value)} 
                        className="w-full accent-[var(--color-accent)] h-1.5 bg-[#161618] rounded-lg appearance-none cursor-pointer" 
                      />
                    </div>
                    <div className="max-w-md flex justify-between text-[11px] text-[var(--color-secondary)] font-mono">
                      <span>15s</span>
                      <span>120s</span>
                    </div>
                  </div>

                  <div className="grid gap-3">
                    <div className="flex justify-between items-center max-w-md">
                      <label className="text-sm font-medium text-[var(--color-primary)]">Overlap</label>
                      <span className="text-sm font-medium text-[var(--color-accent)]">{overlap} sec</span>
                    </div>
                    <div className="max-w-md relative flex items-center h-5">
                      <input 
                        type="range" 
                        min="0" max="30" step="5" 
                        value={overlap} 
                        onChange={e => setOverlap(e.target.value)} 
                        className="w-full accent-[var(--color-accent)] h-1.5 bg-[#161618] rounded-lg appearance-none cursor-pointer" 
                      />
                    </div>
                    <p className="text-xs text-[var(--color-secondary)]">Overlap adjacent segments to preserve context during semantic search.</p>
                  </div>
                </div>
              </section>

              {/* Semantic Indexing */}
              <section className="bg-[var(--color-surface)] border border-[var(--color-border)] rounded-lg">
                <div className="px-6 py-5 border-b border-[var(--color-border)]">
                  <h3 className="text-base font-semibold text-[var(--color-primary)]">Semantic Indexing</h3>
                  <p className="text-sm text-[var(--color-secondary)] mt-1">Configure how transcript segments are converted into searchable vectors.</p>
                </div>
                <div className="p-6 space-y-6">
                  <div className="grid gap-2">
                    <label className="text-sm font-medium text-[var(--color-primary)]">Embedding Model</label>
                    <select 
                      value={procEmbeddingModel}
                      onChange={e => setProcEmbeddingModel(e.target.value)}
                      className="max-w-md px-3 py-2 bg-[#161618] border border-[var(--color-border)] rounded-md text-sm outline-none focus:border-[var(--color-accent)] focus:ring-1 focus:ring-[var(--color-accent)] text-[var(--color-primary)]"
                    >
                      <option>text-embedding-3-small</option>
                      <option>text-embedding-3-large</option>
                    </select>
                  </div>
                  <div className="grid gap-2">
                    <label className="text-sm font-medium text-[var(--color-primary)]">Vector Index</label>
                    <select 
                      value={vectorIndex}
                      onChange={e => setVectorIndex(e.target.value)}
                      className="max-w-md px-3 py-2 bg-[#161618] border border-[var(--color-border)] rounded-md text-sm outline-none focus:border-[var(--color-accent)] focus:ring-1 focus:ring-[var(--color-accent)] text-[var(--color-primary)]"
                    >
                      <option>Local Vector Index</option>
                      <option>Pinecone</option>
                      <option>Qdrant</option>
                    </select>
                  </div>
                  <div className="grid gap-2">
                    <label className="text-sm font-medium text-[var(--color-primary)]">Similarity Metric</label>
                    <select 
                      value={procSimilarityMetric}
                      onChange={e => setProcSimilarityMetric(e.target.value)}
                      className="max-w-md px-3 py-2 bg-[#161618] border border-[var(--color-border)] rounded-md text-sm outline-none focus:border-[var(--color-accent)] focus:ring-1 focus:ring-[var(--color-accent)] text-[var(--color-primary)]"
                    >
                      <option>Cosine Similarity</option>
                      <option>Dot Product</option>
                      <option>Euclidean Distance</option>
                    </select>
                  </div>
                  <div className="grid gap-2">
                    <label className="text-sm font-medium text-[var(--color-primary)]">Top Results</label>
                    <select 
                      value={procTopResults}
                      onChange={e => setProcTopResults(e.target.value)}
                      className="max-w-xs px-3 py-2 bg-[#161618] border border-[var(--color-border)] rounded-md text-sm outline-none focus:border-[var(--color-accent)] focus:ring-1 focus:ring-[var(--color-accent)] text-[var(--color-primary)]"
                    >
                      <option>5</option>
                      <option>10</option>
                      <option>20</option>
                      <option>50</option>
                    </select>
                    <p className="text-xs text-[var(--color-secondary)]">Number of matching segments returned for semantic searches.</p>
                  </div>
                </div>
              </section>

              {/* Processing Behavior */}
              <section className="bg-[var(--color-surface)] border border-[var(--color-border)] rounded-lg">
                <div className="px-6 py-5 border-b border-[var(--color-border)]">
                  <h3 className="text-base font-semibold text-[var(--color-primary)]">Processing Behavior</h3>
                </div>
                <div className="p-6 space-y-6">
                  <div className="flex items-start gap-3">
                    <input 
                      type="checkbox" 
                      id="auto-process" 
                      checked={autoProcess}
                      onChange={e => setAutoProcess(e.target.checked)}
                      className="mt-1 w-4 h-4 rounded bg-[#161618] border-[var(--color-border-subtle)] text-[var(--color-accent)] focus:ring-[var(--color-accent)]" 
                    />
                    <div>
                      <label htmlFor="auto-process" className="text-sm font-medium text-[var(--color-primary)] cursor-pointer">Automatic Processing</label>
                      <p className="text-xs text-[var(--color-secondary)] mt-0.5">Automatically process newly uploaded episodes.</p>
                    </div>
                  </div>
                  <div className="flex items-start gap-3">
                    <input 
                      type="checkbox" 
                      id="generate-embed" 
                      checked={generateEmbeddings}
                      onChange={e => setGenerateEmbeddings(e.target.checked)}
                      className="mt-1 w-4 h-4 rounded bg-[#161618] border-[var(--color-border-subtle)] text-[var(--color-accent)] focus:ring-[var(--color-accent)]" 
                    />
                    <div>
                      <label htmlFor="generate-embed" className="text-sm font-medium text-[var(--color-primary)] cursor-pointer">Generate Embeddings</label>
                      <p className="text-xs text-[var(--color-secondary)] mt-0.5">Generate semantic embeddings after transcription is complete.</p>
                    </div>
                  </div>
                  <div className="flex items-start gap-3">
                    <input 
                      type="checkbox" 
                      id="retry" 
                      checked={retryFailedJobs}
                      onChange={e => setRetryFailedJobs(e.target.checked)}
                      className="mt-1 w-4 h-4 rounded bg-[#161618] border-[var(--color-border-subtle)] text-[var(--color-accent)] focus:ring-[var(--color-accent)]" 
                    />
                    <div>
                      <label htmlFor="retry" className="text-sm font-medium text-[var(--color-primary)] cursor-pointer">Retry Failed Jobs</label>
                    </div>
                  </div>
                  <div className="grid gap-2 pl-7">
                    <label className="text-sm font-medium text-[var(--color-primary)]">Maximum Retries</label>
                    <select 
                      value={maxRetries}
                      onChange={e => setMaxRetries(e.target.value)}
                      className="max-w-xs px-3 py-2 bg-[#161618] border border-[var(--color-border)] rounded-md text-sm outline-none focus:border-[var(--color-accent)] focus:ring-1 focus:ring-[var(--color-accent)] text-[var(--color-primary)]"
                    >
                      <option>1</option>
                      <option>2</option>
                      <option>3</option>
                      <option>5</option>
                    </select>
                  </div>
                </div>
              </section>

              <div className="flex justify-end gap-3 pt-4">
                <Button variant="secondary" onClick={handleReset}>
                  Reset to Defaults
                </Button>
                <Button onClick={handleSave} disabled={saving}>
                  {saving ? "Saving..." : "Save Changes"}
                </Button>
              </div>
            </div>
          )}

          {activeTab === 'Search' && (
            <div className="space-y-8">
              <div className="mb-2">
                <h2 className="text-xl font-semibold text-[var(--color-primary)]">Search</h2>
                <p className="text-sm text-[var(--color-secondary)] mt-1">Configure how semantic searches retrieve and rank transcript segments.</p>
              </div>

              {/* Search Engine */}
              <section className="bg-[var(--color-surface)] border border-[var(--color-border)] rounded-lg">
                <div className="px-6 py-5 border-b border-[var(--color-border)]">
                  <h3 className="text-base font-semibold text-[var(--color-primary)]">Search Engine</h3>
                  <p className="text-sm text-[var(--color-secondary)] mt-1">Configure the semantic retrieval system used across your podcast library.</p>
                </div>
                <div className="p-6 space-y-6">
                  <div className="grid gap-2">
                    <label className="text-sm font-medium text-[var(--color-primary)]">Embedding Model</label>
                    <select 
                      value={searchEmbeddingModel}
                      onChange={e => setSearchEmbeddingModel(e.target.value)}
                      className="max-w-md px-3 py-2 bg-[#161618] border border-[var(--color-border)] rounded-md text-sm outline-none focus:border-[var(--color-accent)] focus:ring-1 focus:ring-[var(--color-accent)] text-[var(--color-primary)]"
                    >
                      <option>text-embedding-3-small</option>
                      <option>text-embedding-3-large</option>
                    </select>
                  </div>
                  <div className="grid gap-2">
                    <label className="text-sm font-medium text-[var(--color-primary)]">Similarity Metric</label>
                    <select 
                      value={searchSimilarityMetric}
                      onChange={e => setSearchSimilarityMetric(e.target.value)}
                      className="max-w-md px-3 py-2 bg-[#161618] border border-[var(--color-border)] rounded-md text-sm outline-none focus:border-[var(--color-accent)] focus:ring-1 focus:ring-[var(--color-accent)] text-[var(--color-primary)]"
                    >
                      <option>Cosine Similarity</option>
                      <option>Dot Product</option>
                      <option>Euclidean Distance</option>
                    </select>
                  </div>
                  <div className="grid gap-2">
                    <label className="text-sm font-medium text-[var(--color-primary)]">Search Mode</label>
                    <select 
                      value={searchMode}
                      onChange={e => setSearchMode(e.target.value)}
                      className="max-w-md px-3 py-2 bg-[#161618] border border-[var(--color-border)] rounded-md text-sm outline-none focus:border-[var(--color-accent)] focus:ring-1 focus:ring-[var(--color-accent)] text-[var(--color-primary)]"
                    >
                      <option>Semantic</option>
                      <option>Keyword</option>
                      <option>Hybrid</option>
                    </select>
                    <p className="text-xs text-[var(--color-secondary)]">Semantic search retrieves conceptually related transcript segments even when the exact words are not present.</p>
                  </div>
                </div>
              </section>

              {/* Result Settings */}
              <section className="bg-[var(--color-surface)] border border-[var(--color-border)] rounded-lg">
                <div className="px-6 py-5 border-b border-[var(--color-border)]">
                  <h3 className="text-base font-semibold text-[var(--color-primary)]">Result Settings</h3>
                </div>
                <div className="p-6 space-y-6">
                  <div className="grid gap-2">
                    <label className="text-sm font-medium text-[var(--color-primary)]">Default Results</label>
                    <select 
                      value={defaultResults} 
                      onChange={e => setDefaultResults(e.target.value)}
                      className="max-w-xs px-3 py-2 bg-[#161618] border border-[var(--color-border)] rounded-md text-sm outline-none focus:border-[var(--color-accent)] focus:ring-1 focus:ring-[var(--color-accent)] text-[var(--color-primary)]"
                    >
                      <option>5</option>
                      <option>10</option>
                      <option>20</option>
                      <option>50</option>
                    </select>
                    <p className="text-xs text-[var(--color-secondary)]">Number of results shown for a new search.</p>
                  </div>

                  <div className="grid gap-3">
                    <div className="flex justify-between items-center max-w-md">
                      <label className="text-sm font-medium text-[var(--color-primary)]">Minimum Similarity</label>
                      <span className="text-sm font-medium text-[var(--color-accent)]">{Number(minSimilarity).toFixed(2)}</span>
                    </div>
                    <div className="max-w-md relative flex items-center h-5">
                      <input 
                        type="range" 
                        min="0.50" max="1.00" step="0.01" 
                        value={minSimilarity} 
                        onChange={e => setMinSimilarity(e.target.value)} 
                        className="w-full accent-[var(--color-accent)] h-1.5 bg-[#161618] rounded-lg appearance-none cursor-pointer" 
                      />
                    </div>
                    <div className="max-w-md flex justify-between text-[11px] text-[var(--color-secondary)] font-mono">
                      <span>0.50</span>
                      <span>1.00</span>
                    </div>
                  </div>

                  <div className="flex items-start gap-3">
                    <input 
                      type="checkbox" 
                      id="show-similarity" 
                      checked={showSimilarityScore}
                      onChange={e => setShowSimilarityScore(e.target.checked)}
                      className="mt-1 w-4 h-4 rounded bg-[#161618] border-[var(--color-border-subtle)] text-[var(--color-accent)] focus:ring-[var(--color-accent)]" 
                    />
                    <div>
                      <label htmlFor="show-similarity" className="text-sm font-medium text-[var(--color-primary)] cursor-pointer">Show Similarity Score</label>
                      <p className="text-xs text-[var(--color-secondary)] mt-0.5">Display the relevance score for each search result.</p>
                    </div>
                  </div>

                  <div className="flex items-start gap-3">
                    <input 
                      type="checkbox" 
                      id="include-context" 
                      checked={includeContext}
                      onChange={e => setIncludeContext(e.target.checked)}
                      className="mt-1 w-4 h-4 rounded bg-[#161618] border-[var(--color-border-subtle)] text-[var(--color-accent)] focus:ring-[var(--color-accent)]" 
                    />
                    <div>
                      <label htmlFor="include-context" className="text-sm font-medium text-[var(--color-primary)] cursor-pointer">Include Context</label>
                      <p className="text-xs text-[var(--color-secondary)] mt-0.5">Include surrounding transcript context around each matching segment.</p>
                    </div>
                  </div>

                  <div className="grid gap-2 pl-7">
                    <label className="text-sm font-medium text-[var(--color-primary)]">Context Window</label>
                    <select 
                      value={contextWindow}
                      onChange={e => setContextWindow(e.target.value)}
                      className="max-w-xs px-3 py-2 bg-[#161618] border border-[var(--color-border)] rounded-md text-sm outline-none focus:border-[var(--color-accent)] focus:ring-1 focus:ring-[var(--color-accent)] text-[var(--color-primary)]"
                    >
                      <option>15 sec</option>
                      <option>30 sec</option>
                      <option>60 sec</option>
                      <option>90 sec</option>
                    </select>
                  </div>
                </div>
              </section>

              {/* Search Scope */}
              <section className="bg-[var(--color-surface)] border border-[var(--color-border)] rounded-lg">
                <div className="px-6 py-5 border-b border-[var(--color-border)]">
                  <h3 className="text-base font-semibold text-[var(--color-primary)]">Search Scope</h3>
                  <p className="text-sm text-[var(--color-secondary)] mt-1">Control which content is included when a search is performed.</p>
                </div>
                <div className="p-6 space-y-6">
                  <div className="flex items-start gap-3">
                    <input 
                      type="checkbox" 
                      id="include-all-episodes" 
                      checked={includeAllEpisodes}
                      onChange={e => setIncludeAllEpisodes(e.target.checked)}
                      className="mt-1 w-4 h-4 rounded bg-[#161618] border-[var(--color-border-subtle)] text-[var(--color-accent)] focus:ring-[var(--color-accent)]" 
                    />
                    <label htmlFor="include-all-episodes" className="text-sm font-medium text-[var(--color-primary)] cursor-pointer">Include All Episodes</label>
                  </div>
                  <div className="flex items-start gap-3">
                    <input 
                      type="checkbox" 
                      id="search-speakers" 
                      checked={searchSpeakers}
                      onChange={e => setSearchSpeakers(e.target.checked)}
                      className="mt-1 w-4 h-4 rounded bg-[#161618] border-[var(--color-border-subtle)] text-[var(--color-accent)] focus:ring-[var(--color-accent)]" 
                    />
                    <label htmlFor="search-speakers" className="text-sm font-medium text-[var(--color-primary)] cursor-pointer">Search Within Speakers</label>
                  </div>
                  <div className="flex items-start gap-3">
                    <input 
                      type="checkbox" 
                      id="search-topics" 
                      checked={searchTopics}
                      onChange={e => setSearchTopics(e.target.checked)}
                      className="mt-1 w-4 h-4 rounded bg-[#161618] border-[var(--color-border-subtle)] text-[var(--color-accent)] focus:ring-[var(--color-accent)]" 
                    />
                    <label htmlFor="search-topics" className="text-sm font-medium text-[var(--color-primary)] cursor-pointer">Search Within Topics</label>
                  </div>
                  <div className="flex items-start gap-3">
                    <input 
                      type="checkbox" 
                      id="search-projects" 
                      checked={searchProjects}
                      onChange={e => setSearchProjects(e.target.checked)}
                      className="mt-1 w-4 h-4 rounded bg-[#161618] border-[var(--color-border-subtle)] text-[var(--color-accent)] focus:ring-[var(--color-accent)]" 
                    />
                    <label htmlFor="search-projects" className="text-sm font-medium text-[var(--color-primary)] cursor-pointer">Search Within Projects</label>
                  </div>
                  <div className="grid gap-2 pt-2">
                    <label className="text-sm font-medium text-[var(--color-primary)]">Default Date Range</label>
                    <select 
                      value={defaultDateRange}
                      onChange={e => setDefaultDateRange(e.target.value)}
                      className="max-w-md px-3 py-2 bg-[#161618] border border-[var(--color-border)] rounded-md text-sm outline-none focus:border-[var(--color-accent)] focus:ring-1 focus:ring-[var(--color-accent)] text-[var(--color-primary)]"
                    >
                      <option>All time</option>
                      <option>Last 7 days</option>
                      <option>Last 30 days</option>
                      <option>Last 3 months</option>
                      <option>Last year</option>
                    </select>
                  </div>
                </div>
              </section>

              {/* Search Behavior */}
              <section className="bg-[var(--color-surface)] border border-[var(--color-border)] rounded-lg">
                <div className="px-6 py-5 border-b border-[var(--color-border)]">
                  <h3 className="text-base font-semibold text-[var(--color-primary)]">Search Behavior</h3>
                </div>
                <div className="p-6 space-y-6">
                  <div className="grid gap-2">
                    <label className="text-sm font-medium text-[var(--color-primary)]">Open result in:</label>
                    <select 
                      value={openResultIn}
                      onChange={e => setOpenResultIn(e.target.value)}
                      className="max-w-md px-3 py-2 bg-[#161618] border border-[var(--color-border)] rounded-md text-sm outline-none focus:border-[var(--color-accent)] focus:ring-1 focus:ring-[var(--color-accent)] text-[var(--color-primary)]"
                    >
                      <option>Transcript</option>
                      <option>Audio Player</option>
                      <option>Episode Detail</option>
                    </select>
                  </div>
                  <div className="flex items-start gap-3">
                    <input 
                      type="checkbox" 
                      id="auto-play" 
                      checked={autoPlay}
                      onChange={e => setAutoPlay(e.target.checked)}
                      className="mt-1 w-4 h-4 rounded bg-[#161618] border-[var(--color-border-subtle)] text-[var(--color-accent)] focus:ring-[var(--color-accent)]" 
                    />
                    <div>
                      <label htmlFor="auto-play" className="text-sm font-medium text-[var(--color-primary)] cursor-pointer">Auto-play when opening timestamp</label>
                      <p className="text-xs text-[var(--color-secondary)] mt-0.5">Automatically begin playback when navigating to a timestamp.</p>
                    </div>
                  </div>
                  <div className="flex items-start gap-3">
                    <input 
                      type="checkbox" 
                      id="preserve-filters" 
                      checked={preserveFilters}
                      onChange={e => setPreserveFilters(e.target.checked)}
                      className="mt-1 w-4 h-4 rounded bg-[#161618] border-[var(--color-border-subtle)] text-[var(--color-accent)] focus:ring-[var(--color-accent)]" 
                    />
                    <div>
                      <label htmlFor="preserve-filters" className="text-sm font-medium text-[var(--color-primary)] cursor-pointer">Preserve Search Filters</label>
                      <p className="text-xs text-[var(--color-secondary)] mt-0.5">Keep filters when navigating between search results and transcript views.</p>
                    </div>
                  </div>
                </div>
              </section>

              {/* Result Display */}
              <section className="bg-[var(--color-surface)] border border-[var(--color-border)] rounded-lg">
                <div className="px-6 py-5 border-b border-[var(--color-border)]">
                  <h3 className="text-base font-semibold text-[var(--color-primary)]">Result Display</h3>
                </div>
                <div className="p-6 space-y-6">
                  <div className="grid gap-2">
                    <label className="text-sm font-medium text-[var(--color-primary)]">Transcript Preview Length</label>
                    <select 
                      value={transcriptPreviewLength}
                      onChange={e => setTranscriptPreviewLength(e.target.value)}
                      className="max-w-xs px-3 py-2 bg-[#161618] border border-[var(--color-border)] rounded-md text-sm outline-none focus:border-[var(--color-accent)] focus:ring-1 focus:ring-[var(--color-accent)] text-[var(--color-primary)]"
                    >
                      <option>1 line</option>
                      <option>2 lines</option>
                      <option>3 lines</option>
                      <option>4 lines</option>
                    </select>
                  </div>
                  <div className="flex items-start gap-3">
                    <input 
                      type="checkbox" 
                      id="highlight-text" 
                      checked={highlightText}
                      onChange={e => setHighlightText(e.target.checked)}
                      className="mt-1 w-4 h-4 rounded bg-[#161618] border-[var(--color-border-subtle)] text-[var(--color-accent)] focus:ring-[var(--color-accent)]" 
                    />
                    <label htmlFor="highlight-text" className="text-sm font-medium text-[var(--color-primary)] cursor-pointer">Highlight Matching Text</label>
                  </div>
                  <div className="flex items-start gap-3">
                    <input 
                      type="checkbox" 
                      id="show-speaker" 
                      checked={showSpeaker}
                      onChange={e => setShowSpeaker(e.target.checked)}
                      className="mt-1 w-4 h-4 rounded bg-[#161618] border-[var(--color-border-subtle)] text-[var(--color-accent)] focus:ring-[var(--color-accent)]" 
                    />
                    <label htmlFor="show-speaker" className="text-sm font-medium text-[var(--color-primary)] cursor-pointer">Show Speaker Name</label>
                  </div>
                  <div className="flex items-start gap-3">
                    <input 
                      type="checkbox" 
                      id="show-timestamp" 
                      checked={showTimestamp}
                      onChange={e => setShowTimestamp(e.target.checked)}
                      className="mt-1 w-4 h-4 rounded bg-[#161618] border-[var(--color-border-subtle)] text-[var(--color-accent)] focus:ring-[var(--color-accent)]" 
                    />
                    <label htmlFor="show-timestamp" className="text-sm font-medium text-[var(--color-primary)] cursor-pointer">Show Timestamp</label>
                  </div>
                  <div className="flex items-start gap-3">
                    <input 
                      type="checkbox" 
                      id="show-episode-metadata" 
                      checked={showEpisodeMetadata}
                      onChange={e => setShowEpisodeMetadata(e.target.checked)}
                      className="mt-1 w-4 h-4 rounded bg-[#161618] border-[var(--color-border-subtle)] text-[var(--color-accent)] focus:ring-[var(--color-accent)]" 
                    />
                    <label htmlFor="show-episode-metadata" className="text-sm font-medium text-[var(--color-primary)] cursor-pointer">Show Episode Metadata</label>
                  </div>
                </div>
              </section>

              <div className="flex justify-end gap-3 pt-4">
                <Button variant="secondary" onClick={handleReset}>
                  Reset to Defaults
                </Button>
                <Button onClick={handleSave} disabled={saving}>
                  {saving ? "Saving..." : "Save Changes"}
                </Button>
              </div>
            </div>
          )}

          {activeTab === 'Account' && (
            <div className="space-y-8">
              <div className="mb-2">
                <h2 className="text-xl font-semibold text-[var(--color-primary)]">Account</h2>
                <p className="text-sm text-[var(--color-secondary)] mt-1">Manage your profile, account preferences, and notifications.</p>
              </div>

              {/* Profile */}
              <section className="bg-[var(--color-surface)] border border-[var(--color-border)] rounded-lg">
                <div className="px-6 py-5 border-b border-[var(--color-border)]">
                  <h3 className="text-base font-semibold text-[var(--color-primary)]">Profile</h3>
                  <p className="text-sm text-[var(--color-secondary)] mt-1">Your personal information used across Podcast Explorer.</p>
                </div>
                <div className="p-6 space-y-6">
                  <div className="flex items-center gap-4">
                    <div className="w-16 h-16 rounded-full bg-[var(--color-accent-subtle)] text-[var(--color-accent)] flex items-center justify-center text-xl font-medium">
                      {fullName ? fullName.charAt(0).toUpperCase() : 'U'}
                    </div>
                    <div>
                      <h4 className="text-sm font-medium text-[var(--color-primary)]">{fullName}</h4>
                      <p className="text-sm text-[var(--color-secondary)]">{email}</p>
                    </div>
                  </div>
                  
                  <div className="grid gap-4 max-w-md">
                    <div className="grid gap-2">
                      <label className="text-sm font-medium text-[var(--color-primary)]">Full Name</label>
                      <input 
                        type="text" 
                        value={fullName}
                        onChange={e => setFullName(e.target.value)}
                        className="w-full px-3 py-2 bg-[#161618] border border-[var(--color-border)] rounded-md text-sm outline-none focus:border-[var(--color-accent)] focus:ring-1 focus:ring-[var(--color-accent)] text-[var(--color-primary)]" 
                      />
                    </div>
                    <div className="grid gap-2">
                      <label className="text-sm font-medium text-[var(--color-primary)]">Email</label>
                      <input 
                        type="email" 
                        value={email} 
                        disabled 
                        className="w-full px-3 py-2 bg-[#161618] border border-[var(--color-border)] rounded-md text-sm text-[var(--color-secondary)] opacity-50 cursor-not-allowed outline-none" 
                      />
                    </div>
                    <div className="grid gap-2">
                      <label className="text-sm font-medium text-[var(--color-primary)]">Role</label>
                      <select 
                        value={role}
                        onChange={e => setRole(e.target.value)}
                        className="w-full px-3 py-2 bg-[#161618] border border-[var(--color-border)] rounded-md text-sm outline-none focus:border-[var(--color-accent)] focus:ring-1 focus:ring-[var(--color-accent)] text-[var(--color-primary)]"
                      >
                        <option>Developer</option>
                        <option>Researcher</option>
                        <option>Product Manager</option>
                        <option>Engineer</option>
                        <option>Other</option>
                      </select>
                    </div>
                  </div>
                  <div className="pt-2">
                    <Button onClick={handleSave} disabled={saving}>
                      {saving ? "Saving..." : "Save Profile"}
                    </Button>
                  </div>
                </div>
              </section>

              {/* Preferences */}
              <section className="bg-[var(--color-surface)] border border-[var(--color-border)] rounded-lg">
                <div className="px-6 py-5 border-b border-[var(--color-border)]">
                  <h3 className="text-base font-semibold text-[var(--color-primary)]">Preferences</h3>
                </div>
                <div className="p-6 space-y-6">
                  <div className="grid gap-4 max-w-md">
                    <div className="grid gap-2">
                      <label className="text-sm font-medium text-[var(--color-primary)]">Language</label>
                      <select 
                        value={accountLanguage}
                        onChange={e => setAccountLanguage(e.target.value)}
                        className="w-full px-3 py-2 bg-[#161618] border border-[var(--color-border)] rounded-md text-sm outline-none focus:border-[var(--color-accent)] focus:ring-1 focus:ring-[var(--color-accent)] text-[var(--color-primary)]"
                      >
                        <option>English</option>
                        <option>Hindi</option>
                        <option>Spanish</option>
                        <option>French</option>
                        <option>German</option>
                      </select>
                    </div>
                    <div className="grid gap-2">
                      <label className="text-sm font-medium text-[var(--color-primary)]">Time Zone</label>
                      <select 
                        value={timeZone}
                        onChange={e => setTimeZone(e.target.value)}
                        className="w-full px-3 py-2 bg-[#161618] border border-[var(--color-border)] rounded-md text-sm outline-none focus:border-[var(--color-accent)] focus:ring-1 focus:ring-[var(--color-accent)] text-[var(--color-primary)]"
                      >
                        <option>Asia/Kolkata (GMT+5:30)</option>
                        <option>America/New_York (GMT-4:00)</option>
                        <option>America/Los_Angeles (GMT-7:00)</option>
                        <option>Europe/London (GMT+1:00)</option>
                        <option>Europe/Paris (GMT+2:00)</option>
                      </select>
                    </div>
                    <div className="grid gap-2">
                      <label className="text-sm font-medium text-[var(--color-primary)]">Date Format</label>
                      <select 
                        value={dateFormat}
                        onChange={e => setDateFormat(e.target.value)}
                        className="w-full px-3 py-2 bg-[#161618] border border-[var(--color-border)] rounded-md text-sm outline-none focus:border-[var(--color-accent)] focus:ring-1 focus:ring-[var(--color-accent)] text-[var(--color-primary)]"
                      >
                        <option>MMM DD, YYYY</option>
                        <option>DD/MM/YYYY</option>
                        <option>MM/DD/YYYY</option>
                      </select>
                    </div>
                  </div>
                </div>
              </section>

              {/* Notifications */}
              <section className="bg-[var(--color-surface)] border border-[var(--color-border)] rounded-lg">
                <div className="px-6 py-5 border-b border-[var(--color-border)]">
                  <h3 className="text-base font-semibold text-[var(--color-primary)]">Notifications</h3>
                  <p className="text-sm text-[var(--color-secondary)] mt-1">Control which events trigger in-app notifications and emails.</p>
                </div>
                <div className="p-6 space-y-4">
                  <div className="flex items-start gap-3">
                    <input 
                      type="checkbox" 
                      id="notif-processed" 
                      checked={notifEpisodeProcessed}
                      onChange={e => setNotifEpisodeProcessed(e.target.checked)}
                      className="mt-1 w-4 h-4 rounded bg-[#161618] border-[var(--color-border-subtle)] text-[var(--color-accent)] focus:ring-[var(--color-accent)]" 
                    />
                    <div>
                      <label htmlFor="notif-processed" className="text-sm font-medium text-[var(--color-primary)] cursor-pointer">Episode Processed</label>
                      <p className="text-xs text-[var(--color-secondary)] mt-0.5">Notify when an uploaded audio file finishes processing and indexing.</p>
                    </div>
                  </div>
                  <div className="flex items-start gap-3">
                    <input 
                      type="checkbox" 
                      id="notif-search" 
                      checked={notifSearchResults}
                      onChange={e => setNotifSearchResults(e.target.checked)}
                      className="mt-1 w-4 h-4 rounded bg-[#161618] border-[var(--color-border-subtle)] text-[var(--color-accent)] focus:ring-[var(--color-accent)]" 
                    />
                    <div>
                      <label htmlFor="notif-search" className="text-sm font-medium text-[var(--color-primary)] cursor-pointer">Saved Search Results</label>
                      <p className="text-xs text-[var(--color-secondary)] mt-0.5">Notify when new episodes match your saved searches.</p>
                    </div>
                  </div>
                  <div className="flex items-start gap-3">
                    <input 
                      type="checkbox" 
                      id="notif-system" 
                      checked={notifSystemUpdates}
                      onChange={e => setNotifSystemUpdates(e.target.checked)}
                      className="mt-1 w-4 h-4 rounded bg-[#161618] border-[var(--color-border-subtle)] text-[var(--color-accent)] focus:ring-[var(--color-accent)]" 
                    />
                    <div>
                      <label htmlFor="notif-system" className="text-sm font-medium text-[var(--color-primary)] cursor-pointer">System Updates</label>
                      <p className="text-xs text-[var(--color-secondary)] mt-0.5">Product announcements and model updates.</p>
                    </div>
                  </div>
                  <div className="flex items-start gap-3 pt-2 border-t border-[var(--color-border-subtle)]">
                    <input 
                      type="checkbox" 
                      id="notif-email" 
                      checked={notifEmail}
                      onChange={e => setNotifEmail(e.target.checked)}
                      className="mt-1 w-4 h-4 rounded bg-[#161618] border-[var(--color-border-subtle)] text-[var(--color-accent)] focus:ring-[var(--color-accent)]" 
                    />
                    <div>
                      <label htmlFor="notif-email" className="text-sm font-medium text-[var(--color-primary)] cursor-pointer">Email Notifications</label>
                      <p className="text-xs text-[var(--color-secondary)] mt-0.5">Receive an email digest of important workspace notifications.</p>
                    </div>
                  </div>
                </div>
              </section>

              {/* Theme & Visuals */}
              <section className="bg-[var(--color-surface)] border border-[var(--color-border)] rounded-lg">
                <div className="px-6 py-5 border-b border-[var(--color-border)]">
                  <h3 className="text-base font-semibold text-[var(--color-primary)]">Theme</h3>
                </div>
                <div className="p-6 space-y-6">
                  <div className="grid gap-2 max-w-md">
                    <label className="text-sm font-medium text-[var(--color-primary)]">Theme Mode</label>
                    <select 
                      value={themeMode}
                      onChange={e => setThemeMode(e.target.value)}
                      className="w-full px-3 py-2 bg-[#161618] border border-[var(--color-border)] rounded-md text-sm outline-none focus:border-[var(--color-accent)] focus:ring-1 focus:ring-[var(--color-accent)] text-[var(--color-primary)]"
                    >
                      <option>Dark</option>
                      <option>Light (System Default)</option>
                    </select>
                  </div>
                  <div className="grid gap-2 max-w-md">
                    <label className="text-sm font-medium text-[var(--color-primary)]">Accent Color</label>
                    <select 
                      value={accentColor}
                      onChange={e => setAccentColor(e.target.value)}
                      className="w-full px-3 py-2 bg-[#161618] border border-[var(--color-border)] rounded-md text-sm outline-none focus:border-[var(--color-accent)] focus:ring-1 focus:ring-[var(--color-accent)] text-[var(--color-primary)]"
                    >
                      <option>Indigo</option>
                      <option>Emerald</option>
                      <option>Blue</option>
                      <option>Violet</option>
                    </select>
                  </div>
                </div>
              </section>

              {/* Danger Zone */}
              <section className="bg-[var(--color-surface)] border border-red-950/40 rounded-lg overflow-hidden">
                <div className="px-6 py-5 border-b border-red-950/40 bg-red-950/10">
                  <h3 className="text-base font-semibold text-red-400">Danger Zone</h3>
                  <p className="text-sm text-[var(--color-secondary)] mt-1">Irreversible and destructive actions.</p>
                </div>
                <div className="p-6 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
                  <div>
                    <h4 className="text-sm font-medium text-[var(--color-primary)]">Delete Account</h4>
                    <p className="text-xs text-[var(--color-secondary)] mt-1">Permanently remove your account and all associated workspace data.</p>
                  </div>
                  <Button variant="danger" className="bg-red-950/30 hover:bg-red-900/50 text-red-400 border border-red-900/50" onClick={() => setShowDeleteModal(true)}>
                    Delete Account
                  </Button>
                </div>
              </section>

              <div className="flex justify-end gap-3 pt-4">
                <Button variant="secondary" onClick={handleReset}>Reset to Defaults</Button>
                <Button onClick={handleSave} disabled={saving}>
                  {saving ? "Saving..." : "Save Changes"}
                </Button>
              </div>
            </div>
          )}

        </div>
      </div>
    </div>
  );
}
