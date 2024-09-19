import { useEffect, useState } from 'react';
import { Box, Heading, Spinner, useMediaQuery } from '@chakra-ui/react';
import Nav from '../navigation/Nav';
import MobileNav from '../navigation/MobileNav';
import { useGetUserBooks } from '../../apis/books';
import { useGetBookParts, useGetTableOfContent } from '../../apis/book_parts';
import { useQuery } from '@tanstack/react-query';
import BookSelector from '../state/BookSelector';
import TableOfContent from '../navigation/TableOfContent';

const Entities = () => {
    const [isLargerThan768] = useMediaQuery('(min-width: 768px)');

    const { getUserBooks } = useGetUserBooks();
    const { getTableOfContent } = useGetTableOfContent();
    const { getBookParts } = useGetBookParts();

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
        refetchInterval: 5000,
    });

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

    return (
        <Box display="flex" flexDirection={{ base: "column", md: "row" }}>
            {isLargerThan768 ? <Nav activeLink="Characters" /> : <MobileNav activeLink="Characters" />}
            <Box flex="1" p={4} mt={isLargerThan768 ? 0 : 20} bg="gray.100" height="100vh" overflowY="auto">
                <Box maxW={{ base: "100%", md: "5xl" }} mx="auto">
                    {userBooks && userBooks.length > 0 && (
                        <Box>
                            <Heading size="lg" color={"gray.700"}>Current Book</Heading>
                            <BookSelector userBooks={userBooks} />
                            <Box mt={4}>
                                <Heading size="lg" color={"gray.700"}>Book Parts</Heading>
                                {(isLoadingBookParts || isLoadingBookPartsContent) ? <Spinner></Spinner> : (
                                    bookParts && bookPartsContent && bookParts.length > 0 && (
                                        <Box>
                                            <TableOfContent bookParts={bookParts} bookPartsContent={bookPartsContent}></TableOfContent>
                                        </Box>
                                    ))}
                            </Box>
                        </Box>
                    )}
                </Box>
            </Box>
        </Box>
    );
};

export default Entities;