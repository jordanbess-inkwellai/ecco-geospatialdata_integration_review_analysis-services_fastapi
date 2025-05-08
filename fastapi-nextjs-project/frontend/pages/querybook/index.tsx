import React from 'react';
import { Container, Typography, Box, Alert, Button } from '@mui/material';
import Layout from '../../components/layout/Layout';
import QuerybookFrame from '../../components/querybook/QuerybookFrame';
import { useRouter } from 'next/router';

const QuerybookPage: React.FC = () => {
  const router = useRouter();
  const queryBookEnabled = process.env.NEXT_PUBLIC_QUERYBOOK_ENABLED === 'true';
  
  // If Querybook is not enabled, show a message and redirect to home
  if (!queryBookEnabled) {
    return (
      <Layout title="Querybook">
        <Container maxWidth={false} sx={{ mt: 4, mb: 4 }}>
          <Alert severity="warning" sx={{ mb: 3 }}>
            Querybook integration is not enabled in this build. Please enable it by setting NEXT_PUBLIC_QUERYBOOK_ENABLED=true in your environment.
          </Alert>
          
          <Button variant="contained" onClick={() => router.push('/')}>
            Return to Dashboard
          </Button>
        </Container>
      </Layout>
    );
  }
  
  return (
    <Layout title="Querybook">
      <Container maxWidth={false} sx={{ mt: 4, mb: 4, height: 'calc(100vh - 128px)' }}>
        <Box sx={{ height: '100%' }}>
          <QuerybookFrame />
        </Box>
      </Container>
    </Layout>
  );
};

export default QuerybookPage;
