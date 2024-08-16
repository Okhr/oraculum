import { Box, IconButton, Image, Drawer, DrawerBody, DrawerOverlay, DrawerContent, useDisclosure, VStack, Button, Link, Icon, DrawerHeader, DrawerCloseButton, Spacer } from '@chakra-ui/react';
import { FaBars, FaHome, FaChartBar, FaBook, FaCog, FaTimes } from 'react-icons/fa';

type MobileNavProps = {
  activeLink?: string;
}

const MobileNav = ({ activeLink }: MobileNavProps) => {
  const { isOpen, onOpen, onClose } = useDisclosure();

  return (
    <Box>
      <Box position="fixed" top={0} left={0} right={0} zIndex={1000} bg="white" px={4} py={3} display="flex" alignItems="center" justifyContent="space-between" shadow="md">
        <IconButton icon={<FaBars />} onClick={onOpen} variant="ghost" aria-label="Open Menu" size="lg" />
        <Link href="/home">
          <Image src="/images/logo.png" alt="Logo" width={16} />
        </Link>
      </Box>
      <Drawer isOpen={isOpen} placement="left" onClose={onClose} size="xs">
        <DrawerOverlay>
          <DrawerContent>
            <DrawerHeader>
              <DrawerCloseButton size="lg" />
            </DrawerHeader>
            <DrawerBody>
              <VStack align="start" spacing={4} h="100%" w="100%">
                <Button
                  key={"/home"}
                  as={Link}
                  href={"/home"}
                  size="md"
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
                  size="md"
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
                  size="md"
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
                <Spacer></Spacer>
                <Button
                  key="/settings"
                  as={Link}
                  href="/settings"
                  size="md"
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
            </DrawerBody>
          </DrawerContent>
        </DrawerOverlay>
      </Drawer>
    </Box >
  );
}


export default MobileNav;
