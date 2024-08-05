import { Box, Button, ButtonGroup, Heading, Icon, IconButton, Input, Modal, ModalBody, ModalCloseButton, ModalContent, ModalFooter, ModalHeader, ModalOverlay, Table, TableContainer, Tbody, Td, Text, Th, Thead, Tr, useDisclosure } from "@chakra-ui/react";
import { keyframes } from '@emotion/react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { useCallback, useState } from "react";
import { FileRejection, useDropzone } from 'react-dropzone';
import toast from "react-hot-toast";
import { LuUpload } from 'react-icons/lu';
import { useNavigate } from "react-router-dom";
import { useDeleteBook, useGetUserBooks, useUpdateBook, useUploadBook } from '../../apis/books';
import { BookResponseSchema, BookUpdateSchema, BookUploadResponseSchema } from '../../types/books';
import Nav from "../Nav/Nav";
import { AxiosError } from "axios";
import { FaEdit, FaPen, FaTrash } from "react-icons/fa";
import { string } from "yup";
import { set } from "react-hook-form";

const wiggle = keyframes`
  0% { transform: rotate(0deg); }
  25% { transform: rotate(5deg); }
  50% { transform: rotate(-5deg); }
  75% { transform: rotate(5deg); }
  100% { transform: rotate(0deg); }
`;

const Books = () => {
  const navigate = useNavigate();

  const { getUserBooks } = useGetUserBooks();
  const { uploadBook } = useUploadBook();
  const { deleteBook } = useDeleteBook();
  const { updateBook } = useUpdateBook();

  const queryClient = useQueryClient();

  const { data: userBooks } = useQuery({
    queryKey: ['userBooks'],
    queryFn: getUserBooks,
  });

  const uploadMutation = useMutation({
    mutationFn: uploadBook,
    onSuccess: (data: BookUploadResponseSchema) => {
      queryClient.invalidateQueries({ queryKey: ['userBooks'] })
      toast.success(`The book "${data.original_file_name}" was uploaded successfully`);
    },
    onError: (error: AxiosError, file: File) => {
      if (error.response) {
        if (error.response.status === 401 || error.response.status === 403) {
          toast.error('Not authenticated. Please login.');
          navigate('/login');
        } else if (error.response.status === 409) {
          toast.error(`The book "${file.name}" already exists.`);
        } else {
          console.log(error)
          toast.error("An error occurred");
        }
      } else {
        console.log(error)
        toast.error("An error occurred");
      }
    }
  })

  const deleteMutation = useMutation({
    mutationFn: deleteBook,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['userBooks'] })
    },
    onError: (error: AxiosError) => {
      if (error.response) {
        if (error.response.status === 401 || error.response.status === 403) {
          toast.error('Not authenticated. Please login.');
          navigate('/login');
        } else if (error.response.status === 404) {
          toast.error('The book doesn\'t exist');
        } else {
          console.log(error)
          toast.error("An error occurred");
        }
      } else {
        console.log(error)
        toast.error("An error occurred");
      }
    }
  })

  const updateMutation = useMutation({
    mutationFn: (variables: { bookId: string, bookUpdate: BookUpdateSchema }) => updateBook(variables.bookId, variables.bookUpdate),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['userBooks'] })
    },
    onError: (error: AxiosError) => {
      if (error.response) {
        if (error.response.status === 401 || error.response.status === 403) {
          toast.error('Not authenticated. Please login.');
          navigate('/login');
        } else if (error.response.status === 404) {
          toast.error('The book doesn\'t exist');
        } else {
          console.log(error)
          toast.error("An error occurred");
        }
      } else {
        console.log(error)
        toast.error("An error occurred");
      }
    }
  })

  const [acceptedFiles, setAcceptedFiles] = useState<File[]>([]);
  const [_, setRejectedFiles] = useState<FileRejection[]>([]);

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

  const { isOpen, onOpen, onClose } = useDisclosure();
  const [editedBookId, setEditedBookId] = useState<string | null>(null);
  const [editedBookContent, setEditedBookContent] = useState<BookUpdateSchema>({ author: undefined, title: undefined });

  const handleEdit = (bookId: string) => {
    setEditedBookId(bookId);
    onOpen();
  };

  const handleSave = () => {
    if (editedBookId) {
      updateMutation.mutate({ bookId: editedBookId, bookUpdate: editedBookContent });
      setEditedBookContent({ author: undefined, title: undefined });
      onClose();
    }
  };

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

          <Heading size="lg" color={"gray.700"}>My library</Heading>
          {userBooks && userBooks.length > 0 ? (
            <Box mt={4} display="flex" flexWrap="wrap" gap={4}>
              {userBooks.map(book => (
                <Box key={book.id} bg="white" borderRadius={8} p={4} flex="1 0 200px" display="flex" flexDirection="column" justifyContent="space-between">
                  <Box>
                    <Text fontWeight="bold" textAlign="center" overflow="hidden" textOverflow="ellipsis" whiteSpace="nowrap">
                      <Box display="flex" alignItems="center" justifyContent="center">
                        <Box position="relative" display="inline-block">
                          {book.title}
                          <Icon
                            as={FaPen}
                            color={"gray.500"}
                            size={"xs"}
                            aria-label="Edit book title"
                            onClick={() => handleEdit(book.id)}
                            position="absolute"
                            top="50%"
                            right="-25px"
                            transform="translateY(-50%)"
                          />
                        </Box>
                      </Box>
                    </Text>
                    <Text textAlign="center" overflow="hidden" textOverflow="ellipsis" whiteSpace="nowrap">
                      {book.author}
                    </Text>
                    <Text textAlign="center">
                      {new Date(book.upload_date).toLocaleDateString()}
                    </Text>
                  </Box>
                  <Box display="flex" justifyContent="space-between" mt={4}>
                    <IconButton
                      colorScheme="purple"
                      variant="outline"
                      size="sm"
                      aria-label="Edit book"
                      icon={<FaEdit />}
                      onClick={() => handleEdit(book.id)}
                    />
                    <IconButton
                      colorScheme='red'
                      variant='outline'
                      size='sm'
                      aria-label='Delete book'
                      icon={<FaTrash />}
                      onClick={() => deleteMutation.mutate(book.id)}
                    />
                  </Box>
                </Box>
              ))}
            </Box>
          ) : (
            <Box mt={4} bg="white" borderRadius={8} p={4} textAlign="center">
              <Text fontSize='xl' color={"gray.700"}>No books available.</Text>
            </Box>
          )}

          <Modal isOpen={isOpen} onClose={onClose} isCentered>
            <ModalOverlay />
            <ModalContent>
              <ModalHeader>Edit Book</ModalHeader>
              <ModalCloseButton />
              <ModalBody>
                <Input
                  placeholder="Title"
                  value={editedBookContent?.title}
                  onChange={(e) =>
                    setEditedBookContent((prev) => ({ ...prev!, title: e.target.value }))
                  }
                />
                <Input
                  placeholder="Author"
                  value={editedBookContent?.author}
                  onChange={(e) =>
                    setEditedBookContent((prev) => ({ ...prev!, author: e.target.value }))
                  }
                />
              </ModalBody>
              <ModalFooter>
                <Button colorScheme="blue" mr={3} onClick={handleSave}>
                  Save
                </Button>
                <Button variant="ghost" onClick={onClose}>
                  Cancel
                </Button>
              </ModalFooter>
            </ModalContent>
          </Modal>
        </Box>
      </Box >
    </Box >
  );
};

export default Books;
