import React, { useState } from "react";
import { DiffEditor } from "@monaco-editor/react";
import type { CodeChangesProps } from "../types/chat.types";
import { getLanguage } from "../utils/commonFunctions";

let MOCK_FILES: CodeChangesProps;

export const MultiFileDiffEditor: React.FC<CodeChangesProps> = (changes) => {
  MOCK_FILES = changes;
  // Track the currently active file ID
  const [activeFileId, setActiveFileId] = useState<number>(
    MOCK_FILES.changes[0].id,
  );

  // Find the details of the active file
  const activeFile =
    MOCK_FILES.changes.find((f) => f.id === activeFileId) ||
    MOCK_FILES.changes[0];

  return (
    <div className="flex h-full w-full bg-slate-50 text-slate-900 font-sans border border-[#ccc] shadow-sm ring-1 ring-inset ring-gray-300 p-1 rounded-xl gap-x-1">
      {/* Sidebar - File Navigator */}
      <aside className="w-64 border-r border-slate-200 bg-slate-white p-4 flex flex-col gap-2">
        <h2 className="text-xs font-semibold uppercase tracking-wider text-slate-500 mb-2">
          Changed Files
        </h2>
        <nav className="flex flex-col gap-1">
          {MOCK_FILES.changes.map((file) => {
            const isActive = file.id === activeFileId;
            return (
              <button
                key={file.id}
                onClick={() => setActiveFileId(file.id)}
                className={`flex items-center cursor-pointer justify-between w-full px-3 py-2 text-sm font-medium rounded-md transition-colors text-left ${
                  isActive
                    ? "bg-[#0d0e12] text-white"
                    : "text-[#0d0e12] hover:bg-slate-100 hover:text-slate-900"
                }`}
              >
                <span className="truncate" title={file.file_path}>
                  {file.file_path}
                </span>
                <span
                  className={`text-xs px-1.5 py-0.5 rounded font-mono ${
                    isActive
                      ? "bg-white text-[#0d0e12]"
                      : "bg-[#0d0e12] text-white"
                  }`}
                >
                  {getLanguage(file.file_path)}
                </span>
              </button>
            );
          })}
        </nav>
      </aside>

      {/* Main Diff Editor Panel */}
      <main className="flex-1 flex flex-col min-w-0 bg-white">
        {/* Top Header / Metadata Bar */}
        <header className="flex items-center justify-between px-6 py-3 border-b border-slate-200 bg-white">
          <div className="flex flex-col">
            <span className="text-sm font-semibold text-slate-900">
              {activeFile.file_path}
            </span>
            <span className="text-xs text-slate-500">
              Comparing old_code vs updated_code version
            </span>
          </div>
          <div className="flex gap-4 text-xs font-mono text-slate-500">
            <span className="flex items-center gap-1">
              <span className="w-2 h-2 rounded-full bg-red-500" /> Original
            </span>
            <span className="flex items-center gap-1">
              <span className="w-2 h-2 rounded-full bg-green-500" /> Modified
            </span>
          </div>
        </header>

        {/* Monaco Diff View Workspace Container */}
        <div className="flex-1 w-full bg-white p-2">
          <DiffEditor
            height="100%"
            language={getLanguage(activeFile.file_path)}
            original={activeFile.old_code}
            modified={activeFile.updated_code}
            theme="vs-light"
            keepCurrentOriginalModel={true}
            keepCurrentModifiedModel={true}
            options={{
              renderSideBySide: true, // Toggle false for inline unified view
              readOnly: true, // Allows edits to the updated_code pane
              originalEditable: false, // Keeps old_code layout frozen
              minimap: { enabled: false }, // Cleans up the panel edges
              fontSize: 14,
              automaticLayout: true, // Responsively handles canvas resizes
            }}
          />
        </div>
      </main>
    </div>
  );
};

export default MultiFileDiffEditor;
