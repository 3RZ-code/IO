import React from 'react';
import { Navigate, Outlet } from 'react-router-dom';

const ProtectedRoute = () => {
    // Basic check for token. 
    // Ideally verify token validity, but for now existence is enough.
    const isAuthenticated = localStorage.getItem('token');

    if (!isAuthenticated) {
        return <Navigate to="/login" replace />;
    }

    return <Outlet />;
};

export default ProtectedRoute;
