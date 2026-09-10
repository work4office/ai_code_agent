export interface RepositoryTypes {
  repo_url: string;
}

export interface RepositoryResponse {
  message: string;
  commit_hash: string;
}

export interface FileTreeResponse {
  name: string;
  path: string;
  type: string; // file | folder
  children: FileTreeResponse[];
}

export interface ProjectFileTreeMap {
  [projectId: string]: FileTreeResponse[];
}

export interface FileNodeProps {
  node: FileTreeResponse;
}

export interface FileExplorerProps {
  data: FileTreeResponse[];
}

export interface FileContentResponse {
  path: string;
  content: string;
}

export interface FileContentsList {
  [path: string]: string;
}

export interface ProjectsResponse {
  project_id: string;
  repo_name: string;
}
