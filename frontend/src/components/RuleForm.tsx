import { useState } from 'react';
import { 
  FormControl, 
  FormLabel, 
  Input, 
  Textarea, 
  Select, 
  Button, 
  VStack,
  useToast
} from '@chakra-ui/react';
import FileUploader from './FileUploader';
import { submitRule } from '../services/api';

export default function RuleForm() {
  const toast = useToast();
  const [formData, setFormData] = useState({
    pattern: '',
    description: '',
    dataType: '',
    region: 'FDA',
    reference: null as File | null
  });
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    
    try {
      await submitRule(formData);
      toast({
        title: 'Rule Submitted',
        description: 'Your rule has been submitted for review',
        status: 'success',
        duration: 5000,
        isClosable: true,
      });
      // Reset form
      setFormData({
        pattern: '',
        description: '',
        dataType: '',
        region: 'FDA',
        reference: null
      });
    } catch (error) {
      toast({
        title: 'Submission Failed',
        description: 'Failed to submit rule. Please try again.',
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <VStack spacing={4} align="stretch">
        <FormControl isRequired>
          <FormLabel>Regular Expression Pattern</FormLabel>
          <Input 
            value={formData.pattern}
            onChange={(e) => setFormData({...formData, pattern: e.target.value})}
            placeholder="e.g. ^[A-Z]{3}\d{5}$"
          />
        </FormControl>
        
        <FormControl>
          <FormLabel>Description</FormLabel>
          <Textarea 
            value={formData.description}
            onChange={(e) => setFormData({...formData, description: e.target.value})}
            placeholder="Describe the purpose of this regex"
          />
        </FormControl>
        
        <FormControl isRequired>
          <FormLabel>Data Type</FormLabel>
          <Input 
            value={formData.dataType}
            onChange={(e) => setFormData({...formData, dataType: e.target.value})}
            placeholder="e.g. Patient ID, Lab Result"
          />
        </FormControl>
        
        <FormControl isRequired>
          <FormLabel>Regulatory Region</FormLabel>
          <Select 
            value={formData.region}
            onChange={(e) => setFormData({...formData, region: e.target.value})}
          >
            <option value="FDA">FDA (US)</option>
            <option value="EMA">EMA (EU)</option>
            <option value="HIPAA">HIPAA</option>
            <option value="Other">Other</option>
          </Select>
        </FormControl>
        
        <FormControl>
          <FormLabel>Reference Document (PDF)</FormLabel>
          <FileUploader 
            accept=".pdf"
            onFileSelected={(file) => setFormData({...formData, reference: file})}
          />
        </FormControl>
        
        <Button 
          type="submit" 
          colorScheme="teal" 
          isLoading={isSubmitting}
          loadingText="Submitting"
        >
          Submit Rule
        </Button>
      </VStack>
    </form>
  );
}
