import { Box, Button, Image, VStack, Spacer, Link, Center, Icon } from '@chakra-ui/react'
import { FaCog, FaHome, FaChartBar, FaBook } from 'react-icons/fa';

type NavProps = {
  activeLink?: string;
}

const Nav = ({ activeLink }: NavProps) => {

  return (
    <Box h="100vh" bg="white.100" px={8} py={4} w={48} borderRightWidth="1px" shadow="md">
      <VStack align="start" spacing={4} h="100%" w="100%">
        <Center w="100%">
          <Image src="/images/logo.png" alt="Logo" width={24} />
        </Center>
        <Button
          key={"/home"}
          as={Link}
          href={"/home"}
          size="sm"
          width="100%"
          color={activeLink === "Home" ? "white" : "gray.700"}
          bg={activeLink === "Home" ? "purple.400" : "transparent"}
          _hover={{
            bg: activeLink === "Home" ? "purple.400" : "purple.100",
            textDecoration: 'none'
          }}
          borderRadius={4}
          leftIcon={<Icon as={FaHome} />}
        >
          {"Home"}
        </Button>
        <Button
          key={"/books"}
          as={Link}
          href={"/books"}
          size="sm"
          width="100%"
          color={activeLink === "Books" ? "white" : "gray.700"}
          bg={activeLink === "Books" ? "purple.400" : "transparent"}
          _hover={{
            bg: activeLink === "Books" ? "purple.400" : "purple.100",
            textDecoration: 'none'
          }}
          borderRadius={4}
          leftIcon={<Icon as={FaBook} />}
        >
          {"Books"}
        </Button>
        <Button
          key={"/analysis"}
          as={Link}
          href={"/analysis"}
          size="sm"
          width="100%"
          color={activeLink === "Analysis" ? "white" : "gray.700"}
          bg={activeLink === "Analysis" ? "purple.400" : "transparent"}
          _hover={{
            bg: activeLink === "Analysis" ? "purple.400" : "purple.100",
            textDecoration: 'none'
          }}
          borderRadius={4}
          leftIcon={<Icon as={FaChartBar} />}
        >
          {"Analysis"}
        </Button>
        <Spacer />
        <Button
          key="/settings"
          as={Link}
          href="/settings"
          size="sm"
          width="100%"
          color={activeLink === "Settings" ? "white" : "gray.700"}
          bg={activeLink === "Settings" ? "purple.400" : "transparent"}
          _hover={{
            bg: activeLink === "Settings" ? "purple.400" : "purple.100",
            textDecoration: 'none'
          }}
          borderRadius={4}
          leftIcon={<Icon as={FaCog} />}
        >
          Settings
        </Button>
      </VStack>
    </Box>
  )
}
export default Nav
