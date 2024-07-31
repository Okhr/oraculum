import { Box, Button, ButtonGroup, Heading, Icon, Table, TableContainer, Tbody, Td, Text, Th, Thead, Tr } from "@chakra-ui/react";
import { keyframes } from '@emotion/react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { useCallback, useState } from "react";
import { FileRejection, useDropzone } from 'react-dropzone';
import toast from "react-hot-toast";
import { LuUpload } from 'react-icons/lu';
import { useNavigate } from "react-router-dom";
import { useGetUploadedBooks, useUploadBook } from '../../apis/books';
import { BookResponseSchema } from '../../types/books';
import Nav from "../Nav/Nav";
import { AxiosError } from "axios";

const wiggle = keyframes`
  0% { transform: rotate(0deg); }
  25% { transform: rotate(5deg); }
  50% { transform: rotate(-5deg); }
  75% { transform: rotate(5deg); }
  100% { transform: rotate(0deg); }
`;

const Books = () => {
  const navigate = useNavigate();

  const { uploadBook } = useUploadBook();
  const { getUploadedBooks } = useGetUploadedBooks();

  const [acceptedFiles, setAcceptedFiles] = useState<File[]>([]);
  const [_, setRejectedFiles] = useState<FileRejection[]>([]);

  const queryClient = useQueryClient();
  const { data: uploadedBooks, isLoading, isError } = useQuery({
    queryKey: ['uploadedBooks'],
    queryFn: getUploadedBooks,
  });
  const uploadMutation = useMutation({
    mutationFn: uploadBook,
    onSuccess: () => {
      // Invalidate and refetch
      queryClient.invalidateQueries({ queryKey: ['uploadedBooks'] })
    },
    onError: (error: AxiosError) => {
      if (error.response && (error.response.status === 401 || error.response.status === 403)) {
        toast.error('Not authenticated. Please login.');
        navigate('/login');
      } else {
        console.log(error)
        toast.error("An error occurred");
      }
    }
  })

  const onDrop = useCallback((newFiles: File[], rejectedFiles: FileRejection[]) => {
    setAcceptedFiles(prevAcceptedFiles => [...prevAcceptedFiles, ...newFiles]);
    setRejectedFiles(prevRejectedFiles => [...prevRejectedFiles, ...rejectedFiles]);
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({ onDrop, accept: { 'application/epub+zip': ['.epub'] } });

  const uploadFiles = () => {
    for (const file of acceptedFiles) {
      uploadMutation.mutate(file);
    }
    setAcceptedFiles([]);
    setRejectedFiles([]);
  }

  return (
    <Box display={"flex"}>
      <Nav activeLink="Books" />
      <Box flex="1" p={4} bg={"gray.100"} height={"100vh"} overflowY={"auto"}>
        <Box maxW={{ base: "100%", md: "768px" }} mx="auto">
          <Heading size="lg" color={"gray.700"}>Upload new books</Heading>
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
              <Text fontSize='xl'>Drop the files here</Text> :
              acceptedFiles.length > 0 ?
                <Text fontSize='xl'>{acceptedFiles.length} files selected, drop more or click to select more files</Text> :
                <Text fontSize='xl'>Drop epub files here, or click to select files</Text>
            }
          </Box>
          {acceptedFiles.length > 0 && (
            <Box display="flex" justifyContent="flex-end" mb={4}>
              <ButtonGroup gap='2'>
                <Button colorScheme='purple' variant='outline' onClick={uploadFiles}>
                  Upload {acceptedFiles.length} book{acceptedFiles.length > 1 ? 's' : ''}
                </Button>
                <Button colorScheme='black' variant='outline' onClick={() => {
                  setAcceptedFiles([])
                  setRejectedFiles([])
                }}>
                  Cancel Upload
                </Button>
              </ButtonGroup>
            </Box>

          )}

          <Heading size="lg" color={"gray.700"}>Book collection</Heading>
          {uploadedBooks && uploadedBooks.length > 0 ? (
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
                  {uploadedBooks.map(book => (
                    <Tr key={book.id}>
                      <Td textAlign="center">{book.title}</Td>
                      <Td textAlign="center">{book.author}</Td>
                      <Td textAlign="center">{book.upload_date}</Td>
                    </Tr>
                  ))}
                </Tbody>
              </Table>
            </TableContainer>
          ) : (
            <Box mt={4} bg="white" borderRadius={8} p={4} textAlign="center">
              <Text fontSize='xl' color={"gray.700"}>No books available.</Text>
            </Box>
          )}
        </Box>
      </Box >
    </Box >
  );
};

export default Books;