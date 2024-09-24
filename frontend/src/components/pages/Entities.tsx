import { useEffect, useState } from 'react';
import { Box, Button, Text, Heading, useMediaQuery, Link, Modal, ModalOverlay, ModalContent, ModalHeader, ModalFooter, ModalBody, ModalCloseButton, useDisclosure, Spinner, Center } from '@chakra-ui/react';
import { RiCopperCoinFill } from "react-icons/ri";
import Nav from '../navigation/Nav';
import MobileNav from '../navigation/MobileNav';
import { useGetUserBooks } from '../../apis/books';
import { useGetBookParts, useGetBookParts, useUpdateBookPart } from '../../apis/book_parts';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import BookSelector from '../state/BookSelector';
import { useGetEntityExtractionProcess, useTriggerExtraction } from '../../apis/book_processes';
import ProgressBar from '../indicators/ProgressBar';
import TableOfContent from '../navigation/TableOfContent';
import { BookPartUpdateSchema } from '../../types/book_parts';
import { useGetBookEntities } from '../../apis/entities';

const Entities = () => {
  const [isLargerThan768] = useMediaQuery('(min-width: 768px)');

  const { isOpen, onOpen, onClose } = useDisclosure();

  const { getUserBooks } = useGetUserBooks();
  const { getTableOfContent } = useGetBookParts();
  const { getBookParts } = useGetBookParts();
  const { getBookEntities } = useGetBookEntities();
  const { triggerExtraction } = useTriggerExtraction();
  const { getEntityExtractionProcess } = useGetEntityExtractionProcess();
  const { updateBookPart } = useUpdateBookPart();

  const queryClient = useQueryClient();

  const [selectedBookId, setSelectedBookId] = useState(localStorage.getItem('selectedBookId') || null);
  useEffect(() => {
    const handleStorageChange = () => {
      const bookId = localStorage.getItem("selectedBookId");
      setSelectedBookId(bookId);
    };

    window.addEventListener('storage', handleStorageChange);
    return () => {
      window.removeEventListener('storage', handleStorageChange);
    };
  }, []);

  const toggleIsStoryPart = (bookPartId: string) => {
    const currentState = tocBookParts?.find(part => part.id === bookPartId)?.is_story_part;
    const updatedState = !currentState;
    updateMutation.mutate({ bookPartId, bookPartUpdate: { is_story_part: updatedState } });
  };

  const { data: userBooks } = useQuery({
    queryKey: ['userBooks'],
    queryFn: getUserBooks,
    refetchInterval: 3000,
  });

  const { data: tocBookParts, isLoading: isLoadingBookParts } = useQuery({
    queryKey: ['bookParts', selectedBookId],
    queryFn: () => selectedBookId ? getTableOfContent(selectedBookId) : null,
    enabled: !!selectedBookId,
  });

  const { data: bookPartsContent, isLoading: isLoadingBookPartsContent } = useQuery({
    queryKey: ['bookPartsContent', selectedBookId],
    queryFn: () => selectedBookId ? getBookParts(selectedBookId) : null,
    enabled: !!selectedBookId,
    select: (data) => {
      if (data) {
        return data.reduce((acc, curr) => {
          const words = curr.content.split(' ');
          const shortenedContent = words.slice(0, 100).join(' ');
          acc.set(curr.id, shortenedContent);
          return acc;
        }, new Map<string, string>());
      }
      return new Map<string, string>();
    },
  });

  const { data: bookEntities } = useQuery({
    queryKey: ['bookEntities', selectedBookId],
    queryFn: () => selectedBookId ? getBookEntities(selectedBookId) : null,
    enabled: !!selectedBookId,
  });

  const { data: entityExtractionProcess } = useQuery({
    queryKey: ['entityExtractionProcess', selectedBookId],
    queryFn: () => selectedBookId ? getEntityExtractionProcess(selectedBookId) : null,
    enabled: !!selectedBookId,
    refetchInterval: 1000,
  });

  const triggerMutation = useMutation({
    mutationFn: triggerExtraction,
    onSuccess: () => {
      if (selectedBookId) {
        queryClient.invalidateQueries({ queryKey: ['entityExtractionProcess', selectedBookId] });
      }
    }
  });

  const updateMutation = useMutation({
    mutationFn: (variables: { bookPartId: string, bookPartUpdate: BookPartUpdateSchema }) => updateBookPart(variables.bookPartId, variables.bookPartUpdate),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['bookParts', selectedBookId] });
      queryClient.invalidateQueries({ queryKey: ['bookPartsContent', selectedBookId] });
    }
  })

  return (
    <Box display="flex" flexDirection={{ base: "column", md: "row" }} height="100vh">
      {isLargerThan768 ? <Nav activeLink="Entities" /> : <MobileNav activeLink="Entities" />}
      <Box flex="1" p={4} mt={isLargerThan768 ? 0 : 20} bg="gray.100" height="100vh" overflowY="auto">
        <Box maxW={{ base: "100%", md: "5xl" }} mx="auto">
          {userBooks && userBooks.length > 0 ? (
            <>
              <Heading size="lg" color={"gray.700"}>Current Book</Heading>
              <BookSelector userBooks={userBooks} />
              {selectedBookId ? (
                <Box mt={4} bg="white" borderRadius={8} p={4} textAlign="center">
                  {entityExtractionProcess && (
                    entityExtractionProcess.is_requested && entityExtractionProcess.completeness !== undefined && entityExtractionProcess.requested_at ? (
                      entityExtractionProcess.completeness === 1.0 ? (
                        bookEntities && bookEntities.length > 0 && (
                          <Box mt={4}>
                            {bookEntities.map((entity) => (
                              <Box key={`${entity.name}-${entity.category}`} borderWidth="1px" borderRadius="lg" overflow="hidden" p={4} mb={4}>
                                <Heading size="md" color={"gray.700"}>{entity.name}</Heading>
                                <Text mt={2} color={"gray.700"}><strong>Alternative Names:</strong> {entity.alternative_names.join(', ')}</Text>
                                <Text mt={2} color={"gray.700"}><strong>Category:</strong> {entity.category}</Text>
                                <Text mt={2} color={"gray.700"}><strong>Facts:</strong></Text>
                                <ul>
                                  {entity.facts.map((fact, index) => (
                                    <li key={index}>
                                      <Text><strong>Book Part ID:</strong> {fact.book_part_id}</Text>
                                      <Text><strong>Content:</strong> {fact.content}</Text>
                                      <Text><strong>Sibling Index:</strong> {fact.sibling_index}</Text>
                                      <Text><strong>Sibling Total:</strong> {fact.sibling_total}</Text>
                                    </li>
                                  ))}
                                </ul>
                              </Box>
                            ))}
                          </Box>
                        )
                      ) : (
                        <ProgressBar title="The oracle is reading your book..." completeness={entityExtractionProcess.completeness} startDate={new Date(entityExtractionProcess.requested_at)}></ProgressBar>
                      )
                    ) : (
                      <Box>
                        <Text fontSize='md' color={"gray.700"}>
                          Click the button below to extract characters, locations, organizations and concepts from your book.
                        </Text>
                        <Button
                          colorScheme="purple"
                          onClick={onOpen}
                          mt={2}
                        >
                          Extract entities ({Math.round(entityExtractionProcess.estimated_cost)} <RiCopperCoinFill style={{ "marginLeft": "2px" }} color='#FFD700' />)
                        </Button>

                        <Modal isOpen={isOpen} onClose={onClose} isCentered size={"lg"}>
                          <ModalOverlay />
                          <ModalContent maxHeight={"90vh"}>
                            <ModalHeader>Confirm Extraction</ModalHeader>
                            <ModalCloseButton />
                            <ModalBody p={0}>
                              <Text px={6}>
                                Please make sure each part is correctly classified. Entities will be extracted from narrative parts only. Click on the part to toggle its selection.
                              </Text>
                              {isLoadingBookParts || isLoadingBookPartsContent ?
                                <Center><Spinner /></Center> :
                                <Box
                                  mt={4}
                                  bg="gray.100"
                                  px={6}
                                  py={2}
                                  pb={1}
                                  maxHeight={"calc(90vh - 220px)"}
                                  overflowY="auto"
                                  boxShadow="0 0 5px rgba(0, 0, 0, 0.2)" // Added inside box shadow
                                >
                                  <TableOfContent
                                    bookParts={tocBookParts ? tocBookParts : []}
                                    bookPartsContent={bookPartsContent ? bookPartsContent : new Map<string, string>()}
                                    onTocEntryClick={toggleIsStoryPart}
                                  />
                                </Box>
                              }
                            </ModalBody>
                            <ModalFooter>
                              <Button colorScheme='purple' onClick={() => { triggerMutation.mutate(selectedBookId); onClose(); }} mr={3}>
                                Confirm
                              </Button>
                              <Button colorScheme='purple' variant={'ghost'} onClick={onClose}>
                                Close
                              </Button>
                            </ModalFooter>
                          </ModalContent>
                        </Modal>

                      </Box>
                    )
                  )}
                </Box>
              ) : (
                <Box mt={4} bg="white" borderRadius={8} p={4} textAlign="center">
                  <Text fontSize='lg' color={"gray.700"}>
                    Select a book to continue
                  </Text>
                </Box>
              )}
            </>
          ) : (
            <Box mt={4} bg="white" borderRadius={8} p={4} textAlign="center">
              <Text fontSize='lg' color={"gray.700"}>
                No books available. <Link style={{ textDecoration: 'underline' }} color="purple.500" href="/library">Upload a book</Link> to get started.
              </Text>
            </Box>
          )}
        </Box>
      </Box>
    </Box>
  );
};

export default Entities;
