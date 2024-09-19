import { Box, Text, Tag, Flex } from '@chakra-ui/react';
import { TocBookPartResponseSchema } from '../../types/book_parts';

type TableOfContentProps = {
    bookParts: TocBookPartResponseSchema[];
    bookPartsContent: Map<string, string>,
    depth?: number;
};

const TableOfContent = ({ bookParts, bookPartsContent, depth = 0 }: TableOfContentProps) => {
    return (
        <>
            {bookParts.map(bookPart => (
                <Box key={bookPart.id} m={0} p={0} ml={depth * 8}>
                    <Box bg={"white"} p={1} borderRadius={8} my={2} boxShadow={"0px 2px 5px rgba(127, 127, 127, 0.2)"}>
                        <Flex justifyContent="space-between" alignItems="center">
                            <Text bg="gray.100" px={2} borderRadius={6} border={"solid #bbb 1px"}>{bookPart.label}</Text>
                            <Text flex="1" mx={2} ml={4} whiteSpace="nowrap" overflow="hidden" textOverflow="ellipsis">
                                {bookPartsContent.has(bookPart.id) && bookPartsContent.get(bookPart.id)}
                            </Text>
                            <Tag size={"sm"} colorScheme={bookPart.is_story_part ? 'purple' : 'gray'} borderRadius={6} px={2}>
                                {bookPart.is_story_part ? 'Story' : 'Non-Story'}
                            </Tag>
                        </Flex>
                    </Box>
                    {bookPart.children && <TableOfContent bookParts={bookPart.children} bookPartsContent={bookPartsContent} depth={depth + 1} />}
                </Box >
            ))}
        </>
    );
};

export default TableOfContent;