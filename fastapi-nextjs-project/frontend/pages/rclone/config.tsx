import React from 'react';
import Layout from '../../components/Layout';
import RcloneConfig from '../../components/rclone/RcloneConfig';

const RcloneConfigPage: React.FC = () => {
  return (
    <Layout title="Rclone Configuration">
      <RcloneConfig />
    </Layout>
  );
};

export default RcloneConfigPage;
