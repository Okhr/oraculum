import { Box, Text, Tag, Flex } from '@chakra-ui/react';
import { TocBookPartResponseSchema } from '../../types/book_parts';

type TableOfContentProps = {
    bookParts: TocBookPartResponseSchema[];
    bookPartsContent: Map<string, string>;
    onTocEntryClick: (bookPartId: string) => void;
    depth?: number;
};

const TableOfContent = ({ bookParts, bookPartsContent, onTocEntryClick: onEntryClick = () => { }, depth = 0 }: TableOfContentProps) => {

    return (
        <>
            {bookParts.map(bookPart => (
                <Box key={bookPart.id} m={0} p={0} ml={depth * 4}>
                    <Box bg={"white"} p={1} borderRadius={8} mb={2} boxShadow={"0px 2px 5px rgba(127, 127, 127, 0.2)"}>
                        <Flex
                            justifyContent="space-between"
                            alignItems="center"
                            _hover={{ cursor: "pointer" }}
                            onClick={() => onEntryClick(bookPart.id)}
                        >
                            <Text fontSize={"sm"} bg="gray.100" px={2} borderRadius={6} border={"solid #bbb 1px"}>{bookPart.label}</Text>
                            <Text fontSize={"xs"} flex="1" mx={2} whiteSpace="nowrap" overflow="hidden" textOverflow="ellipsis">
                                {bookPartsContent.has(bookPart.id) && bookPartsContent.get(bookPart.id)}
                            </Text>
                            {bookPart.is_story_part ? (
                                <Tag size={"sm"} colorScheme="purple" borderRadius={6} px={1} m={0}>
                                    Narrative
                                </Tag>
                            ) : (
                                <Tag size={"sm"} color={"gray.400"} colorScheme="gray" borderRadius={6} px={1} m={0} textDecoration="line-through">
                                    Narrative
                                </Tag>
                            )}
                        </Flex>
                    </Box>
                    {bookPart.children && <TableOfContent bookParts={bookPart.children} bookPartsContent={bookPartsContent} onTocEntryClick={onEntryClick} depth={depth + 1} />}
                </Box >
            ))}
        </>
    );
};

export default TableOfContent;