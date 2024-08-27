import { useQuery } from '@tanstack/react-query';
import { useGetUserBooks } from '../../apis/books';
import { Spinner, Alert, AlertIcon, AlertTitle, AlertDescription, Box } from '@chakra-ui/react';
import { Select as ChakraSelect } from 'chakra-react-select';

const BookSelector = () => {
    const { getUserBooks } = useGetUserBooks();
    const { data: userBooks, isLoading, isError, error } = useQuery({
        queryKey: ['userBooks'],
        queryFn: getUserBooks,
        refetchInterval: 10000,
    });

    const handleBookChange = (selectedOption: any) => {
        localStorage.setItem('selectedBook', selectedOption.value);
    }

    return (
        <Box my={4}>
            {isLoading && <Spinner />}
            {isError && (
                <Alert status='error'>
                    <AlertIcon />
                    <AlertTitle>Error!</AlertTitle>
                    <AlertDescription>{error.message}</AlertDescription>
                </Alert>
            )}
            {userBooks && (
                <ChakraSelect
                    placeholder="Select book"
                    onChange={handleBookChange}
                    options={userBooks.map((book) => ({
                        value: book.id,
                        label: `📖${book.title} ✒️${book.author}`,
                    }))}
                    chakraStyles={{
                        control: (provided) => ({
                            ...provided,
                            borderColor: 'gray.400',
                            borderWidth: '2px',
                            _hover: {
                                borderColor: 'purple.400',
                            },
                            _focus: {
                                borderColor: 'purple.400',
                                boxShadow: 'none',
                            },
                        }),
                        option: (provided, state) => ({
                            ...provided,
                            color: state.isSelected ? 'white' : 'gray.700',
                            _selected: {
                                backgroundColor: state.isSelected ? 'purple.400' : 'transparent',
                            },
                            _hover: {
                                backgroundColor: state.isSelected ? 'purple.400' : 'gray.100',
                            },
                        }),
                    }}
                />
            )}
        </Box>
    )
};

export default BookSelector;
