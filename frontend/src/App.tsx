import {
  BrowserRouter as Router,
  Route,
  Routes,
  Navigate,
} from "react-router-dom";
import { ChakraProvider } from "@chakra-ui/react";
import AuthProvider from "react-auth-kit";
import { QueryClientProvider, QueryClient } from '@tanstack/react-query';
import { ReactQueryDevtools } from '@tanstack/react-query-devtools';
import RequireAuth from "@auth-kit/react-router/RequireAuth";
import createStore from "react-auth-kit/createStore";
import RegistrationForm from "./components/auth/RegistrationForm/RegistrationForm.tsx";
import LoginForm from "./components/auth/LoginForm/LoginForm.tsx";
import Home from "./components/Home/Home.tsx";
import "./App.css";
import { Toaster } from "react-hot-toast";
import Books from "./components/Books/Books.tsx";

const store = createStore({
  authName: "_auth",
  authType: "cookie",
  cookieDomain: window.location.hostname,
  cookieSecure: window.location.protocol === "https:",
});

const queryClient = new QueryClient()

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <AuthProvider store={store}>
        <ChakraProvider>
          <Router>
            <Routes>
              <Route path="/" element={<Navigate replace to="/home" />} />
              <Route
                path="/home"
                element={
                  <RequireAuth fallbackPath={"/login"}>
                    <Home />
                  </RequireAuth>
                }
              />
              <Route
                path="/books"
                element={
                  <RequireAuth fallbackPath={"/login"}>
                    <Books />
                  </RequireAuth>
                }
              />
              <Route path="/register" element={<RegistrationForm />} />
              <Route path="/login" element={<LoginForm />} />
            </Routes>
          </Router>
          <Toaster
            position="top-right"
            gutter={8}
            toastOptions={{ duration: 3000 }}
          />
          <ReactQueryDevtools initialIsOpen={false} />
        </ChakraProvider>
      </AuthProvider>
    </QueryClientProvider>
  );
}

export default App;
