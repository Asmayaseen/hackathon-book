/**
 * Root component wrapper for Docusaurus.
 *
 * This component wraps the entire application and provides
 * global components like the ChatWidget that should appear on all pages.
 *
 * Docusaurus automatically uses this file if it exists in src/theme/
 */

import React from 'react';
import { ChatWidget } from '../components/ChatWidget/ChatWidget';

// Root wrapper that adds ChatWidget to every page
export default function Root({ children }: { children: React.ReactNode }) {
  return (
    <>
      {/* Render the main Docusaurus content */}
      {children}

      {/* Add ChatWidget - appears on all pages */}
      <ChatWidget />
    </>
  );
}
