import type { AxiosResponse } from "axios";
import type {
  FileContentResponse,
  FileTreeResponse,
  ProjectFileTreeMap,
  ProjectsResponse,
} from "../types/repository.types";
import { repositoryService } from "../api/repositoryService";
import { useCommonContext } from "../context/CommonContext";
import type { ChatResponse, UserConfirmResponse } from "../types/chat.types";
import { chatService } from "../api/chatService";
import { useAuth } from "../context/AuthContext";
import type {
  CreateUserRequest,
  CreateUserResponse,
} from "../types/auth.types";
import { userService } from "../api/userService";

const useApi = () => {
  const { user } = useAuth();
  const {
    activeProject,
    projects,
    setProjects,
    fileExplorer,
    setFileExplorer,
    fileContents,
    setFileContents,
  } = useCommonContext();

  const chat = async (user_ask: string, project_id: string) => {
    if (!user) return;
    const response: AxiosResponse<ChatResponse> = await chatService.user_ask(
      user_ask,
      project_id,
    );
    return response.data;
  };

  const confirm_changes = async (is_confirmed: boolean, project_id: string) => {
    if (!user) return;
    const response: AxiosResponse<UserConfirmResponse> =
      await chatService.user_confirm(is_confirmed, project_id);
    return response.data;
  };

  const get_all_projects = async () => {
    if (!user || projects?.length > 0) {
      return;
    }
    const response: AxiosResponse<ProjectsResponse[]> =
      await repositoryService.get_projects();
    setProjects(response.data);
  };

  const get_file_tree = async (
    projectId: string,
    reloadRequired: boolean = false,
  ) => {
    if (
      (!user || fileExplorer?.some((obj) => projectId in obj)) &&
      !reloadRequired
    ) {
      return;
    }
    const response: AxiosResponse<FileTreeResponse[]> =
      await repositoryService.get_file_tree(projectId);
    const newFileTree: Record<string, any> = {};
    newFileTree[projectId] = response.data;
    const newExplorer = fileExplorer
      ? fileExplorer?.map((item) => {
          if (Object.keys(item)[0].toString() === projectId.toString()) {
            item[projectId] = response.data;
          }
          return item;
        })
      : ([newFileTree] as ProjectFileTreeMap[]);
    setFileExplorer(newExplorer);
  };

  const get_file_content = async (path: string) => {
    if (
      !user ||
      fileContents?.some((obj) => path in obj) ||
      activeProject === ""
    ) {
      return;
    }
    const response: AxiosResponse<FileContentResponse> =
      await repositoryService.get_file_content(activeProject, path);
    const newFileContent: Record<string, any> = {};
    newFileContent[response.data.path] = response.data.content;
    setFileContents((prevArray) => [...(prevArray || []), newFileContent]);
  };

  const create_user = async (requestBody: CreateUserRequest) => {
    const response: AxiosResponse<CreateUserResponse> =
      await userService.create_user(requestBody);
    return response;
  };

  return {
    get_all_projects,
    get_file_tree,
    get_file_content,
    chat,
    confirm_changes,
    create_user,
  };
};

export default useApi;
