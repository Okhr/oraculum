import { useForm } from 'react-hook-form';
import { yupResolver } from '@hookform/resolvers/yup';
import * as yup from 'yup';
import {
  Box,
  Button,
  FormControl,
  FormLabel,
  Input,
  VStack,
  Center,
  FormErrorMessage,
} from '@chakra-ui/react';

type FormValues = {
  name: string;
  email: string;
  password: string;
  passwordConfirm: string;
};

const schema = yup.object().shape({
  name: yup.string().required('Name is required'),
  email: yup.string().email('Email is invalid').required('Email is required'),
  password: yup.string().min(8, 'Password must be at least 8 characters').required('Password is required'),
  passwordConfirm: yup.string()
    .oneOf([yup.ref('password')], 'Passwords must match')
    .required('Confirm Password is required'),
});

const RegistrationForm = () => {
  const { register, handleSubmit, formState: { errors } } = useForm<FormValues>({
    resolver: yupResolver(schema),
  });

  const onSubmit = (data: FormValues) => {
    console.log(data);
  };

  return (
    <Center height="100vh">
      <Box p={5} border='1px' borderColor="gray.200" boxShadow="md" rounded="md" bg="white">
        <form onSubmit={handleSubmit(onSubmit)}>
          <VStack spacing={5}>
            <FormControl isInvalid={!!errors.name}>
              <FormLabel htmlFor="name">Name</FormLabel>
              <Input id="name" {...register('name')} />
              <FormErrorMessage>{errors.name?.message}</FormErrorMessage>
            </FormControl>
            <FormControl isInvalid={!!errors.email}>
              <FormLabel htmlFor="email">Email</FormLabel>
              <Input id="email" type="email" {...register('email')} />
              <FormErrorMessage>{errors.email?.message}</FormErrorMessage>
            </FormControl>
            <FormControl isInvalid={!!errors.password}>
              <FormLabel htmlFor="password">Password</FormLabel>
              <Input id="password" type="password" {...register('password')} />
              <FormErrorMessage>{errors.password?.message}</FormErrorMessage>
            </FormControl>
            <FormControl isInvalid={!!errors.passwordConfirm}>
              <FormLabel htmlFor="passwordConfirm">Confirm Password</FormLabel>
              <Input id="passwordConfirm" type="password" {...register('passwordConfirm')} />
              <FormErrorMessage>{errors.passwordConfirm?.message}</FormErrorMessage>
            </FormControl>
            <Button type="submit" colorScheme="blue">Register</Button>
          </VStack>
        </form>
      </Box>
    </Center>
  );
};

export default RegistrationForm;

