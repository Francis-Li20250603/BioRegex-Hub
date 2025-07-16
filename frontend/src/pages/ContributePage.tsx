import { VStack, Heading, Box } from '@chakra-ui/react';
import RuleForm from '../components/RuleForm';

export default function ContributePage() {
  return (
    <VStack spacing={6} align="stretch">
      <Heading as="h1" size="xl">Contribute a New Rule</Heading>
      <Box bg="white" p={6} borderRadius="md" boxShadow="md">
        <RuleForm />
      </Box>
      <Box mt={4}>
        <Heading as="h2" size="md" mb={2}>Submission Guidelines</Heading>
        <ul>
          <li>All regex patterns must be validated against official documentation</li>
          <li>Provide a clear description of the pattern's purpose</li>
          <li>Upload supporting PDF documentation where possible</li>
          <li>Submitted rules will be reviewed by our expert team</li>
        </ul>
      </Box>
    </VStack>
  );
}
