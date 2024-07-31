import { Box, Card, CardBody, Text } from "@chakra-ui/react";
import axios from "axios";
import { useEffect, useState } from "react";
import useAuthHeader from "react-auth-kit/hooks/useAuthHeader";
import config from "../../config.json";
import { useNavigate } from "react-router-dom";
import { UserResponseSchema } from "../../types/users";
import Nav from "../Nav/Nav";

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
        }).catch((error) => {
          console.log(error);
        });
    } else {
      navigate("/login");
    }
  }, [authHeader, navigate]);

  return (
    <Box display={"flex"}>
      <Nav activeLink="Home" />
      <Box flex="1" p={4} bg={"gray.100"} height={"100vh"} overflowY={"auto"}>
        <Card maxW='sm'>
          <CardBody>
            <Text>ID: {user?.id}</Text>
            <Text>Name: {user?.name}</Text>
            <Text>Email: {user?.email}</Text>
            <Text>Role: {user?.role}</Text>
            <Text>Created At: {user?.created_at}</Text>
          </CardBody>
        </Card>

      </Box>
    </Box>
  );
};

export default Home;
