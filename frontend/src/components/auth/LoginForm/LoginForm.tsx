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
} from "@chakra-ui/react";
import useSignIn from "react-auth-kit/hooks/useSignIn";
import config from "../../../config.json";
import axios from "axios";
import toast from "react-hot-toast";
import { jwtDecode } from "jwt-decode";

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

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<FormValues>({
    resolver: yupResolver(schema),
  });

  const onSubmit = (data: FormValues) => {
    console.log(data);
    axios
      .post(config.API_URL + "/auth/login", data, {
        headers: { "Content-Type": "multipart/form-data" },
      })
      .then((response) => {
        if (response.status === 200) {
          console.log(jwtDecode(response.data.access_token));
          if (
            signIn({
              auth: {
                token: response.data.access_token,
                type: "Bearer",
              },
            })
          ) {
            toast.success("Login successful");
          } else {
            toast.error("Error while signing in");
          }
        }
      })
      .catch((error) => {
        toast.error(error.response.data.detail);
      });
  };

  return (
    <Center height="100vh">
      <Box
        p={5}
        border="1px"
        borderColor="gray.200"
        boxShadow="md"
        rounded="md"
        bg="white"
      >
        <form onSubmit={handleSubmit(onSubmit)}>
          <VStack spacing={5}>
            <FormControl isInvalid={!!errors.username}>
              <FormLabel htmlFor="username">Username</FormLabel>
              <Input id="username" type="text" {...register("username")} />
              <FormErrorMessage>{errors.username?.message}</FormErrorMessage>
            </FormControl>
            <FormControl isInvalid={!!errors.password}>
              <FormLabel htmlFor="password">Password</FormLabel>
              <Input id="password" type="password" {...register("password")} />
              <FormErrorMessage>{errors.password?.message}</FormErrorMessage>
            </FormControl>
            <Button type="submit" colorScheme="blue">
              Login
            </Button>
            <Text fontSize="sm">
              Not a member?{" "}
              <Link color="blue.500" href="/register">
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
