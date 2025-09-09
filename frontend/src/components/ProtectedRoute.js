/**
 * Protected Route Component
 */
import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import LoadingSpinner from './LoadingSpinner';

const ProtectedRoute = ({ 
  children, 
  requiredPermissions = [], 
  requiredRole = null,
  fallbackPath = '/login' 
}) => {
  const { isAuthenticated, user, loading } = useAuth();
  const location = useLocation();

  // Show loading spinner while checking authentication
  if (loading) {
    return <LoadingSpinner />;
  }

  // Redirect to login if not authenticated
  if (!isAuthenticated) {
    return (
      <Navigate 
        to={fallbackPath} 
        state={{ from: location }} 
        replace 
      />
    );
  }

  // Check role requirement
  if (requiredRole && user?.role?.name !== requiredRole) {
    return (
      <Navigate 
        to="/unauthorized" 
        state={{ 
          from: location,
          message: `This page requires ${requiredRole} role` 
        }} 
        replace 
      />
    );
  }

  // Check permission requirements
  if (requiredPermissions.length > 0) {
    const userPermissions = user?.role?.permissions || {};
    const hasPermission = requiredPermissions.every(permission => {
      const [resource, action] = permission.split(':');
      return userPermissions[resource]?.includes(action);
    });

    if (!hasPermission) {
      return (
        <Navigate 
          to="/unauthorized" 
          state={{ 
            from: location,
            message: `You don't have permission to access this page` 
          }} 
          replace 
        />
      );
    }
  }

  return children;
};

export default ProtectedRoute;









