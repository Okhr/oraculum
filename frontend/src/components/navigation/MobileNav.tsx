import { Box, Button, Image, VStack, Spacer, Link, Icon, useDisclosure, IconButton, Drawer, DrawerOverlay, DrawerContent, DrawerHeader, DrawerCloseButton, DrawerBody } from '@chakra-ui/react'
import { FaBars, FaCog, FaGhost, FaMountain } from 'react-icons/fa';
import { IoLibrary } from 'react-icons/io5';

type MobileNavProps = {
  activeLink?: string;
}

const MobileNav = ({ activeLink }: MobileNavProps) => {
  const { isOpen, onOpen, onClose } = useDisclosure();

  return (
    <Box>
      <Box position="fixed" top={0} left={0} right={0} zIndex={1000} bg="white" px={4} py={3} display="flex" alignItems="center" justifyContent="space-between" shadow="md">
        <IconButton icon={<FaBars />} onClick={onOpen} variant="ghost" aria-label="Open Menu" size="lg" />
        <Link href="/library">
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
                  key={"/library"}
                  as={Link}
                  href={"/library"}
                  size="md"
                  width="100%"
                  color={activeLink === "Library" ? "white" : "gray.700"}
                  bg={activeLink === "Library" ? "purple.400" : "transparent"}
                  _hover={{
                    bg: activeLink === "Library" ? "purple.400" : "purple.100",
                    textDecoration: 'none'
                  }}
                  borderRadius={4}
                  leftIcon={<Icon as={IoLibrary} />}
                >
                  {"Library"}
                </Button>
                <Box height="1px" width="100%" bg="gray.400" my={4} />
                <Button
                  key={"/characters"}
                  as={Link}
                  href={"/characters"}
                  size="md"
                  width="100%"
                  color={activeLink === "Characters" ? "white" : "gray.700"}
                  bg={activeLink === "Characters" ? "purple.400" : "transparent"}
                  _hover={{
                    bg: activeLink === "Characters" ? "purple.400" : "purple.100",
                    textDecoration: 'none'
                  }}
                  borderRadius={4}
                  leftIcon={<Icon as={FaGhost} />}
                >
                  {"Characters"}
                </Button>
                <Button
                  key={"/locations"}
                  as={Link}
                  href={"/locations"}
                  size="md"
                  width="100%"
                  color={activeLink === "Locations" ? "white" : "gray.700"}
                  bg={activeLink === "Locations" ? "purple.400" : "transparent"}
                  _hover={{
                    bg: activeLink === "Locations" ? "purple.400" : "purple.100",
                    textDecoration: 'none'
                  }}
                  borderRadius={4}
                  leftIcon={<Icon as={FaMountain} />}
                >
                  {"Locations"}
                </Button>
                <Spacer />
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

