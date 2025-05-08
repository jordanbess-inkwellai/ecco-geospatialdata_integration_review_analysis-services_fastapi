import React from 'react';
import Layout from '../../components/Layout';
import RcloneFileBrowser from '../../components/rclone/RcloneFileBrowser';

const RcloneFileBrowserPage: React.FC = () => {
  return (
    <Layout title="Rclone File Browser">
      <RcloneFileBrowser />
    </Layout>
  );
};

export default RcloneFileBrowserPage;
