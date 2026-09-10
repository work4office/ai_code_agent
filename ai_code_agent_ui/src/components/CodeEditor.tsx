import React, { useEffect } from "react";
import { X } from "lucide-react";
import { Editor } from "@monaco-editor/react";
import { FileExplorer } from "../pages/FileExplorer";
import { useCommonContext } from "../context/CommonContext";
import { getLanguage } from "../utils/commonFunctions";
import { useNavigate } from "react-router-dom";
import AIChatBot from "../pages/AIChatBot";

export default function CodeEditor() {
  const navigate = useNavigate();
  const { fileExplorer, activeProject, fileContents, activeFilePath, setActiveFilePath } =
    useCommonContext();

  const project = fileExplorer?.find((item) => item[activeProject])?.[
    activeProject
  ];
  const activeFileContents = fileContents?.find(
    (item) => item[activeFilePath],
  )?.[activeFilePath];

  useEffect(() => {
    if (project) {
      return;
    }
    navigate("/");
  }, [project]);

  return (
    <div className="flex h-[500px] border border-[#ccc] shadow-sm ring-1 ring-inset ring-gray-300 p-4 rounded-xl gap-x-1">
      {project && (
        <div className="flex flex-col shadow-sm ring-1 ring-inset ring-gray-300 rounded-xl">
          <div className="pl-4 border-b border-gray-300 text-sm font-normal md:font-bold text-[#0d0e12]">
            Explorer
          </div>
          <FileExplorer data={project} />
        </div>
      )}
      <div className="flex flex-row w-full gap-x-1">
        {activeFileContents && (
          <div className="flex flex-col w-full min-w-[625px] border border-[#ccc] shadow-sm ring-inset ring-gray-300 rounded-xl">
            <div className="pl-7 pr-4 border-b border-gray-300 text-sm font-normal md:font-bold text-[#0d0e12] flex items-center justify-between">
              <span>{activeFilePath}</span>
              <button
                onClick={() => {
                  setActiveFilePath("");
                }}
                className="cursor-pointer p-1 rounded-md hover:bg-gray-100 text-gray-500 hover:text-gray-700 transition-colors"
                aria-label="Close file"
              >
                <X size={16} />
              </button>
            </div>
            <Editor
              path={activeFilePath}
              value={activeFileContents}
              language={getLanguage(activeFilePath)}
              height={"100%"}
            />
          </div>
        )}
        <AIChatBot />
      </div>
    </div>
  );
}
