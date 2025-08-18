import React, { Children } from "react";
import { useContext } from "react";
import { BrowserRouter, Routes, Route,Navigate } from "react-router-dom";
import { AuthProvider } from "./AuthContext";
import AuthContext from "./AuthContext";
import Signup from "./Signup";
import Login from "./Login";
import AddJob from "./AddJob";
import JobList from "./JobList";
import Dashboard  from "./Dashboard";
import Navbar from "./Navbar";
import JobDetail from "./JobDetail";
import ProfilePage from "./ProfilePage";

function useAuthToken(){
const context = useContext(AuthContext);//opens the box and gives you access to whatever is inside the context
return context?.token || localStorage.getItem("token");//got the token
};
const ProtectedRoute = ({children})=>{
  const token = useAuthToken();//get the token
  return token?children:<Navigate to="/login" replace />;
};
const AuthRedirect = ({ children }) => {
  const token = useAuthToken();
  return token ? <Navigate to="/dashboard" replace /> : children;
};
const RootRedirect = () => {
  const token = useAuthToken();
  return token ? <Navigate to="/dashboard" replace /> : <Navigate to="/login" replace />;
};

export default function App(){
return (
  <AuthProvider>
    <BrowserRouter>
      {/* Navbar only when NOT on login/signup */}
      {window.location.pathname !== "/login" && window.location.pathname !== "/signup" && (
        <Navbar />
      )}

      <div className="container-fluid p-3">
        <Routes>
          <Route path="/" element={<RootRedirect />} />
          <Route path="/login" element={<AuthRedirect><Login /></AuthRedirect>} />
          <Route path="/signup" element={<AuthRedirect><Signup /></AuthRedirect>} />
          <Route path="/dashboard" element={<ProtectedRoute><Dashboard /></ProtectedRoute>} />
          <Route path="/jobs" element={<ProtectedRoute><JobList /></ProtectedRoute>} />
          <Route path="/jobs/:id" element={<ProtectedRoute><JobDetail /></ProtectedRoute>} />
          <Route path="/add-job" element={<ProtectedRoute><AddJob /></ProtectedRoute>} />
          <Route path="/profile" element={<ProtectedRoute><ProfilePage /></ProtectedRoute>} />
        </Routes>
      </div>
    </BrowserRouter>
  </AuthProvider>
);

}
