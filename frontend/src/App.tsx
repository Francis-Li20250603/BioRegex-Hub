import { Box } from '@chakra-ui/react';
import Header from './components/Header';
import Footer from './components/Footer';
import AppRoutes from './routes';

function App() {
  return (
    <Box minH="100vh" display="flex" flexDirection="column">
      <Header />
      <Box flex="1" p={6}>
        <AppRoutes />
      </Box>
      <Footer />
    </Box>
  );
}

export default App;
