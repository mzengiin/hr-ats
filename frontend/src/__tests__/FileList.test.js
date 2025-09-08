/**
 * Tests for FileList component
 */
import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import FileList from '../components/FileList';

// Mock the API service
jest.mock('../services/api', () => ({
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

const mockFiles = [
  {
    id: '1',
    original_filename: 'test1.pdf',
    file_size: 1024000,
    mime_type: 'application/pdf',
    upload_date: '2025-09-05T10:00:00Z'
  },
  {
    id: '2',
    original_filename: 'test2.docx',
    file_size: 2048000,
    mime_type: 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    upload_date: '2025-09-05T11:00:00Z'
  }
];

describe('FileList Component', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('renders file list', () => {
    render(<FileList files={mockFiles} />);
    
    expect(screen.getByText('test1.pdf')).toBeInTheDocument();
    expect(screen.getByText('test2.docx')).toBeInTheDocument();
  });

  test('shows file information', () => {
    render(<FileList files={mockFiles} />);
    
    expect(screen.getByText('1000 KB')).toBeInTheDocument();
    expect(screen.getByText('2 MB')).toBeInTheDocument();
    expect(screen.getByText('PDF')).toBeInTheDocument();
    expect(screen.getByText('DOCX')).toBeInTheDocument();
  });

  test('handles file download', async () => {
    const mockApi = require('../services/api');
    mockApi.get.mockResolvedValue({
      data: new Blob(['test content'], { type: 'application/pdf' })
    });

    // Mock URL.createObjectURL
    global.URL.createObjectURL = jest.fn(() => 'mock-url');
    global.URL.revokeObjectURL = jest.fn();

    render(<FileList files={mockFiles} />);
    
    const downloadButtons = screen.getAllByText(/download/i);
    fireEvent.click(downloadButtons[0]);
    
    await waitFor(() => {
      expect(mockApi.get).toHaveBeenCalledWith('/files/1', { responseType: 'blob' });
    });
  });

  test('handles file deletion', async () => {
    const mockApi = require('../services/api');
    mockApi.delete.mockResolvedValue({
      data: { message: 'File deleted successfully' }
    });

    const mockOnFileDeleted = jest.fn();
    render(<FileList files={mockFiles} onFileDeleted={mockOnFileDeleted} />);
    
    const deleteButtons = screen.getAllByText(/delete/i);
    fireEvent.click(deleteButtons[0]);
    
    // Confirm deletion
    const confirmButton = screen.getByText(/yes, delete/i);
    fireEvent.click(confirmButton);
    
    await waitFor(() => {
      expect(mockApi.delete).toHaveBeenCalledWith('/files/1');
      expect(mockOnFileDeleted).toHaveBeenCalledWith('1');
    });
  });

  test('shows confirmation dialog for deletion', () => {
    render(<FileList files={mockFiles} />);
    
    const deleteButtons = screen.getAllByText(/delete/i);
    fireEvent.click(deleteButtons[0]);
    
    expect(screen.getByText(/are you sure/i)).toBeInTheDocument();
    expect(screen.getByText(/this action cannot be undone/i)).toBeInTheDocument();
  });

  test('cancels deletion', () => {
    const mockOnFileDeleted = jest.fn();
    render(<FileList files={mockFiles} onFileDeleted={mockOnFileDeleted} />);
    
    const deleteButtons = screen.getAllByText(/delete/i);
    fireEvent.click(deleteButtons[0]);
    
    const cancelButton = screen.getByText(/cancel/i);
    fireEvent.click(cancelButton);
    
    expect(mockOnFileDeleted).not.toHaveBeenCalled();
  });

  test('handles empty file list', () => {
    render(<FileList files={[]} />);
    
    expect(screen.getByText(/no files uploaded yet/i)).toBeInTheDocument();
    expect(screen.getByText(/upload your first cv file/i)).toBeInTheDocument();
  });

  test('handles loading state', () => {
    render(<FileList files={[]} loading={true} />);
    
    expect(screen.getByText(/loading files/i)).toBeInTheDocument();
  });

  test('handles error state', () => {
    render(<FileList files={[]} error="Failed to load files" />);
    
    expect(screen.getByText(/failed to load files/i)).toBeInTheDocument();
  });

  test('formats file size correctly', () => {
    const filesWithDifferentSizes = [
      { ...mockFiles[0], id: '1', file_size: 500 }, // 0.5 KB
      { ...mockFiles[1], id: '2', file_size: 1024 }, // 1 KB
      { ...mockFiles[0], id: '3', file_size: 1024 * 1024 }, // 1 MB
      { ...mockFiles[1], id: '4', file_size: 5 * 1024 * 1024 }, // 5 MB
    ];
    
    render(<FileList files={filesWithDifferentSizes} />);
    
    expect(screen.getByText('500 Bytes')).toBeInTheDocument();
    expect(screen.getByText('1 KB')).toBeInTheDocument();
    expect(screen.getByText('1 MB')).toBeInTheDocument();
    expect(screen.getByText('5 MB')).toBeInTheDocument();
  });

  test('shows file type icons', () => {
    render(<FileList files={mockFiles} />);
    
    // Check for file type indicators
    const pdfElements = screen.getAllByText('PDF');
    const docxElements = screen.getAllByText('DOCX');
    
    expect(pdfElements.length).toBeGreaterThan(0);
    expect(docxElements.length).toBeGreaterThan(0);
  });

  test('handles download error', async () => {
    const mockApi = require('../services/api');
    const consoleSpy = jest.spyOn(console, 'error').mockImplementation(() => {});
    const alertSpy = jest.spyOn(window, 'alert').mockImplementation(() => {});
    
    mockApi.get.mockRejectedValue({
      response: { data: { detail: 'File not found' } }
    });

    render(<FileList files={mockFiles} />);
    
    const downloadButtons = screen.getAllByText(/download/i);
    fireEvent.click(downloadButtons[0]);
    
    await waitFor(() => {
      expect(consoleSpy).toHaveBeenCalledWith('Download failed:', expect.any(Object));
      expect(alertSpy).toHaveBeenCalledWith('Download failed. Please try again.');
    });
    
    consoleSpy.mockRestore();
    alertSpy.mockRestore();
  });
});
