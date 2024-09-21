import { useEffect, useState } from 'react';
import { Box, Button, Text, Heading, useMediaQuery, Link } from '@chakra-ui/react';
import { RiCopperCoinFill } from "react-icons/ri";
import Nav from '../navigation/Nav';
import MobileNav from '../navigation/MobileNav';
import { useGetUserBooks } from '../../apis/books';
import { useGetBookParts, useGetTableOfContent } from '../../apis/book_parts';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import BookSelector from '../state/BookSelector';
import { useGetEntityExtractionProcess, useTriggerExtraction } from '../../apis/book_processes';
import ProgressBar from '../indicators/ProgressBar';

const Entities = () => {
    const [isLargerThan768] = useMediaQuery('(min-width: 768px)');

    const { getUserBooks } = useGetUserBooks();
    const { getTableOfContent } = useGetTableOfContent();
    const { getBookParts } = useGetBookParts();
    const { triggerExtraction } = useTriggerExtraction();
    const { getEntityExtractionProcess } = useGetEntityExtractionProcess();

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

    const { data: userBooks } = useQuery({
        queryKey: ['userBooks'],
        queryFn: getUserBooks,
        refetchInterval: 3000,
    });

    /*
    const { data: bookParts, isLoading: isLoadingBookParts } = useQuery({
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
                    acc.set(curr.id, curr.content);
                    return acc;
                }, new Map<string, string>());
            }
            return new Map<string, string>();
        },
    });
    */

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

    return (
        <Box display="flex" flexDirection={{ base: "column", md: "row" }} height="100vh">
            {isLargerThan768 ? <Nav activeLink="Characters" /> : <MobileNav activeLink="Characters" />}
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
                                            <ProgressBar title="The oracle is reading your book..." completeness={entityExtractionProcess.completeness} startDate={new Date(entityExtractionProcess.requested_at)}></ProgressBar>
                                        ) : (
                                            <Box>
                                                <Text fontSize='md' color={"gray.700"}>
                                                    Click the button below to extract characters, locations, organizations and concepts from your book.
                                                </Text>
                                                <Button
                                                    colorScheme="purple"
                                                    onClick={() => triggerMutation.mutate(selectedBookId)}
                                                    mt={2}
                                                >
                                                    Extract entities ({Math.round(entityExtractionProcess.estimated_cost)} <RiCopperCoinFill style={{ "marginLeft": "2px" }} color='#FFD700' />)
                                                </Button>
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