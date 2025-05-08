import React from 'react';
import Layout from '../../components/Layout';
import BoxIntegration from '../../components/rclone/BoxIntegration';

const BoxIntegrationPage: React.FC = () => {
  return (
    <Layout title="Box.com Integration">
      <BoxIntegration />
    </Layout>
  );
};

export default BoxIntegrationPage;
