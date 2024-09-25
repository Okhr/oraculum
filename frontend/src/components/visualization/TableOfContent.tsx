import { useState } from 'react';
import { Box, Text, Tag, Flex } from '@chakra-ui/react';
import { BookPartResponseSchema } from '../../types/book_parts';

type TableOfContentProps = {
    bookParts: BookPartResponseSchema[];
    onTocEntryClick: (bookPartId: string, isStoryPart: boolean) => void;
};

const TableOfContent = ({ bookParts, onTocEntryClick }: TableOfContentProps) => {
    const [storyPartStates, setStoryPartStates] = useState(bookParts.map(bookPart => bookPart.is_story_part));

    const toggleStoryPart = (index: number) => {
        const newStates = [...storyPartStates];
        newStates[index] = !newStates[index];
        setStoryPartStates(newStates);
    };

    return (
        <>
            {bookParts.map((bookPart, index) => (
                <Box key={bookPart.id} m={0} p={0} ml={bookPart.level * 4}>
                    <Box bg={"white"} p={1} borderRadius={8} mb={2} boxShadow={"0px 2px 5px rgba(127, 127, 127, 0.2)"}>
                        <Flex
                            justifyContent="space-between"
                            alignItems="center"
                            _hover={{ cursor: "pointer" }}
                            onClick={() => {
                                toggleStoryPart(index);
                                onTocEntryClick(bookPart.id, !storyPartStates[index]);
                            }}
                        >
                            <Text fontSize={"sm"} bg="gray.100" px={2} borderRadius={6} border={"solid #bbb 1px"}>{bookPart.label}</Text>
                            <Text fontSize={"xs"} flex="1" mx={2} whiteSpace="nowrap" overflow="hidden" textOverflow="ellipsis">
                                {bookPart.content}
                            </Text>
                            <Tag
                                size={"sm"}
                                colorScheme={storyPartStates[index] ? "purple" : "gray"}
                                borderRadius={6}
                                px={1}
                                m={0}
                                textDecoration={storyPartStates[index] ? "none" : "line-through"}
                            >
                                Narrative
                            </Tag>
                        </Flex>
                    </Box>
                </Box >
            ))}
        </>
    );
};

export default TableOfContent;