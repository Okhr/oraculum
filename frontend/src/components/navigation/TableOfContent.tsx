import { Box, Text, Badge, Flex } from '@chakra-ui/react';
import { TocBookPartResponseSchema } from '../../types/book_parts';

type TableOfContentProps = {
    bookParts: TocBookPartResponseSchema[];
    depth?: number;
};

const TableOfContent = ({ bookParts, depth = 0 }: TableOfContentProps) => {
    return (
        <>
            {bookParts.map(bookPart => (
                <Box key={bookPart.id} m={0} p={0} ml={depth * 8}>
                    <Box bg={"white"} p={1} px={2} borderRadius="md" my={2} boxShadow={"0px 2px 5px rgba(127, 127, 127, 0.2)"}>
                        <Flex justifyContent="space-between" alignItems="center">
                            <Text size={depth !== 0 ? "sm" : "md"}>{bookPart.label}</Text>
                            <Badge size={"sm"} colorScheme={bookPart.is_story_part ? 'purple' : 'gray'} borderRadius="sm" px={2}>
                                {bookPart.is_story_part ? 'Story' : 'Non-Story'}
                            </Badge>
                        </Flex>
                    </Box>
                    {bookPart.children && <TableOfContent bookParts={bookPart.children} depth={depth + 1} />}
                </Box >
            ))}
        </>
    );
};

export default TableOfContent;