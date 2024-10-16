import { useState } from 'react';
import { Box, Text, Input, Button, Icon, Flex, Card, CardBody, Badge } from '@chakra-ui/react';
import { EntityResponseSchema } from '../../types/entities';
import { MdPerson, MdLocationOn, MdGroups, MdLightbulb } from 'react-icons/md';

const filters = ['all', 'person', 'location', 'organization', 'concept'];
const categoryColors = ['#ff6f91', '#ff9671', '#008f7a', '#0089ba'];
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
      <Box my={4} display="grid" gridTemplateColumns="repeat(auto-fill, minmax(300px, 1fr))" gap={4}>
        {filteredEntities.sort((a, b) =>
          b.facts.reduce((sum, fact) => sum + fact.occurrences, 0) - a.facts.reduce((sum, fact) => sum + fact.occurrences, 0)
        ).map(entity => (
          <Card key={entity.name} borderRadius={4} overflow="hidden" display="flex" flexDirection="column" height={"170px"}>
            <CardBody>
              <Flex align="center" mb={2}>
                <Text fontSize="lg" mr={2} whiteSpace="nowrap" overflow="hidden" textOverflow="ellipsis" fontWeight="bold">
                  {entity.name.charAt(0).toUpperCase() + entity.name.slice(1)}
                </Text>
                <Badge variant="solid" fontSize={"sm"} backgroundColor={categoryColors[filters.indexOf(entity.category.toLowerCase()) - 1]}>
                  {entity.category.toUpperCase()}
                </Badge>
              </Flex>
              <Box borderBottom="1px solid" borderColor="gray.300" mb={2} />
              <Text fontSize="sm" mb={2} whiteSpace="nowrap" overflow="hidden" textOverflow="ellipsis">
                <Flex flexWrap="wrap" gap={1}>
                  {entity.alternative_names.map(name => (
                    <Text fontSize={"sm"} bg="gray.100" px={2} borderRadius={6} border={"solid #bbb 1px"}>{name}</Text>
                  ))}
                </Flex>
              </Text>
            </CardBody>
            <Flex justify="space-between" align="center" p={4} mt="auto">
              <Text fontSize="sm">{entity.facts.reduce((sum, fact) => sum + fact.occurrences, 0)} occurrences</Text>
              <Button borderColor={"gray.400"} bgColor={'white'} variant={"outline"} size="sm">
                See more
              </Button>
            </Flex>
          </Card>
        ))}
      </Box>
    </Box>
  );
};

export default EntityVisualizer;
