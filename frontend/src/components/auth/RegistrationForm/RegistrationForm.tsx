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
import config from "../../../config.json";
import axios from "axios";
import toast from "react-hot-toast";
import { useNavigate } from "react-router-dom";

type FormValues = {
  name: string;
  email: string;
  password: string;
  password_confirm: string;
};

const schema = yup.object().shape({
  name: yup.string().required("Username is required"),
  email: yup.string().email("Email is invalid").required("Email is required"),
  password: yup
    .string()
    .min(8, "Password must be at least 8 characters")
    .required("Password is required"),
  password_confirm: yup
    .string()
    .oneOf([yup.ref("password")], "Passwords must match")
    .required("Confirm Password is required"),
});

const RegistrationForm = () => {
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
      .post(config.API_URL + "/auth/register", data)
      .then((response) => {
        if (response.status === 201) {
          toast.success("Succesfully registered");
          navigate("/login");
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
            <FormControl isInvalid={!!errors.name}>
              <FormLabel htmlFor="name">Username</FormLabel>
              <Input id="name" {...register("name")} />
              <FormErrorMessage>{errors.name?.message}</FormErrorMessage>
            </FormControl>
            <FormControl isInvalid={!!errors.email}>
              <FormLabel htmlFor="email">Email</FormLabel>
              <Input id="email" type="email" {...register("email")} />
              <FormErrorMessage>{errors.email?.message}</FormErrorMessage>
            </FormControl>
            <FormControl isInvalid={!!errors.password}>
              <FormLabel htmlFor="password">Password</FormLabel>
              <Input id="password" type="password" {...register("password")} />
              <FormErrorMessage>{errors.password?.message}</FormErrorMessage>
            </FormControl>
            <FormControl isInvalid={!!errors.password_confirm}>
              <FormLabel htmlFor="password_confirm">Confirm Password</FormLabel>
              <Input
                id="password_confirm"
                type="password"
                {...register("password_confirm")}
              />
              <FormErrorMessage>
                {errors.password_confirm?.message}
              </FormErrorMessage>
            </FormControl>
            <Button type="submit" colorScheme="blue">
              Register
            </Button>
            <Box>
              <Text>
                Already have an account?{" "}
                <Link color="blue.500" href="/login">
                  Login
                </Link>
              </Text>
            </Box>
          </VStack>
        </form>
      </Box>
    </Center>
  );
};

export default RegistrationForm;
