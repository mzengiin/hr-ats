import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { usersAPI, handleAPIError } from '../services/api';
import api from '../services/api';
import LoadingSpinner from './LoadingSpinner';

const UserProfileNew = ({ isOpen, onClose }) => {
  const { user, getCurrentUser, changePassword } = useAuth();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  const [activeTab, setActiveTab] = useState('profile');
  const [profileData, setProfileData] = useState({
    first_name: '',
    last_name: '',
    email: '',
    phone: '',
  });
  const [passwordData, setPasswordData] = useState({
    current_password: '',
    new_password: '',
    confirm_password: '',
  });
  const [profilePhoto, setProfilePhoto] = useState(null);
  const [previewImage, setPreviewImage] = useState(null);
  const [userRole, setUserRole] = useState(null);
  const [userPermissions, setUserPermissions] = useState([]);

  // Load user data
  useEffect(() => {
    const loadUserData = async () => {
      try {
        console.log('🔄 useEffect: getCurrentUser çağrılıyor...');
        const currentUser = await getCurrentUser();
        console.log('✅ useEffect: getCurrentUser başarılı:', currentUser);
      } catch (error) {
        console.error('❌ useEffect: getCurrentUser hatası:', error);
      }
    };
    
    loadUserData();
  }, []);

  useEffect(() => {
    if (user) {
      console.log('🔄 useEffect: User data yükleniyor:', user);
      console.log('🔄 useEffect: User profile_photo:', user.profile_photo);
      console.log('🔄 useEffect: User phone:', user.phone);
      console.log('🔄 useEffect: User keys:', Object.keys(user));
      setProfileData({
        first_name: user.first_name || '',
        last_name: user.last_name || '',
        email: user.email || '',
        phone: user.phone || '',
      });
      console.log('✅ useEffect: ProfileData state güncellendi:', {
        first_name: user.first_name || '',
        last_name: user.last_name || '',
        email: user.email || '',
        phone: user.phone || '',
      });
      
      // Set profile image preview
      if (user.profile_photo) {
        // Convert relative path to full URL
        const fullImageUrl = user.profile_photo.startsWith('http') 
          ? user.profile_photo 
          : `http://localhost:8001${user.profile_photo}`;
        console.log('🖼️ useEffect: Profil resmi yükleniyor:', fullImageUrl);
        console.log('🖼️ useEffect: Original profile_photo:', user.profile_photo);
        setPreviewImage(fullImageUrl);
      } else {
        console.log('🖼️ useEffect: User.profile_photo yok veya boş');
        console.log('🖼️ useEffect: User.profile_photo değeri:', user.profile_photo);
        setPreviewImage(null);
      }
      
      // Set role and permissions safely
      if (user.role) {
        console.log('🔐 useEffect: User role:', user.role);
        console.log('🔐 useEffect: User role permissions:', user.role.permissions);
        const roleName = typeof user.role === 'string' ? user.role : (user.role.name || 'Kullanıcı');
        setUserRole({
          name: roleName,
          description: user.role.description || '',
          permissions: Array.isArray(user.role.permissions) ? user.role.permissions : []
        });
        setUserPermissions(Array.isArray(user.role.permissions) ? user.role.permissions : []);
        console.log('✅ useEffect: UserRole state güncellendi:', {
          name: roleName,
          description: user.role.description || '',
          permissions: Array.isArray(user.role.permissions) ? user.role.permissions : []
        });
      }
    }
  }, [user]);

  // Load role and permissions from API
  useEffect(() => {
    const loadRoleData = async () => {
      try {
        // Get all roles and find the one matching user's role
        const response = await api.get('/roles/');
        if (response.data.success) {
          const roles = response.data.data.roles;
          const userRoleData = roles.find(role => role.name === user?.role);
          if (userRoleData) {
            setUserRole({
              name: userRoleData.name || 'Kullanıcı',
              description: userRoleData.description || '',
              permissions: Array.isArray(userRoleData.permissions) ? userRoleData.permissions : []
            });
            setUserPermissions(Array.isArray(userRoleData.permissions) ? userRoleData.permissions : []);
          }
        }
      } catch (error) {
        console.error('Error loading role data:', error);
        // Fallback to basic role info
        if (user?.role) {
          const roleName = typeof user.role === 'string' ? user.role : 'Kullanıcı';
          setUserRole({
            name: roleName,
            description: 'Kullanıcı rolü',
            permissions: []
          });
        }
      }
    };

    if (user?.role) {
      loadRoleData();
    }
  }, [user]);

  // Handle profile update
  const handleProfileUpdate = async (e) => {
    e.preventDefault();
    console.log('🔄 Profil güncelleme başlatılıyor...');
    setLoading(true);
    setError(null);
    setSuccess(null);

    try {
      // Debug: Form state'ini kontrol et
      console.log('📝 Form state (profileData):', profileData);
      
      // Create FormData for file upload
      const formData = new FormData();
      formData.append('first_name', profileData.first_name);
      formData.append('last_name', profileData.last_name);
      formData.append('phone', profileData.phone);
      
      // Debug: FormData içeriğini kontrol et
      console.log('📦 FormData içeriği:');
      for (let [key, value] of formData.entries()) {
        console.log(`  ${key}: ${value}`);
      }
      
      if (profilePhoto) {
        console.log('📷 Profil resmi ekleniyor:', profilePhoto.name, profilePhoto.size);
        formData.append('profile_photo', profilePhoto);
      } else {
        console.log('📷 Profil resmi yok');
      }

      console.log('📤 Backend\'e istek gönderiliyor...');
      const updateResponse = await usersAPI.updateProfileInfo(formData);
      console.log('📥 Backend yanıtı:', updateResponse.data);
      console.log('📥 Backend data detayı:', JSON.stringify(updateResponse.data.data, null, 2));
      
      // Update profileData state with response data
      if (updateResponse.data.success && updateResponse.data.data) {
        const updatedData = updateResponse.data.data;
        console.log('🔄 State güncelleniyor:', updatedData);
        console.log('🔄 Profil resmi URL:', updatedData.profile_photo);
        setProfileData({
          first_name: updatedData.first_name || '',
          last_name: updatedData.last_name || '',
          email: updatedData.email || '',
          phone: updatedData.phone || '',
        });
        console.log('✅ State güncellendi!');
        
        // Update profile image preview
        if (updatedData.profile_photo) {
          // Convert relative path to full URL
          const fullImageUrl = updatedData.profile_photo.startsWith('http') 
            ? updatedData.profile_photo 
            : `http://localhost:8001${updatedData.profile_photo}`;
          console.log('🖼️ Profil resmi güncelleniyor:', fullImageUrl);
          setPreviewImage(fullImageUrl);
        } else {
          console.log('🖼️ Profil resmi URL yok');
        }
      }
      
      // Profil güncelleme sonrası getCurrentUser() çağrısı yapmıyoruz
      // Çünkü zaten response'dan gelen verileri kullanıyoruz
      console.log('✅ Profil güncelleme tamamlandı!');
      
      setSuccess('Profil başarıyla güncellendi');
      setProfilePhoto(null); // Clear file input
    } catch (error) {
      console.error('❌ Profil güncelleme hatası:', error);
      console.error('❌ Hata detayları:', error.response?.data);
      setError(handleAPIError(error));
    } finally {
      setLoading(false);
    }
  };

  // Handle password change
  const handlePasswordChange = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setSuccess(null);

    if (passwordData.new_password !== passwordData.confirm_password) {
      setError('Yeni şifreler eşleşmiyor');
      setLoading(false);
      return;
    }

    try {
      // Create FormData for password update
      const formData = new FormData();
      formData.append('current_password', passwordData.current_password);
      formData.append('new_password', passwordData.new_password);

      await usersAPI.updateProfilePassword(formData);
      setSuccess('Şifre başarıyla değiştirildi');
      setPasswordData({
        current_password: '',
        new_password: '',
        confirm_password: '',
      });
      
      // Şifre değiştirme sonrası getCurrentUser() çağrısı yapmıyoruz
      // Çünkü şifre değiştirme profil bilgilerini etkilememeli
    } catch (error) {
      setError(handleAPIError(error));
    } finally {
      setLoading(false);
    }
  };

  // Handle input changes
  const handleProfileChange = (e) => {
    const { name, value } = e.target;
    console.log(`🔄 Input değişikliği: ${name} = "${value}"`);
    
    // Telefon numarası mask'ı - UserForm ile aynı
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
      
      setProfileData(prev => ({
        ...prev,
        [name]: maskedValue
      }));
    } else {
      setProfileData(prev => ({
        ...prev,
        [name]: value
      }));
    }
  };

  // Handle image change
  const handleImageChange = (e) => {
    const file = e.target.files[0];
    console.log('📷 Resim seçildi:', file);
    if (file) {
      // Validate file type
      if (!file.type.startsWith('image/')) {
        console.log('❌ Geçersiz dosya türü:', file.type);
        setError('Lütfen geçerli bir resim dosyası seçin');
        return;
      }
      
      // Validate file size (max 5MB)
      if (file.size > 5 * 1024 * 1024) {
        console.log('❌ Dosya çok büyük:', file.size);
        setError('Resim dosyası 5MB\'dan küçük olmalıdır');
        return;
      }

      console.log('✅ Resim geçerli, state güncelleniyor');
      setProfilePhoto(file);

      // Create preview
      const reader = new FileReader();
      reader.onload = (e) => {
        setPreviewImage(e.target.result);
      };
      reader.readAsDataURL(file);
    }
  };

  const handlePasswordChangeInput = (e) => {
    const { name, value } = e.target;
    setPasswordData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const clearMessages = () => {
    setError(null);
    setSuccess(null);
  };

  if (!isOpen) return null;

  if (!user) {
    return (
      <div className="fixed inset-0 z-50 overflow-y-auto">
        <div className="fixed inset-0 bg-black bg-opacity-50 transition-opacity" onClick={onClose}></div>
        <div className="flex min-h-full items-center justify-center p-4">
          <div className="relative bg-white rounded-lg shadow-xl w-full max-w-4xl max-h-[90vh] overflow-hidden">
            <div className="flex items-center justify-center h-64">
              <LoadingSpinner />
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto">
      {/* Backdrop */}
      <div className="fixed inset-0 bg-black bg-opacity-50 transition-opacity" onClick={onClose}></div>
      
      {/* Modal */}
      <div className="flex min-h-full items-center justify-center p-4">
        <div className="relative bg-white rounded-lg shadow-xl w-full max-w-4xl max-h-[90vh] overflow-hidden">
          {/* Close button */}
          <button
            onClick={onClose}
            className="absolute top-4 right-4 z-10 p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-full transition-colors"
          >
            <span className="material-symbols-outlined text-xl">close</span>
          </button>
          
          {/* Modal content */}
          <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
            {/* Header */}
            <div className="mb-8">
              <h1 className="text-3xl font-bold text-gray-900">Kullanıcı Profili</h1>
              <p className="mt-2 text-gray-600">Profil bilgilerinizi görüntüleyin ve düzenleyin</p>
            </div>

            {/* Tabs */}
            <div className="bg-white rounded-lg shadow-sm border border-gray-200">
              <div className="border-b border-gray-200">
                <nav className="flex space-x-8 px-6" aria-label="Tabs">
                  <button
                    className={`flex items-center whitespace-nowrap border-b-2 py-4 px-1 text-sm font-semibold ${
                      activeTab === 'profile'
                        ? 'border-blue-600 text-blue-600'
                        : 'border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700'
                    }`}
                    onClick={() => setActiveTab('profile')}
                  >
                    <span className="material-symbols-outlined mr-2 text-xl">person</span>
                    Profil Bilgileri
                  </button>
                  <button
                    className={`flex items-center whitespace-nowrap border-b-2 py-4 px-1 text-sm font-semibold ${
                      activeTab === 'password'
                        ? 'border-blue-600 text-blue-600'
                        : 'border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700'
                    }`}
                    onClick={() => setActiveTab('password')}
                  >
                    <span className="material-symbols-outlined mr-2 text-xl">lock</span>
                    Şifre Değiştir
                  </button>
                  <button
                    className={`flex items-center whitespace-nowrap border-b-2 py-4 px-1 text-sm font-semibold ${
                      activeTab === 'roles'
                        ? 'border-blue-600 text-blue-600'
                        : 'border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700'
                    }`}
                    onClick={() => setActiveTab('roles')}
                  >
                    <span className="material-symbols-outlined mr-2 text-xl">verified_user</span>
                    Yetkilerim
                  </button>
                </nav>
              </div>

              {/* Tab Content */}
              <div className="p-6">
                {/* Profile Tab */}
                {activeTab === 'profile' && (
                  <div className="space-y-6">
                    {/* Profile Image Section */}
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
                    <p className="text-xs text-gray-500 text-center">JPG, PNG veya GIF. Maksimum 5MB.</p>

                    {/* Basic Information */}
                    <form onSubmit={handleProfileUpdate} className="space-y-4">
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-2">
                            Ad *
                          </label>
                          <input
                            type="text"
                            name="first_name"
                            value={profileData.first_name}
                            onChange={handleProfileChange}
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
                            value={profileData.last_name}
                            onChange={handleProfileChange}
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
                            type="email"
                            name="email"
                            value={profileData.email}
                            disabled
                            className="w-full px-3 py-2 h-10 border border-gray-300 rounded-lg focus:ring-2 focus:ring-[#137fec] focus:border-transparent bg-gray-100"
                            placeholder="ornek@email.com"
                          />
                          <p className="text-xs text-gray-500 mt-1">E-posta değiştirilemez</p>
                        </div>

                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-2">
                            Telefon
                          </label>
                          <input
                            type="tel"
                            name="phone"
                            value={profileData.phone}
                            onChange={handleProfileChange}
                            maxLength="13"
                            className="w-full px-3 py-2 h-10 border border-gray-300 rounded-lg focus:ring-2 focus:ring-[#137fec] focus:border-transparent"
                            placeholder="555 000 00 00"
                          />
                          {profileData.phone && profileData.phone.replace(/\D/g, '').length < 10 && (
                            <p className="text-xs text-red-500 mt-1">
                              Lütfen geçerli bir telefon numarası girin
                            </p>
                          )}
                        </div>
                      </div>

                      <div className="flex justify-end pt-4">
                        <button
                          type="submit"
                          className="bg-[#137fec] text-white px-6 py-2 rounded-lg hover:bg-blue-700 transition-colors font-medium"
                          disabled={loading}
                        >
                          {loading ? 'Güncelleniyor...' : 'Kaydet'}
                        </button>
                      </div>
                    </form>
                  </div>
                )}

                {/* Password Tab */}
                {activeTab === 'password' && (
                  <div className="max-w-md mx-auto">
                    <h3 className="text-lg font-semibold text-gray-900 mb-6">Şifrenizi Güvenle Değiştirin</h3>
                    <form onSubmit={handlePasswordChange} className="space-y-6">
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2" htmlFor="current_password">
                          Mevcut Şifre
                        </label>
                        <input
                          className="w-full px-3 py-2 h-10 border border-gray-300 rounded-lg focus:ring-2 focus:ring-[#137fec] focus:border-transparent"
                          id="current_password"
                          name="current_password"
                          placeholder="Mevcut şifrenizi girin"
                          type="password"
                          value={passwordData.current_password}
                          onChange={handlePasswordChangeInput}
                          required
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2" htmlFor="new_password">
                          Yeni Şifre
                        </label>
                        <input
                          className="w-full px-3 py-2 h-10 border border-gray-300 rounded-lg focus:ring-2 focus:ring-[#137fec] focus:border-transparent"
                          id="new_password"
                          name="new_password"
                          placeholder="Yeni şifrenizi oluşturun"
                          type="password"
                          value={passwordData.new_password}
                          onChange={handlePasswordChangeInput}
                          required
                          minLength="8"
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2" htmlFor="confirm_password">
                          Yeni Şifre Tekrarı
                        </label>
                        <input
                          className="w-full px-3 py-2 h-10 border border-gray-300 rounded-lg focus:ring-2 focus:ring-[#137fec] focus:border-transparent"
                          id="confirm_password"
                          name="confirm_password"
                          placeholder="Yeni şifrenizi doğrulayın"
                          type="password"
                          value={passwordData.confirm_password}
                          onChange={handlePasswordChangeInput}
                          required
                          minLength="8"
                        />
                      </div>
                      <div className="flex justify-end pt-4">
                        <button
                          className="bg-[#137fec] text-white px-6 py-2 rounded-lg hover:bg-blue-700 transition-colors font-medium"
                          type="submit"
                          disabled={loading}
                        >
                          {loading ? 'Değiştiriliyor...' : 'Şifreyi Değiştir'}
                        </button>
                      </div>
                    </form>
                  </div>
                )}

                {/* Roles Tab */}
                {activeTab === 'roles' && (
                  <div className="max-h-[calc(90vh-300px)] overflow-y-auto custom-scrollbar">
                    <h2 className="text-xl font-bold text-gray-800">Rol ve Yetki Bilgileri</h2>
                    <p className="mt-1 text-sm text-gray-500">Kullanıcı rolünüz ve bu role atanmış yetkiler aşağıda listelenmiştir.</p>
                    
                    <div className="border-t border-gray-200 px-6 md:px-8 py-6">
                      <div className="space-y-6">
                        <div className="grid md:grid-cols-3 gap-2 md:gap-4 items-center">
                          <p className="text-sm font-medium text-gray-600">Rol(ler)</p>
                          <div className="md:col-span-2">
                            <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-semibold bg-blue-100 text-blue-600">
                              {userRole?.name || 'Kullanıcı'}
                            </span>
                            {userRole?.description && (
                              <p className="text-xs text-gray-500 mt-1">{userRole.description}</p>
                            )}
                          </div>
                        </div>
                        
                        <div className="space-y-6">
                          <h3 className="text-lg font-semibold text-gray-800 border-b border-gray-200 pb-2">Yetki Kategorileri</h3>
                          {userRole?.permissions && userRole.permissions.length > 0 ? (
                            (() => {
                              // Kategorilere göre grupla
                              const groupedPermissions = userRole.permissions.reduce((acc, permission) => {
                                const category = permission.category || 'Diğer';
                                if (!acc[category]) {
                                  acc[category] = [];
                                }
                                acc[category].push(permission);
                                return acc;
                              }, {});

                              return (
                                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                                  {Object.entries(groupedPermissions).map(([category, permissions]) => (
                                    <div key={category} className="bg-gray-50 rounded-lg p-4">
                                      <div className="flex items-center gap-2 mb-3">
                                        <span className="material-symbols-outlined text-blue-600 text-xl">
                                          {category.includes('Kullanıcı') ? 'person' :
                                           category.includes('Aday') ? 'folder_open' :
                                           category.includes('Mülakat') ? 'event' :
                                           category.includes('Rapor') ? 'bar_chart' :
                                           category.includes('Dashboard') ? 'dashboard' :
                                           category.includes('Rol') ? 'admin_panel_settings' : 'settings'}
                                        </span>
                                        <h4 className="text-base font-semibold text-gray-800">{category}</h4>
                                        <span className="text-xs text-gray-500 bg-blue-100 text-blue-700 px-2 py-1 rounded-full">
                                          {permissions.length} yetki
                                        </span>
                                      </div>
                                      <div className="grid grid-cols-1 gap-2">
                                        {permissions.map((permission, index) => {
                                          const action = permission.code.split(':')[1];
                                          const colorClass = action === 'create' ? 'text-green-700 bg-green-50 border-green-200' :
                                                           action === 'update' ? 'text-yellow-700 bg-yellow-50 border-yellow-200' :
                                                           action === 'delete' ? 'text-red-700 bg-red-50 border-red-200' :
                                                           'text-blue-700 bg-blue-50 border-blue-200';
                                          const icon = action === 'create' ? 'add_circle' :
                                                     action === 'update' ? 'edit' :
                                                     action === 'delete' ? 'delete' :
                                                     'visibility';
                                          
                                          return (
                                            <div
                                              key={index}
                                              className={`flex items-center gap-2 text-sm px-3 py-2 rounded-md border ${colorClass}`}
                                              title={permission.description}
                                            >
                                              <span className="material-symbols-outlined text-base">
                                                {icon}
                                              </span>
                                              <span className="font-medium">{permission.name}</span>
                                            </div>
                                          );
                                        })}
                                      </div>
                                    </div>
                                  ))}
                                </div>
                              );
                            })()
                          ) : (
                            <div className="text-center py-8">
                              <span className="material-symbols-outlined text-gray-400 text-4xl mb-2 block">lock</span>
                              <p className="text-gray-500">Yetki bilgisi bulunamadı</p>
                            </div>
                          )}
                        </div>
                      </div>
                    </div>
                  </div>
                )}

                {/* Messages */}
                {error && (
                  <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-lg" onClick={clearMessages}>
                    <div className="flex">
                      <div className="flex-shrink-0">
                        <span className="material-symbols-outlined text-red-400">error</span>
                      </div>
                      <div className="ml-3">
                        <p className="text-sm text-red-800">{error}</p>
                      </div>
                    </div>
                  </div>
                )}

                {success && (
                  <div className="mt-4 p-4 bg-green-50 border border-green-200 rounded-lg" onClick={clearMessages}>
                    <div className="flex">
                      <div className="flex-shrink-0">
                        <span className="material-symbols-outlined text-green-400">check_circle</span>
                      </div>
                      <div className="ml-3">
                        <p className="text-sm text-green-800">{success}</p>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default UserProfileNew;