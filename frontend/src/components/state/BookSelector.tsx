import { Box } from '@chakra-ui/react';
import { Select as ChakraSelect, SingleValue } from 'chakra-react-select';
import { BookResponseSchema } from '../../types/books';
import { useEffect, useState } from 'react';

interface BookSelectorProps {
  userBooks: BookResponseSchema[];
}

const BookSelector = ({ userBooks }: BookSelectorProps) => {

  const [selectedBookId, setSelectedBookId] = useState<string | null>(null);


  interface OptionType {
    value: string;
    label: string;
  }

  const handleBookChange = (selectedOption: SingleValue<OptionType>) => {
    if (selectedOption) {
      localStorage.setItem('selectedBookId', selectedOption.value);
      window.dispatchEvent(new Event('storage'))
      setSelectedBookId(selectedOption.value);
    }
  }

  useEffect(() => {
    const storedBookId = localStorage.getItem('selectedBookId');
    if (storedBookId && userBooks.some(book => book.id === storedBookId)) {
      setSelectedBookId(storedBookId);
    } else {
      localStorage.removeItem('selectedBookId');
      window.dispatchEvent(new Event('storage'))
      setSelectedBookId(null);
    }
  }, [userBooks]);

  return (
    <Box my={4}>
      {userBooks && (
        <ChakraSelect
          placeholder="Select book"
          onChange={handleBookChange}
          options={
            userBooks.map((book) => ({
              value: book.id,
              label: book.title,
            }))
          }
          value={
            selectedBookId
              ? {
                value: selectedBookId,
                label: userBooks.find((book) => book.id === selectedBookId)?.title || 'Book not found',
              }
              : null
          }
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
                backgroundColor: 'purple.400',
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
