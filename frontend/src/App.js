import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import LoginForm from './components/LoginForm';
import Layout from './components/Layout';
import DashboardNew from './components/DashboardNew';
import CandidateList from './components/CandidateList';
import CandidateForm from './components/CandidateForm';
import CandidateDetail from './components/CandidateDetail';
import InterviewCalendar from './components/InterviewCalendar';
import CaseStudyList from './components/CaseStudyList';
import RoleList from './components/RoleList';
import UserList from './components/UserList';
import ProtectedRoute from './components/ProtectedRoute';
import './App.css';

// Main App component with routing
function AppContent() {
  const { isAuthenticated, loading } = useAuth();

  if (loading) {
    return (
      <div className="loading-container">
        <div className="loading-spinner"></div>
        <p>Loading...</p>
      </div>
    );
  }

  return (
    <Router future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
      <div className="App">
        <Routes>
          <Route 
            path="/login" 
            element={
              isAuthenticated ? <Navigate to="/dashboard" replace /> : <LoginForm />
            } 
          />
          <Route 
            path="/" 
            element={
              <ProtectedRoute>
                <Layout />
              </ProtectedRoute>
            }
          >
            <Route index element={<Navigate to="/dashboard" replace />} />
            <Route path="dashboard" element={<DashboardNew />} />
            <Route path="candidates" element={<CandidateList />} />
            <Route path="candidates/new" element={<CandidateForm />} />
            <Route path="candidates/:id" element={<CandidateDetail />} />
            <Route path="candidates/:id/edit" element={<CandidateForm />} />
            <Route path="interviews" element={<InterviewCalendar />} />
            <Route path="case-studies" element={<CaseStudyList />} />
            <Route path="users" element={<UserList />} />
            <Route path="roles" element={<RoleList />} />
            <Route path="reports" element={<div className="p-8"><h1 className="text-2xl font-bold">Raporlar</h1><p className="text-gray-600">Bu sayfa yakında eklenecek...</p></div>} />
          </Route>
        </Routes>
      </div>
    </Router>
  );
}

// App wrapper with AuthProvider
function App() {
  return (
    <AuthProvider>
      <AppContent />
    </AuthProvider>
  );
}

export default App;
