import { useForm } from "react-hook-form";
import { yupResolver } from "@hookform/resolvers/yup";
import * as yup from "yup";
import {
  Box,
  Button,
  FormControl,
  FormLabel,
  Input,
  VStack,
  Center,
  FormErrorMessage,
  Text,
  Link,
  Heading,
} from "@chakra-ui/react";
import useSignIn from "react-auth-kit/hooks/useSignIn";
import config from "../../config.json";
import axios from "axios";
import toast from "react-hot-toast";
import { jwtDecode } from "jwt-decode";
import { useNavigate } from "react-router-dom";

type FormValues = {
  username: string;
  password: string;
};

const schema = yup.object().shape({
  username: yup.string().required("Username is required"),
  password: yup.string().required("Password is required"),
});

const LoginForm = () => {
  const signIn = useSignIn();
  const navigate = useNavigate();

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<FormValues>({
    resolver: yupResolver(schema),
  });

  const onSubmit = (data: FormValues) => {
    axios
      .post(config.API_URL + "/auth/login", data, {
        headers: { "Content-Type": "multipart/form-data" },
      })
      .then((response) => {
        if (response.status === 200) {
          if (
            signIn({
              auth: {
                token: response.data.access_token,
                type: "Bearer",
              },
              userState: {
                username: jwtDecode(response.data.access_token).sub,
              },
            })
          ) {
            toast.success("Login successful");
            navigate("/library");
          } else {
            toast.error("Error while signing in");
          }
        }
      })
      .catch((error) => {
        if (error.response) {
          toast.error(error.response.data.detail);
        } else if (error.request) {
          toast.error("Network error. Please try again.");
        } else {
          toast.error("An error occurred. Please try again.");
        }
      });
  };

  return (
    <Center height="100vh" bg={"gray.100"}>
      <Box
        p={5}
        border="1px"
        borderColor="gray.300"
        boxShadow="md"
        rounded="md"
        bg="white"
      >
        <Heading size="lg" color={"gray.700"} mb={4}>
          Login
        </Heading>
        <form onSubmit={handleSubmit(onSubmit)}>
          <VStack spacing={3}>
            <FormControl isInvalid={!!errors.username}>
              <FormLabel htmlFor="username">Username</FormLabel>
              <Input
                id="username"
                type="text"
                {...register("username")}
                autoComplete="on"
                _focus={{ boxShadow: '0 0 0 1px #805AD5', borderColor: '#805AD5' }}
              />
              <FormErrorMessage>{errors.username?.message}</FormErrorMessage>
            </FormControl>
            <FormControl isInvalid={!!errors.password}>
              <FormLabel htmlFor="password">Password</FormLabel>
              <Input
                id="password"
                type="password"
                {...register("password")}
                autoComplete="on"
                _focus={{ boxShadow: '0 0 0 1px #805AD5', borderColor: '#805AD5' }}
              />
              <FormErrorMessage>{errors.password?.message}</FormErrorMessage>
            </FormControl>
            <Button type="submit" colorScheme="purple">
              Login
            </Button>
            <Text fontSize="sm">
              Not a member?{" "}
              <Link color="purple.500" href="/register">
                Register
              </Link>
            </Text>
          </VStack>
        </form>
      </Box>
    </Center>
  );
};

export default LoginForm;

