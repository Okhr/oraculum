import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import { ChakraProvider } from '@chakra-ui/react';
import RegistrationForm from './components/auth/RegistrationForm/RegistrationForm.tsx';
import LoginForm from './components/auth/LoginForm/LoginForm.tsx';
import Home from './components/Home/Home.tsx';
import './App.css';

function App() {
  return (
    <ChakraProvider>
      <Router>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/register" element={<RegistrationForm />} />
          <Route path="/login" element={<LoginForm />} />
        </Routes>
      </Router>
    </ChakraProvider>
  );
}

export default App;
