import React from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsList, TabsTrigger, TabsContent } from '@/components/ui/tabs';
import { Table, TableHeader, TableRow, TableHead, TableBody, TableCell } from '@/components/ui/table';
import { Modal } from '@/components/ui/modal';
import {
  Search, Play, Pause, FastForward, Rewind, MoreHorizontal, Link as LinkIcon, Check,
  Info, AlertCircle, CheckCircle2, ChevronRight, Activity, Clock, FileText, X
} from 'lucide-react';

export default function DesignSystemPage() {
  return (
    <div className="mx-auto w-[calc(100%-32px)] md:w-[calc(100%-48px)] lg:w-[calc(100%-64px)] max-w-6xl space-y-16 pb-24">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-semibold tracking-tight text-[var(--color-primary)]">Design System</h1>
        <p className="text-sm text-[var(--color-secondary)] mt-1">Core visual language and reusable interface components used across Podcast Explorer.</p>
        <div className="flex items-center gap-4 mt-6 text-xs text-[var(--color-secondary)] font-mono border-t border-[var(--color-border)] pt-4">
          <span>Version 1.0</span>
          <span className="text-[var(--color-border-subtle)]">|</span>
          <span>Last updated Aug 2026</span>
        </div>
      </div>
      
      {/* SECTION 1 - FOUNDATIONS */}
      <section className="space-y-10">
        <div className="border-b border-[var(--color-border)] pb-2">
          <h2 className="text-lg font-medium text-[var(--color-primary)]">Foundations</h2>
        </div>
        
        {/* Colors */}
        <div className="space-y-4">
          <h3 className="text-sm font-semibold text-[var(--color-primary)] uppercase tracking-wider">Colors</h3>
          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-4">
            <ColorSwatch name="Background" token="--color-background" hex="#09090b" usage="App background" />
            <ColorSwatch name="Surface" token="--color-surface" hex="#0c0c0e" usage="Cards, sidebars" />
            <ColorSwatch name="Border" token="--color-border" hex="#1d1d21" usage="Main dividers" />
            <ColorSwatch name="Border Subtle" token="--color-border-subtle" hex="#27272a" usage="Secondary dividers" />
            
            <ColorSwatch name="Primary Text" token="--color-primary" hex="#fafafa" usage="Headings, body" />
            <ColorSwatch name="Secondary Text" token="--color-secondary" hex="#a1a1aa" usage="Metadata, labels" />
            
            <ColorSwatch name="Accent" token="--color-accent" hex="#6366f1" usage="Primary actions" />
            <ColorSwatch name="Accent Hover" token="--color-accent-hover" hex="#818cf8" usage="Button hover" />
            
            <ColorSwatch name="Success" token="--color-success" hex="#22c55e" usage="Completed state" />
            <ColorSwatch name="Warning" token="--color-warning" hex="#f59e0b" usage="Pending state" />
            <ColorSwatch name="Error" token="--color-error" hex="#ef4444" usage="Failed state" />
          </div>
        </div>

        {/* Typography */}
        <div className="space-y-4">
          <h3 className="text-sm font-semibold text-[var(--color-primary)] uppercase tracking-wider">Typography</h3>
          <div className="space-y-6 bg-[var(--color-surface)] border border-[var(--color-border)] rounded-lg p-6">
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4 pb-4 border-b border-[var(--color-border-subtle)]">
              <div className="text-sm text-[var(--color-secondary)]">Page Title</div>
              <div className="md:col-span-3">
                <h1 className="text-2xl font-semibold tracking-tight text-[var(--color-primary)]">Scaling Distributed Systems Without Sacrificing Reliability</h1>
                <div className="text-xs text-[var(--color-secondary)] font-mono mt-2">24px / Semibold / -0.025em</div>
              </div>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4 pb-4 border-b border-[var(--color-border-subtle)]">
              <div className="text-sm text-[var(--color-secondary)]">Section Heading</div>
              <div className="md:col-span-3">
                <h2 className="text-lg font-medium text-[var(--color-primary)]">Processing Activity</h2>
                <div className="text-xs text-[var(--color-secondary)] font-mono mt-2">18px / Medium</div>
              </div>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4 pb-4 border-b border-[var(--color-border-subtle)]">
              <div className="text-sm text-[var(--color-secondary)]">Body</div>
              <div className="md:col-span-3">
                <p className="text-[15px] leading-relaxed text-[var(--color-primary)]">The database looked healthy from a CPU perspective, but the real bottleneck was connection saturation across the primary writer node during the initial migration window.</p>
                <div className="text-xs text-[var(--color-secondary)] font-mono mt-2">15px / Regular / 1.625</div>
              </div>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4 pb-4 border-b border-[var(--color-border-subtle)]">
              <div className="text-sm text-[var(--color-secondary)]">Secondary Text</div>
              <div className="md:col-span-3">
                <p className="text-sm text-[var(--color-secondary)]">Manage your workspace preferences and processing configuration.</p>
                <div className="text-xs text-[var(--color-secondary)] font-mono mt-2">14px / Regular</div>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-4 gap-4 pb-4 border-b border-[var(--color-border-subtle)]">
              <div className="text-sm text-[var(--color-secondary)]">Label</div>
              <div className="md:col-span-3">
                <span className="text-xs font-medium text-[var(--color-primary)] uppercase tracking-wider">Search Results</span>
                <div className="text-xs text-[var(--color-secondary)] font-mono mt-2">12px / Medium / Uppercase / Wider</div>
              </div>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div className="text-sm text-[var(--color-secondary)]">Monospace / Technical</div>
              <div className="md:col-span-3">
                <span className="text-xs font-mono text-[var(--color-secondary)] bg-[var(--color-background)] px-1 py-0.5 rounded border border-[var(--color-border-subtle)]">00:18:42</span>
                <div className="text-xs text-[var(--color-secondary)] font-mono mt-2">12px / JetBrains Mono</div>
              </div>
            </div>
          </div>
        </div>

        {/* Spacing & Border Radius */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          <div className="space-y-4">
            <h3 className="text-sm font-semibold text-[var(--color-primary)] uppercase tracking-wider">Spacing</h3>
            <div className="space-y-3 font-mono text-xs">
              {[4, 8, 12, 16, 24, 32, 48].map((space) => (
                <div key={space} className="flex items-center gap-4">
                  <div className="w-8 text-right text-[var(--color-secondary)]">{space}px</div>
                  <div className="h-4 bg-[var(--color-border-subtle)] rounded-sm" style={{ width: space }}></div>
                </div>
              ))}
            </div>
          </div>
          
          <div className="space-y-4">
            <h3 className="text-sm font-semibold text-[var(--color-primary)] uppercase tracking-wider">Border Radius</h3>
            <div className="space-y-4 text-sm">
              <div className="flex items-center gap-4">
                <div className="w-16 font-mono text-xs text-[var(--color-secondary)]">4px</div>
                <div className="w-12 h-12 bg-[var(--color-surface)] border border-[var(--color-border)] rounded-sm"></div>
                <div className="text-[var(--color-secondary)] text-xs">Checkboxes, small badges</div>
              </div>
              <div className="flex items-center gap-4">
                <div className="w-16 font-mono text-xs text-[var(--color-secondary)]">6px</div>
                <div className="w-12 h-12 bg-[var(--color-surface)] border border-[var(--color-border)] rounded-md"></div>
                <div className="text-[var(--color-secondary)] text-xs">Buttons, inputs, dropdowns</div>
              </div>
              <div className="flex items-center gap-4">
                <div className="w-16 font-mono text-xs text-[var(--color-secondary)]">8px</div>
                <div className="w-12 h-12 bg-[var(--color-surface)] border border-[var(--color-border)] rounded-lg"></div>
                <div className="text-[var(--color-secondary)] text-xs">Cards, transcript segments</div>
              </div>
              <div className="flex items-center gap-4">
                <div className="w-16 font-mono text-xs text-[var(--color-secondary)]">9999px</div>
                <div className="w-12 h-12 bg-[var(--color-surface)] border border-[var(--color-border)] rounded-full"></div>
                <div className="text-[var(--color-secondary)] text-xs">Avatars, circular icons</div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* SECTION 2 - COMPONENTS */}
      <section className="space-y-10">
        <div className="border-b border-[var(--color-border)] pb-2">
          <h2 className="text-lg font-medium text-[var(--color-primary)]">Components</h2>
        </div>
        
        {/* Buttons */}
        <div className="space-y-4">
          <h3 className="text-sm font-semibold text-[var(--color-primary)] uppercase tracking-wider">Buttons</h3>
          <div className="bg-[var(--color-surface)] border border-[var(--color-border)] rounded-lg p-6 overflow-x-auto">
            <table className="w-full text-left text-sm whitespace-nowrap">
              <thead>
                <tr className="text-[var(--color-secondary)] border-b border-[var(--color-border-subtle)]">
                  <th className="font-normal pb-3 w-1/4">Variant</th>
                  <th className="font-normal pb-3 w-1/4">Default</th>
                  <th className="font-normal pb-3 w-1/4">Disabled</th>
                  <th className="font-normal pb-3 w-1/4">Loading</th>
                </tr>
              </thead>
              <tbody>
                <tr className="border-b border-[var(--color-border-subtle)]">
                  <td className="py-4 text-[var(--color-secondary)]">Primary</td>
                  <td className="py-4"><Button>Upload Episode</Button></td>
                  <td className="py-4"><Button disabled>Upload Episode</Button></td>
                  <td className="py-4"><Button disabled className="opacity-70"><div className="w-4 h-4 mr-2 border-2 border-white/20 border-t-white rounded-full animate-spin"></div>Uploading...</Button></td>
                </tr>
                <tr className="border-b border-[var(--color-border-subtle)]">
                  <td className="py-4 text-[var(--color-secondary)]">Secondary</td>
                  <td className="py-4"><Button variant="secondary">Cancel</Button></td>
                  <td className="py-4"><Button variant="secondary" disabled>Cancel</Button></td>
                  <td className="py-4"><Button variant="secondary" disabled className="opacity-70"><div className="w-4 h-4 mr-2 border-2 border-[var(--color-primary)]/20 border-t-[var(--color-primary)] rounded-full animate-spin"></div>Processing</Button></td>
                </tr>
                <tr className="border-b border-[var(--color-border-subtle)]">
                  <td className="py-4 text-[var(--color-secondary)]">Outline</td>
                  <td className="py-4"><Button variant="outline">Search</Button></td>
                  <td className="py-4"><Button variant="outline" disabled>Search</Button></td>
                  <td className="py-4"><Button variant="outline" disabled className="opacity-70"><div className="w-4 h-4 mr-2 border-2 border-[var(--color-primary)]/20 border-t-[var(--color-primary)] rounded-full animate-spin"></div>Searching</Button></td>
                </tr>
                <tr className="border-b border-[var(--color-border-subtle)]">
                  <td className="py-4 text-[var(--color-secondary)]">Ghost</td>
                  <td className="py-4"><Button variant="ghost">Save Search</Button></td>
                  <td className="py-4"><Button variant="ghost" disabled>Save Search</Button></td>
                  <td className="py-4"><Button variant="ghost" disabled className="opacity-70"><div className="w-4 h-4 mr-2 border-2 border-[var(--color-primary)]/20 border-t-[var(--color-primary)] rounded-full animate-spin"></div>Saving</Button></td>
                </tr>
                <tr>
                  <td className="py-4 text-[var(--color-secondary)]">Icon</td>
                  <td className="py-4"><Button variant="secondary" size="icon"><Play className="w-4 h-4" /></Button></td>
                  <td className="py-4"><Button variant="secondary" size="icon" disabled><Play className="w-4 h-4" /></Button></td>
                  <td className="py-4"></td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        {/* Inputs */}
        <div className="space-y-4">
          <h3 className="text-sm font-semibold text-[var(--color-primary)] uppercase tracking-wider">Inputs</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 bg-[var(--color-surface)] border border-[var(--color-border)] rounded-lg p-6">
            <div className="space-y-2">
              <label className="text-xs font-medium text-[var(--color-primary)]">Text Input</label>
              <Input placeholder="Enter project name..." />
            </div>
            <div className="space-y-2">
              <label className="text-xs font-medium text-[var(--color-primary)]">Search Input</label>
              <Input icon={<Search className="w-4 h-4" />} placeholder="Search transcripts..." />
            </div>
            <div className="space-y-2">
              <label className="text-xs font-medium text-[var(--color-primary)]">Disabled</label>
              <Input disabled placeholder="Cannot edit this field" value="System generated ID" />
            </div>
            <div className="space-y-2">
              <label className="text-xs font-medium text-[var(--color-primary)]">Select / Dropdown</label>
              <select className="flex h-9 w-full rounded-md border border-[var(--color-border)] bg-[var(--color-background)] px-3 py-1 text-sm text-[var(--color-primary)] shadow-sm transition-colors focus-visible:outline-none focus-visible:border-[var(--color-accent)] focus-visible:ring-1 focus-visible:ring-[var(--color-accent)] disabled:cursor-not-allowed disabled:opacity-50">
                <option>Filter by speaker</option>
                <option>Priya Shah</option>
                <option>Alex Morgan</option>
              </select>
            </div>
          </div>
        </div>

        {/* Badges */}
        <div className="space-y-4">
          <h3 className="text-sm font-semibold text-[var(--color-primary)] uppercase tracking-wider">Badges / Status</h3>
          <div className="flex flex-wrap gap-4 bg-[var(--color-surface)] border border-[var(--color-border)] rounded-lg p-6">
            <Badge variant="default">Indexed</Badge>
            <Badge variant="secondary">Draft</Badge>
            <Badge variant="outline">Saved</Badge>
            
            <div className="flex items-center gap-1.5 px-2 py-0.5 rounded-md border border-[var(--color-warning-bg)] bg-[var(--color-warning-bg)]/20 text-[var(--color-warning)] text-xs font-medium">
              <div className="w-1.5 h-1.5 rounded-full bg-[var(--color-warning)] animate-pulse"></div>
              Processing
            </div>
            
            <div className="flex items-center gap-1.5 px-2 py-0.5 rounded-md border border-[var(--color-error-bg)] bg-[var(--color-error-bg)]/20 text-[var(--color-error)] text-xs font-medium">
              <div className="w-1.5 h-1.5 rounded-full bg-[var(--color-error)]"></div>
              Failed
            </div>
          </div>
        </div>

        {/* Tabs */}
        <div className="space-y-4">
          <h3 className="text-sm font-semibold text-[var(--color-primary)] uppercase tracking-wider">Tabs</h3>
          <div className="bg-[var(--color-surface)] border border-[var(--color-border)] rounded-lg p-6">
            <Tabs defaultValue="overview">
              <TabsList>
                <TabsTrigger value="overview">Overview</TabsTrigger>
                <TabsTrigger value="transcript">Transcript</TabsTrigger>
                <TabsTrigger value="speakers">Speakers</TabsTrigger>
                <TabsTrigger value="search">Search</TabsTrigger>
              </TabsList>
            </Tabs>
          </div>
        </div>

        {/* Table */}
        <div className="space-y-4">
          <h3 className="text-sm font-semibold text-[var(--color-primary)] uppercase tracking-wider">Table</h3>
          <div className="bg-[var(--color-surface)] border border-[var(--color-border)] rounded-lg overflow-hidden">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Episode</TableHead>
                  <TableHead>Duration</TableHead>
                  <TableHead>Speakers</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead className="text-right">Added</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                <TableRow className="bg-[#161618]">
                  <TableCell className="font-medium">Scaling Distributed Systems...</TableCell>
                  <TableCell className="font-mono text-xs text-[var(--color-secondary)]">45:22</TableCell>
                  <TableCell>
                    <div className="flex -space-x-2">
                      <div className="w-6 h-6 rounded-full bg-emerald-900 border border-[var(--color-surface)] flex items-center justify-center text-[10px] font-bold text-emerald-400">PS</div>
                      <div className="w-6 h-6 rounded-full bg-indigo-900 border border-[var(--color-surface)] flex items-center justify-center text-[10px] font-bold text-indigo-400">AM</div>
                    </div>
                  </TableCell>
                  <TableCell><Badge>Indexed</Badge></TableCell>
                  <TableCell className="text-right text-[var(--color-secondary)]">2 hours ago</TableCell>
                </TableRow>
                <TableRow>
                  <TableCell className="font-medium">React Server Components</TableCell>
                  <TableCell className="font-mono text-xs text-[var(--color-secondary)]">1:12:05</TableCell>
                  <TableCell>
                    <div className="flex -space-x-2">
                      <div className="w-6 h-6 rounded-full bg-[var(--color-border-subtle)] border border-[var(--color-surface)] flex items-center justify-center text-[10px] font-bold text-[var(--color-secondary)]">DC</div>
                    </div>
                  </TableCell>
                  <TableCell>
                    <div className="flex items-center gap-1.5 px-2 py-0.5 rounded-md border border-[var(--color-warning-bg)] bg-[var(--color-warning-bg)]/20 text-[var(--color-warning)] text-xs font-medium inline-flex">
                      <div className="w-1.5 h-1.5 rounded-full bg-[var(--color-warning)] animate-pulse"></div>
                      Processing
                    </div>
                  </TableCell>
                  <TableCell className="text-right text-[var(--color-secondary)]">5 hours ago</TableCell>
                </TableRow>
              </TableBody>
            </Table>
          </div>
        </div>
      </section>

      {/* SECTION 3 - PRODUCT COMPONENTS */}
      <section className="space-y-10">
        <div className="border-b border-[var(--color-border)] pb-2">
          <h2 className="text-lg font-medium text-[var(--color-primary)]">Product Components</h2>
        </div>
        
        {/* Transcript Segment */}
        <div className="space-y-4">
          <h3 className="text-sm font-semibold text-[var(--color-primary)] uppercase tracking-wider">Transcript Segment</h3>
          <div className="bg-[var(--color-background)] border border-[var(--color-border)] rounded-lg p-6 space-y-4">
            
            {/* Active State */}
            <div className="group relative flex flex-col sm:flex-row gap-3 sm:gap-6 p-4 md:px-6 md:py-5 rounded-lg transition-all border bg-[#161618] border-[var(--color-border)]">
              <div className="sm:w-20 shrink-0 pt-0.5 flex items-center sm:items-start justify-between sm:justify-start">
                <button className="font-mono text-sm transition-all flex items-center gap-2 text-[var(--color-accent)] font-semibold">
                  <span className="flex items-center justify-center w-6 h-6 rounded-full transition-colors bg-[var(--color-accent-subtle)]">
                    <Play className="w-3 h-3 fill-current" />
                  </span>
                  <span>00:18:42</span>
                </button>
              </div>
              <div className="flex-1 space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-sm font-semibold text-emerald-400">Priya Shah</span>
                  <div className="hidden sm:flex opacity-100 transition-opacity">
                    <Button variant="ghost" size="sm" className="h-7 px-2 text-xs gap-1.5 text-[var(--color-secondary)] hover:text-[var(--color-primary)]">
                      <LinkIcon className="w-3.5 h-3.5" /> Copy Link
                    </Button>
                  </div>
                </div>
                <p className="text-[15px] leading-relaxed transition-colors text-[var(--color-primary)]">
                  The database looked healthy from a CPU perspective, but the real bottleneck was connection saturation across the primary writer node during the initial migration window.
                </p>
              </div>
            </div>

            {/* Inactive State */}
            <div className="group relative flex flex-col sm:flex-row gap-3 sm:gap-6 p-4 md:px-6 md:py-5 rounded-lg transition-all border border-transparent hover:bg-[#161618]/50">
              <div className="sm:w-20 shrink-0 pt-0.5 flex items-center sm:items-start justify-between sm:justify-start">
                <button className="font-mono text-sm transition-all flex items-center gap-2 text-[var(--color-secondary)] group-hover:text-[var(--color-primary)]">
                  <span className="flex items-center justify-center w-6 h-6 rounded-full transition-colors group-hover:bg-[var(--color-surface)] group-hover:border group-hover:border-[var(--color-border)]">
                    <span className="group-hover:hidden">00:18:55</span>
                    <Play className="w-3 h-3 fill-current hidden group-hover:block" />
                  </span>
                </button>
              </div>
              <div className="flex-1 space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-sm font-semibold text-indigo-400">Alex Morgan</span>
                  <div className="hidden sm:flex opacity-0 group-hover:opacity-100 transition-opacity">
                    <Button variant="ghost" size="sm" className="h-7 px-2 text-xs gap-1.5 text-[var(--color-secondary)] hover:text-[var(--color-primary)]">
                      <LinkIcon className="w-3.5 h-3.5" /> Copy Link
                    </Button>
                  </div>
                </div>
                <p className="text-[15px] leading-relaxed transition-colors text-[var(--color-secondary)] group-hover:text-gray-300">
                  Exactly. And once we implemented PgBouncer with a strict connection pooling limit, we saw a massive drop in latency spikes during peak load.
                </p>
              </div>
            </div>

          </div>
        </div>

        {/* Audio Player */}
        <div className="space-y-4">
          <h3 className="text-sm font-semibold text-[var(--color-primary)] uppercase tracking-wider">Audio Player</h3>
          <div className="bg-[var(--color-background)] border border-[var(--color-border)] rounded-lg p-6">
            <div className="flex flex-col gap-4 bg-[var(--color-surface)] border border-[var(--color-border)] rounded-lg p-4">
              <div className="flex items-center gap-4">
                <div className="flex items-center gap-2">
                  <Button variant="secondary" size="icon" className="w-8 h-8 rounded-full">
                    <Rewind className="w-4 h-4" />
                  </Button>
                  <Button size="icon" className="w-10 h-10 rounded-full bg-[var(--color-primary)] hover:bg-white text-black">
                    <Pause className="w-4 h-4 fill-current" />
                  </Button>
                  <Button variant="secondary" size="icon" className="w-8 h-8 rounded-full">
                    <FastForward className="w-4 h-4" />
                  </Button>
                </div>
                <div className="text-xs font-mono text-[var(--color-secondary)]">00:18:42 / 45:22</div>
                <div className="flex-1 flex items-center group cursor-pointer relative h-2">
                  <div className="absolute inset-0 bg-[#161618] rounded-full overflow-hidden border border-[var(--color-border-subtle)]">
                    <div className="h-full bg-[var(--color-accent)] rounded-full w-[40%] relative">
                      <div className="absolute right-0 top-1/2 -translate-y-1/2 w-2 h-2 bg-white rounded-full shadow blur-[1px]"></div>
                    </div>
                  </div>
                </div>
                <div className="hidden sm:flex items-center gap-2">
                  <button className="text-xs font-mono bg-[var(--color-background)] border border-[var(--color-border-subtle)] px-2 py-1 rounded text-[var(--color-secondary)] hover:text-[var(--color-primary)] transition-colors">
                    1.2x
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Search Result */}
        <div className="space-y-4">
          <h3 className="text-sm font-semibold text-[var(--color-primary)] uppercase tracking-wider">Search Result</h3>
          <div className="bg-[var(--color-background)] border border-[var(--color-border)] rounded-lg p-6">
            <div className="group bg-[var(--color-surface)] border border-[var(--color-border)] rounded-lg p-5 transition-all hover:border-[var(--color-border-subtle)] hover:shadow-md cursor-pointer flex flex-col sm:flex-row gap-5">
              <div className="flex-1 space-y-3">
                <div className="flex items-start justify-between">
                  <div>
                    <h3 className="text-base font-medium text-[var(--color-primary)] group-hover:text-[var(--color-accent)] transition-colors">Scaling Distributed Systems</h3>
                    <div className="flex items-center gap-3 mt-1 text-xs text-[var(--color-secondary)]">
                      <span className="font-medium text-[var(--color-primary)]">Engineering Podcast</span>
                      <span>Oct 12, 2023</span>
                    </div>
                  </div>
                  <Badge variant="secondary" className="bg-[var(--color-accent-subtle)] text-[var(--color-accent)] hover:bg-[var(--color-accent-subtle)] border-transparent">95% Match</Badge>
                </div>
                
                <div className="bg-[var(--color-background)] border border-[var(--color-border-subtle)] rounded-md p-4 space-y-2">
                  <div className="flex items-center gap-2">
                    <span className="text-[10px] font-bold text-[var(--color-secondary)] uppercase tracking-wider">Priya Shah</span>
                    <span className="text-xs font-mono text-[var(--color-secondary)]">@ 18:42</span>
                  </div>
                  <p className="text-sm text-[var(--color-primary)] leading-relaxed italic border-l-2 border-[var(--color-accent)] pl-3">
                    &quot;...the real bottleneck wasquot;...the real bottleneck was <span className="bg-[var(--color-accent-subtle)] text-[var(--color-accent)] font-medium px-1 rounded">connection saturation</span> across the primary writer node during the initial migration window.&quot;
                  </p>
                </div>
              </div>
              <div className="flex sm:flex-col gap-2 shrink-0">
                <Button variant="secondary" size="sm" className="flex-1 sm:flex-none justify-start">
                  <Play className="w-4 h-4 mr-2" /> Play Match
                </Button>
                <Button variant="outline" size="sm" className="flex-1 sm:flex-none justify-start">
                  <LinkIcon className="w-4 h-4 mr-2" /> Open Episode
                </Button>
              </div>
            </div>
          </div>
        </div>
        
        {/* Modal / Drawer */}
        <div className="space-y-4">
          <h3 className="text-sm font-semibold text-[var(--color-primary)] uppercase tracking-wider">Modal Example</h3>
          <div className="bg-[var(--color-background)] border border-[var(--color-border)] rounded-lg p-6 relative overflow-hidden h-96 flex items-center justify-center">
             <div className="absolute inset-0 bg-black/60 flex items-center justify-center p-4">
                <div className="bg-[var(--color-surface)] w-full max-w-sm rounded-lg shadow-lg overflow-hidden border border-[var(--color-border)] flex flex-col">
                  <div className="px-6 py-4 border-b border-[var(--color-border)] flex flex-col gap-1 bg-[#161618]">
                    <div className="flex items-center justify-between">
                      <h2 className="text-lg font-semibold text-[var(--color-primary)]">Episode Insight</h2>
                      <button className="p-1.5 -mr-1.5 text-[var(--color-secondary)] hover:text-[var(--color-primary)] rounded-md transition-colors ml-auto">
                        <X className="w-4 h-4" />
                      </button>
                    </div>
                    <p className="text-sm text-[var(--color-secondary)]">View detailed episode statistics.</p>
                  </div>
                  <div className="p-6 text-sm text-[var(--color-primary)]">
                    <p className="leading-relaxed">This episode has a higher than average word density and discusses technical topics heavily. The primary speakers are Alex Morgan and Priya Shah.</p>
                  </div>
                  <div className="px-6 py-4 border-t border-[var(--color-border)] bg-[#161618] flex items-center justify-end gap-2">
                    <Button variant="secondary">Close</Button>
                  </div>
                </div>
             </div>
          </div>
        </div>

      </section>

      {/* SECTION 4 - STATES */}
      <section className="space-y-10">
        <div className="border-b border-[var(--color-border)] pb-2">
          <h2 className="text-lg font-medium text-[var(--color-primary)]">States</h2>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Empty State */}
          <div className="bg-[var(--color-surface)] border border-[var(--color-border)] rounded-lg p-8 flex flex-col items-center justify-center text-center">
            <div className="w-12 h-12 bg-[#161618] rounded-full flex items-center justify-center border border-[var(--color-border-subtle)] mb-4">
              <Search className="w-5 h-5 text-[var(--color-secondary)]" />
            </div>
            <h3 className="text-base font-medium text-[var(--color-primary)]">No episodes found</h3>
            <p className="text-sm text-[var(--color-secondary)] mt-1 max-w-[250px]">
              Upload an episode to begin building your searchable library.
            </p>
            <Button className="mt-6" variant="outline">Clear Filters</Button>
          </div>
          
          {/* Error State */}
          <div className="bg-[var(--color-surface)] border border-[var(--color-error-bg)] rounded-lg p-8 flex flex-col items-center justify-center text-center">
            <div className="w-12 h-12 bg-[var(--color-error-bg)] rounded-full flex items-center justify-center border border-[var(--color-error)]/20 mb-4">
              <AlertCircle className="w-5 h-5 text-[var(--color-error)]" />
            </div>
            <h3 className="text-base font-medium text-[var(--color-error)]">Unable to process episode</h3>
            <p className="text-sm text-[var(--color-secondary)] mt-1 max-w-[250px]">
              Something went wrong while generating the transcript. Check the processing logs for details.
            </p>
            <Button className="mt-6" variant="secondary">View Logs</Button>
          </div>
          
          {/* Loading State */}
          <div className="bg-[var(--color-surface)] border border-[var(--color-border)] rounded-lg p-8 flex flex-col items-center justify-center text-center">
             <div className="w-12 h-12 border-2 border-[var(--color-border)] border-t-[var(--color-accent)] rounded-full animate-spin mb-4"></div>
             <h3 className="text-base font-medium text-[var(--color-primary)]">Indexing episode...</h3>
             <p className="text-sm text-[var(--color-secondary)] mt-1 max-w-[250px]">
               Generating transcript and semantic embeddings.
             </p>
          </div>
          
          {/* Success State */}
          <div className="bg-[var(--color-surface)] border border-[var(--color-success-bg)] rounded-lg p-8 flex flex-col items-center justify-center text-center">
            <div className="w-12 h-12 bg-[var(--color-success-bg)] rounded-full flex items-center justify-center border border-[var(--color-success)]/20 mb-4">
              <CheckCircle2 className="w-5 h-5 text-[var(--color-success)]" />
            </div>
            <h3 className="text-base font-medium text-[var(--color-success)]">Processing Complete</h3>
            <p className="text-sm text-[var(--color-secondary)] mt-1 max-w-[250px]">
              Episode has been fully indexed and is now searchable.
            </p>
            <Button className="mt-6" variant="secondary">View Episode</Button>
          </div>
        </div>
      </section>
      
      {/* SECTION 5 - ICONOGRAPHY */}
      <section className="space-y-6">
        <div className="border-b border-[var(--color-border)] pb-2">
          <h2 className="text-lg font-medium text-[var(--color-primary)]">Iconography</h2>
        </div>
        <div className="bg-[var(--color-surface)] border border-[var(--color-border)] rounded-lg p-6">
          <p className="text-sm text-[var(--color-secondary)] mb-6">Podcast Explorer uses <span className="font-medium text-[var(--color-primary)]">Lucide React</span> exclusively for icons. Avoid mixing icon sets.</p>
          
          <div className="grid grid-cols-1 sm:grid-cols-4 gap-6">
            <div className="space-y-3">
              <div className="flex items-end gap-3 text-[var(--color-secondary)]">
                <Clock className="w-3.5 h-3.5" />
                <span className="text-xs font-mono">14px (w-3.5)</span>
              </div>
              <p className="text-xs text-[var(--color-secondary)] leading-relaxed">Used for inline metadata, labels, and inside small badges.</p>
            </div>
            <div className="space-y-3">
              <div className="flex items-end gap-3 text-[var(--color-primary)]">
                <Search className="w-4 h-4" />
                <span className="text-xs font-mono text-[var(--color-secondary)]">16px (w-4)</span>
              </div>
              <p className="text-xs text-[var(--color-secondary)] leading-relaxed">Standard size for buttons, inputs, and secondary actions.</p>
            </div>
            <div className="space-y-3">
              <div className="flex items-end gap-3 text-[var(--color-primary)]">
                <Activity className="w-[18px] h-[18px]" />
                <span className="text-xs font-mono text-[var(--color-secondary)]">18px</span>
              </div>
              <p className="text-xs text-[var(--color-secondary)] leading-relaxed">Used in primary sidebar navigation items.</p>
            </div>
            <div className="space-y-3">
              <div className="flex items-end gap-3 text-[var(--color-primary)]">
                <Play className="w-5 h-5" />
                <span className="text-xs font-mono text-[var(--color-secondary)]">20px (w-5)</span>
              </div>
              <p className="text-xs text-[var(--color-secondary)] leading-relaxed">Reserved for prominent actions like main audio playback controls.</p>
            </div>
          </div>
        </div>
      </section>

      {/* SECTION 6 - INTERACTION RULES */}
      <section className="space-y-6">
        <div className="border-b border-[var(--color-border)] pb-2">
          <h2 className="text-lg font-medium text-[var(--color-primary)]">Interaction Rules</h2>
        </div>
        <div className="bg-[var(--color-surface)] border border-[var(--color-border)] rounded-lg divide-y divide-[var(--color-border-subtle)]">
          <InteractionRule 
            state="Hover" 
            desc="Slightly lighten backgrounds or borders. Increase text contrast (e.g., secondary to primary)." 
            classNames="hover:bg-[var(--color-border-subtle)] hover:text-[var(--color-primary)]" 
          />
          <InteractionRule 
            state="Focus" 
            desc="Use outline-none and provide a distinct ring using the accent color for accessibility." 
            classNames="focus:outline-none focus:ring-1 focus:ring-[var(--color-accent)] focus:border-[var(--color-accent)]" 
          />
          <InteractionRule 
            state="Active" 
            desc="Use subtle accent background with accent colored text for selected navigation items or tabs." 
            classNames="bg-[var(--color-accent-subtle)] text-[var(--color-accent)]" 
          />
          <InteractionRule 
            state="Disabled" 
            desc="Reduce opacity to 50% (opacity-50). Change cursor to not-allowed. Prevent hover effects." 
            classNames="disabled:opacity-50 disabled:cursor-not-allowed" 
          />
        </div>
      </section>
      
    </div>
  );
}

