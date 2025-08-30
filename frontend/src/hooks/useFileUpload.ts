import { useCallback, useState } from '@lynx-js/react';
import type { UploadedFile } from '@/types/chat';
import {
  formatFileSize,
  getFileIcon,
  validateFile,
} from '@/utils/file-validation';

export const useFileUpload = () => {
  const [files, setFiles] = useState<UploadedFile[]>([]);
  const [isUploading, setIsUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const addFiles = useCallback(async (fileList: FileList) => {
    setError(null);
    setIsUploading(true);

    try {
      const newFiles: UploadedFile[] = [];
      const filesToValidate = Array.from(fileList);

      // Check total size of all files including existing ones
      const existingFileSizes = files
        .map((f) => f.size)
        .reduce((sum, size) => sum + size, 0);
      const newFileSizes = filesToValidate
        .map((f) => f.size)
        .reduce((sum, size) => sum + size, 0);

      if (existingFileSizes + newFileSizes > 10 * 1024 * 1024) {
        setError('Total file size exceeds 10MB limit');
        return;
      }

      for (let i = 0; i < fileList.length; i++) {
        const file = fileList[i];
        const validation = validateFile(file);

        if (!validation.isValid) {
          setError(validation.error || 'File validation failed');
          continue;
        }

        const reader = new FileReader();
        const data = await new Promise<string | ArrayBuffer>(
          (resolve, reject) => {
            reader.onload = () => resolve(reader.result!);
            reader.onerror = () => reject(reader.error);

            if (file.type.startsWith('image/')) {
              reader.readAsDataURL(file);
            } else {
              reader.readAsText(file);
            }
          },
        );

        const uploadedFile: UploadedFile = {
          id: `${Date.now()}-${i}`,
          name: file.name,
          size: file.size,
          type: file.type,
          data: file, // Keep the original File object for FormData sending
          content: data, // Store the processed content separately
        };

        newFiles.push(uploadedFile);
      }

      setFiles((prev) => [...prev, ...newFiles]);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to upload files');
    } finally {
      setIsUploading(false);
    }
  }, [files]);

  const removeFile = useCallback((fileId: string) => {
    setFiles((prev) => prev.filter((file) => file.id !== fileId));
    setError(null);
  }, []);

  const clearFiles = useCallback(() => {
    setFiles([]);
    setError(null);
  }, []);

  const getFileInfo = useCallback(
    (file: UploadedFile) => ({
      icon: getFileIcon(file.type),
      sizeText: formatFileSize(file.size),
    }),
    [],
  );

  return {
    files,
    isUploading,
    error,
    addFiles,
    removeFile,
    clearFiles,
    getFileInfo,
  };
};
