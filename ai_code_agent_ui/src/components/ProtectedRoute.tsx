import React from 'react';
import { Navigate, Outlet } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

export const ProtectedRoute: React.FC = () => {
    const { user } = useAuth();

    // If user is absent from memory, drop them back to login page safely
    return user ? <Outlet /> : <Navigate to="/signIn" replace />;
};
