import React, {children, createContext, useState, useEffect  } from "react";
const AuthContext = createContext();//creates a new context object/box to hold values
export const AuthProvider = ({children})=>{
// const [user,setUser] = useState(localStorage.getItem("user")
//       ? JSON.parse(localStorage.getItem("user"))
//       : null);
// const [token,setToken] = useState(localStorage.getItem("token")|| "");

  const [token, setToken] = useState("");
  const [user, setUser] = useState(null);

  useEffect(() => {
    const storedToken = localStorage.getItem("token");
    const storedUser = localStorage.getItem("user");

    if (storedToken) setToken(storedToken);
    if (storedUser) setUser(JSON.parse(storedUser));
  }, []);

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