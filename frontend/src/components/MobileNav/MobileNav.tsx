import { Box, IconButton, Image, Drawer, DrawerBody, DrawerOverlay, DrawerContent, useDisclosure, VStack, Button, Link, Icon, DrawerHeader, DrawerCloseButton } from '@chakra-ui/react';
import { FaBars, FaHome, FaChartBar, FaBook, FaCog, FaTimes } from 'react-icons/fa';

type MobileNavProps = {
  activeLink?: string;
}

const MobileNav = ({ activeLink }: MobileNavProps) => {
  const { isOpen, onOpen, onClose } = useDisclosure();

  return (
    <Box>
      <Box bg="white.100" px={4} py={3} display="flex" alignItems="center" justifyContent="space-between" shadow="md">
        <IconButton icon={<FaBars />} onClick={onOpen} variant="ghost" aria-label="Open Menu" size="lg" />
        <Image src="/images/logo.png" alt="Logo" width={16} />
      </Box>
      <Drawer isOpen={isOpen} placement="left" onClose={onClose} size="xs">
        <DrawerOverlay>
          <DrawerContent>
            <DrawerHeader>
              <DrawerCloseButton size="lg" />
            </DrawerHeader>
            <DrawerBody>
              <VStack align="start" spacing={6}>
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
                {/* Add other menu items here */}
              </VStack>
            </DrawerBody>
          </DrawerContent>
        </DrawerOverlay>
      </Drawer>
    </Box>
  );
}


export default MobileNav;