// Helpers
function ColorSwatch({ name, token, hex, usage }: { name: string, token: string, hex: string, usage: string }) {
  return (
    <div className="flex flex-col gap-2">
      <div 
        className="h-16 w-full rounded-md border border-[var(--color-border)] shadow-sm"
        style={{ backgroundColor: `var(${token})` }}
      />
      <div>
        <div className="text-sm font-medium text-[var(--color-primary)]">{name}</div>
        <div className="text-xs font-mono text-[var(--color-secondary)] mt-0.5">{token}</div>
        <div className="text-xs font-mono text-[var(--color-secondary)] mt-0.5">{hex}</div>
        <div className="text-xs text-[var(--color-secondary)] mt-1">{usage}</div>
      </div>
    </div>
  );
}

function InteractionRule({ state, desc, classNames }: { state: string, desc: string, classNames: string }) {
  return (
    <div className="p-4 sm:p-6 flex flex-col sm:flex-row sm:items-center gap-4">
      <div className="sm:w-32 shrink-0">
        <span className="text-sm font-medium text-[var(--color-primary)]">{state}</span>
      </div>
      <div className="flex-1 text-sm text-[var(--color-secondary)] leading-relaxed">
        {desc}
      </div>
      <div className="sm:w-1/3 shrink-0">
        <div className="text-xs font-mono bg-[#161618] text-[var(--color-secondary)] p-2 rounded border border-[var(--color-border-subtle)] break-all">
          {classNames}
        </div>
      </div>
    </div>
  );
}
