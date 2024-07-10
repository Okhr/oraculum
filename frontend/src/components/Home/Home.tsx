import { Box, Text } from "@chakra-ui/react";
import axios from "axios";
import { useEffect, useState } from "react";
import useAuthHeader from "react-auth-kit/hooks/useAuthHeader";
import config from "../../config.json";
import { useNavigate } from "react-router-dom";
import { UserResponseSchema } from "../../types/user";

const Home = () => {
  const navigate = useNavigate();
  const authHeader = useAuthHeader();
  const [user, setUser] = useState<UserResponseSchema | null>(null);

  useEffect(() => {
    if (authHeader) {
      axios
        .get(config.API_URL + "/users/me", {
          headers: {
            Authorization: authHeader,
          },
        })
        .then((response) => {
          setUser(response.data);
        });
    } else {
      navigate("/login");
    }
  }, [authHeader, navigate, user]);

  return (
    <Box p={5} shadow="md" borderWidth="1px" borderRadius="md" bg="white">
      <Text fontSize="xl" fontWeight="bold" mb={2}>
        {user?.name}
      </Text>
      <Text fontSize="md" mb={1}>
        ID: {user?.id}
      </Text>
      <Text fontSize="md" mb={1}>
        Role: {user?.role}
      </Text>
      <Text fontSize="md">Created At: {user?.created_at}</Text>
    </Box>
  );
};

export default Home;
