import { Box, Heading, Accordion, AccordionItem, AccordionButton, AccordionPanel, AccordionIcon } from '@chakra-ui/react';
import { TocBookPartResponseSchema } from '../../types/book_parts';

type TableOfContentProps = {
    parts: TocBookPartResponseSchema[];
};

const TableOfContent = ({ parts }: TableOfContentProps) => {
    const renderBookParts = (parts: TocBookPartResponseSchema[]) => {
        return parts.map(part => (
            part.children && part.children.length > 0 ? (
                <Accordion key={part.id} allowMultiple>
                    <AccordionItem>
                        <AccordionButton>
                            <Box flex="1" textAlign="left">
                                <Heading size="sm" color={"gray.600"}>
                                    {part.label}
                                </Heading>
                            </Box>
                            <AccordionIcon />
                        </AccordionButton>
                        <AccordionPanel pb={2}>
                            {renderBookParts(part.children)}
                        </AccordionPanel>
                    </AccordionItem>
                </Accordion>
            ) : (
                <Box key={part.id} p={2}>
                    <Heading size="sm" color={"gray.600"}>
                        {part.label}
                    </Heading>
                </Box >
            )
        ));
    };

    return <>{renderBookParts(parts)}</>;
};

export default TableOfContent;