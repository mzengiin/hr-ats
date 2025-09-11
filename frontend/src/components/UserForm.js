import React, { useState, useEffect } from 'react';
import api from '../services/api';

const UserForm = ({ isOpen, onClose, userId, onSuccess }) => {
  const isEdit = Boolean(userId);
  const formKey = isEdit ? `edit-${userId}` : 'new';

  const [formData, setFormData] = useState({
    first_name: '',
    last_name: '',
    email: '',
    phone: '',
    password: '',
    role_id: '',
    is_active: true,
    profile_photo: null
  });


  const [roles, setRoles] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [previewImage, setPreviewImage] = useState(null);

  // Reset form function
  const resetForm = () => {
    setFormData({
      first_name: '',
      last_name: '',
      email: '',
      phone: '',
      password: '',
      role_id: '',
      is_active: true,
      profile_photo: null
    });
    setPreviewImage(null);
    setError(null);
  };

  useEffect(() => {
    if (isOpen) {
      fetchRoles();
      if (isEdit && userId) {
        fetchUser();
      } else {
        // Reset form for new user
        resetForm();
      }
    } else {
      // Reset form when modal is closed
      resetForm();
    }
  }, [isOpen, userId, isEdit]);

  const fetchRoles = async () => {
    try {
      const response = await api.get('/roles');
      if (response.data.success) {
        setRoles(response.data.data.roles || []);
      }
    } catch (error) {
      console.error('Error fetching roles:', error);
    }
  };

  const fetchUser = async () => {
    try {
      setLoading(true);
      const response = await api.get(`/users/${userId}`);
      
      if (response.data.success) {
        const user = response.data.data;
      setFormData({
          first_name: user.first_name,
          last_name: user.last_name,
          email: user.email,
          phone: user.phone || '',
          password: '', // Don't pre-fill password
          role_id: user.role_id || '',
          is_active: user.is_active,
          profile_photo: null
        });
        setPreviewImage(user.profile_photo ? `http://localhost:8001${user.profile_photo}` : null);
      } else {
        setError('Kullanıcı bilgileri yüklenirken hata oluştu');
      }
    } catch (error) {
      console.error('Error fetching user:', error);
      setError('Kullanıcı bilgileri yüklenirken hata oluştu');
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (e) => {
    const { name, value, type, checked } = e.target;
    
    // Telefon numarası mask'ı
    if (name === 'phone') {
      let maskedValue = value.replace(/\D/g, ''); // Sadece rakamları al
      if (maskedValue.length > 0) {
        if (maskedValue.length <= 3) {
          maskedValue = maskedValue;
        } else if (maskedValue.length <= 6) {
          maskedValue = maskedValue.slice(0, 3) + ' ' + maskedValue.slice(3);
        } else if (maskedValue.length <= 8) {
          maskedValue = maskedValue.slice(0, 3) + ' ' + maskedValue.slice(3, 6) + ' ' + maskedValue.slice(6);
        } else if (maskedValue.length <= 10) {
          maskedValue = maskedValue.slice(0, 3) + ' ' + maskedValue.slice(3, 6) + ' ' + maskedValue.slice(6, 8) + ' ' + maskedValue.slice(8);
        } else {
          maskedValue = maskedValue.slice(0, 3) + ' ' + maskedValue.slice(3, 6) + ' ' + maskedValue.slice(6, 8) + ' ' + maskedValue.slice(8, 10);
        }
      }
      
    setFormData(prev => ({
        ...prev,
        [name]: maskedValue
      }));
    } else {
    setFormData(prev => ({
        ...prev,
        [name]: type === 'checkbox' ? checked : value
      }));
    }
  };

  const handleImageChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      // Validate file type
      if (!file.type.startsWith('image/')) {
        setError('Lütfen geçerli bir resim dosyası seçin');
        return;
      }
      
      // Validate file size (max 5MB)
      if (file.size > 5 * 1024 * 1024) {
        setError('Resim dosyası 5MB\'dan küçük olmalıdır');
        return;
      }

      setFormData(prev => ({
        ...prev,
        profile_photo: file
      }));

      // Create preview
      const reader = new FileReader();
      reader.onload = (e) => {
        setPreviewImage(e.target.result);
      };
      reader.readAsDataURL(file);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      // Create FormData for file upload
      const submitData = new FormData();
      submitData.append('first_name', formData.first_name);
      submitData.append('last_name', formData.last_name);
      submitData.append('email', formData.email);
      submitData.append('phone', formData.phone);
      submitData.append('role_id', formData.role_id);
      submitData.append('is_active', formData.is_active);
      
      if (formData.password) {
        submitData.append('password', formData.password);
      }
      
      if (formData.profile_photo) {
        submitData.append('profile_photo', formData.profile_photo);
      }

      const response = isEdit 
        ? await api.put(`/users/${userId}`, submitData, {
            headers: {
              'Content-Type': 'multipart/form-data',
            },
          })
        : await api.post('/users', submitData, {
            headers: {
              'Content-Type': 'multipart/form-data',
            },
          });

      if (response.data.success) {
        onSuccess && onSuccess();
        resetForm();
        onClose();
      } else {
        setError(response.data.message || 'Kullanıcı kaydedilirken hata oluştu');
      }
    } catch (error) {
      console.error('Error saving user:', error);
      console.error('Error response:', error.response?.data);
      const errorMessage = error.response?.data?.detail || error.response?.data?.message || 'Kullanıcı kaydedilirken hata oluştu';
      setError(typeof errorMessage === 'string' ? errorMessage : 'Kullanıcı kaydedilirken hata oluştu');
    } finally {
      setLoading(false);
    }
  };

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
      <div key={isOpen ? 'modal-open' : 'modal-closed'} className="bg-white rounded-xl max-w-4xl w-full max-h-[85vh] overflow-hidden flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <div>
            <h2 className="text-2xl font-bold text-gray-900">
              {isEdit ? 'Kullanıcı Düzenle' : 'Yeni Kullanıcı Ekle'}
            </h2>
            <p className="text-gray-600 mt-1">
              {isEdit ? 'Kullanıcı bilgilerini düzenleyin' : 'Yeni bir kullanıcı oluşturun'}
            </p>
          </div>
        <button
            onClick={() => {
              resetForm();
              onClose();
            }}
            className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <span className="material-symbols-outlined text-gray-600">close</span>
        </button>
      </div>

        <div className="p-6 overflow-y-auto flex-1">
          <form key={formKey} onSubmit={handleSubmit} autoComplete="new-password" className="space-y-4">
            {/* Profile Photo */}
            <div className="bg-gray-50 p-4 rounded-xl">
              <h3 className="text-lg font-semibold text-gray-900 mb-3">Profil Fotoğrafı</h3>
              <div className="flex justify-center">
                <div className="relative">
                  <div className="h-24 w-24 flex-shrink-0">
                    {previewImage ? (
                      <img
                        className="h-24 w-24 rounded-full object-cover"
                        src={previewImage}
                        alt="Profil önizleme"
                      />
                    ) : (
                      <div className="h-24 w-24 rounded-full bg-gray-200 flex items-center justify-center">
                        <span className="material-symbols-outlined text-gray-500 text-3xl">person</span>
                      </div>
                    )}
                  </div>
                  <button
                    type="button"
                    onClick={() => document.getElementById('profile-photo-input').click()}
                    className="absolute -bottom-1 -right-1 h-8 w-8 bg-[#137fec] text-white rounded-full flex items-center justify-center hover:bg-blue-700 transition-colors"
                  >
                    <span className="material-symbols-outlined text-sm">edit</span>
                  </button>
                  <input
                    id="profile-photo-input"
                    type="file"
                    accept="image/*"
                    onChange={handleImageChange}
                    className="hidden"
                  />
                </div>
              </div>
              <p className="text-xs text-gray-500 text-center mt-2">JPG, PNG veya GIF. Maksimum 5MB.</p>
            </div>

            {/* Basic Information */}
            <div className="bg-gray-50 p-4 rounded-xl">
              <h3 className="text-lg font-semibold text-gray-900 mb-3">Temel Bilgiler</h3>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
              Ad *
            </label>
            <input
              type="text"
              name="first_name"
              value={formData.first_name}
                    onChange={handleInputChange}
                    required
                    className="w-full px-3 py-2 h-10 border border-gray-300 rounded-lg focus:ring-2 focus:ring-[#137fec] focus:border-transparent"
                    placeholder="Ad"
                  />
          </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
              Soyad *
            </label>
            <input
              type="text"
              name="last_name"
              value={formData.last_name}
                    onChange={handleInputChange}
                    required
                    className="w-full px-3 py-2 h-10 border border-gray-300 rounded-lg focus:ring-2 focus:ring-[#137fec] focus:border-transparent"
                    placeholder="Soyad"
                  />
        </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    E-posta *
          </label>
          <input
                    key={`email-${isEdit ? userId : 'new'}`}
            type="email"
            name="email"
            value={formData.email}
                    onChange={handleInputChange}
                    required
                    autoComplete="new-email"
                    className="w-full px-3 py-2 h-10 border border-gray-300 rounded-lg focus:ring-2 focus:ring-[#137fec] focus:border-transparent"
                    placeholder="ornek@email.com"
                  />
        </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Telefon
            </label>
            <input
                    type="tel"
                    name="phone"
                    value={formData.phone}
                    onChange={handleInputChange}
                    maxLength="13"
                    className="w-full px-3 py-2 h-10 border border-gray-300 rounded-lg focus:ring-2 focus:ring-[#137fec] focus:border-transparent"
                    placeholder="555 000 00 00"
                  />
          </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Şifre {!isEdit && '*'}
              </label>
              <input
                    key={`password-${isEdit ? userId : 'new'}`}
                type="password"
                    name="password"
                    value={formData.password}
                    onChange={handleInputChange}
                    required={!isEdit}
                    autoComplete="new-password"
                    className="w-full px-3 py-2 h-10 border border-gray-300 rounded-lg focus:ring-2 focus:ring-[#137fec] focus:border-transparent"
                    placeholder={isEdit ? "Değiştirmek için yeni şifre girin" : "Şifre"}
                  />
                  {isEdit && (
                    <p className="text-xs text-gray-500 mt-1">Boş bırakırsanız şifre değişmez</p>
          )}
        </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Rol *
          </label>
                  <select
                    name="role_id"
            value={formData.role_id}
                    onChange={handleInputChange}
                    required
                    className="w-full px-3 py-2 h-10 border border-gray-300 rounded-lg focus:ring-2 focus:ring-[#137fec] focus:border-transparent"
                  >
                    <option value="">Rol Seçin</option>
                    {roles.map((role) => (
                      <option key={role.id} value={role.id}>
                        {role.name}
                      </option>
                    ))}
                  </select>
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

            {/* Error Message */}
            {error && (
              <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                <div className="flex">
                  <span className="material-symbols-outlined text-red-400 mr-2">error</span>
                  <p className="text-sm text-red-700">
                    {typeof error === 'string' ? error : JSON.stringify(error)}
                  </p>
                </div>
          </div>
        )}

            {/* Actions */}
            <div className="flex justify-end gap-4 pt-4 border-t border-gray-200">
          <button
            type="button"
                onClick={() => {
                  resetForm();
                  onClose();
                }}
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

export default UserForm;