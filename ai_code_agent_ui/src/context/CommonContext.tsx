import React, { createContext, useContext, useState } from "react";
import type { CommonContextType } from "../types/common.types";
import type {
  FileContentsList,
  ProjectFileTreeMap,
  ProjectsResponse,
} from "../types/repository.types";

const CommonContext = createContext<CommonContextType | undefined>(undefined);

export const CommonProvider: React.FC<{ children: React.ReactNode }> = ({
  children,
}) => {
  const [fileExplorer, setFileExplorer] = useState<ProjectFileTreeMap[]>();
  const [projects, setProjects] = useState<ProjectsResponse[]>([]);
  const [fileContents, setFileContents] = useState<FileContentsList[]>([]);
  const [activeProject, setActiveProject] = useState("");
  const [activeFilePath, setActiveFilePath] = useState("");

  const resetContext = () => {
    setActiveProject("");
    setFileExplorer([]);
    setProjects([]);
  };

  return (
    <CommonContext.Provider
      value={{
        fileExplorer,
        setFileExplorer,
        activeProject,
        setActiveProject,
        resetContext,
        projects,
        setProjects,
        fileContents,
        setFileContents,
        activeFilePath,
        setActiveFilePath,
      }}
    >
      {children}
    </CommonContext.Provider>
  );
};

export const useCommonContext = () => {
  const context = useContext(CommonContext);
  if (context === undefined) {
    throw new Error("useCommonContext must be used within a CommonProvider");
  }
  return context;
};
