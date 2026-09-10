import type { Dispatch, SetStateAction } from "react";
import type {
  FileContentsList,
  ProjectFileTreeMap,
  ProjectsResponse,
} from "./repository.types";

export interface CommonContextType {
  fileExplorer: ProjectFileTreeMap[] | undefined;
  setFileExplorer: Dispatch<SetStateAction<ProjectFileTreeMap[] | undefined>>;
  activeProject: string;
  setActiveProject: Dispatch<SetStateAction<string>>;
  resetContext: () => void;
  projects: ProjectsResponse[];
  setProjects: Dispatch<SetStateAction<ProjectsResponse[]>>;
  fileContents: FileContentsList[];
  setFileContents: Dispatch<SetStateAction<FileContentsList[]>>;
  activeFilePath: string;
  setActiveFilePath: Dispatch<SetStateAction<string>>;
}

export interface SidebarProps {
  isOpen: boolean;
  toggleSidebar?: () => void;
}

export type ToastType = "success" | "error" | "warning" | "info";

export interface Toast {
  id: string;
  type: ToastType;
  message: string;
  duration?: number; // Time in ms before auto-closing
}
