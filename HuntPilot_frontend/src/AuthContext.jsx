import React, {children, createContext, useState, useEffect  } from "react";
const AuthContext = createContext();//creates a new context object/box to hold values
export const AuthProvider = ({children})=>{
const [token, setToken] = useState(() => localStorage.getItem("token") || "");
  const [user, setUser] = useState(() => {
    const storedUser = localStorage.getItem("user");
    return storedUser ? JSON.parse(storedUser) : null;
  });

const login= ({token,user}) =>{//data sent by backend
setUser(user);
setToken(token);
localStorage.setItem("token",token);
localStorage.setItem("user", JSON.stringify(user));
};

const logout= () =>{
setUser(null);
setToken("");
localStorage.removeItem("token");
localStorage.removeItem("user");
};

  return(
    <AuthContext.Provider value ={{user,token,login,logout}}>
      {/* Wraps your app and supplies values (like token, user) into the context */}
      {children}
    </AuthContext.Provider>
  )
};
export default AuthContext;