/**
 * Role Selector Component
 */
import React, { useState } from 'react';
import './RoleSelector.css';

const RoleSelector = ({ 
  roles = [], 
  value = '', 
  onChange, 
  disabled = false 
}) => {
  const [isOpen, setIsOpen] = useState(false);

  const selectedRole = roles.find(role => role.id === value);

  const handleRoleSelect = (roleId) => {
    console.log('Role selected:', roleId);
    if (onChange) {
      onChange(roleId);
    }
    setIsOpen(false);
  };

  const handleToggle = () => {
    if (!disabled) {
      setIsOpen(!isOpen);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault();
      handleToggle();
    } else if (e.key === 'Escape') {
      setIsOpen(false);
    }
  };

  return (
    <div className="role-selector">
      <div
        className={`role-selector-trigger ${isOpen ? 'open' : ''} ${disabled ? 'disabled' : ''}`}
        onClick={handleToggle}
        onKeyDown={handleKeyDown}
        tabIndex={disabled ? -1 : 0}
        role="button"
        aria-haspopup="listbox"
        aria-expanded={isOpen}
      >
        <div className="role-selector-content">
          {selectedRole ? (
            <>
              <span className="role-name">{selectedRole.description}</span>
              <span className="role-type">{selectedRole.name}</span>
            </>
          ) : (
            <span className="role-placeholder">Select a role</span>
          )}
        </div>
        <span className="role-selector-arrow">
          {isOpen ? '▲' : '▼'}
        </span>
      </div>

      {isOpen && (
        <div className="role-selector-dropdown">
          {roles.map(role => (
            <div
              key={role.id}
              className={`role-option ${value === role.id ? 'selected' : ''}`}
              onClick={() => handleRoleSelect(role.id)}
              onKeyDown={(e) => {
                if (e.key === 'Enter' || e.key === ' ') {
                  e.preventDefault();
                  handleRoleSelect(role.id);
                }
              }}
              tabIndex={0}
              role="option"
              aria-selected={value === role.id}
            >
              <div className="role-option-content">
                <div className="role-option-name">{role.description}</div>
                <div className="role-option-type">{role.name}</div>
                {role.permissions && (
                  <div className="role-option-permissions">
                    {Array.isArray(role.permissions) ? (
                      // If permissions is an array, display it directly
                      role.permissions.map((permission, index) => (
                        <span key={index} className="permission-tag">
                          {permission}
                        </span>
                      ))
                    ) : (
                      // If permissions is an object, display key-value pairs
                      Object.entries(role.permissions).map(([resource, actions]) => (
                        <span key={resource} className="permission-tag">
                          {resource}: {Array.isArray(actions) ? actions.join(', ') : actions}
                        </span>
                      ))
                    )}
                  </div>
                )}
              </div>
              {value === role.id && (
                <span className="role-option-check">✓</span>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default RoleSelector;


