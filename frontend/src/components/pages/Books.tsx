import { Box, Button, ButtonGroup, Card, CardBody, Heading, HStack, Icon, Input, Modal, ModalBody, ModalCloseButton, ModalContent, ModalFooter, ModalHeader, ModalOverlay, Text, useDisclosure, useMediaQuery, VStack } from "@chakra-ui/react";
import { keyframes } from '@emotion/react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { useCallback, useEffect, useState } from "react";
import { FileRejection, useDropzone } from 'react-dropzone';
import toast from "react-hot-toast";
import { LuUpload } from 'react-icons/lu';
import { useNavigate } from "react-router-dom";
import { useDeleteBook, useGetUserBooks, useUpdateBook, useUploadBook } from '../../apis/books';
import { BookUpdateSchema, BookUploadResponseSchema } from '../../types/books';
import Nav from "../navigation/Nav";
import MobileNav from "../navigation/MobileNav";
import { AxiosError } from "axios";
import { FaCheck, FaPen, FaTrash } from "react-icons/fa";
import BookSelector from "../state/BookSelector";

const wiggle = keyframes`
  0% { transform: rotate(0deg); }
  25% { transform: rotate(5deg); }
  50% { transform: rotate(-5deg); }
  75% { transform: rotate(5deg); }
  100% { transform: rotate(0deg); }
`;

const up = keyframes`
  0% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-5px);
  }
  100% {
    transform: translateY(0);
  }
`;

const Books = () => {
  const [isLargerThan768] = useMediaQuery('(min-width: 768px)');
  const navigate = useNavigate();

  const { getUserBooks } = useGetUserBooks();
  const { uploadBook } = useUploadBook();
  const { deleteBook } = useDeleteBook();
  const { updateBook } = useUpdateBook();

  const queryClient = useQueryClient();

  const { data: userBooks, isError: isUserBooksError, error: userBooksError } = useQuery({
    queryKey: ['userBooks'],
    queryFn: getUserBooks,
    refetchInterval: 10000,
  });

  useEffect(() => {
    if (isUserBooksError) {
      if (userBooksError instanceof AxiosError && (userBooksError.response?.status === 401 || userBooksError.response?.status === 403)) {
        toast.error('Not authenticated. Please login.');
        navigate('/login');
      } else {
        console.error('Error fetching user books:', userBooksError);
      }
    }
  }, [isUserBooksError, userBooksError, navigate]);

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

  const handleEdit = (bookId: string, bookContent: BookUpdateSchema) => {
    setEditedBookId(bookId);
    setEditedBookContent(bookContent);
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
    <Box display="flex" flexDirection={{ base: "column", md: "row" }}>
      {isLargerThan768 ? <Nav activeLink="Library" /> : <MobileNav activeLink="Library" />}
      <Box flex="1" p={4} mt={isLargerThan768 ? 0 : 20} bg="gray.100" height="100vh" overflowY="auto">
        <Box maxW={{ base: "100%", md: "5xl" }} mx="auto">
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

          <Heading size="lg" color={"gray.700"}>Current Book</Heading>
          <BookSelector />

          <Heading size="lg" color={"gray.700"}>My library</Heading>
          {userBooks && userBooks.length > 0 ? (
            <Box my={4} display="grid" gridTemplateColumns="repeat(auto-fill, minmax(300px, 1fr))" gap={4}>
              {userBooks.sort((a, b) => new Date(b.upload_date).getTime() - new Date(a.upload_date).getTime()).map(book => (
                <Card key={book.id} borderRadius={4} overflow="hidden" display="flex" flexDirection="row" height={"200px"}>
                  <Box
                    display="flex"
                    alignItems="center"
                    justifyContent="center"
                    p={4}
                    height={"100%"}
                    width={"150px"}
                    overflow="hidden"
                  >
                    <Box
                      style={{
                        backgroundImage: book.cover_image_base64 ? `url(data:image/jpeg;base64,${book.cover_image_base64})` : 'url(/images/placeholder.jpg)'
                      }}
                      backgroundSize="100% 100%"
                      backgroundRepeat="no-repeat"
                      backgroundPosition="center"
                      width="100%"
                      height="100%"
                      borderRadius={4}
                      boxShadow="0 2px 4px rgba(0, 0, 0, 0.2)"
                    />
                  </Box>
                  <CardBody py={4} pl={0} pr={4} flex="1" display="flex" flexDirection="column" justifyContent="space-between" alignItems="flex-end">
                    <VStack align='end' spacing='2'>
                      <Text fontWeight="bold" fontSize="md" textAlign="right" noOfLines={3} textOverflow="ellipsis">{book.title}</Text>
                      <Text fontSize="sm" textAlign="right" noOfLines={1} textOverflow="ellipsis">{book.author}</Text>
                      <Text fontSize="sm" fontStyle="italic" textAlign="right">Uploaded : {new Date(book.upload_date).toLocaleDateString('en-US', { year: '2-digit', month: 'short', day: 'numeric' })}</Text>
                    </VStack>
                    <HStack spacing={4}>
                      {book.is_parsed ? (
                        <Text fontSize="sm" color="gray.500">
                          <Icon as={FaCheck} boxSize={3} color="gray.500" transform="translateY(1px)" /> Extracted
                        </Text>
                      ) : (
                        <Text fontSize="sm" color="gray.500">
                          Extracting
                          <Text as="span" animation={`${up} 1s infinite`} display="inline-block" mx={1}>.</Text>
                          <Text as="span" animation={`${up} 1s infinite 0.2s`} display="inline-block" mr={1}>.</Text>
                          <Text as="span" animation={`${up} 1s infinite 0.4s`} display="inline-block" mr={1}>.</Text>
                        </Text>
                      )
                      }
                      < Icon
                        as={FaPen}
                        boxSize={4}
                        color="gray.500"
                        cursor="pointer"
                        onClick={() => handleEdit(book.id, { author: book.author, title: book.title })}
                        transition="transform 0.1s ease-in-out"
                        _hover={{ transform: 'scale(1.2)', color: 'purple.500' }}
                      />
                      <Icon
                        as={FaTrash}
                        boxSize={4}
                        color="gray.500"
                        cursor="pointer"
                        onClick={() => deleteMutation.mutate(book.id)}
                        transition="transform 0.1s ease-in-out"
                        _hover={{ transform: 'scale(1.2)', color: 'red.500' }}
                      />
                    </HStack>
                  </CardBody>
                </Card>
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
                <VStack spacing={3} align="stretch">
                  <Box>
                    <Text fontSize="sm" fontWeight="bold" mb={1}>Title</Text>
                    <Input
                      id="title"
                      type="text"
                      value={editedBookContent?.title}
                      onChange={(e) =>
                        setEditedBookContent((prev) => ({ ...prev!, title: e.target.value }))
                      }
                      _focus={{ boxShadow: '0 0 0 1px #805AD5', borderColor: '#805AD5' }}
                    />
                  </Box>
                  <Box>
                    <Text fontSize="sm" fontWeight="bold" mb={1}>Author</Text>
                    <Input
                      id="author"
                      type="text"
                      value={editedBookContent?.author}
                      onChange={(e) =>
                        setEditedBookContent((prev) => ({ ...prev!, author: e.target.value }))
                      }
                      _focus={{ boxShadow: '0 0 0 1px #805AD5', borderColor: '#805AD5' }}
                    />
                  </Box>
                </VStack>
              </ModalBody>
              <ModalFooter>
                <Button colorScheme="purple" mr={3} onClick={handleSave}>
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

