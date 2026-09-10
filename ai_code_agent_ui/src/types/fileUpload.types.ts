export interface FileUploadProps {
    maxSizeMB?: number;
    allowedTypes?: string[];
    onFilesSelected: (files: File[]) => void;
}