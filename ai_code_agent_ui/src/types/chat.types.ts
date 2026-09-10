export interface CodeChanges {
  id: number;
  old_code: string;
  updated_code: string;
  file_path: string;
}

export interface ChatResponse {
  changes: CodeChanges[];
  message: string;
}

export interface ChatBody {
  user_request: string;
  project_id: string;
}

export interface UserConfirmBody {
  project_id: string;
  is_confirmed: boolean;
}

export interface CodeChangesProps {
  changes: CodeChanges[];
}

export interface UserConfirmResponse {
  status: string;
  approved: boolean;
  applied_files: string[];
}
