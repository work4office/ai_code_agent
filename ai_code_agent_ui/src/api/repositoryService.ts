import type { AxiosResponse } from "axios";
import type {
  FileContentResponse,
  FileTreeResponse,
  ProjectsResponse,
  RepositoryResponse,
  RepositoryTypes,
} from "../types/repository.types";
import { api } from "./axios";

class RepositoryService {
  urlPrefix = "repositories/";

  ingest_repo = async (repo_url: string) => {
    const requestBody: RepositoryTypes = { repo_url: repo_url };
    const response: RepositoryResponse = await api.post(
      this.urlPrefix,
      requestBody,
    );
    return response;
  };

  get_file_tree = async (project_id: string) => {
    const response: AxiosResponse<FileTreeResponse[]> = await api.get(
      this.urlPrefix + project_id + "/tree",
    );
    return response;
  };

  get_file_content = async (project_id: string, path: string) => {
    const response: AxiosResponse<FileContentResponse> = await api.get(
      this.urlPrefix + project_id + "/file",
      {
        params: {
          path: path,
        },
      },
    );
    return response;
  };

  get_projects = async () => {
    const response: AxiosResponse<ProjectsResponse[]> = await api.get(
      this.urlPrefix + "projects",
    );
    return response;
  };
}

export const repositoryService = new RepositoryService();
