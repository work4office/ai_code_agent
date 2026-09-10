import { api } from "./axios";
import type {
  ChatBody,
  ChatResponse,
  UserConfirmBody,
  UserConfirmResponse,
} from "../types/chat.types";
import type { AxiosResponse } from "axios";

class ChatService {
  urlPrefix = "chat/";

  user_ask = async (user_ask: string, project_id: string) => {
    const requestBody: ChatBody = {
      user_request: user_ask,
      project_id: project_id,
    };
    const response: AxiosResponse<ChatResponse> = await api.post(
      this.urlPrefix,
      requestBody,
    );
    return response;
  };

  user_confirm = async (is_confirmed: boolean, project_id: string) => {
    const requestBody: UserConfirmBody = {
      project_id: project_id,
      is_confirmed: is_confirmed,
    };
    const response: AxiosResponse<UserConfirmResponse> = await api.post(
      this.urlPrefix + "confirm",
      requestBody,
    );
    return response;
  };
}

export const chatService = new ChatService();
