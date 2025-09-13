import React from 'react';

const DeleteConfirmModal = ({ isOpen, onClose, onConfirm, title, message, itemName, isLoading = false }) => {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl w-full max-w-md">
        {/* Header */}
        <div className="flex items-center justify-center p-6 border-b border-gray-200">
          <div className="flex items-center justify-center w-12 h-12 bg-red-100 rounded-full">
            <span className="material-symbols-outlined text-red-600 text-2xl">
              warning
            </span>
          </div>
        </div>

        {/* Content */}
        <div className="p-6 text-center">
          <h3 className="text-lg font-semibold text-gray-900 mb-2">
            {title || 'Silme Onayı'}
          </h3>
          <p className="text-sm text-gray-600 mb-4">
            {message || `"${itemName}" öğesini silmek istediğinizden emin misiniz?`}
          </p>
          <p className="text-xs text-red-600 font-medium">
            Bu işlem geri alınamaz.
          </p>
        </div>

        {/* Footer */}
        <div className="flex justify-end gap-3 p-6 border-t border-gray-200 bg-gray-50">
          <button
            type="button"
            onClick={onClose}
            disabled={isLoading}
            className="px-4 py-2 text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            İptal
          </button>
          <button
            type="button"
            onClick={onConfirm}
            disabled={isLoading}
            className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors flex items-center gap-2"
          >
            {isLoading && (
              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
            )}
            {isLoading ? 'Siliniyor...' : 'Sil'}
          </button>
        </div>
      </div>
    </div>
  );
};

export default DeleteConfirmModal;
