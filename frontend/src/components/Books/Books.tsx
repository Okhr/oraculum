import { Box, Heading, Text, Icon, TableContainer, Table, Thead, Tr, Th, Tbody, Td } from "@chakra-ui/react";
import { LuUpload } from 'react-icons/lu';
import { useDropzone } from 'react-dropzone';
import Nav from "../Nav/Nav";
import config from "../../config.json";
import { useCallback } from "react";
import { keyframes } from '@emotion/react';
import axios from "axios";
import { useNavigate } from "react-router-dom";
import useAuthHeader from "react-auth-kit/hooks/useAuthHeader";

const wiggle = keyframes`
  0% { transform: rotate(0deg); }
  25% { transform: rotate(5deg); }
  50% { transform: rotate(-5deg); }
  75% { transform: rotate(5deg); }
  100% { transform: rotate(0deg); }
`;

const books = [
  { id: 1, title: 'Book 1', author: 'Author 1', uploadDate: '2022-01-01' },
  { id: 2, title: 'Book 2', author: 'Author 2', uploadDate: '2022-02-01' },
  { id: 3, title: 'Book 3', author: 'Author 3', uploadDate: '2022-03-01' },
];

const Books = () => {

  const navigate = useNavigate();
  const authHeader = useAuthHeader();

  const onDrop = useCallback((acceptedFiles: File[]) => {
    const file = acceptedFiles[0];
    const formData = new FormData();
    formData.append('uploaded_file', file);

    axios.post(config.API_URL + '/books/upload/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
        'Authorization': authHeader,
      },
    })
      .then(response => {
        console.log(response.data);
        // Handle the response as needed
      })
      .catch(error => {
        if (error.response.status === 403 || error.response.status === 401) {
          navigate('/login');
        }
        console.error(error);
        // Handle the error as needed
      });
  }, [])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({ onDrop, maxFiles: 1, accept: { 'application/epub+zip': ['.epub'] } });

  return (
    <Box display={"flex"}>
      <Nav activeLink="Books" />
      <Box flex="1" p={4} bg={"gray.100"} height={"100vh"} overflowY={"auto"}>
        <Box maxW={{ base: "100%", md: "768px" }} mx="auto">
          <Heading size="lg" color={"gray.700"}>Upload a new book</Heading>
          <Box my={4}
            {...getRootProps()}
            p={4}
            borderWidth={2}
            borderRadius={8}
            borderColor="gray.300"
            borderStyle="dashed"
            textAlign="center"
            cursor="pointer"
            bg='white'
          >
            <Icon as={LuUpload} boxSize={16} mb={4} animation={isDragActive ? `${wiggle} 0.2s infinite` : 'none'} />
            <input {...getInputProps()} />
            {isDragActive ?
              <Text fontSize='xl'>Drop the file here</Text> :
              <Text fontSize='xl'>Drag'n drop an epub file here, or click to select a file</Text>
            }
          </Box>
          <Heading size="lg" color={"gray.700"}>Book collection</Heading>
          {books.length > 0 ? (
            <TableContainer mt={4} bg="white" borderRadius={8}>
              <Table variant='simple'>
                <Thead>
                  <Tr>
                    <Th textAlign="center">Title</Th>
                    <Th textAlign="center">Author</Th>
                    <Th textAlign="center">Upload Date</Th>
                  </Tr>
                </Thead>
                <Tbody>
                  {books.map(book => (
                    <Tr key={book.id}>
                      <Td textAlign="center">{book.title}</Td>
                      <Td textAlign="center">{book.author}</Td>
                      <Td textAlign="center">{book.uploadDate}</Td>
                    </Tr>
                  ))}
                </Tbody>
              </Table>
            </TableContainer>
          ) : (
            <Box mt={4} bg="white" borderRadius={8} p={4} textAlign="center">
              < Text fontSize='xl' color={"gray.700"}>No books available.</Text>
            </Box>
          )}
        </Box>
      </Box >
    </Box >
  );
};

export default Books;
