'use client';

import React from 'react';
import Link from 'next/link';
import { Button } from '@/components/ui/button';

export default function NotFound() {
  return (
    <div className="flex flex-col items-center justify-center min-h-[60vh] space-y-4 text-center px-4">
      <h2 className="text-2xl font-bold text-[var(--color-primary)]">Page Not Found</h2>
      <p className="text-sm text-[var(--color-secondary)] max-w-md">
        The podcast episode, search query, or configuration you are looking for could not be found.
      </p>
      <Link href="/episodes">
        <Button variant="outline">Return to Episodes</Button>
      </Link>
    </div>
  );
}
