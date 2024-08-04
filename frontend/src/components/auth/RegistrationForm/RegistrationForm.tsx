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
  email: yup
    .string()
    .matches(
      /^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$/i,
      "Email must be a valid email address"
    )
    .required("Email is required"),
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
          toast.success("Successfully registered");
          navigate("/login");
        }
      })
      .catch((error) => {
        console.log(error)
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
          Register
        </Heading>
        <form onSubmit={handleSubmit(onSubmit)}>
          <VStack spacing={3}>
            <FormControl isInvalid={!!errors.name}>
              <FormLabel htmlFor="name">Username</FormLabel>
              <Input
                id="name"
                type="text"
                {...register("name")}
                autoComplete="on"
                _focus={{ boxShadow: '0 0 0 1px #805AD5', borderColor: '#805AD5' }}
              />
              <FormErrorMessage>{errors.name?.message}</FormErrorMessage>
            </FormControl>
            <FormControl isInvalid={!!errors.email}>
              <FormLabel htmlFor="email">Email</FormLabel>
              <Input
                id="email"
                type="text"
                {...register("email")}
                autoComplete="on"
                _focus={{ boxShadow: '0 0 0 1px #805AD5', borderColor: '#805AD5' }}
              />
              <FormErrorMessage>{errors.email?.message}</FormErrorMessage>
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
            <FormControl isInvalid={!!errors.password_confirm}>
              <FormLabel htmlFor="password_confirm">Confirm Password</FormLabel>
              <Input
                id="password_confirm"
                type="password"
                {...register("password_confirm")}
                autoComplete="on"
                _focus={{ boxShadow: '0 0 0 1px #805AD5', borderColor: '#805AD5' }}
              />
              <FormErrorMessage>
                {errors.password_confirm?.message}
              </FormErrorMessage>
            </FormControl>
            <Button type="submit" colorScheme="purple">
              Register
            </Button>
            <Text fontSize="sm">
              Already have an account?{" "}
              <Link color="purple.500" href="/login">
                Login
              </Link>
            </Text>
          </VStack>
        </form>
      </Box>
    </Center>
  );
};

export default RegistrationForm;

