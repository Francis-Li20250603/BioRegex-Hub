import { Table, Thead, Tbody, Tr, Th, Td, Box, Text } from '@chakra-ui/react';
import React, { useMemo } from 'react';
import { Rule } from '../types/types';

interface RuleTableProps {
  rules: Rule[];
  isLoading: boolean;
}

export default function RuleTable({ rules, isLoading }: RuleTableProps) {
  const memoizedRules = useMemo(() => rules, [rules]);

  if (isLoading) {
    return <Box p={4}>Loading rules...</Box>;
  }

  if (memoizedRules.length === 0) {
    return <Text p={4}>No rules found</Text>;
  }

  return (
    <Box overflowX="auto">
      <Table variant="striped" size="sm">
        <Thead>
          <Tr>
            <Th>Pattern</Th>
            <Th>Description</Th>
            <Th>Data Type</Th>
            <Th>Region</Th>
          </Tr>
        </Thead>
        <Tbody>
          {memoizedRules.map((rule) => (
            <Tr key={rule.id}>
              <Td fontFamily="monospace">{rule.pattern}</Td>
              <Td>{rule.description}</Td>
              <Td>{rule.dataType}</Td>
              <Td>{rule.region}</Td>
            </Tr>
          ))}
        </Tbody>
      </Table>
    </Box>
  );
}
