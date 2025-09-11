import React, { useState, useEffect } from 'react';
import api from '../services/api';

const RoleForm = ({ isOpen, onClose, roleId, onSuccess }) => {
  const isEdit = Boolean(roleId);

  const [formData, setFormData] = useState({
    name: '',
    code: '',
    description: '',
    is_active: true,
    permissions: []
  });

  const [permissions, setPermissions] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Mock permissions - gerçek uygulamada API'den gelecek
  const availablePermissions = [
    { id: 'users:read', name: 'Kullanıcıları Görüntüle', category: 'Kullanıcı Yönetimi' },
    { id: 'users:create', name: 'Kullanıcı Oluştur', category: 'Kullanıcı Yönetimi' },
    { id: 'users:update', name: 'Kullanıcı Düzenle', category: 'Kullanıcı Yönetimi' },
    { id: 'users:delete', name: 'Kullanıcı Sil', category: 'Kullanıcı Yönetimi' },
    { id: 'candidates:read', name: 'Adayları Görüntüle', category: 'Aday Yönetimi' },
    { id: 'candidates:create', name: 'Aday Oluştur', category: 'Aday Yönetimi' },
    { id: 'candidates:update', name: 'Aday Düzenle', category: 'Aday Yönetimi' },
    { id: 'candidates:delete', name: 'Aday Sil', category: 'Aday Yönetimi' },
    { id: 'interviews:read', name: 'Mülakatları Görüntüle', category: 'Mülakat Yönetimi' },
    { id: 'interviews:create', name: 'Mülakat Oluştur', category: 'Mülakat Yönetimi' },
    { id: 'interviews:update', name: 'Mülakat Düzenle', category: 'Mülakat Yönetimi' },
    { id: 'interviews:delete', name: 'Mülakat Sil', category: 'Mülakat Yönetimi' },
    { id: 'reports:read', name: 'Raporları Görüntüle', category: 'Raporlar' },
    { id: 'dashboard:read', name: 'Dashboard Görüntüle', category: 'Dashboard' },
  ];

  useEffect(() => {
    if (isEdit && roleId) {
      fetchRole();
    }
  }, [roleId, isEdit]);

  const fetchRole = async () => {
    try {
      setLoading(true);
      const response = await api.get(`/roles/${roleId}`);
      
      if (response.data.success) {
        const role = response.data.data;
        setFormData({
          name: role.name,
          code: role.code,
          description: role.description || '',
          is_active: role.is_active,
          permissions: role.permissions || []
        });
      } else {
        setError('Rol bilgileri yüklenirken hata oluştu');
      }
    } catch (error) {
      console.error('Error fetching role:', error);
      setError('Rol bilgileri yüklenirken hata oluştu');
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }));
  };

  const handlePermissionChange = (permissionId, checked) => {
    setFormData(prev => ({
      ...prev,
      permissions: checked
        ? [...prev.permissions, permissionId]
        : prev.permissions.filter(id => id !== permissionId)
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const response = isEdit 
        ? await api.put(`/roles/${roleId}`, formData)
        : await api.post('/roles', formData);

      if (response.data.success) {
        onSuccess && onSuccess();
        onClose();
      } else {
        setError(response.data.message || 'Rol kaydedilirken hata oluştu');
      }
    } catch (error) {
      console.error('Error saving role:', error);
      setError('Rol kaydedilirken hata oluştu');
    } finally {
      setLoading(false);
    }
  };

  const groupedPermissions = availablePermissions.reduce((acc, permission) => {
    if (!acc[permission.category]) {
      acc[permission.category] = [];
    }
    acc[permission.category].push(permission);
    return acc;
  }, {});

  if (!isOpen) return null;

  if (loading && isEdit) {
    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-[#137fec]"></div>
      </div>
    );
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-xl max-w-4xl w-full max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <div>
            <h2 className="text-2xl font-bold text-gray-900">
              {isEdit ? 'Rol Düzenle' : 'Yeni Rol Ekle'}
            </h2>
            <p className="text-gray-600 mt-1">
              {isEdit ? 'Rol bilgilerini düzenleyin' : 'Yeni bir rol oluşturun'}
            </p>
          </div>
          <button
            onClick={onClose}
            className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <span className="material-symbols-outlined text-gray-600">close</span>
          </button>
        </div>

        <div className="p-6">
          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Basic Information */}
            <div className="bg-gray-50 p-6 rounded-xl">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Temel Bilgiler</h3>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Rol Adı *
                </label>
                <input
                  type="text"
                  name="name"
                  value={formData.name}
                  onChange={handleInputChange}
                  required
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-[#137fec] focus:border-transparent"
                  placeholder="Örn: Yönetici, Editör"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Rol Kodu *
                </label>
                <input
                  type="text"
                  name="code"
                  value={formData.code}
                  onChange={handleInputChange}
                  required
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-[#137fec] focus:border-transparent"
                  placeholder="Örn: admin, editor"
                />
              </div>

              <div className="md:col-span-2">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Açıklama
                </label>
                <textarea
                  name="description"
                  value={formData.description}
                  onChange={handleInputChange}
                  rows={3}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-[#137fec] focus:border-transparent"
                  placeholder="Rol hakkında açıklama..."
                />
              </div>

              <div className="md:col-span-2">
                <div className="flex items-center">
                  <input
                    type="checkbox"
                    name="is_active"
                    checked={formData.is_active}
                    onChange={handleInputChange}
                    className="h-4 w-4 text-[#137fec] focus:ring-[#137fec] border-gray-300 rounded"
                  />
                  <label className="ml-2 block text-sm text-gray-700">
                    Aktif
                  </label>
                </div>
              </div>
            </div>
            </div>

            {/* Permissions */}
            <div className="bg-gray-50 p-6 rounded-xl">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Yetkiler</h3>
            
            <div className="space-y-6">
              {Object.entries(groupedPermissions).map(([category, categoryPermissions]) => (
                <div key={category}>
                  <h3 className="text-md font-medium text-gray-800 mb-3">{category}</h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
                    {categoryPermissions.map((permission) => (
                      <div key={permission.id} className="flex items-center">
                        <input
                          type="checkbox"
                          id={permission.id}
                          checked={formData.permissions.includes(permission.id)}
                          onChange={(e) => handlePermissionChange(permission.id, e.target.checked)}
                          className="h-4 w-4 text-[#137fec] focus:ring-[#137fec] border-gray-300 rounded"
                        />
                        <label htmlFor={permission.id} className="ml-2 block text-sm text-gray-700">
                          {permission.name}
                        </label>
                      </div>
                    ))}
                  </div>
                </div>
              ))}
            </div>
            </div>

            {/* Error Message */}
            {error && (
              <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                <div className="flex">
                  <span className="material-symbols-outlined text-red-400 mr-2">error</span>
                  <p className="text-sm text-red-700">{error}</p>
                </div>
              </div>
            )}

            {/* Actions */}
            <div className="flex justify-end gap-4 pt-4 border-t border-gray-200">
              <button
                type="button"
                onClick={onClose}
                className="px-6 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 transition-colors"
              >
                İptal
              </button>
              <button
                type="submit"
                disabled={loading}
                className="px-6 py-2 bg-[#137fec] text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
              >
                {loading && (
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                )}
                {isEdit ? 'Güncelle' : 'Oluştur'}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};

export default RoleForm;
