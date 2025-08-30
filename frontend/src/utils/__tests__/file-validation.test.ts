import { describe, expect, it } from 'vitest';
import { formatFileSize, getFileIcon, validateFile } from '../file-validation';

describe('file-validation', () => {
  describe('validateFile', () => {
    it('validates file size within limit', () => {
      const file = new File(['test'], 'test.txt', { type: 'text/plain' });
      const result = validateFile(file);

      expect(result.isValid).toBe(true);
      expect(result.error).toBeUndefined();
    });

    it('rejects file exceeding size limit', () => {
      const largeContent = new Array(11 * 1024 * 1024).fill('a').join('');
      const file = new File([largeContent], 'large.txt', {
        type: 'text/plain',
      });
      const result = validateFile(file);

      expect(result.isValid).toBe(false);
      expect(result.error).toContain('File size exceeds');
    });

    it('validates allowed file types', () => {
      const file = new File(['test'], 'test.txt', { type: 'text/plain' });
      const result = validateFile(file);

      expect(result.isValid).toBe(true);
    });

    it('rejects disallowed file types', () => {
      const file = new File(['test'], 'test.exe', {
        type: 'application/x-executable',
      });
      const result = validateFile(file);

      expect(result.isValid).toBe(false);
      expect(result.error).toContain('File type not supported');
    });
  });

  describe('formatFileSize', () => {
    it('formats bytes correctly', () => {
      expect(formatFileSize(0)).toBe('0 B');
      expect(formatFileSize(500)).toBe('500 B');
      expect(formatFileSize(1024)).toBe('1.0 KB');
      expect(formatFileSize(1536)).toBe('1.5 KB');
      expect(formatFileSize(1024 * 1024)).toBe('1.0 MB');
      expect(formatFileSize(1024 * 1024 * 1024)).toBe('1.0 GB');
    });
  });

  describe('getFileIcon', () => {
    it('returns correct icons for different file types', () => {
      expect(getFileIcon('image/jpeg')).toBe('🖼️');
      expect(getFileIcon('image/png')).toBe('🖼️');
      expect(getFileIcon('application/pdf')).toBe('📄');
      expect(getFileIcon('application/msword')).toBe('📝');
      expect(getFileIcon('text/csv')).toBe('📊');
      expect(getFileIcon('application/json')).toBe('🔧');
      expect(getFileIcon('text/plain')).toBe('📎');
      expect(getFileIcon('unknown/type')).toBe('📎');
    });
  });
});
