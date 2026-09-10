import React, { useState } from "react";
import type {
  FileExplorerProps,
  FileNodeProps,
} from "../types/repository.types";
import { ChevronDown, ChevronRight, Folder, File } from "lucide-react";
import useApi from "../hooks/useApi";
import { useCommonContext } from "../context/CommonContext";
import { EllipsisChecker } from "../utils/EllipsisChecker";

const FileNode: React.FC<FileNodeProps> = ({ node }) => {
  const [isOpen, setIsOpen] = useState<boolean>(false);
  const { get_file_content } = useApi();
  const { setActiveFilePath, activeFilePath } = useCommonContext();
  const isFolder = node.type === "folder";

  const toggleExpand = (e: React.MouseEvent<HTMLDivElement>) => {
    if (isFolder) {
      setIsOpen(!isOpen);
    } else {
      e.stopPropagation();
      openFile(node.path);
    }
  };

  const openFile = async (path: string) => {
    setActiveFilePath(path);
    await get_file_content(path);
  };

  return (
    <div className="select-none font-sans text-[13px] text-[#cccccc]">
      {/* Node Row */}
      <div
        onClick={(e) => toggleExpand(e)}
        className={`cursor-pointer flex items-center py-0.5 px-2 w-full group transition-colors duration-150 hover:bg-[#0d0e12]/90 focus:bg-[#0d0e12] text-[#0d0e12] rounded-md ${node.path === activeFilePath ? "bg-[#0d0e12]/90 text-white" : ""}`}
      >
        {/* Expand/Collapse Arrow */}
        <span className="w-4 h-4 flex items-center justify-center mr-1 text-[#0d0e12] group-hover:text-white">
          {isFolder ? (
            isOpen ? (
              <ChevronDown size={14} />
            ) : (
              <ChevronRight size={14} />
            )
          ) : null}
        </span>

        {/* File/Folder Icon */}
        <span
          className={`mr-2 flex items-center ${isFolder ? "text-[#e8a838]" : "text-[#858585]"}`}
        >
          {isFolder ? (
            <Folder
              size={16}
              fill={isOpen ? "#e8a838" : "none"}
              className="opacity-90"
            />
          ) : (
            <File size={16} />
          )}
        </span>

        {/* Name */}
        <span className="truncate group-hover:text-white">
          <EllipsisChecker>{node.name}</EllipsisChecker>
        </span>
      </div>

      {/* Render Children Recursively with VS Code Indentation Lines */}
      {isFolder && isOpen && node.children && (
        <div className="ml-3.5 pl-2 border-l border-[#333333] hover:border-[#444444] transition-colors">
          {node.children.map((child) => (
            <FileNode key={child.path} node={child} />
          ))}
        </div>
      )}
    </div>
  );
};

export const FileExplorer: React.FC<FileExplorerProps> = ({ data }) => {
  return (
    <div className="overflow-y-auto h-full p-1">
      {data.map((rootNode) => (
        <FileNode key={rootNode.path} node={rootNode} />
      ))}
    </div>
  );
};

export default FileExplorer;
