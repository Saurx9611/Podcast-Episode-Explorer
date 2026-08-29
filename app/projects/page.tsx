'use client';

import React, { useState, useEffect } from 'react';
import { Plus, FolderGit2, Library, Clock, MoreHorizontal, Sparkles } from 'lucide-react';
import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { getProjects, createProject, Project } from '@/lib/api/projects';
import { Modal } from '@/components/ui/modal';
import { Input } from '@/components/ui/input';

const FALLBACK_PROJECTS: Project[] = [
  {
    id: 'proj-1',
    user_id: 'default-user',
    name: 'Engineering Podcasts',
    description: 'Deep dives into system design, architecture, and scaling distributed applications.',
    created_at: '',
    updated_at: '',
  },
  {
    id: 'proj-2',
    user_id: 'default-user',
    name: 'AI Research',
    description: 'Latest research papers, LLM advancements, and AI agent architectures.',
    created_at: '',
    updated_at: '',
  },
  {
    id: 'proj-3',
    user_id: 'default-user',
    name: 'Founder Interviews',
    description: 'Conversations with technical startup founders on growth and architecture decisions.',
    created_at: '',
    updated_at: '',
  },
  {
    id: 'proj-4',
    user_id: 'default-user',
    name: 'System Design',
    description: 'In-depth case studies on distributed databases and event streaming.',
    created_at: '',
    updated_at: '',
  }
];

export default function ProjectsPage() {
  const [projects, setProjects] = useState<Project[]>(FALLBACK_PROJECTS);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [newProjectName, setNewProjectName] = useState('');
  const [newProjectDesc, setNewProjectDesc] = useState('');

  const loadProjects = async () => {
    try {
      const data = await getProjects();
      if (data && data.length > 0) {
        setProjects(data);
      }
    } catch {
      // Keep fallback
    }
  };

  useEffect(() => {
    loadProjects();
  }, []);

  const handleCreateProject = async () => {
    if (!newProjectName.trim()) return;
    try {
      const created = await createProject({
        name: newProjectName.trim(),
        description: newProjectDesc.trim() || undefined,
      });
      setProjects(prev => [created, ...prev]);
      setIsModalOpen(false);
      setNewProjectName('');
      setNewProjectDesc('');
    } catch (err: any) {
      alert(err.message || 'Failed to create project.');
    }
  };

  return (
    <div className="space-y-8 max-w-6xl mx-auto pb-16">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div className="space-y-1">
          <h1 className="text-2xl font-semibold tracking-tight text-[var(--color-primary)]">Project Workspaces</h1>
          <p className="text-xs sm:text-sm text-[var(--color-secondary)]">Group audio collections and partition vector search indexes.</p>
        </div>
        <Button onClick={() => setIsModalOpen(true)} variant="accent" className="gap-2 h-8 text-xs">
          <Plus className="w-3.5 h-3.5" />
          New Project
        </Button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {projects.map((project, idx) => (
          <div 
            key={project.id || idx} 
            className="bg-[var(--color-surface)] border border-[var(--color-border)] hover:border-[var(--color-border-subtle)] rounded-lg p-5 transition-all duration-150 group flex flex-col justify-between space-y-4"
          >
            <div className="space-y-3">
              <div className="flex justify-between items-start">
                <div className="p-2 bg-[var(--color-surface-elevated)] rounded-md text-[var(--color-accent)] border border-[var(--color-border)]">
                  <FolderGit2 className="w-4 h-4" />
                </div>
                <Badge variant="secondary" className="font-mono text-[10px]">Active</Badge>
              </div>
              
              <div>
                <h2 className="text-sm font-semibold text-[var(--color-primary)] group-hover:text-[var(--color-accent)] transition-colors">
                  {project.name}
                </h2>
                <p className="text-xs text-[var(--color-secondary)] mt-1 line-clamp-2 leading-relaxed">
                  {project.description || 'No description provided.'}
                </p>
              </div>
            </div>

            <div className="flex items-center justify-between pt-3 border-t border-[var(--color-border)] text-xs font-mono text-[var(--color-muted)]">
              <div className="flex items-center gap-1.5">
                <Library className="w-3.5 h-3.5" />
                <span>Indexed Collection</span>
              </div>
              <Link href={`/episodes?project=${project.id}`} className="text-[var(--color-accent)] hover:underline text-[11px]">
                Browse →
              </Link>
            </div>
          </div>
        ))}
      </div>

      <Modal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        title="Create New Project"
        description="Organize your episodes and vector search scope."
      >
        <div className="space-y-3.5 pt-2">
          <div className="space-y-1">
            <label className="text-xs font-medium text-[var(--color-muted)]">Project Name</label>
            <Input 
              placeholder="e.g. Distributed Systems Masterclass" 
              value={newProjectName}
              onChange={(e) => setNewProjectName(e.target.value)}
              className="h-8 text-xs"
            />
          </div>
          <div className="space-y-1">
            <label className="text-xs font-medium text-[var(--color-muted)]">Description</label>
            <Input 
              placeholder="e.g. In-depth audio series on distributed storage..." 
              value={newProjectDesc}
              onChange={(e) => setNewProjectDesc(e.target.value)}
              className="h-8 text-xs"
            />
          </div>
          <div className="flex justify-end gap-2 pt-3 border-t border-[var(--color-border)]">
            <Button variant="outline" size="sm" onClick={() => setIsModalOpen(false)}>Cancel</Button>
            <Button variant="accent" size="sm" onClick={handleCreateProject} disabled={!newProjectName.trim()}>
              Create Project
            </Button>
          </div>
        </div>
      </Modal>
    </div>
  );
}
