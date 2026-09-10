import { api } from "./axios";
import type { AxiosResponse } from "axios";
import type {
  CreateUserRequest,
  CreateUserResponse,
} from "../types/auth.types";

class UserService {
  urlPrefix = "user/";

  create_user = async (requestBody: CreateUserRequest) => {
    const response: AxiosResponse<CreateUserResponse> = await api.post(
      this.urlPrefix,
      requestBody,
    );
    return response;
  };
}

export const userService = new UserService();
