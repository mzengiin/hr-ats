/**
 * Tests for FileUpload component
 */
import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import FileUpload from '../components/FileUpload';

// Mock the API service
jest.mock('../services/api', () => ({
  post: jest.fn(),
  get: jest.fn(),
  delete: jest.fn(),
}));

// Mock the AuthContext
const mockAuthContext = {
  user: { id: 'test-user-id', email: 'test@example.com' },
  isAuthenticated: true,
  loading: false,
};

jest.mock('../contexts/AuthContext', () => ({
  useAuth: () => mockAuthContext,
}));

describe('FileUpload Component', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('renders file upload interface', () => {
    render(<FileUpload />);
    
    expect(screen.getByText(/CV Dosyalarını Yükle/i)).toBeInTheDocument();
    expect(screen.getByText(/Dosyaları buraya sürükleyin/i)).toBeInTheDocument();
    expect(screen.getByText(/veya dosya seçmek için tıklayın/i)).toBeInTheDocument();
  });

  test('shows supported file types', () => {
    render(<FileUpload />);
    
    expect(screen.getByText(/Desteklenen formatlar: PDF, DOC, DOCX/i)).toBeInTheDocument();
    expect(screen.getByText(/Maksimum dosya boyutu: 10MB/i)).toBeInTheDocument();
  });

  test('handles file selection', async () => {
    render(<FileUpload />);
    
    const fileInput = screen.getByLabelText(/file input/i);
    const file = new File(['test content'], 'test.pdf', { type: 'application/pdf' });
    
    fireEvent.change(fileInput, { target: { files: [file] } });
    
    await waitFor(() => {
      expect(screen.getByText('test.pdf')).toBeInTheDocument();
    });
  });

  test('validates file type', async () => {
    render(<FileUpload />);
    
    const fileInput = screen.getByLabelText(/file input/i);
    const invalidFile = new File(['test content'], 'test.txt', { type: 'text/plain' });
    
    fireEvent.change(fileInput, { target: { files: [invalidFile] } });
    
    await waitFor(() => {
      expect(screen.getByText(/unsupported file type/i)).toBeInTheDocument();
    });
  });

  test('validates file size', async () => {
    render(<FileUpload />);
    
    const fileInput = screen.getByLabelText(/file input/i);
    // Create a large file (11MB)
    const largeFile = new File(['x'.repeat(11 * 1024 * 1024)], 'large.pdf', { type: 'application/pdf' });
    
    fireEvent.change(fileInput, { target: { files: [largeFile] } });
    
    await waitFor(() => {
      expect(screen.getByText(/file too large/i)).toBeInTheDocument();
    });
  });

  test('shows upload progress', async () => {
    const mockApi = require('../services/api');
    mockApi.post.mockResolvedValue({
      data: {
        message: 'Files uploaded successfully',
        uploaded_files: [{ id: '1', original_filename: 'test.pdf' }]
      }
    });

    render(<FileUpload />);
    
    const fileInput = screen.getByLabelText(/file input/i);
    const file = new File(['test content'], 'test.pdf', { type: 'application/pdf' });
    
    fireEvent.change(fileInput, { target: { files: [file] } });
    
    // Click upload button
    const uploadButton = screen.getByText(/upload 1 file/i);
    fireEvent.click(uploadButton);
    
    await waitFor(() => {
      expect(screen.getByText(/uploading/i)).toBeInTheDocument();
    });
  });

  test('handles upload success', async () => {
    const mockApi = require('../services/api');
    mockApi.post.mockResolvedValue({
      data: {
        message: 'Files uploaded successfully',
        uploaded_files: [{ 
          id: '1', 
          original_filename: 'test.pdf',
          file_size: 1024,
          mime_type: 'application/pdf'
        }]
      }
    });

    render(<FileUpload />);
    
    const fileInput = screen.getByLabelText(/file input/i);
    const file = new File(['test content'], 'test.pdf', { type: 'application/pdf' });
    
    fireEvent.change(fileInput, { target: { files: [file] } });
    
    const uploadButton = screen.getByText(/upload 1 file/i);
    fireEvent.click(uploadButton);
    
    await waitFor(() => {
      // After successful upload, files should be cleared and upload button should be disabled
      expect(screen.queryByText('test.pdf')).not.toBeInTheDocument();
    });
  });

  test('handles upload error', async () => {
    const mockApi = require('../services/api');
    mockApi.post.mockRejectedValue({
      response: {
        data: { detail: 'Upload failed' }
      }
    });

    render(<FileUpload />);
    
    const fileInput = screen.getByLabelText(/file input/i);
    const file = new File(['test content'], 'test.pdf', { type: 'application/pdf' });
    
    fireEvent.change(fileInput, { target: { files: [file] } });
    
    const uploadButton = screen.getByText(/upload 1 file/i);
    fireEvent.click(uploadButton);
    
    await waitFor(() => {
      expect(screen.getByText(/upload failed/i)).toBeInTheDocument();
    });
  });

  test('handles drag and drop', () => {
    render(<FileUpload />);
    
    const dropZone = screen.getByText(/Dosyaları buraya sürükleyin/i);
    
    const file = new File(['test content'], 'test.pdf', { type: 'application/pdf' });
    
    fireEvent.dragOver(dropZone);
    fireEvent.drop(dropZone, { dataTransfer: { files: [file] } });
    
    expect(screen.getByText('test.pdf')).toBeInTheDocument();
  });

  test('removes file from list', async () => {
    render(<FileUpload />);
    
    const fileInput = screen.getByLabelText(/file input/i);
    const file = new File(['test content'], 'test.pdf', { type: 'application/pdf' });
    
    fireEvent.change(fileInput, { target: { files: [file] } });
    
    await waitFor(() => {
      expect(screen.getByText('test.pdf')).toBeInTheDocument();
    });
    
    const removeButton = screen.getByText(/remove/i);
    fireEvent.click(removeButton);
    
    expect(screen.queryByText('test.pdf')).not.toBeInTheDocument();
  });
});
