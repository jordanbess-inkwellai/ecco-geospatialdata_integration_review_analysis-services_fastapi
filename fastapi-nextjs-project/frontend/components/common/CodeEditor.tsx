import React from 'react';
import { Box } from '@mui/material';
import Editor from '@monaco-editor/react';

interface CodeEditorProps {
  value: string;
  onChange: (value: string) => void;
  language?: string;
  height?: string;
  placeholder?: string;
  readOnly?: boolean;
}

const CodeEditor: React.FC<CodeEditorProps> = ({
  value,
  onChange,
  language = 'javascript',
  height = '300px',
  placeholder = '',
  readOnly = false
}) => {
  return (
    <Box sx={{ border: '1px solid #ccc', borderRadius: 1, overflow: 'hidden' }}>
      <Editor
        height={height}
        language={language}
        value={value}
        onChange={(value) => onChange(value || '')}
        options={{
          minimap: { enabled: false },
          scrollBeyondLastLine: false,
          wordWrap: 'on',
          wrappingIndent: 'same',
          automaticLayout: true,
          readOnly,
          lineNumbers: 'on',
          tabSize: 2,
          fontFamily: 'monospace',
          fontSize: 14
        }}
      />
    </Box>
  );
};

export default CodeEditor;
