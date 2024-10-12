import { useState } from 'react';
import { Box, Heading, Text, Input, Button, Icon } from '@chakra-ui/react';
import { EntityResponseSchema } from '../../types/entities';
import { MdPerson, MdLocationOn, MdGroups, MdLightbulb } from 'react-icons/md';

const filters = ['all', 'person', 'location', 'organization', 'concept'];
const filterIcons = [MdPerson, MdLocationOn, MdGroups, MdLightbulb];

type EntityVisualizerProps = {
    entities: EntityResponseSchema[];
};

const EntityVisualizer = ({ entities }: EntityVisualizerProps) => {
    const [searchTerm, setSearchTerm] = useState('');
    const [selectedFilter, setSelectedFilter] = useState('all');

    const filteredEntities = entities.filter(entity =>
        entity.name.toLowerCase().includes(searchTerm.toLowerCase()) &&
        (selectedFilter === 'all' || entity.category.toLowerCase() === selectedFilter.toLowerCase())
    );

    return (
        <Box mt={4} color={"gray.700"}>
            <Box display="flex" flexWrap="wrap" gap={2} mb={4}>
                {filters.map(filter => (
                    <Button
                        key={filter}
                        onClick={() => setSelectedFilter(filter)}
                        variant={selectedFilter === filter ? 'solid' : 'outline'}
                        borderColor={"gray.400"}
                        bgColor={selectedFilter === filter ? 'gray.300' : 'white'}
                        {...filter !== "all" && { leftIcon: <Icon as={filterIcons[filters.indexOf(filter) - 1]} /> }}
                    >
                        {filter.charAt(0).toUpperCase() + filter.slice(1)}
                    </Button>
                ))}
            </Box>
            <Input
                placeholder="Search..."
                value={searchTerm}
                focusBorderColor='purple.500'
                mb={4}
                borderColor={"gray.400"}
                onChange={e => setSearchTerm(e.target.value)}
            />
            <Box display="grid" gridTemplateColumns="repeat(auto-fill, minmax(300px, 1fr))" gap={4}>
                {filteredEntities.sort((a, b) =>
                    b.facts.reduce((sum, fact) => sum + fact.occurrences, 0) -
                    a.facts.reduce((sum, fact) => sum + fact.occurrences, 0)
                ).map(entity => (
                    <Box
                        p={4}
                        key={entity.name}
                        bg="white"
                        borderRadius="md"
                        boxShadow="md"
                        border="1px"
                        borderColor={"gray.400"}
                        height={"200px"}
                        position="relative"
                    >
                        <Icon
                            as={filterIcons[filters.indexOf(entity.category.toLowerCase()) - 1]}
                            position="absolute"
                            top={4}
                            right={4}
                            boxSize={6}
                        />
                        <Heading size="sm">{entity.name.charAt(0).toUpperCase() + entity.name.slice(1)}</Heading>
                        <Text fontSize="sm" fontStyle="italic">
                            {entity.alternative_names.length > 0 ? entity.alternative_names.map(name => name.charAt(0).toUpperCase() + name.slice(1)).join(', ') : ' '}
                        </Text>
                        <Text fontSize="sm">Total Occurrences: {entity.facts.reduce((sum, fact) => sum + fact.occurrences, 0)}</Text>
                    </Box>
                ))}
            </Box>
        </Box >
    );
};

export default EntityVisualizer;
