import React, {
  useState,
  useRef,
  type ChangeEvent,
  type DragEvent,
} from "react";
import type { FileUploadProps } from "../types/fileUpload.types";

export const FileUpload: React.FC<FileUploadProps> = ({
  maxSizeMB = 5,
  allowedTypes = ["image/jpeg", "image/png", "application/pdf"],
  onFilesSelected,
}) => {
  const [isDragActive, setIsDragActive] = useState<boolean>(false);
  const [files, setFiles] = useState<File[]>([]);
  const [error, setError] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Validate file size and type
  const validateFiles = (fileList: FileList): File[] => {
    const validFiles: File[] = [];
    setError(null);

    for (let i = 0; i < fileList.length; i++) {
      const file = fileList[i];

      if (!allowedTypes.includes(file.type)) {
        setError(`Unsupported file type: ${file.name}`);
        continue;
      }

      if (file.size > maxSizeMB * 1024 * 1024) {
        setError(`File too large (Max ${maxSizeMB}MB): ${file.name}`);
        continue;
      }

      validFiles.push(file);
    }

    return validFiles;
  };

  const handleFileChange = (e: ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      const newFiles = validateFiles(e.target.files);
      const updatedFiles = [...files, ...newFiles];
      setFiles(updatedFiles);
      onFilesSelected(updatedFiles);
    }
  };

  const handleDrag = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setIsDragActive(true);
    } else if (e.type === "dragleave") {
      setIsDragActive(false);
    }
  };

  const handleDrop = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragActive(false);

    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      const newFiles = validateFiles(e.dataTransfer.files);
      const updatedFiles = [...files, ...newFiles];
      setFiles(updatedFiles);
      onFilesSelected(updatedFiles);
    }
  };

  const removeFile = (indexToRemove: number) => {
    const updatedFiles = files.filter((_, idx) => idx !== indexToRemove);
    setFiles(updatedFiles);
    onFilesSelected(updatedFiles);
  };

  return (
    <div className="w-full max-w-md mx-auto p-6 bg-white rounded-xl shadow-md border border-slate-100">
      {/* Drop Zone */}
      <div
        onDragEnter={handleDrag}
        onDragOver={handleDrag}
        onDragLeave={handleDrag}
        onDrop={handleDrop}
        onClick={() => fileInputRef.current?.click()}
        className={`flex flex-col items-center justify-center border-2 border-dashed rounded-lg p-6 cursor-pointer transition-colors ${
          isDragActive
            ? "border-blue-500 bg-blue-50/50"
            : "border-slate-300 hover:border-slate-400 bg-slate-50"
        }`}
      >
        <input
          ref={fileInputRef}
          type="file"
          multiple
          className="hidden"
          onChange={handleFileChange}
          accept={allowedTypes.join(",")}
        />

        {/* Cloud Upload Icon */}
        <svg
          className="w-10 h-10 mb-3 text-slate-400"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
          xmlns="http://w3.org"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth="2"
            path="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"
          ></path>
        </svg>

        <p className="mb-2 text-sm text-slate-600">
          Upload
        </p>
        {/* <p className="text-xs text-slate-400">
          PNG, JPG, or PDF up to {maxSizeMB}MB
        </p> */}
      </div>

      {/* Error Message */}
      {error && (
        <div className="mt-3 text-sm text-red-500 font-medium bg-red-50 p-2 rounded border border-red-200">
          {error}
        </div>
      )}

      {/* Selected File List */}
      {files.length > 0 && (
        <div className="mt-4">
          <p className="text-sm font-medium text-slate-700 mb-2">
            Selected Files:
          </p>
          <ul className="space-y-2">
            {files.map((file, idx) => (
              <li
                key={`${file.name}-${idx}`}
                className="flex items-center justify-between text-sm bg-slate-50 p-2 rounded-md border border-slate-200"
              >
                <span className="truncate max-w-[70%] text-slate-600 font-medium">
                  {file.name}
                </span>
                <div className="flex items-center space-x-3">
                  <span className="text-xs text-slate-400">
                    {(file.size / (1024 * 1024)).toFixed(2)} MB
                  </span>
                  <button
                    type="button"
                    onClick={(e) => {
                      e.stopPropagation();
                      removeFile(idx);
                    }}
                    className="text-slate-400 hover:text-red-500 transition-colors"
                  >
                    <svg
                      className="w-4 h-4"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth="2"
                        d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
                      />
                    </svg>
                  </button>
                </div>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
};
