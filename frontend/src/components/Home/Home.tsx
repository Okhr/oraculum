import { Box, Card, CardBody, Text, useMediaQuery } from "@chakra-ui/react";
import axios from "axios";
import { useEffect, useState } from "react";
import useAuthHeader from "react-auth-kit/hooks/useAuthHeader";
import config from "../../config.json";
import { useNavigate } from "react-router-dom";
import { UserResponseSchema } from "../../types/users";
import Nav from "../Nav/Nav";
import MobileNav from "../MobileNav/MobileNav";

const Home = () => {
  const [isLargerThan768] = useMediaQuery('(min-width: 768px)');
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
      {isLargerThan768 ? <Nav activeLink="Home" /> : <MobileNav activeLink="Home" />}
      <Box flex="1" p={4} mt={isLargerThan768 ? 0 : 20} bg={"gray.100"} height={"100vh"} overflowY={"auto"}>
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
