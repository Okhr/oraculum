import { Box, Button, Image, VStack, Spacer, Link, Center, Icon } from '@chakra-ui/react'
import { FaCog, FaGhost } from 'react-icons/fa';
import { IoLibrary } from 'react-icons/io5';

type NavProps = {
  activeLink?: string;
}

const Nav = ({ activeLink }: NavProps) => {

  return (
    <Box h="100vh" bg="white.100" px={8} py={4} w={48} borderRightWidth="1px" shadow="md">
      <VStack align="start" spacing={4} h="100%" w="100%">

        <Center w="100%">
          <Link href="/">
            <Image src="/images/logo.png" alt="Logo" width={24} />
          </Link>
        </Center>
        <Button
          key={"/library"}
          as={Link}
          href={"/library"}
          size="sm"
          width="100%"
          color={activeLink === "Library" ? "white" : "gray.700"}
          bg={activeLink === "Library" ? "purple.400" : "transparent"}
          _hover={{
            bg: activeLink === "Library" ? "purple.400" : "purple.100",
            textDecoration: 'none'
          }}
          borderRadius={4}
          leftIcon={<Icon as={IoLibrary} />} // Changed FaHome to FaBook as it's more appropriate for a library
        >
          {"Library"}
        </Button>
        <Box height="1px" width="100%" bg="gray.400" my={4} />
        <Button
          key={"/entities"}
          as={Link}
          href={"/entities"}
          size="sm"
          width="100%"
          color={activeLink === "Entities" ? "white" : "gray.700"}
          bg={activeLink === "Entities" ? "purple.400" : "transparent"}
          _hover={{
            bg: activeLink === "Entities" ? "purple.400" : "purple.100",
            textDecoration: 'none'
          }}
          borderRadius={4}
          leftIcon={<Icon as={FaGhost} />}
        >
          {"Entities"}
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
